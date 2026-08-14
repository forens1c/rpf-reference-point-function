# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import unittest
from dataclasses import replace

from rpf_validator import (
    Calibration,
    CompetenceAssessment,
    CompetenceStatus,
    DeclaredConstraint,
    InputValidationError,
    ProcessStatus,
    ReasonCode,
    ReferenceFrame,
    ReferenceFrameStatus,
    RuleId,
    RuleStatus,
    TerminationState,
    UncertaintyReport,
    ValidatorConfig,
    evaluate,
    to_json,
)
from tests.test_models import make_valid_input


def rule(result, rule_id: RuleId):
    return next(item for item in result.rule_results if item.rule_id is rule_id)


class EvaluatorFlowTests(unittest.TestCase):
    def test_weather_case_passes_end_to_end(self) -> None:
        model = make_valid_input()

        result = evaluate(model)

        self.assertEqual(result.overall_status, ProcessStatus.PASS)
        self.assertEqual(
            tuple(item.rule_id for item in result.rule_results),
            tuple(RuleId),
        )
        self.assertEqual(rule(result, RuleId.P3).status, RuleStatus.NOT_APPLICABLE)
        self.assertEqual(rule(result, RuleId.P4).status, RuleStatus.SATISFIED)
        self.assertEqual(
            result.residual_uncertainty,
            ("The actual weather outcome remains unknown.",),
        )

    def test_identical_input_produces_identical_result_and_json(self) -> None:
        model = make_valid_input()

        first = evaluate(model)
        second = evaluate(model)

        self.assertEqual(first, second)
        self.assertEqual(to_json(first), to_json(second))

    def test_non_model_input_is_a_technical_input_error(self) -> None:
        with self.assertRaises(InputValidationError) as caught:
            evaluate({"case_id": "not-a-model"})  # type: ignore[arg-type]

        self.assertEqual(caught.exception.path, "validator_input")
        self.assertEqual(
            caught.exception.reason_code,
            ReasonCode.INPUT_SCHEMA_INVALID,
        )


class CompetenceRuleTests(unittest.TestCase):
    def test_insufficient_competence_delegates_and_gates_later_rules(self) -> None:
        model = make_valid_input(competence_status=CompetenceStatus.INSUFFICIENT)

        result = evaluate(model)

        self.assertEqual(result.overall_status, ProcessStatus.DELEGATE)
        self.assertEqual(
            rule(result, RuleId.A1).reason_codes,
            (ReasonCode.COMPETENCE_INSUFFICIENT,),
        )
        self.assertTrue(
            all(
                item.status is RuleStatus.NOT_EVALUATED
                for item in result.rule_results[1:]
            )
        )

    def test_unknown_competence_delegates(self) -> None:
        model = make_valid_input(competence_status=CompetenceStatus.UNKNOWN)

        result = evaluate(model)

        self.assertEqual(result.overall_status, ProcessStatus.DELEGATE)
        self.assertEqual(
            rule(result, RuleId.A1).reason_codes,
            (ReasonCode.COMPETENCE_UNKNOWN,),
        )


class CalibrationRuleTests(unittest.TestCase):
    def test_configured_divergence_is_a_warning_not_a_truth_decision(self) -> None:
        model = make_valid_input()
        calibration = replace(
            model.calibration,
            internal_confidence=0.9,
            external_evidence=0.2,
        )
        config = ValidatorConfig(
            config_id="divergence-test",
            calibration_values_comparable=True,
            confidence_evidence_divergence_threshold=0.4,
        )

        result = evaluate(
            replace(model, calibration=calibration, validator_config=config)
        )

        self.assertEqual(result.overall_status, ProcessStatus.WARN)
        self.assertEqual(
            rule(result, RuleId.A2).reason_codes,
            (ReasonCode.CONFIDENCE_EVIDENCE_DIVERGENCE,),
        )

    def test_divergence_equal_to_threshold_does_not_signal(self) -> None:
        model = make_valid_input()
        calibration = replace(
            model.calibration,
            internal_confidence=0.75,
            external_evidence=0.5,
        )
        config = ValidatorConfig(
            config_id="boundary-test",
            calibration_values_comparable=True,
            confidence_evidence_divergence_threshold=0.25,
        )

        result = evaluate(
            replace(model, calibration=calibration, validator_config=config)
        )

        self.assertEqual(result.overall_status, ProcessStatus.PASS)

    def test_external_evidence_without_source_signals_traceability(self) -> None:
        model = make_valid_input()
        calibration = Calibration(
            internal_confidence=model.calibration.internal_confidence,
            internal_confidence_rationale=(
                model.calibration.internal_confidence_rationale
            ),
            external_evidence=model.calibration.external_evidence,
            external_evidence_rationale=(
                model.calibration.external_evidence_rationale
            ),
        )

        hypotheses = tuple(
            replace(hypothesis, evidence_source_ids=())
            for hypothesis in model.hypotheses
        )

        result = evaluate(
            replace(model, calibration=calibration, hypotheses=hypotheses)
        )

        self.assertEqual(result.overall_status, ProcessStatus.WARN)
        self.assertEqual(
            rule(result, RuleId.A2).reason_codes,
            (ReasonCode.CALIBRATION_NOT_SEPARATED,),
        )


