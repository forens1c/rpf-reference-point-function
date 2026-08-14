# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import unittest
from dataclasses import FrozenInstanceError, fields

from rpf_validator import (
    INPUT_SCHEMA_VERSION,
    PROCESS_STATUS_PRIORITY,
    RESULT_SCHEMA_VERSION,
    __version__,
    Calibration,
    CandidateAction,
    CompetenceAssessment,
    CompetenceStatus,
    Conflict,
    DeclaredConstraint,
    EvidenceSource,
    ExpectedEffect,
    Hypothesis,
    InputValidationError,
    Observation,
    ProcessStatus,
    ReferenceFrame,
    ReferenceFrameClass,
    ReferenceFrameStatus,
    RevisionScope,
    RuleId,
    RuleResult,
    RuleStatus,
    TerminationState,
    TimeHorizon,
    UncertaintyItem,
    UncertaintyReport,
    ValidatorConfig,
    ValidatorInput,
    ValidatorResult,
    to_json,
)


def make_valid_input(
    *, competence_status: CompetenceStatus = CompetenceStatus.SUFFICIENT
) -> ValidatorInput:
    sources = (
        EvidenceSource(
            source_id="forecast-a",
            description="Forecast from service A",
            provenance="https://example.invalid/a",
            quality_note="Public forecast; model details are incomplete.",
        ),
        EvidenceSource(
            source_id="forecast-b",
            description="Forecast from service B",
            provenance="https://example.invalid/b",
            quality_note="Independent public forecast.",
        ),
    )
    constraints = (
        DeclaredConstraint(
            code="LOW_COST",
            description="Avoid disproportionate cost for a routine forecast.",
            hard=False,
        ),
    )
    horizons = (
        TimeHorizon(horizon_id="now", label="Immediate", order=0),
        TimeHorizon(horizon_id="later", label="Later today", order=1),
    )
    action = CandidateAction(
        action_id="carry-umbrella",
        description="Carry an umbrella.",
        effects=(
            ExpectedEffect(
                horizon_id="now",
                expected_benefit="Prepared for possible rain.",
                expected_cost="Small carrying cost.",
            ),
            ExpectedEffect(
                horizon_id="later",
                expected_benefit="Reduced impact if rain occurs.",
                expected_cost="No lasting commitment.",
            ),
        ),
        reversible=True,
        rationale="Low-cost action remains useful under both hypotheses.",
        rollback_cost="Stop carrying the umbrella.",
    )
    return ValidatorInput(
        schema_version=INPUT_SCHEMA_VERSION,
        case_id="weather-001",
        observation=Observation(
            content="Two services report different rain probabilities.",
            provenance="Declared neutral reference case",
        ),
        problem_domain="Interpretation of public weather forecasts",
        competence=CompetenceAssessment(
            status=competence_status,
            rationale="Competence is declared for reading public forecasts.",
            provenance="Case fixture",
        ),
        calibration=Calibration(
            internal_confidence=0.55,
            internal_confidence_rationale="Forecasts remain close and uncertain.",
            external_evidence=0.60,
            external_evidence_rationale="Two traceable but divergent sources.",
            evidence_sources=sources,
        ),
        conflict=Conflict(present=True, revision_scope=RevisionScope.LOCAL),
        reference_frame=ReferenceFrame(
            status=ReferenceFrameStatus.IDENTIFIED,
            classes=(ReferenceFrameClass.OBJECTIVE_MEASUREMENT,),
            scope="Same location and afternoon; compare forecast assumptions.",
            assumptions=("Both services refer to the same location.",),
            constraints=constraints,
        ),
        hypotheses=(
            Hypothesis(
                hypothesis_id="rain",
                statement="Rain occurs during the afternoon.",
                evidence_source_ids=("forecast-a",),
                internal_confidence=0.55,
            ),
            Hypothesis(
                hypothesis_id="dry",
                statement="No rain occurs during the afternoon.",
                evidence_source_ids=("forecast-b",),
                internal_confidence=0.45,
            ),
        ),
        termination=TerminationState(
            information_gain=0.05,
            information_gain_epsilon=0.01,
            iteration=1,
            max_iterations=5,
            elapsed_ms=4.0,
            max_time_ms=100.0,
            budget_remaining=10.0,
            budget_minimum=1.0,
        ),
        time_horizons=horizons,
        candidate_actions=(action,),
        residual_uncertainty=UncertaintyReport(
            items=(
                UncertaintyItem(
                    item_id="forecast-outcome",
                    description="The actual weather outcome remains unknown.",
                    missing_information=("Future observation",),
                ),
            )
        ),
        validator_config=ValidatorConfig(config_id="prototype-defaults-0.1"),
        selected_action_id="carry-umbrella",
        selection_rationale=(
            "The reversible precaution remains proportionate under both hypotheses."
        ),
    )


