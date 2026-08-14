# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Strict, versioned JSON parsing for experimental RPF validator inputs."""

from __future__ import annotations

import json
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import TypeVar

from rpf_validator.enums import (
    CompetenceStatus,
    ReferenceFrameClass,
    ReferenceFrameStatus,
    RevisionScope,
)
from rpf_validator.errors import InputValidationError
from rpf_validator.models import (
    Calibration,
    CandidateAction,
    CompetenceAssessment,
    Conflict,
    DeclaredConstraint,
    EvidenceSource,
    ExpectedEffect,
    Hypothesis,
    Observation,
    ReferenceFrame,
    TerminationState,
    TimeHorizon,
    UncertaintyItem,
    UncertaintyReport,
    ValidatorConfig,
    ValidatorInput,
)

_T = TypeVar("_T")
_EnumT = TypeVar("_EnumT", bound=Enum)


class _DuplicateKeyError(ValueError):
    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(key)


class _NonStandardConstantError(ValueError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__(value)


def _join(path: str, suffix: str) -> str:
    return f"$.{suffix}" if path == "$" else f"{path}.{suffix}"


def _object(
    value: object,
    path: str,
    *,
    required: tuple[str, ...],
    optional: tuple[str, ...] = (),
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise InputValidationError(path, "must be a JSON object")
    if not all(isinstance(key, str) for key in value):
        raise InputValidationError(path, "must contain only string keys")

    allowed = set(required) | set(optional)
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise InputValidationError(
            path,
            "contains unknown fields: " + ", ".join(unknown),
        )
    missing = sorted(set(required) - set(value))
    if missing:
        raise InputValidationError(
            path,
            "is missing required fields: " + ", ".join(missing),
        )
    return value


def _array(
    value: object,
    path: str,
    parser: Callable[[object, str], _T],
) -> tuple[_T, ...]:
    if not isinstance(value, list):
        raise InputValidationError(path, "must be a JSON array")
    return tuple(parser(item, f"{path}[{index}]") for index, item in enumerate(value))


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise InputValidationError(path, "must be a string")
    return value


def _enum(value: object, expected: type[_EnumT], path: str) -> _EnumT:
    if not isinstance(value, str):
        raise InputValidationError(path, f"must be a {expected.__name__} string")
    try:
        return expected(value)
    except ValueError as exc:
        choices = ", ".join(item.value for item in expected)
        raise InputValidationError(path, f"must be one of: {choices}") from exc


def _construct(
    factory: Callable[..., _T],
    path: str,
    model_prefix: str | None,
    **values: object,
) -> _T:
    try:
        return factory(**values)
    except InputValidationError as exc:
        suffix = exc.path
        if model_prefix is not None:
            if suffix == model_prefix:
                raise InputValidationError(path, exc.message) from exc
            prefix = model_prefix + "."
            if suffix.startswith(prefix):
                suffix = suffix[len(prefix) :]
        raise InputValidationError(_join(path, suffix), exc.message) from exc


def _parse_observation(value: object, path: str) -> Observation:
    data = _object(
        value,
        path,
        required=("content", "provenance"),
        optional=("observed_at",),
    )
    return _construct(
        Observation,
        path,
        "observation",
        content=data["content"],
        provenance=data["provenance"],
        observed_at=data.get("observed_at"),
    )


def _parse_evidence_source(value: object, path: str) -> EvidenceSource:
    data = _object(
        value,
        path,
        required=("source_id", "description", "provenance", "quality_note"),
    )
    return _construct(
        EvidenceSource,
        path,
        "evidence_source",
        source_id=data["source_id"],
        description=data["description"],
        provenance=data["provenance"],
        quality_note=data["quality_note"],
    )


def _parse_competence(value: object, path: str) -> CompetenceAssessment:
    data = _object(
        value,
        path,
        required=("status", "rationale", "provenance"),
    )
    return _construct(
        CompetenceAssessment,
        path,
        "competence",
        status=_enum(data["status"], CompetenceStatus, _join(path, "status")),
        rationale=data["rationale"],
        provenance=data["provenance"],
    )


def _parse_calibration(value: object, path: str) -> Calibration:
    data = _object(
        value,
        path,
        required=(
            "internal_confidence",
            "internal_confidence_rationale",
            "external_evidence",
            "external_evidence_rationale",
        ),
        optional=("evidence_sources", "scale_id"),
    )
    sources = _array(
        data.get("evidence_sources", []),
        _join(path, "evidence_sources"),
        _parse_evidence_source,
    )
    return _construct(
        Calibration,
        path,
        "calibration",
        internal_confidence=data["internal_confidence"],
        internal_confidence_rationale=data["internal_confidence_rationale"],
        external_evidence=data["external_evidence"],
        external_evidence_rationale=data["external_evidence_rationale"],
        evidence_sources=sources,
        scale_id=data.get("scale_id", "unit-interval-0.1"),
    )


def _parse_conflict(value: object, path: str) -> Conflict:
    data = _object(
        value,
        path,
        required=("present", "revision_scope"),
    )
    return _construct(
        Conflict,
        path,
        "conflict",
        present=data["present"],
        revision_scope=_enum(
            data["revision_scope"],
            RevisionScope,
            _join(path, "revision_scope"),
        ),
    )


def _parse_constraint(value: object, path: str) -> DeclaredConstraint:
    data = _object(
        value,
        path,
        required=("code", "description", "hard"),
    )
    return _construct(
        DeclaredConstraint,
        path,
        "constraint",
        code=data["code"],
        description=data["description"],
        hard=data["hard"],
    )


def _parse_reference_frame(value: object, path: str) -> ReferenceFrame:
    data = _object(
        value,
        path,
        required=("status",),
        optional=("classes", "scope", "assumptions", "constraints"),
    )
    classes = _array(
        data.get("classes", []),
        _join(path, "classes"),
        lambda item, item_path: _enum(item, ReferenceFrameClass, item_path),
    )
    assumptions = _array(
        data.get("assumptions", []),
        _join(path, "assumptions"),
        _string,
    )
    constraints = _array(
        data.get("constraints", []),
        _join(path, "constraints"),
        _parse_constraint,
    )
    return _construct(
        ReferenceFrame,
        path,
        "reference_frame",
        status=_enum(
            data["status"],
            ReferenceFrameStatus,
            _join(path, "status"),
        ),
        classes=classes,
        scope=data.get("scope"),
        assumptions=assumptions,
        constraints=constraints,
    )


def _parse_hypothesis(value: object, path: str) -> Hypothesis:
    data = _object(
        value,
        path,
        required=("hypothesis_id", "statement"),
        optional=("evidence_source_ids", "internal_confidence"),
    )
    evidence_source_ids = _array(
        data.get("evidence_source_ids", []),
        _join(path, "evidence_source_ids"),
        _string,
    )
    return _construct(
        Hypothesis,
        path,
        "hypothesis",
        hypothesis_id=data["hypothesis_id"],
        statement=data["statement"],
        evidence_source_ids=evidence_source_ids,
        internal_confidence=data.get("internal_confidence"),
    )


def _parse_termination(value: object, path: str) -> TerminationState:
    data = _object(
        value,
        path,
        required=(
            "information_gain",
            "information_gain_epsilon",
            "iteration",
            "max_iterations",
            "elapsed_ms",
            "max_time_ms",
            "budget_remaining",
            "budget_minimum",
        ),
        optional=("reflexive", "recursion_depth", "max_recursion_depth"),
    )
    return _construct(
        TerminationState,
        path,
        "termination",
        information_gain=data["information_gain"],
        information_gain_epsilon=data["information_gain_epsilon"],
        iteration=data["iteration"],
        max_iterations=data["max_iterations"],
        elapsed_ms=data["elapsed_ms"],
        max_time_ms=data["max_time_ms"],
        budget_remaining=data["budget_remaining"],
        budget_minimum=data["budget_minimum"],
        reflexive=data.get("reflexive", False),
        recursion_depth=data.get("recursion_depth", 0),
        max_recursion_depth=data.get("max_recursion_depth"),
    )


def _parse_time_horizon(value: object, path: str) -> TimeHorizon:
    data = _object(
        value,
        path,
        required=("horizon_id", "label", "order"),
    )
    return _construct(
        TimeHorizon,
        path,
        "time_horizon",
        horizon_id=data["horizon_id"],
        label=data["label"],
        order=data["order"],
    )


def _parse_effect(value: object, path: str) -> ExpectedEffect:
    data = _object(
        value,
        path,
        required=("horizon_id", "expected_benefit", "expected_cost"),
        optional=("constraint_conflicts",),
    )
    conflicts = _array(
        data.get("constraint_conflicts", []),
        _join(path, "constraint_conflicts"),
        _string,
    )
    return _construct(
        ExpectedEffect,
        path,
        "effect",
        horizon_id=data["horizon_id"],
        expected_benefit=data["expected_benefit"],
        expected_cost=data["expected_cost"],
        constraint_conflicts=conflicts,
    )


def _parse_action(value: object, path: str) -> CandidateAction:
    data = _object(
        value,
        path,
        required=(
            "action_id",
            "description",
            "effects",
            "reversible",
            "rationale",
        ),
        optional=("rollback_cost",),
    )
    effects = _array(
        data["effects"],
        _join(path, "effects"),
        _parse_effect,
    )
    return _construct(
        CandidateAction,
        path,
        "candidate_action",
        action_id=data["action_id"],
        description=data["description"],
        effects=effects,
        reversible=data["reversible"],
        rationale=data["rationale"],
        rollback_cost=data.get("rollback_cost"),
    )


def _parse_uncertainty_item(value: object, path: str) -> UncertaintyItem:
    data = _object(
        value,
        path,
        required=("item_id", "description"),
        optional=("missing_information",),
    )
    missing_information = _array(
        data.get("missing_information", []),
        _join(path, "missing_information"),
        _string,
    )
    return _construct(
        UncertaintyItem,
        path,
        "uncertainty_item",
        item_id=data["item_id"],
        description=data["description"],
        missing_information=missing_information,
    )


def _parse_uncertainty_report(value: object, path: str) -> UncertaintyReport:
    data = _object(
        value,
        path,
        required=(),
        optional=("items", "empty_rationale"),
    )
    items = _array(
        data.get("items", []),
        _join(path, "items"),
        _parse_uncertainty_item,
    )
    return _construct(
        UncertaintyReport,
        path,
        "residual_uncertainty",
        items=items,
        empty_rationale=data.get("empty_rationale"),
    )


def _parse_config(value: object, path: str) -> ValidatorConfig:
    data = _object(
        value,
        path,
        required=("config_id",),
        optional=(
            "minimum_time_horizons",
            "calibration_values_comparable",
            "confidence_evidence_divergence_threshold",
        ),
    )
    return _construct(
        ValidatorConfig,
        path,
        "validator_config",
        config_id=data["config_id"],
        minimum_time_horizons=data.get("minimum_time_horizons", 2),
        calibration_values_comparable=data.get(
            "calibration_values_comparable",
            False,
        ),
        confidence_evidence_divergence_threshold=data.get(
            "confidence_evidence_divergence_threshold"
        ),
    )


def parse_input(value: object) -> ValidatorInput:
    """Parse JSON-compatible primitives into a strict ``ValidatorInput``."""

    data = _object(
        value,
        "$",
        required=(
            "schema_version",
            "case_id",
            "observation",
            "problem_domain",
            "competence",
            "calibration",
            "conflict",
            "reference_frame",
            "hypotheses",
            "termination",
            "time_horizons",
            "candidate_actions",
            "residual_uncertainty",
            "validator_config",
        ),
        optional=("selected_action_id", "selection_rationale"),
    )
    hypotheses = _array(
        data["hypotheses"],
        "$.hypotheses",
        _parse_hypothesis,
    )
    horizons = _array(
        data["time_horizons"],
        "$.time_horizons",
        _parse_time_horizon,
    )
    actions = _array(
        data["candidate_actions"],
        "$.candidate_actions",
        _parse_action,
    )
    return _construct(
        ValidatorInput,
        "$",
        None,
        schema_version=data["schema_version"],
        case_id=data["case_id"],
        observation=_parse_observation(data["observation"], "$.observation"),
        problem_domain=data["problem_domain"],
        competence=_parse_competence(data["competence"], "$.competence"),
        calibration=_parse_calibration(data["calibration"], "$.calibration"),
        conflict=_parse_conflict(data["conflict"], "$.conflict"),
        reference_frame=_parse_reference_frame(
            data["reference_frame"],
            "$.reference_frame",
        ),
        hypotheses=hypotheses,
        termination=_parse_termination(data["termination"], "$.termination"),
        time_horizons=horizons,
        candidate_actions=actions,
        residual_uncertainty=_parse_uncertainty_report(
            data["residual_uncertainty"],
            "$.residual_uncertainty",
        ),
        validator_config=_parse_config(
            data["validator_config"],
            "$.validator_config",
        ),
        selected_action_id=data.get("selected_action_id"),
        selection_rationale=data.get("selection_rationale"),
    )


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _reject_non_standard_constant(value: str) -> object:
    raise _NonStandardConstantError(value)


def parse_json(text: str) -> ValidatorInput:
    """Parse strict RFC-compatible JSON text into ``ValidatorInput``."""

    if not isinstance(text, str):
        raise InputValidationError("$", "must be JSON text")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_standard_constant,
        )
    except json.JSONDecodeError as exc:
        raise InputValidationError(
            "$",
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        ) from exc
    except _DuplicateKeyError as exc:
        raise InputValidationError(
            "$",
            f"contains duplicate object key {exc.key!r}",
        ) from exc
    except _NonStandardConstantError as exc:
        raise InputValidationError(
            "$",
            f"contains non-standard numeric constant {exc.value!r}",
        ) from exc
    return parse_input(value)


def load_input(path: str | Path) -> ValidatorInput:
    """Read one UTF-8 JSON file and parse it as ``ValidatorInput``."""

    return parse_json(Path(path).read_text(encoding="utf-8"))