class TerminationRuleTests(unittest.TestCase):
    def test_all_reached_termination_conditions_remain_visible(self) -> None:
        model = make_valid_input()
        termination = TerminationState(
            information_gain=0.01,
            information_gain_epsilon=0.01,
            iteration=5,
            max_iterations=5,
            elapsed_ms=100.0,
            max_time_ms=100.0,
            budget_remaining=1.0,
            budget_minimum=1.0,
        )

        result = evaluate(replace(model, termination=termination))

        self.assertEqual(result.overall_status, ProcessStatus.STOP)
        self.assertEqual(
            rule(result, RuleId.A3).reason_codes,
            (
                ReasonCode.INFORMATION_GAIN_LIMIT,
                ReasonCode.ITERATION_LIMIT,
                ReasonCode.TIME_LIMIT,
                ReasonCode.RESOURCE_LIMIT,
            ),
        )

    def test_missing_hard_bound_stops(self) -> None:
        model = make_valid_input()
        termination = TerminationState(
            information_gain=0.05,
            information_gain_epsilon=0.01,
            iteration=0,
            max_iterations=None,
            elapsed_ms=0.0,
            max_time_ms=None,
            budget_remaining=None,
            budget_minimum=None,
        )

        result = evaluate(replace(model, termination=termination))

        self.assertEqual(result.overall_status, ProcessStatus.STOP)
        self.assertEqual(
            rule(result, RuleId.A3).reason_codes,
            (ReasonCode.TERMINATION_BOUND_MISSING,),
        )

    def test_stop_has_priority_but_retains_calibration_signal(self) -> None:
        model = make_valid_input()
        calibration = replace(
            model.calibration,
            internal_confidence=0.9,
            external_evidence=0.2,
        )
        config = ValidatorConfig(
            config_id="priority-test",
            calibration_values_comparable=True,
            confidence_evidence_divergence_threshold=0.4,
        )
        termination = replace(model.termination, elapsed_ms=100.0)

        result = evaluate(
            replace(
                model,
                calibration=calibration,
                validator_config=config,
                termination=termination,
            )
        )

        self.assertEqual(result.overall_status, ProcessStatus.STOP)
        self.assertEqual(rule(result, RuleId.A2).status, RuleStatus.SIGNAL)
        self.assertEqual(
            rule(result, RuleId.A3).reason_codes,
            (ReasonCode.TIME_LIMIT,),
        )


class ReferenceAndUncertaintyRuleTests(unittest.TestCase):
    def test_missing_reference_frame_returns_no_reference(self) -> None:
        model = make_valid_input()
        frame = ReferenceFrame(status=ReferenceFrameStatus.MISSING)

        result = evaluate(replace(model, reference_frame=frame))

        self.assertEqual(result.overall_status, ProcessStatus.NO_REFERENCE)
        self.assertEqual(
            rule(result, RuleId.P1).reason_codes,
            (ReasonCode.REFERENCE_FRAME_MISSING,),
        )

    def test_ambiguous_reference_frame_warns(self) -> None:
        model = make_valid_input()
        frame = replace(
            model.reference_frame,
            status=ReferenceFrameStatus.AMBIGUOUS,
        )

        result = evaluate(replace(model, reference_frame=frame))

        self.assertEqual(result.overall_status, ProcessStatus.WARN)
        self.assertEqual(
            rule(result, RuleId.P1).reason_codes,
            (ReasonCode.REFERENCE_FRAME_AMBIGUOUS,),
        )

    def test_empty_uncertainty_without_rationale_warns(self) -> None:
        model = make_valid_input()

        result = evaluate(
            replace(model, residual_uncertainty=UncertaintyReport())
        )

        self.assertEqual(result.overall_status, ProcessStatus.WARN)
        self.assertEqual(
            rule(result, RuleId.P2).reason_codes,
            (ReasonCode.UNCERTAINTY_NOT_REPORTED,),
        )

    def test_empty_uncertainty_with_rationale_is_explicit(self) -> None:
        model = make_valid_input()
        report = UncertaintyReport(
            empty_rationale="No residual uncertainty is declared for this fixture."
        )

        result = evaluate(replace(model, residual_uncertainty=report))

        self.assertEqual(result.overall_status, ProcessStatus.PASS)
        self.assertEqual(rule(result, RuleId.P2).status, RuleStatus.SATISFIED)