class InputModelTests(unittest.TestCase):
    def test_implementation_and_schema_versions_are_explicit(self) -> None:
        self.assertEqual(__version__, "0.3.0.dev0")
        self.assertEqual(INPUT_SCHEMA_VERSION, "rpf-validator-input-0.2")
        self.assertEqual(RESULT_SCHEMA_VERSION, "rpf-validator-result-0.2")

    def test_valid_weather_input_is_immutable(self) -> None:
        model = make_valid_input()

        self.assertEqual(model.case_id, "weather-001")
        self.assertTrue(model.termination.has_hard_bound)
        with self.assertRaises(FrozenInstanceError):
            model.case_id = "changed"  # type: ignore[misc]

    def test_confidence_and_evidence_are_separate_fields(self) -> None:
        names = {item.name for item in fields(Calibration)}

        self.assertIn("internal_confidence", names)
        self.assertIn("external_evidence", names)
        self.assertNotIn("trust_score", names)

    def test_domain_unknown_competence_is_structurally_valid(self) -> None:
        model = make_valid_input(competence_status=CompetenceStatus.UNKNOWN)

        self.assertEqual(model.competence.status, CompetenceStatus.UNKNOWN)

    def test_out_of_range_confidence_is_input_error(self) -> None:
        with self.assertRaises(InputValidationError) as caught:
            Calibration(
                internal_confidence=1.2,
                internal_confidence_rationale="Declared value.",
                external_evidence=0.5,
                external_evidence_rationale="Declared evidence.",
            )

        self.assertEqual(caught.exception.path, "calibration.internal_confidence")

    def test_non_finite_numbers_are_input_errors(self) -> None:
        with self.assertRaises(InputValidationError):
            Calibration(
                internal_confidence=float("nan"),
                internal_confidence_rationale="Declared value.",
                external_evidence=0.5,
                external_evidence_rationale="Declared evidence.",
            )
        with self.assertRaises(InputValidationError):
            TerminationState(
                information_gain=0.1,
                information_gain_epsilon=0.01,
                iteration=0,
                max_iterations=5,
                elapsed_ms=float("inf"),
                max_time_ms=10.0,
                budget_remaining=None,
                budget_minimum=None,
            )

    def test_missing_hard_bound_is_semantic_not_structural(self) -> None:
        state = TerminationState(
            information_gain=None,
            information_gain_epsilon=None,
            iteration=0,
            max_iterations=None,
            elapsed_ms=0.0,
            max_time_ms=None,
            budget_remaining=None,
            budget_minimum=None,
        )

        self.assertFalse(state.has_hard_bound)

    def test_empty_uncertainty_report_is_semantically_evaluable(self) -> None:
        report = UncertaintyReport()

        self.assertFalse(report.items)
        self.assertIsNone(report.empty_rationale)

    def test_divergence_threshold_requires_explicit_comparability(self) -> None:
        with self.assertRaises(InputValidationError):
            ValidatorConfig(
                config_id="invalid-config",
                confidence_evidence_divergence_threshold=0.4,
            )

        config = ValidatorConfig(
            config_id="comparable-config",
            calibration_values_comparable=True,
            confidence_evidence_divergence_threshold=0.4,
        )
        self.assertEqual(config.confidence_evidence_divergence_threshold, 0.4)

    def test_unknown_evidence_reference_is_input_error(self) -> None:
        model = make_valid_input()
        invalid_hypothesis = Hypothesis(
            hypothesis_id="unknown-source",
            statement="A hypothesis references an absent source.",
            evidence_source_ids=("not-present",),
        )

        with self.assertRaises(InputValidationError) as caught:
            ValidatorInput(
                schema_version=model.schema_version,
                case_id=model.case_id,
                observation=model.observation,
                problem_domain=model.problem_domain,
                competence=model.competence,
                calibration=model.calibration,
                conflict=model.conflict,
                reference_frame=model.reference_frame,
                hypotheses=(invalid_hypothesis,),
                termination=model.termination,
                time_horizons=model.time_horizons,
                candidate_actions=model.candidate_actions,
                residual_uncertainty=model.residual_uncertainty,
                validator_config=model.validator_config,
            )

        self.assertIn("unknown source identifiers", caught.exception.message)

    def test_unknown_action_horizon_is_input_error(self) -> None:
        model = make_valid_input()
        action = CandidateAction(
            action_id="bad-horizon",
            description="References an unknown horizon.",
            effects=(
                ExpectedEffect(
                    horizon_id="tomorrow",
                    expected_benefit="Unknown.",
                    expected_cost="Unknown.",
                ),
            ),
            reversible=True,
            rationale="Fixture for reference validation.",
        )

        with self.assertRaises(InputValidationError) as caught:
            ValidatorInput(
                schema_version=model.schema_version,
                case_id=model.case_id,
                observation=model.observation,
                problem_domain=model.problem_domain,
                competence=model.competence,
                calibration=model.calibration,
                conflict=model.conflict,
                reference_frame=model.reference_frame,
                hypotheses=model.hypotheses,
                termination=model.termination,
                time_horizons=model.time_horizons,
                candidate_actions=(action,),
                residual_uncertainty=model.residual_uncertainty,
                validator_config=model.validator_config,
            )

        self.assertIn("unknown horizon", caught.exception.message)

    def test_unknown_selected_action_is_input_error(self) -> None:
        model = make_valid_input()

        with self.assertRaises(InputValidationError) as caught:
            ValidatorInput(
                schema_version=model.schema_version,
                case_id=model.case_id,
                observation=model.observation,
                problem_domain=model.problem_domain,
                competence=model.competence,
                calibration=model.calibration,
                conflict=model.conflict,
                reference_frame=model.reference_frame,
                hypotheses=model.hypotheses,
                termination=model.termination,
                time_horizons=model.time_horizons,
                candidate_actions=model.candidate_actions,
                residual_uncertainty=model.residual_uncertainty,
                validator_config=model.validator_config,
                selected_action_id="not-present",
            )

        self.assertEqual(caught.exception.path, "selected_action_id")

    def test_selection_rationale_requires_selected_action(self) -> None:
        model = make_valid_input()

        with self.assertRaises(InputValidationError) as caught:
            ValidatorInput(
                schema_version=model.schema_version,
                case_id=model.case_id,
                observation=model.observation,
                problem_domain=model.problem_domain,
                competence=model.competence,
                calibration=model.calibration,
                conflict=model.conflict,
                reference_frame=model.reference_frame,
                hypotheses=model.hypotheses,
                termination=model.termination,
                time_horizons=model.time_horizons,
                candidate_actions=model.candidate_actions,
                residual_uncertainty=model.residual_uncertainty,
                validator_config=model.validator_config,
                selection_rationale="No selected action exists.",
            )

        self.assertEqual(caught.exception.path, "selection_rationale")


