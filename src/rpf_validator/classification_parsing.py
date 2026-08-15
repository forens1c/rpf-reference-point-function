# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Strict JSON parsing for classification proposal contract 0.1."""

from __future__ import annotations

import json
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import TypeVar

from rpf_validator.classification import (
    ClassificationProposal,
    ContentDigest,
    DigestAlgorithm,
    DigestCanonicalization,
    EvidenceFragment,
    FrameCandidate,
    ProposalInputReference,
    ProposalRole,
    ProposalUncertainty,
    ProviderKind,
    ProviderMetadata,
)
from rpf_validator.enums import ReferenceFrameClass, ReferenceFrameStatus
from rpf_validator.errors import InputValidationError

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


def _parse_digest(value: object, path: str) -> ContentDigest:
    data = _object(
        value,
        path,
        required=("algorithm", "canonicalization", "value"),
    )
    return _construct(
        ContentDigest,
        path,
        "digest",
        algorithm=_enum(
            data["algorithm"],
            DigestAlgorithm,
            _join(path, "algorithm"),
        ),
        canonicalization=_enum(
            data["canonicalization"],
            DigestCanonicalization,
            _join(path, "canonicalization"),
        ),
        value=data["value"],
    )


def _parse_provider(value: object, path: str) -> ProviderMetadata:
    data = _object(
        value,
        path,
        required=(
            "provider_id",
            "provider_version",
            "provider_kind",
            "configuration_digest",
        ),
        optional=("model_id", "model_version"),
    )
    return _construct(
        ProviderMetadata,
        path,
        "provider",
        provider_id=data["provider_id"],
        provider_version=data["provider_version"],
        provider_kind=_enum(
            data["provider_kind"],
            ProviderKind,
            _join(path, "provider_kind"),
        ),
        configuration_digest=_parse_digest(
            data["configuration_digest"],
            _join(path, "configuration_digest"),
        ),
        model_id=data.get("model_id"),
        model_version=data.get("model_version"),
    )


def _parse_input_reference(value: object, path: str) -> ProposalInputReference:
    data = _object(
        value,
        path,
        required=(
            "case_id",
            "assessment_subject_id",
            "source_id",
            "media_type",
            "payload_digest",
        ),
    )
    return _construct(
        ProposalInputReference,
        path,
        "input_reference",
        case_id=data["case_id"],
        assessment_subject_id=data["assessment_subject_id"],
        source_id=data["source_id"],
        media_type=data["media_type"],
        payload_digest=_parse_digest(
            data["payload_digest"],
            _join(path, "payload_digest"),
        ),
    )


def _parse_evidence_fragment(value: object, path: str) -> EvidenceFragment:
    data = _object(
        value,
        path,
        required=(
            "evidence_id",
            "source_id",
            "start_byte",
            "end_byte",
            "fragment_digest",
        ),
        optional=("excerpt",),
    )
    return _construct(
        EvidenceFragment,
        path,
        "evidence_fragment",
        evidence_id=data["evidence_id"],
        source_id=data["source_id"],
        start_byte=data["start_byte"],
        end_byte=data["end_byte"],
        fragment_digest=_parse_digest(
            data["fragment_digest"],
            _join(path, "fragment_digest"),
        ),
        excerpt=data.get("excerpt"),
    )


def _parse_candidate(value: object, path: str) -> FrameCandidate:
    data = _object(
        value,
        path,
        required=(
            "candidate_id",
            "status",
            "classes",
            "scope",
            "rationale",
            "provider_confidence",
            "provider_confidence_rationale",
            "confidence_scale_id",
            "evidence_ids",
            "assumptions",
        ),
    )
    classes = _array(
        data["classes"],
        _join(path, "classes"),
        lambda item, item_path: _enum(item, ReferenceFrameClass, item_path),
    )
    evidence_ids = _array(
        data["evidence_ids"],
        _join(path, "evidence_ids"),
        _string,
    )
    assumptions = _array(
        data["assumptions"],
        _join(path, "assumptions"),
        _string,
    )
    return _construct(
        FrameCandidate,
        path,
        "candidate",
        candidate_id=data["candidate_id"],
        status=_enum(
            data["status"],
            ReferenceFrameStatus,
            _join(path, "status"),
        ),
        classes=classes,
        scope=data["scope"],
        rationale=data["rationale"],
        provider_confidence=data["provider_confidence"],
        provider_confidence_rationale=data["provider_confidence_rationale"],
        confidence_scale_id=data["confidence_scale_id"],
        evidence_ids=evidence_ids,
        assumptions=assumptions,
    )


def _parse_uncertainty(value: object, path: str) -> ProposalUncertainty:
    data = _object(
        value,
        path,
        required=("uncertainty_id", "description", "affects_candidate_ids"),
    )
    affected = _array(
        data["affects_candidate_ids"],
        _join(path, "affects_candidate_ids"),
        _string,
    )
    return _construct(
        ProposalUncertainty,
        path,
        "uncertainty",
        uncertainty_id=data["uncertainty_id"],
        description=data["description"],
        affects_candidate_ids=affected,
    )


def parse_classification_proposal(value: object) -> ClassificationProposal:
    """Parse JSON-compatible primitives into a strict proposal model."""

    data = _object(
        value,
        "$",
        required=(
            "schema_version",
            "proposal_id",
            "proposal_role",
            "provider",
            "input_reference",
            "preferred_candidate_id",
            "candidates",
            "evidence_fragments",
            "uncertainties",
        ),
        optional=("generated_at",),
    )
    candidates = _array(data["candidates"], "$.candidates", _parse_candidate)
    evidence = _array(
        data["evidence_fragments"],
        "$.evidence_fragments",
        _parse_evidence_fragment,
    )
    uncertainties = _array(
        data["uncertainties"],
        "$.uncertainties",
        _parse_uncertainty,
    )
    return _construct(
        ClassificationProposal,
        "$",
        "classification_proposal",
        schema_version=data["schema_version"],
        proposal_id=data["proposal_id"],
        proposal_role=_enum(
            data["proposal_role"],
            ProposalRole,
            "$.proposal_role",
        ),
        provider=_parse_provider(data["provider"], "$.provider"),
        input_reference=_parse_input_reference(
            data["input_reference"],
            "$.input_reference",
        ),
        preferred_candidate_id=data["preferred_candidate_id"],
        candidates=candidates,
        evidence_fragments=evidence,
        uncertainties=uncertainties,
        generated_at=data.get("generated_at"),
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


def parse_classification_proposal_json(text: str) -> ClassificationProposal:
    """Parse strict RFC-compatible JSON text into a proposal."""

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
    return parse_classification_proposal(value)


def load_classification_proposal(path: str | Path) -> ClassificationProposal:
    """Read one UTF-8 JSON file and parse it as a proposal."""

    return parse_classification_proposal_json(
        Path(path).read_text(encoding="utf-8")
    )
