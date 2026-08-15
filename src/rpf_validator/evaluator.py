# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Deterministic evaluation of the experimental RPF process rules.

The evaluator operates only on already validated :class:`ValidatorInput`
objects. It reads declared values and thresholds; it does not infer truth,
measure competence, select an action, or consult a wall clock.
"""

from __future__ import annotations

from collections.abc import Callable

from rpf_validator.enums import (
    PROCESS_STATUS_PRIORITY,
    CompetenceStatus,
    ProcessStatus,
    ReasonCode,
    ReferenceFrameStatus,
    RevisionScope,
    RuleId,
    RuleStatus,
)
from rpf_validator.errors import InputValidationError
from rpf_validator.models import (
    RESULT_SCHEMA_VERSION,
    CandidateAction,
    RuleResult,
    ValidatorInput,
    ValidatorResult,
)

RuleEvaluation = tuple[RuleResult, ProcessStatus]
RuleEvaluator = Callable[[ValidatorInput], RuleEvaluation]


def _result(
    rule_id: RuleId,
    status: RuleStatus,
    rationale: str,
    *reason_codes: ReasonCode,
) -> RuleResult:
    return RuleResult(
        rule_id=rule_id,
        status=status,
        rationale=rationale,
        reason_codes=reason_codes,
    )


def _evaluate_a1(model: ValidatorInput) -> RuleEvaluation:
    status = model.competence.status
    if status is CompetenceStatus.INSUFFICIENT:
        return (
            _result(
                RuleId.A1,
                RuleStatus.TRIGGERED,
                "Declared competence is insufficient for the named problem domain.",
                ReasonCode.COMPETENCE_INSUFFICIENT,
            ),
            ProcessStatus.DELEGATE,
        )
    if status is CompetenceStatus.UNKNOWN:
        return (
            _result(
                RuleId.A1,
                RuleStatus.TRIGGERED,
                "Competence fit is explicitly unknown for the named problem domain.",
                ReasonCode.COMPETENCE_UNKNOWN,
            ),
            ProcessStatus.DELEGATE,
        )
    return (
        _result(
            RuleId.A1,
            RuleStatus.SATISFIED,
            "Declared competence is sufficient and has separate rationale "
            "and provenance.",
        ),
        ProcessStatus.PASS,
    )


def _evaluate_a2(model: ValidatorInput) -> RuleEvaluation:
    calibration = model.calibration
    config = model.validator_config
    codes: list[ReasonCode] = []
    details: list[str] = []

    if (
        calibration.external_evidence is not None
        and not calibration.evidence_sources
    ):
        codes.append(ReasonCode.CALIBRATION_NOT_SEPARATED)
        details.append("external evidence has no traceable evidence source")

    threshold = config.confidence_evidence_divergence_threshold
    if (
        config.calibration_values_comparable
        and threshold is not None
        and calibration.internal_confidence is not None
        and calibration.external_evidence is not None
    ):
        divergence = abs(
            calibration.internal_confidence - calibration.external_evidence
        )
        if divergence > threshold:
            codes.append(ReasonCode.CONFIDENCE_EVIDENCE_DIVERGENCE)
            details.append(
                f"declared divergence {divergence:.6g} exceeds configured "
                f"threshold {threshold:.6g}"
            )

    if codes:
        return (
            _result(
                RuleId.A2,
                RuleStatus.SIGNAL,
                "Dual calibration produced a signal: " + "; ".join(details) + ".",
                *codes,
            ),
            ProcessStatus.WARN,
        )

    return (
        _result(
            RuleId.A2,
            RuleStatus.SATISFIED,
            "Internal confidence and external evidence remain explicitly separate; "
            "no configured divergence signal was triggered.",
        ),
        ProcessStatus.PASS,
    )


def _evaluate_a3(model: ValidatorInput) -> RuleEvaluation:
    state = model.termination
    if not state.has_hard_bound:
        return (
            _result(
                RuleId.A3,
                RuleStatus.TRIGGERED,
                "No explicit iteration, time, or resource termination bound "
                "is available.",
                ReasonCode.TERMINATION_BOUND_MISSING,
            ),
            ProcessStatus.STOP,
        )

    reached: list[tuple[ReasonCode, str]] = []
    if (
        state.information_gain is not None
        and state.information_gain_epsilon is not None
        and state.information_gain <= state.information_gain_epsilon
    ):
        reached.append(
            (
                ReasonCode.INFORMATION_GAIN_LIMIT,
                f"information gain {state.information_gain:.6g} <= "
                f"epsilon {state.information_gain_epsilon:.6g}",
            )
        )
    if (
        state.max_iterations is not None
        and state.iteration >= state.max_iterations
    ):
        reached.append(
            (
                ReasonCode.ITERATION_LIMIT,
                f"iteration {state.iteration} >= maximum "
                f"{state.max_iterations}",
            )
        )
    if state.max_time_ms is not None and state.elapsed_ms >= state.max_time_ms:
        reached.append(
            (
                ReasonCode.TIME_LIMIT,
                f"elapsed time {state.elapsed_ms:.6g} ms >= maximum "
                f"{state.max_time_ms:.6g} ms",
            )
        )
    if (
        state.budget_remaining is not None
        and state.budget_minimum is not None
        and state.budget_remaining <= state.budget_minimum
    ):
        reached.append(
            (
                ReasonCode.RESOURCE_LIMIT,
                f"remaining budget {state.budget_remaining:.6g} <= minimum "
                f"{state.budget_minimum:.6g}",
            )
        )

    if reached:
        return (
            _result(
                RuleId.A3,
                RuleStatus.TRIGGERED,
                "One or more declared termination conditions were reached: "
                + "; ".join(detail for _, detail in reached)
                + ".",
                *(code for code, _ in reached),
            ),
            ProcessStatus.STOP,
        )

    return (
        _result(
            RuleId.A3,
            RuleStatus.SATISFIED,
            "At least one hard termination bound is declared and none is reached.",
        ),
        ProcessStatus.PASS,
    )


def _selected_action(model: ValidatorInput) -> CandidateAction | None:
    if model.selected_action_id is None:
        return None
    return next(
        action
        for action in model.candidate_actions
        if action.action_id == model.selected_action_id
    )


def _hard_constraint_conflicts(model: ValidatorInput) -> tuple[str, ...]:
    selected = _selected_action(model)
    if selected is None:
        return ()
    hard_codes = {
        constraint.code
        for constraint in model.reference_frame.constraints
        if constraint.hard
    }
    return tuple(
        sorted(
            {
                code
                for effect in selected.effects
                for code in effect.constraint_conflicts
                if code in hard_codes
            }
        )
    )


def _evaluate_a4(model: ValidatorInput) -> RuleEvaluation:
    minimum = model.validator_config.minimum_time_horizons
    incomplete_actions = tuple(
        action.action_id
        for action in model.candidate_actions
        if len({effect.horizon_id for effect in action.effects}) < minimum
    )
    missing_horizons = len(model.time_horizons) < minimum or bool(
        incomplete_actions
    )
    hard_conflicts = _hard_constraint_conflicts(model)

    codes: list[ReasonCode] = []
    details: list[str] = []
    if missing_horizons:
        codes.append(ReasonCode.TIME_HORIZON_MISSING)
        if len(model.time_horizons) < minimum:
            details.append(
                f"only {len(model.time_horizons)} of {minimum} required "
                "horizons are declared"
            )
        if incomplete_actions:
            details.append(
                "actions without the required horizon coverage: "
                + ", ".join(incomplete_actions)
            )
    if hard_conflicts:
        codes.append(ReasonCode.DECLARED_CONSTRAINT_CONFLICT)
        details.append(
            "the selected action conflicts with hard constraints: "
            + ", ".join(hard_conflicts)
        )

    if hard_conflicts:
        return (
            _result(
                RuleId.A4,
                RuleStatus.TRIGGERED,
                "Temporal evaluation triggered a hard stop: "
                + "; ".join(details)
                + ".",
                *codes,
            ),
            ProcessStatus.STOP,
        )
    if missing_horizons:
        return (
            _result(
                RuleId.A4,
                RuleStatus.SIGNAL,
                "Temporal evaluation is incomplete: " + "; ".join(details) + ".",
                *codes,
            ),
            ProcessStatus.WARN,
        )
    return (
        _result(
            RuleId.A4,
            RuleStatus.SATISFIED,
            f"At least {minimum} time horizons are declared for every "
            "candidate action.",
        ),
        ProcessStatus.PASS,
    )


def _evaluate_p1(model: ValidatorInput) -> RuleEvaluation:
    applies = (
        model.conflict.present
        or model.conflict.revision_scope is not RevisionScope.NONE
    )
    if not applies:
        return (
            _result(
                RuleId.P1,
                RuleStatus.NOT_APPLICABLE,
                "No conflict or model revision requires reference-frame "
                "classification.",
            ),
            ProcessStatus.PASS,
        )

    frame = model.reference_frame
    missing_details = (
        frame.status is ReferenceFrameStatus.MISSING
        or not frame.classes
        or frame.scope is None
    )
    if missing_details:
        return (
            _result(
                RuleId.P1,
                RuleStatus.TRIGGERED,
                "A conflict or revision is declared, but no complete reference frame "
                "with class and scope is available.",
                ReasonCode.REFERENCE_FRAME_MISSING,
            ),
            ProcessStatus.NO_REFERENCE,
        )
    if frame.status is ReferenceFrameStatus.AMBIGUOUS:
        return (
            _result(
                RuleId.P1,
                RuleStatus.SIGNAL,
                "The required reference frame remains explicitly ambiguous.",
                ReasonCode.REFERENCE_FRAME_AMBIGUOUS,
            ),
            ProcessStatus.WARN,
        )
    return (
        _result(
            RuleId.P1,
            RuleStatus.SATISFIED,
            "The conflict or revision has an identified reference-frame "
            "class and scope.",
        ),
        ProcessStatus.PASS,
    )


def _evaluate_p2(model: ValidatorInput) -> RuleEvaluation:
    report = model.residual_uncertainty
    if report.items or report.empty_rationale is not None:
        return (
            _result(
                RuleId.P2,
                RuleStatus.SATISFIED,
                "Residual uncertainty is explicit, including a rationale "
                "when the list is empty.",
            ),
            ProcessStatus.PASS,
        )
    return (
        _result(
            RuleId.P2,
            RuleStatus.SIGNAL,
            "Residual uncertainty is empty without an explicit rationale.",
            ReasonCode.UNCERTAINTY_NOT_REPORTED,
        ),
        ProcessStatus.WARN,
    )


def _evaluate_p3(model: ValidatorInput) -> RuleEvaluation:
    state = model.termination
    if not state.reflexive:
        return (
            _result(
                RuleId.P3,
                RuleStatus.NOT_APPLICABLE,
                "The run is not declared reflexive.",
            ),
            ProcessStatus.PASS,
        )
    if not state.has_hard_bound or state.max_recursion_depth is None:
        return (
            _result(
                RuleId.P3,
                RuleStatus.TRIGGERED,
                "A reflexive run requires both a hard termination bound and "
                "a recursion-depth bound.",
                ReasonCode.TERMINATION_BOUND_MISSING,
            ),
            ProcessStatus.STOP,
        )
    if state.recursion_depth >= state.max_recursion_depth:
        return (
            _result(
                RuleId.P3,
                RuleStatus.TRIGGERED,
                f"Reflexive recursion depth {state.recursion_depth} reached "
                f"the declared maximum {state.max_recursion_depth}.",
                ReasonCode.REFLEXIVE_DEPTH_LIMIT,
            ),
            ProcessStatus.STOP,
        )
    return (
        _result(
            RuleId.P3,
            RuleStatus.SATISFIED,
            "The reflexive run remains inside its termination and "
            "recursion-depth bounds.",
        ),
        ProcessStatus.PASS,
    )


def _evaluate_p4(model: ValidatorInput) -> RuleEvaluation:
    selected = _selected_action(model)
    if len(model.hypotheses) < 2 or selected is None:
        return (
            _result(
                RuleId.P4,
                RuleStatus.NOT_APPLICABLE,
                "No selected action under multiple explicit hypotheses "
                "requires a reversibility check.",
            ),
            ProcessStatus.PASS,
        )

    hard_conflicts = _hard_constraint_conflicts(model)
    if hard_conflicts:
        return (
            _result(
                RuleId.P4,
                RuleStatus.TRIGGERED,
                "The selected action conflicts with declared hard constraints: "
                + ", ".join(hard_conflicts)
                + ".",
                ReasonCode.DECLARED_CONSTRAINT_CONFLICT,
            ),
            ProcessStatus.STOP,
        )
    if not selected.reversible and model.selection_rationale is None:
        reversible_available = any(
            action.reversible for action in model.candidate_actions
        )
        availability = (
            " while a reversible candidate is available"
            if reversible_available
            else ""
        )
        return (
            _result(
                RuleId.P4,
                RuleStatus.SIGNAL,
                "An irreversible action was selected without an explicit selection "
                f"rationale{availability}.",
                ReasonCode.IRREVERSIBLE_ACTION_UNJUSTIFIED,
            ),
            ProcessStatus.WARN,
        )
    return (
        _result(
            RuleId.P4,
            RuleStatus.SATISFIED,
            "The selected action is reversible or its irreversible selection "
            "is explicitly justified.",
        ),
        ProcessStatus.PASS,
    )


_RULE_EVALUATORS: tuple[RuleEvaluator, ...] = (
    _evaluate_a2,
    _evaluate_a3,
    _evaluate_a4,
    _evaluate_p1,
    _evaluate_p2,
    _evaluate_p3,
    _evaluate_p4,
)


def _not_evaluated(rule_id: RuleId) -> RuleResult:
    return _result(
        rule_id,
        RuleStatus.NOT_EVALUATED,
        "The A1 competence gate prevents further domain-rule evaluation.",
    )


def _next_step(status: ProcessStatus) -> str:
    return {
        ProcessStatus.PASS: (
            "Proceed only within the declared constraints and retain the "
            "reported uncertainty."
        ),
        ProcessStatus.WARN: (
            "Review every reported signal and the retained uncertainty before "
            "relying on the process output."
        ),
        ProcessStatus.NO_REFERENCE: (
            "Establish a traceable reference frame before revising the model "
            "or acting on the conflict."
        ),
        ProcessStatus.DELEGATE: (
            "Obtain suitable external expertise or evidence before domain "
            "evaluation continues."
        ),
        ProcessStatus.STOP: (
            "Stop this run and address every triggered hard limit or declared "
            "constraint before continuing."
        ),
    }[status]


def _build_result(
    model: ValidatorInput,
    rule_results: tuple[RuleResult, ...],
    overall_status: ProcessStatus,
) -> ValidatorResult:
    return ValidatorResult(
        schema_version=RESULT_SCHEMA_VERSION,
        case_id=model.case_id,
        overall_status=overall_status,
        rule_results=rule_results,
        residual_uncertainty=tuple(
            item.description for item in model.residual_uncertainty.items
        ),
        next_step=_next_step(overall_status),
        config_id=model.validator_config.config_id,
    )


def evaluate(model: ValidatorInput) -> ValidatorResult:
    """Evaluate A1–A4 and P1–P4 in a deterministic, side-effect-free run.

    A1 is a gate. If competence is insufficient or unknown, the evaluator
    returns ``DELEGATE`` and records all later rules as ``NOT_EVALUATED``.
    Otherwise every remaining rule is evaluated and the aggregate status uses
    ``STOP > DELEGATE > NO_REFERENCE > WARN > PASS``.
    """

    if not isinstance(model, ValidatorInput):
        raise InputValidationError("validator_input", "must be ValidatorInput")

    a1_result, a1_status = _evaluate_a1(model)
    if a1_status is ProcessStatus.DELEGATE:
        remaining = tuple(_not_evaluated(rule_id) for rule_id in tuple(RuleId)[1:])
        return _build_result(
            model,
            (a1_result, *remaining),
            ProcessStatus.DELEGATE,
        )

    evaluations = tuple(evaluator(model) for evaluator in _RULE_EVALUATORS)
    rule_results = (a1_result, *(result for result, _ in evaluations))
    statuses = (a1_status, *(status for _, status in evaluations))
    overall_status = max(statuses, key=PROCESS_STATUS_PRIORITY.__getitem__)
    return _build_result(model, rule_results, overall_status)