class TemporalAndReversibilityRuleTests(unittest.TestCase):
    def test_incomplete_horizon_coverage_warns(self) -> None:
        model = make_valid_input()
        action = replace(
            model.candidate_actions[0],
            effects=(model.candidate_actions[0].effects[0],),
        )

        result = evaluate(
            replace(
                model,
                time_horizons=(model.time_horizons[0],),
                candidate_actions=(action,),
            )
        )

        self.assertEqual(result.overall_status, ProcessStatus.WARN)
        self.assertEqual(
            rule(result, RuleId.A4).reason_codes,
            (ReasonCode.TIME_HORIZON_MISSING,),
        )

    def test_selected_action_hard_constraint_conflict_stops(self) -> None:
        model = make_valid_input()
        hard_constraint = DeclaredConstraint(
            code="DO_NOT_PROCEED",
            description="Fixture hard stop.",
            hard=True,
        )
        frame = replace(
            model.reference_frame,
            constraints=(*model.reference_frame.constraints, hard_constraint),
        )
        first_effect = replace(
            model.candidate_actions[0].effects[0],
            constraint_conflicts=("DO_NOT_PROCEED",),
        )
        action = replace(
            model.candidate_actions[0],
            effects=(first_effect, model.candidate_actions[0].effects[1]),
        )

        result = evaluate(
            replace(model, reference_frame=frame, candidate_actions=(action,))
        )

        self.assertEqual(result.overall_status, ProcessStatus.STOP)
        self.assertIn(
            ReasonCode.DECLARED_CONSTRAINT_CONFLICT,
            rule(result, RuleId.A4).reason_codes,
        )
        self.assertIn(
            ReasonCode.DECLARED_CONSTRAINT_CONFLICT,
            rule(result, RuleId.P4).reason_codes,
        )

    def test_reflexive_depth_limit_stops(self) -> None:
        model = make_valid_input()
        termination = replace(
            model.termination,
            reflexive=True,
            recursion_depth=3,
            max_recursion_depth=3,
        )

        result = evaluate(replace(model, termination=termination))

        self.assertEqual(result.overall_status, ProcessStatus.STOP)
        self.assertEqual(
            rule(result, RuleId.P3).reason_codes,
            (ReasonCode.REFLEXIVE_DEPTH_LIMIT,),
        )

    def test_controlled_reflexive_run_passes(self) -> None:
        model = make_valid_input()
        termination = replace(
            model.termination,
            reflexive=True,
            recursion_depth=1,
            max_recursion_depth=3,
        )

        result = evaluate(replace(model, termination=termination))

        self.assertEqual(result.overall_status, ProcessStatus.PASS)
        self.assertEqual(rule(result, RuleId.P3).status, RuleStatus.SATISFIED)

    def test_unjustified_irreversible_selection_warns(self) -> None:
        model = make_valid_input()
        irreversible = replace(
            model.candidate_actions[0],
            action_id="irreversible-action",
            description="Take an irreversible action.",
            reversible=False,
            rollback_cost=None,
        )

        result = evaluate(
            replace(
                model,
                candidate_actions=(*model.candidate_actions, irreversible),
                selected_action_id=irreversible.action_id,
                selection_rationale=None,
            )
        )

        self.assertEqual(result.overall_status, ProcessStatus.WARN)
        self.assertEqual(
            rule(result, RuleId.P4).reason_codes,
            (ReasonCode.IRREVERSIBLE_ACTION_UNJUSTIFIED,),
        )

    def test_justified_irreversible_selection_is_traceable(self) -> None:
        model = make_valid_input()
        irreversible = replace(
            model.candidate_actions[0],
            action_id="irreversible-action",
            description="Take an irreversible action.",
            reversible=False,
            rollback_cost=None,
        )

        result = evaluate(
            replace(
                model,
                candidate_actions=(*model.candidate_actions, irreversible),
                selected_action_id=irreversible.action_id,
                selection_rationale=(
                    "The fixture explicitly records why the irreversible "
                    "option was selected."
                ),
            )
        )

        self.assertEqual(result.overall_status, ProcessStatus.PASS)
        self.assertEqual(rule(result, RuleId.P4).status, RuleStatus.SATISFIED)


if __name__ == "__main__":
    unittest.main()