class ResultModelTests(unittest.TestCase):
    def test_status_priority_matches_operationalization(self) -> None:
        ordered = sorted(
            ProcessStatus,
            key=PROCESS_STATUS_PRIORITY.__getitem__,
            reverse=True,
        )

        self.assertEqual(
            ordered,
            [
                ProcessStatus.STOP,
                ProcessStatus.DELEGATE,
                ProcessStatus.NO_REFERENCE,
                ProcessStatus.WARN,
                ProcessStatus.PASS,
            ],
        )

    def test_pass_may_retain_residual_uncertainty(self) -> None:
        result = ValidatorResult(
            schema_version=RESULT_SCHEMA_VERSION,
            case_id="weather-001",
            overall_status=ProcessStatus.PASS,
            rule_results=(
                RuleResult(
                    rule_id=RuleId.P2,
                    status=RuleStatus.SATISFIED,
                    rationale="Residual uncertainty is explicit.",
                ),
            ),
            residual_uncertainty=("The future weather remains unknown.",),
            next_step="Carry a reversible low-cost precaution.",
            config_id="prototype-defaults-0.1",
        )

        self.assertEqual(result.overall_status, ProcessStatus.PASS)
        self.assertTrue(result.residual_uncertainty)

    def test_json_serialization_uses_enum_values_and_lists(self) -> None:
        model = make_valid_input()

        payload = json.loads(to_json(model))

        self.assertEqual(payload["competence"]["status"], "SUFFICIENT")
        self.assertIsInstance(payload["hypotheses"], list)
        self.assertEqual(payload["schema_version"], INPUT_SCHEMA_VERSION)
        self.assertEqual(payload["selected_action_id"], "carry-umbrella")


if __name__ == "__main__":
    unittest.main()
