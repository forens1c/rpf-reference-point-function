# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Immutable input and output models for the experimental RPF validator.

The classes in this module validate structure, ranges, identifiers, and
references. They deliberately do not decide whether an RPF rule is satisfied.
Domain-level unknowns remain representable so that missing knowledge is not
confused with malformed input.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from numbers import Real
from typing import TypeVar

from rpf_validator.enums import (
    CompetenceStatus,
    ProcessStatus,
    ReasonCode,
    ReferenceFrameClass,
    ReferenceFrameStatus,
    RevisionScope,
    RuleId,
    RuleStatus,
)
from rpf_validator.errors import InputValidationError

INPUT_SCHEMA_VERSION = "rpf-validator-input-0.1"
RESULT_SCHEMA_VERSION = "rpf-validator-result-0.1"

_EnumT = TypeVar("_EnumT")


def _non_empty(value: object, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InputValidationError(path, "must be a non-empty string")


def _optional_non_empty(value: object, path: str) -> None:
    if value is not None:
        _non_empty(value, path)


def _enum(value: object, expected: type[_EnumT], path: str) -> None:
    if not isinstance(value, expected):
        raise InputValidationError(path, f"must be {expected.__name__}")


def _boolean(value: object, path: str) -> None:
    if not isinstance(value, bool):
        raise InputValidationError(path, "must be a boolean")


def _tuple(value: object, item_type: type[object], path: str) -> None:
    if not isinstance(value, tuple):
        raise InputValidationError(path, "must be a tuple")
    for index, item in enumerate(value):
        if not isinstance(item, item_type):
            raise InputValidationError(
                f"{path}[{index}]", f"must be {item_type.__name__}"
            )


def _string_tuple(value: object, path: str) -> None:
    _tuple(value, str, path)
    for index, item in enumerate(value):
        _non_empty(item, f"{path}[{index}]")


def _unit_interval(value: object, path: str, *, optional: bool = False) -> None:
    if value is None and optional:
        return
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputValidationError(path, "must be a number from 0.0 to 1.0")
    numeric = float(value)
    if not isfinite(numeric) or not 0.0 <= numeric <= 1.0:
        raise InputValidationError(path, "must be between 0.0 and 1.0")


def _non_negative(value: object, path: str, *, optional: bool = False) -> None:
    if value is None and optional:
        return
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputValidationError(path, "must be a non-negative number")
    numeric = float(value)
    if not isfinite(numeric) or numeric < 0.0:
        raise InputValidationError(path, "must be finite and non-negative")


def _non_negative_int(value: object, path: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InputValidationError(path, "must be a non-negative integer")


def _positive_int(value: object, path: str, *, optional: bool = False) -> None:
    if value is None and optional:
        return
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise InputValidationError(path, "must be a positive integer")


def _positive_number(value: object, path: str, *, optional: bool = False) -> None:
    if value is None and optional:
        return
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputValidationError(path, "must be a positive number")
    numeric = float(value)
    if not isfinite(numeric) or numeric <= 0:
        raise InputValidationError(path, "must be finite and positive")


def _unique(values: tuple[str, ...], path: str) -> None:
    if len(values) != len(set(values)):
        raise InputValidationError(path, "must contain unique identifiers")


@dataclass(frozen=True, slots=True)
class Observation:
    """Observed content kept separate from attributed meaning."""

    content: str
    provenance: str
    observed_at: str | None = None

    def __post_init__(self) -> None:
        _non_empty(self.content, "observation.content")
        _non_empty(self.provenance, "observation.provenance")
        _optional_non_empty(self.observed_at, "observation.observed_at")


@dataclass(frozen=True, slots=True)
class EvidenceSource:
    """Traceable source used to justify declared external evidence."""

    source_id: str
    description: str
    provenance: str
    quality_note: str

    def __post_init__(self) -> None:
        _non_empty(self.source_id, "evidence_source.source_id")
        _non_empty(self.description, "evidence_source.description")
        _non_empty(self.provenance, "evidence_source.provenance")
        _non_empty(self.quality_note, "evidence_source.quality_note")


@dataclass(frozen=True, slots=True)
class CompetenceAssessment:
    """Declared competence fit for one named problem domain."""

    status: CompetenceStatus
    rationale: str
    provenance: str

    def __post_init__(self) -> None:
        _enum(self.status, CompetenceStatus, "competence.status")
        _non_empty(self.rationale, "competence.rationale")
        _non_empty(self.provenance, "competence.provenance")


@dataclass(frozen=True, slots=True)
class Calibration:
    """Separate representations of internal confidence and external evidence."""

    internal_confidence: float | None
    internal_confidence_rationale: str
    external_evidence: float | None
    external_evidence_rationale: str
    evidence_sources: tuple[EvidenceSource, ...] = field(default_factory=tuple)
    scale_id: str = "unit-interval-0.1"

    def __post_init__(self) -> None:
        _unit_interval(
            self.internal_confidence,
            "calibration.internal_confidence",
            optional=True,
        )
        _non_empty(
            self.internal_confidence_rationale,
            "calibration.internal_confidence_rationale",
        )
        _unit_interval(
            self.external_evidence,
            "calibration.external_evidence",
            optional=True,
        )
        _non_empty(
            self.external_evidence_rationale,
            "calibration.external_evidence_rationale",
        )
        _tuple(self.evidence_sources, EvidenceSource, "calibration.evidence_sources")
        _unique(
            tuple(source.source_id for source in self.evidence_sources),
            "calibration.evidence_sources",
        )
        _non_empty(self.scale_id, "calibration.scale_id")


@dataclass(frozen=True, slots=True)
class Conflict:
    """Whether a conflict exists and how broadly revision is proposed."""

    present: bool
    revision_scope: RevisionScope

    def __post_init__(self) -> None:
        _boolean(self.present, "conflict.present")
        _enum(self.revision_scope, RevisionScope, "conflict.revision_scope")


@dataclass(frozen=True, slots=True)
class DeclaredConstraint:
    """Constraint supplied to the validator rather than invented by it."""

    code: str
    description: str
    hard: bool

    def __post_init__(self) -> None:
        _non_empty(self.code, "constraint.code")
        _non_empty(self.description, "constraint.description")
        _boolean(self.hard, "constraint.hard")


@dataclass(frozen=True, slots=True)
class ReferenceFrame:
    """Declared status, classes, scope, assumptions, and constraints."""

    status: ReferenceFrameStatus
    classes: tuple[ReferenceFrameClass, ...] = field(default_factory=tuple)
    scope: str | None = None
    assumptions: tuple[str, ...] = field(default_factory=tuple)
    constraints: tuple[DeclaredConstraint, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _enum(self.status, ReferenceFrameStatus, "reference_frame.status")
        _tuple(self.classes, ReferenceFrameClass, "reference_frame.classes")
        if len(self.classes) != len(set(self.classes)):
            raise InputValidationError(
                "reference_frame.classes", "must not contain duplicates"
            )
        _optional_non_empty(self.scope, "reference_frame.scope")
        _string_tuple(self.assumptions, "reference_frame.assumptions")
        _tuple(
            self.constraints,
            DeclaredConstraint,
            "reference_frame.constraints",
        )
        _unique(
            tuple(constraint.code for constraint in self.constraints),
            "reference_frame.constraints",
        )


@dataclass(frozen=True, slots=True)
class Hypothesis:
    """One explicitly identified, testable interpretation."""

    hypothesis_id: str
    statement: str
    evidence_source_ids: tuple[str, ...] = field(default_factory=tuple)
    internal_confidence: float | None = None

    def __post_init__(self) -> None:
        _non_empty(self.hypothesis_id, "hypothesis.hypothesis_id")
        _non_empty(self.statement, "hypothesis.statement")
        _string_tuple(self.evidence_source_ids, "hypothesis.evidence_source_ids")
        _unique(self.evidence_source_ids, "hypothesis.evidence_source_ids")
        _unit_interval(
            self.internal_confidence,
            "hypothesis.internal_confidence",
            optional=True,
        )


@dataclass(frozen=True, slots=True)
class TerminationState:
    """Current information-gain, iteration, time, resource, and reflexive state."""

    information_gain: float | None
    information_gain_epsilon: float | None
    iteration: int
    max_iterations: int | None
    elapsed_ms: float
    max_time_ms: float | None
    budget_remaining: float | None
    budget_minimum: float | None
    reflexive: bool = False
    recursion_depth: int = 0
    max_recursion_depth: int | None = None

    def __post_init__(self) -> None:
        _non_negative(
            self.information_gain,
            "termination.information_gain",
            optional=True,
        )
        _non_negative(
            self.information_gain_epsilon,
            "termination.information_gain_epsilon",
            optional=True,
        )
        _non_negative_int(self.iteration, "termination.iteration")
        _positive_int(
            self.max_iterations,
            "termination.max_iterations",
            optional=True,
        )
        _non_negative(self.elapsed_ms, "termination.elapsed_ms")
        _positive_number(
            self.max_time_ms,
            "termination.max_time_ms",
            optional=True,
        )
        _non_negative(
            self.budget_remaining,
            "termination.budget_remaining",
            optional=True,
        )
        _non_negative(
            self.budget_minimum,
            "termination.budget_minimum",
            optional=True,
        )
        _boolean(self.reflexive, "termination.reflexive")
        _non_negative_int(self.recursion_depth, "termination.recursion_depth")
        _positive_int(
            self.max_recursion_depth,
            "termination.max_recursion_depth",
            optional=True,
        )

    @property
    def has_hard_bound(self) -> bool:
        """Whether at least one iteration, time, or resource bound is explicit."""

        has_resource_bound = (
            self.budget_remaining is not None and self.budget_minimum is not None
        )
        return (
            self.max_iterations is not None
            or self.max_time_ms is not None
            or has_resource_bound
        )


@dataclass(frozen=True, slots=True)
class TimeHorizon:
    """One named horizon used for temporal comparison."""

    horizon_id: str
    label: str
    order: int

    def __post_init__(self) -> None:
        _non_empty(self.horizon_id, "time_horizon.horizon_id")
        _non_empty(self.label, "time_horizon.label")
        _non_negative_int(self.order, "time_horizon.order")


@dataclass(frozen=True, slots=True)
class ExpectedEffect:
    """Qualitative action effect for one configured time horizon."""

    horizon_id: str
    expected_benefit: str
    expected_cost: str
    constraint_conflicts: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _non_empty(self.horizon_id, "effect.horizon_id")
        _non_empty(self.expected_benefit, "effect.expected_benefit")
        _non_empty(self.expected_cost, "effect.expected_cost")
        _string_tuple(self.constraint_conflicts, "effect.constraint_conflicts")
        _unique(self.constraint_conflicts, "effect.constraint_conflicts")


@dataclass(frozen=True, slots=True)
class CandidateAction:
    """Action option with temporal effects and reversibility metadata."""

    action_id: str
    description: str
    effects: tuple[ExpectedEffect, ...]
    reversible: bool
    rationale: str
    rollback_cost: str | None = None

    def __post_init__(self) -> None:
        _non_empty(self.action_id, "candidate_action.action_id")
        _non_empty(self.description, "candidate_action.description")
        _tuple(self.effects, ExpectedEffect, "candidate_action.effects")
        _unique(
            tuple(effect.horizon_id for effect in self.effects),
            "candidate_action.effects",
        )
        _boolean(self.reversible, "candidate_action.reversible")
        _non_empty(self.rationale, "candidate_action.rationale")
        _optional_non_empty(self.rollback_cost, "candidate_action.rollback_cost")


@dataclass(frozen=True, slots=True)
class UncertaintyItem:
    """One unresolved question or missing piece of information."""

    item_id: str
    description: str
    missing_information: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _non_empty(self.item_id, "uncertainty_item.item_id")
        _non_empty(self.description, "uncertainty_item.description")
        _string_tuple(
            self.missing_information,
            "uncertainty_item.missing_information",
        )


@dataclass(frozen=True, slots=True)
class UncertaintyReport:
    """Residual uncertainty plus an optional rationale for an empty report."""

    items: tuple[UncertaintyItem, ...] = field(default_factory=tuple)
    empty_rationale: str | None = None

    def __post_init__(self) -> None:
        _tuple(self.items, UncertaintyItem, "residual_uncertainty.items")
        _unique(
            tuple(item.item_id for item in self.items),
            "residual_uncertainty.items",
        )
        _optional_non_empty(
            self.empty_rationale,
            "residual_uncertainty.empty_rationale",
        )


@dataclass(frozen=True, slots=True)
class ValidatorConfig:
    """Traceable prototype settings; no threshold is canonical RPF."""

    config_id: str
    minimum_time_horizons: int = 2
    calibration_values_comparable: bool = False
    confidence_evidence_divergence_threshold: float | None = None

    def __post_init__(self) -> None:
        _non_empty(self.config_id, "validator_config.config_id")
        _positive_int(
            self.minimum_time_horizons,
            "validator_config.minimum_time_horizons",
        )
        if self.minimum_time_horizons < 2:
            raise InputValidationError(
                "validator_config.minimum_time_horizons",
                "must be at least 2",
            )
        _boolean(
            self.calibration_values_comparable,
            "validator_config.calibration_values_comparable",
        )
        _unit_interval(
            self.confidence_evidence_divergence_threshold,
            "validator_config.confidence_evidence_divergence_threshold",
            optional=True,
        )
        if (
            self.confidence_evidence_divergence_threshold is not None
            and not self.calibration_values_comparable
        ):
            raise InputValidationError(
                "validator_config.confidence_evidence_divergence_threshold",
                "requires calibration_values_comparable=True",
            )


@dataclass(frozen=True, slots=True)
class ValidatorInput:
    """Complete structural input for a future deterministic validator run."""

    schema_version: str
    case_id: str
    observation: Observation
    problem_domain: str
    competence: CompetenceAssessment
    calibration: Calibration
    conflict: Conflict
    reference_frame: ReferenceFrame
    hypotheses: tuple[Hypothesis, ...]
    termination: TerminationState
    time_horizons: tuple[TimeHorizon, ...]
    candidate_actions: tuple[CandidateAction, ...]
    residual_uncertainty: UncertaintyReport
    validator_config: ValidatorConfig

    def __post_init__(self) -> None:
        if self.schema_version != INPUT_SCHEMA_VERSION:
            raise InputValidationError(
                "schema_version",
                f"must equal {INPUT_SCHEMA_VERSION!r}",
            )
        _non_empty(self.case_id, "case_id")
        if not isinstance(self.observation, Observation):
            raise InputValidationError("observation", "must be Observation")
        _non_empty(self.problem_domain, "problem_domain")
        if not isinstance(self.competence, CompetenceAssessment):
            raise InputValidationError("competence", "must be CompetenceAssessment")
        if not isinstance(self.calibration, Calibration):
            raise InputValidationError("calibration", "must be Calibration")
        if not isinstance(self.conflict, Conflict):
            raise InputValidationError("conflict", "must be Conflict")
        if not isinstance(self.reference_frame, ReferenceFrame):
            raise InputValidationError(
                "reference_frame", "must be ReferenceFrame"
            )
        _tuple(self.hypotheses, Hypothesis, "hypotheses")
        _unique(
            tuple(hypothesis.hypothesis_id for hypothesis in self.hypotheses),
            "hypotheses",
        )
        if not isinstance(self.termination, TerminationState):
            raise InputValidationError("termination", "must be TerminationState")
        _tuple(self.time_horizons, TimeHorizon, "time_horizons")
        _unique(
            tuple(horizon.horizon_id for horizon in self.time_horizons),
            "time_horizons",
        )
        horizon_orders = tuple(str(horizon.order) for horizon in self.time_horizons)
        _unique(horizon_orders, "time_horizons.order")
        _tuple(self.candidate_actions, CandidateAction, "candidate_actions")
        _unique(
            tuple(action.action_id for action in self.candidate_actions),
            "candidate_actions",
        )
        if not isinstance(self.residual_uncertainty, UncertaintyReport):
            raise InputValidationError(
                "residual_uncertainty", "must be UncertaintyReport"
            )
        if not isinstance(self.validator_config, ValidatorConfig):
            raise InputValidationError(
                "validator_config", "must be ValidatorConfig"
            )
        self._validate_references()

    def _validate_references(self) -> None:
        evidence_ids = {
            source.source_id for source in self.calibration.evidence_sources
        }
        for hypothesis_index, hypothesis in enumerate(self.hypotheses):
            unknown_sources = set(hypothesis.evidence_source_ids) - evidence_ids
            if unknown_sources:
                unknown = ", ".join(sorted(unknown_sources))
                raise InputValidationError(
                    f"hypotheses[{hypothesis_index}].evidence_source_ids",
                    f"contains unknown source identifiers: {unknown}",
                )

        horizon_ids = {horizon.horizon_id for horizon in self.time_horizons}
        constraint_codes = {
            constraint.code for constraint in self.reference_frame.constraints
        }
        for action_index, action in enumerate(self.candidate_actions):
            for effect_index, effect in enumerate(action.effects):
                if effect.horizon_id not in horizon_ids:
                    raise InputValidationError(
                        (
                            f"candidate_actions[{action_index}]"
                            f".effects[{effect_index}].horizon_id"
                        ),
                        f"references unknown horizon {effect.horizon_id!r}",
                    )
                unknown_constraints = (
                    set(effect.constraint_conflicts) - constraint_codes
                )
                if unknown_constraints:
                    unknown = ", ".join(sorted(unknown_constraints))
                    raise InputValidationError(
                        (
                            f"candidate_actions[{action_index}]"
                            f".effects[{effect_index}].constraint_conflicts"
                        ),
                        f"contains unknown constraint codes: {unknown}",
                    )


@dataclass(frozen=True, slots=True)
class RuleResult:
    """Machine-readable and human-readable result for one RPF rule."""

    rule_id: RuleId
    status: RuleStatus
    rationale: str
    reason_codes: tuple[ReasonCode, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _enum(self.rule_id, RuleId, "rule_result.rule_id")
        _enum(self.status, RuleStatus, "rule_result.status")
        _non_empty(self.rationale, "rule_result.rationale")
        _tuple(self.reason_codes, ReasonCode, "rule_result.reason_codes")
        if len(self.reason_codes) != len(set(self.reason_codes)):
            raise InputValidationError(
                "rule_result.reason_codes", "must not contain duplicates"
            )


@dataclass(frozen=True, slots=True)
class ValidatorResult:
    """Aggregate process result; PASS may retain explicit uncertainty."""

    schema_version: str
    case_id: str
    overall_status: ProcessStatus
    rule_results: tuple[RuleResult, ...]
    residual_uncertainty: tuple[str, ...]
    next_step: str
    config_id: str

    def __post_init__(self) -> None:
        if self.schema_version != RESULT_SCHEMA_VERSION:
            raise InputValidationError(
                "schema_version",
                f"must equal {RESULT_SCHEMA_VERSION!r}",
            )
        _non_empty(self.case_id, "case_id")
        _enum(self.overall_status, ProcessStatus, "overall_status")
        _tuple(self.rule_results, RuleResult, "rule_results")
        if len({result.rule_id for result in self.rule_results}) != len(
            self.rule_results
        ):
            raise InputValidationError(
                "rule_results", "must contain at most one result per rule"
            )
        _string_tuple(self.residual_uncertainty, "residual_uncertainty")
        _non_empty(self.next_step, "next_step")
        _non_empty(self.config_id, "config_id")
