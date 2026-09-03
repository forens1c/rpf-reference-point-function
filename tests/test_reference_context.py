# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime
import unittest

import rpf_validator
from rpf_validator._reference_context import (
    AdmissibilityAssertion,
    AdmissibilityStatus,
    ClaimAnchor,
    ClaimDependency,
    ClaimId,
    ClaimReferenceRoots,
    ClaimScope,
    ReferenceCandidate,
    ReferenceContext,
    ReferenceContextError,
    ReferenceId,
    ReferenceSupport,
    ScopeSource,
    TargetId,
    TemporalFact,
    TemporalMarker,
    TemporalRole,
)
from tests.test_models import make_valid_input


def instant(day: int, hour: int = 0) -> datetime:
    return datetime(2026, 1, day, hour, tzinfo=UTC)


RAIN = ClaimId.hypothesis("rain")
DRY = ClaimId.hypothesis("dry")
OBSERVATION = ClaimId.observation()
FORECAST_A = ReferenceId.evidence_source("forecast-a")
FORECAST_B = ReferenceId.evidence_source("forecast-b")


def internal_claim(
    local_id: str,
    *,
    target_id: TargetId | None = None,
    scope: ClaimScope | None = None,
) -> ClaimAnchor:
    return ClaimAnchor(
        ClaimId.internal(local_id),
        internal_statement=f"Internal claim {local_id}",
        target_id=target_id,
        scope=scope,
    )


def rrc_context() -> ReferenceContext:
    derived = ClaimId.internal("derived")
    conclusion = ClaimId.internal("conclusion")
    return ReferenceContext(
        validator_input=make_valid_input(),
        claims=(
            ClaimAnchor(RAIN),
            internal_claim("derived"),
            internal_claim("conclusion"),
        ),
        reference_supports=(ReferenceSupport(FORECAST_B, RAIN),),
        claim_dependencies=(
            ClaimDependency(RAIN, derived),
            ClaimDependency(derived, conclusion),
        ),
        admissibility_assertions=(
            AdmissibilityAssertion(
                reference_id=FORECAST_A,
                admissible=False,
                effective_at=instant(2),
                known_at=instant(3),
                rationale="The source failed a later admissibility check.",
            ),
        ),
    )


class ClaimAndReferenceIdentityTests(unittest.TestCase):
    def test_hypothesis_id_is_a_claim_anchor(self) -> None:
        model = make_valid_input()
        context = ReferenceContext(
            validator_input=model,
            claims=(ClaimAnchor(RAIN),),
        )

        self.assertEqual(context.claim_content(RAIN), model.hypotheses[0].statement)
        self.assertIsNone(context.claims[0].internal_statement)
        self.assertEqual(
            context.direct_dependencies(RAIN).reference_ids,
            (FORECAST_A,),
        )

    def test_observation_can_be_explicitly_enrolled_as_a_claim(self) -> None:
        model = make_valid_input()
        context = ReferenceContext(
            validator_input=model,
            claims=(ClaimAnchor(OBSERVATION),),
        )

        self.assertEqual(context.claim_content(OBSERVATION), model.observation.content)
        self.assertIsNone(context.claims[0].internal_statement)

    def test_internal_non_hypothesis_claim_has_its_own_content(self) -> None:
        claim = internal_claim("analysis-step")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(claim,),
        )

        self.assertEqual(
            context.claim_content(claim.claim_id),
            "Internal claim analysis-step",
        )

    def test_additional_candidate_does_not_require_an_evidence_source(self) -> None:
        candidate_id = ReferenceId.candidate("possible-archive")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            reference_candidates=(
                ReferenceCandidate(candidate_id, "A hypothesized archive entry."),
            ),
        )

        self.assertIn(candidate_id, context.reference_ids)
        self.assertEqual(
            context.reference_description(candidate_id),
            "A hypothesized archive entry.",
        )
        self.assertNotIn(
            "possible-archive",
            {
                source.source_id
                for source in context.validator_input.calibration.evidence_sources
            },
        )

    def test_evidence_source_existence_does_not_imply_admissibility(self) -> None:
        context = ReferenceContext(validator_input=make_valid_input())

        self.assertEqual(
            context.current_admissibility(FORECAST_A, instant(2)),
            AdmissibilityStatus.UNRESOLVED,
        )

    def test_typed_namespaces_prevent_cross_kind_collisions(self) -> None:
        internal_rain = ClaimId.internal("rain")
        candidate_forecast = ReferenceId.candidate("forecast-a")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(
                ClaimAnchor(RAIN),
                ClaimAnchor(
                    internal_rain,
                    internal_statement="A separate internal claim.",
                ),
            ),
            reference_candidates=(
                ReferenceCandidate(
                    candidate_forecast,
                    "A candidate distinct from the EvidenceSource.",
                ),
            ),
        )

        self.assertNotEqual(RAIN, internal_rain)
        self.assertNotEqual(FORECAST_A, candidate_forecast)
        self.assertIn(RAIN, context.claim_ids)
        self.assertIn(internal_rain, context.claim_ids)
        self.assertIn(FORECAST_A, context.reference_ids)
        self.assertIn(candidate_forecast, context.reference_ids)

    def test_existing_hypothesis_support_cannot_be_duplicated(self) -> None:
        with self.assertRaises(ReferenceContextError):
            ReferenceContext(
                validator_input=make_valid_input(),
                claims=(ClaimAnchor(RAIN),),
                reference_supports=(ReferenceSupport(FORECAST_A, RAIN),),
            )


class DependencyQueryTests(unittest.TestCase):
    def test_direct_dependencies_keep_reference_and_claim_edges_distinct(self) -> None:
        derived = ClaimId.internal("derived")
        candidate = ReferenceId.candidate("candidate-a")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(RAIN), internal_claim("derived")),
            reference_candidates=(
                ReferenceCandidate(candidate, "One unconfirmed candidate."),
            ),
            reference_supports=(ReferenceSupport(candidate, derived),),
            claim_dependencies=(ClaimDependency(RAIN, derived),),
        )

        dependencies = context.direct_dependencies(derived)

        self.assertEqual(dependencies.reference_ids, (candidate,))
        self.assertEqual(dependencies.claim_ids, (RAIN,))

    def test_transitive_dependents_follow_claim_chains(self) -> None:
        context = rrc_context()

        self.assertEqual(
            context.transitive_dependents(RAIN),
            (ClaimId.internal("conclusion"), ClaimId.internal("derived")),
        )

    def test_transitive_traversal_is_cycle_safe(self) -> None:
        first = ClaimId.internal("first")
        second = ClaimId.internal("second")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(internal_claim("first"), internal_claim("second")),
            claim_dependencies=(
                ClaimDependency(first, second),
                ClaimDependency(second, first),
            ),
        )

        self.assertEqual(context.transitive_dependents(first), (second,))
        self.assertEqual(context.transitive_dependents(second), (first,))

    def test_reference_roots_include_direct_and_upstream_support(self) -> None:
        context = rrc_context()

        self.assertEqual(
            context.reference_roots(ClaimId.internal("conclusion")),
            (FORECAST_A, FORECAST_B),
        )

    def test_multiple_derived_claims_collapse_to_one_root_identifier(self) -> None:
        first = ClaimId.internal("echo-1")
        second = ClaimId.internal("echo-2")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(
                ClaimAnchor(RAIN),
                internal_claim("echo-1"),
                internal_claim("echo-2"),
            ),
            claim_dependencies=(
                ClaimDependency(RAIN, first),
                ClaimDependency(first, second),
            ),
        )

        self.assertEqual(context.reference_roots(first), (FORECAST_A,))
        self.assertEqual(context.reference_roots(second), (FORECAST_A,))

    def test_different_root_ids_do_not_create_an_independence_assessment(self) -> None:
        context = rrc_context()

        self.assertEqual(context.reference_roots(RAIN), (FORECAST_A, FORECAST_B))
        self.assertNotIn(
            "independent",
            {item.name for item in fields(ReferenceContext)},
        )
        self.assertFalse(hasattr(context, "independence_score"))


class ResidualReferenceContaminationTests(unittest.TestCase):
    def test_invalidated_root_finds_direct_dependents(self) -> None:
        impact = rrc_context().invalidation_impact(FORECAST_A)

        self.assertEqual(impact.direct_claims, (RAIN,))

    def test_invalidated_root_finds_transitive_dependents(self) -> None:
        impact = rrc_context().invalidation_impact(FORECAST_A)

        self.assertEqual(
            impact.transitive_dependents,
            (ClaimId.internal("conclusion"), ClaimId.internal("derived")),
        )

    def test_invalidation_keeps_other_roots_visible_per_affected_claim(self) -> None:
        impact = rrc_context().invalidation_impact(FORECAST_A)

        self.assertEqual(
            impact.remaining_roots,
            (
                ClaimReferenceRoots(RAIN, (FORECAST_B,)),
                ClaimReferenceRoots(ClaimId.internal("conclusion"), (FORECAST_B,)),
                ClaimReferenceRoots(ClaimId.internal("derived"), (FORECAST_B,)),
            ),
        )

    def test_invalidation_does_not_set_claim_truth_or_remove_history(self) -> None:
        context = rrc_context()
        before = context.claim_content(RAIN)

        impact = context.invalidation_impact(FORECAST_A)

        self.assertEqual(context.claim_content(RAIN), before)
        self.assertIn(RAIN, context.claim_ids)
        self.assertIn(FORECAST_A, context.reference_roots(RAIN))
        self.assertEqual(
            impact.affected_claims,
            context.transitive_dependents(FORECAST_A),
        )
        forbidden = {"truth", "false", "sufficient", "overall_status"}
        self.assertTrue(forbidden.isdisjoint({item.name for item in fields(impact)}))


class HindsightReferenceLeakageTests(unittest.TestCase):
    def test_effective_and_known_times_remain_separate(self) -> None:
        assertion = AdmissibilityAssertion(
            reference_id=FORECAST_A,
            admissible=False,
            effective_at=instant(1),
            known_at=instant(3),
            rationale="The defect was discovered later.",
        )
        context = ReferenceContext(
            validator_input=make_valid_input(),
            admissibility_assertions=(assertion,),
        )

        self.assertNotEqual(assertion.effective_at, assertion.known_at)
        self.assertEqual(
            context.admissibility_at(
                FORECAST_A,
                effective_at=instant(2),
                known_at=instant(2),
            ),
            AdmissibilityStatus.UNRESOLVED,
        )
        self.assertEqual(
            context.admissibility_at(
                FORECAST_A,
                effective_at=instant(2),
                known_at=instant(3),
            ),
            AdmissibilityStatus.INADMISSIBLE,
        )

    def test_later_information_is_absent_from_an_earlier_reference_view(self) -> None:
        ground_truth = ReferenceId.candidate("later-ground-truth")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(RAIN),),
            reference_candidates=(
                ReferenceCandidate(ground_truth, "Outcome learned later."),
            ),
            reference_supports=(ReferenceSupport(ground_truth, RAIN),),
            temporal_facts=(
                TemporalFact(
                    ground_truth,
                    TemporalRole.AVAILABLE_TO_CONTEXT,
                    instant(3),
                ),
            ),
        )

        self.assertNotIn(
            ground_truth,
            context.available_reference_roots(RAIN, instant(2)),
        )

    def test_retrospective_view_reveals_later_information_without_rewriting(
        self,
    ) -> None:
        ground_truth = ReferenceId.candidate("later-ground-truth")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(RAIN),),
            reference_candidates=(
                ReferenceCandidate(ground_truth, "Outcome learned later."),
            ),
            reference_supports=(ReferenceSupport(ground_truth, RAIN),),
            temporal_facts=(
                TemporalFact(
                    ground_truth,
                    TemporalRole.AVAILABLE_TO_CONTEXT,
                    instant(3),
                ),
            ),
        )

        early = context.available_reference_roots(RAIN, instant(2))
        later = context.available_reference_roots(RAIN, instant(4))

        self.assertNotIn(ground_truth, early)
        self.assertIn(ground_truth, later)
        self.assertNotIn(
            ground_truth,
            context.available_reference_roots(RAIN, instant(2)),
        )
        self.assertIn(ground_truth, context.reference_roots(RAIN))

    def test_later_claim_availability_blocks_its_upstream_root_historically(
        self,
    ) -> None:
        later_claim = ClaimId.internal("later-ground-truth-claim")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(RAIN), internal_claim("later-ground-truth-claim")),
            reference_supports=(ReferenceSupport(FORECAST_B, later_claim),),
            claim_dependencies=(ClaimDependency(later_claim, RAIN),),
            temporal_facts=(
                TemporalFact(
                    FORECAST_B,
                    TemporalRole.AVAILABLE_TO_CONTEXT,
                    instant(1),
                ),
                TemporalFact(
                    later_claim,
                    TemporalRole.AVAILABLE_TO_CONTEXT,
                    instant(3),
                ),
            ),
        )

        self.assertNotIn(
            FORECAST_B,
            context.available_reference_roots(RAIN, instant(2)),
        )
        self.assertIn(
            FORECAST_B,
            context.available_reference_roots(RAIN, instant(4)),
        )


class ObservationProjectionDivergenceTests(unittest.TestCase):
    def test_observation_anchor_records_origin_without_modality_or_truth(self) -> None:
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(OBSERVATION),),
        )

        self.assertEqual(context.claim_ids, (OBSERVATION,))
        claim_fields = {item.name for item in fields(context.claims[0])}
        self.assertNotIn("modality", claim_fields)
        self.assertNotIn("truth", claim_fields)

    def test_past_state_derivation_is_representable_without_a_modality_field(
        self,
    ) -> None:
        target = TargetId("world-state-1")
        reconstructed = ClaimId.internal("reconstructed-state")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(
                ClaimAnchor(OBSERVATION),
                internal_claim("reconstructed-state", target_id=target),
            ),
            claim_dependencies=(ClaimDependency(OBSERVATION, reconstructed),),
            temporal_facts=(
                TemporalFact(
                    reconstructed,
                    TemporalRole.TARGET_EVENT,
                    instant(1),
                ),
                TemporalFact(
                    reconstructed,
                    TemporalRole.CREATION_DERIVATION,
                    instant(2),
                ),
            ),
        )

        self.assertEqual(
            context.direct_dependencies(reconstructed).claim_ids,
            (OBSERVATION,),
        )
        self.assertLess(
            context.temporal_value(reconstructed, TemporalRole.TARGET_EVENT),
            context.temporal_value(reconstructed, TemporalRole.CREATION_DERIVATION),
        )
        self.assertFalse(hasattr(context._claim(reconstructed), "modality"))

    def test_future_target_is_representable_without_a_modality_field(self) -> None:
        target = TargetId("future-world-state")
        projected = ClaimId.internal("future-claim")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(internal_claim("future-claim", target_id=target),),
            temporal_facts=(
                TemporalFact(
                    projected,
                    TemporalRole.CREATION_DERIVATION,
                    instant(1),
                ),
                TemporalFact(
                    projected,
                    TemporalRole.TARGET_EVENT,
                    instant(3),
                ),
            ),
        )

        self.assertGreater(
            context.temporal_value(projected, TemporalRole.TARGET_EVENT),
            context.temporal_value(projected, TemporalRole.CREATION_DERIVATION),
        )
        self.assertFalse(hasattr(context._claim(projected), "modality"))

    def test_missing_modality_basis_remains_unmodeled(self) -> None:
        claim_id = ClaimId.internal("temporally-open")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(internal_claim("temporally-open"),),
        )

        self.assertIsNone(
            context.temporal_value(claim_id, TemporalRole.TARGET_EVENT)
        )
        self.assertIsNone(
            context.temporal_value(claim_id, TemporalRole.CREATION_DERIVATION)
        )
        self.assertFalse(hasattr(context._claim(claim_id), "modality"))


class TemporalReferenceDivergenceTests(unittest.TestCase):
    def _context(self) -> tuple[ReferenceContext, ClaimId, ClaimId]:
        target = TargetId("shared-world-state")
        early_claim = ClaimId.internal("early-view")
        late_claim = ClaimId.internal("late-view")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(
                internal_claim("early-view", target_id=target),
                internal_claim("late-view", target_id=target),
            ),
            reference_supports=(
                ReferenceSupport(FORECAST_A, early_claim),
                ReferenceSupport(FORECAST_B, late_claim),
            ),
            temporal_facts=(
                TemporalFact(
                    FORECAST_A,
                    TemporalRole.AVAILABLE_TO_CONTEXT,
                    instant(1),
                ),
                TemporalFact(
                    FORECAST_B,
                    TemporalRole.AVAILABLE_TO_CONTEXT,
                    instant(3),
                ),
            ),
        )
        return context, early_claim, late_claim

    def test_claims_can_share_one_opaque_target_id(self) -> None:
        context, early_claim, late_claim = self._context()

        self.assertEqual(
            context._claim(early_claim).target_id,
            context._claim(late_claim).target_id,
        )

    def test_references_can_have_different_context_availability_times(self) -> None:
        context, _, _ = self._context()

        self.assertEqual(
            context.temporal_value(
                FORECAST_A, TemporalRole.AVAILABLE_TO_CONTEXT
            ),
            instant(1),
        )
        self.assertEqual(
            context.temporal_value(
                FORECAST_B, TemporalRole.AVAILABLE_TO_CONTEXT
            ),
            instant(3),
        )

    def test_historical_reference_view_changes_at_the_declared_time(self) -> None:
        context, early_claim, late_claim = self._context()

        self.assertEqual(
            context.available_reference_roots(early_claim, instant(2)),
            (FORECAST_A,),
        )
        self.assertEqual(
            context.available_reference_roots(late_claim, instant(2)),
            (),
        )
        self.assertEqual(
            context.available_reference_roots(late_claim, instant(4)),
            (FORECAST_B,),
        )
        self.assertFalse(hasattr(context, "agent_access"))


class ScopeAndTemporalFactTests(unittest.TestCase):
    def test_same_references_with_different_claim_scopes_remain_distinct(self) -> None:
        narrow = ClaimId.internal("narrow")
        broad = ClaimId.internal("broad")
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(
                internal_claim(
                    "narrow",
                    scope=ClaimScope.local("One station during one afternoon."),
                ),
                internal_claim(
                    "broad",
                    scope=ClaimScope.local("All stations during the full week."),
                ),
            ),
            reference_supports=(
                ReferenceSupport(FORECAST_A, narrow),
                ReferenceSupport(FORECAST_A, broad),
            ),
        )

        self.assertEqual(
            context.reference_roots(narrow),
            context.reference_roots(broad),
        )
        self.assertNotEqual(context.scope_text(narrow), context.scope_text(broad))

    def test_reference_frame_scope_is_explicitly_reused_not_copied(self) -> None:
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(RAIN, scope=ClaimScope.reference_frame()),),
        )

        self.assertEqual(context.claims[0].scope.source, ScopeSource.REFERENCE_FRAME)
        self.assertIsNone(context.claims[0].scope.text)
        self.assertIs(
            context.scope_text(RAIN),
            context.validator_input.reference_frame.scope,
        )

    def test_missing_claim_scope_does_not_fall_back_to_reference_frame(self) -> None:
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(RAIN),),
        )

        self.assertIsNotNone(context.validator_input.reference_frame.scope)
        self.assertIsNone(context.scope_text(RAIN))

    def test_temporal_fact_accepts_timezone_aware_timestamp_only(self) -> None:
        fact = TemporalFact(
            RAIN,
            TemporalRole.CREATION_DERIVATION,
            instant(1),
        )

        self.assertEqual(fact.value, instant(1))
        with self.assertRaises(ReferenceContextError):
            TemporalFact(
                RAIN,
                TemporalRole.CREATION_DERIVATION,
                datetime(2026, 1, 1),
            )

    def test_unknown_temporal_value_remains_explicit(self) -> None:
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(RAIN),),
            temporal_facts=(
                TemporalFact(
                    RAIN,
                    TemporalRole.TARGET_EVENT,
                    TemporalMarker.UNKNOWN,
                ),
            ),
        )

        self.assertIs(
            context.temporal_value(RAIN, TemporalRole.TARGET_EVENT),
            TemporalMarker.UNKNOWN,
        )

    def test_not_applicable_temporal_value_remains_explicit(self) -> None:
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(RAIN),),
            temporal_facts=(
                TemporalFact(
                    RAIN,
                    TemporalRole.TARGET_EVENT,
                    TemporalMarker.NOT_APPLICABLE,
                ),
            ),
        )

        self.assertIs(
            context.temporal_value(RAIN, TemporalRole.TARGET_EVENT),
            TemporalMarker.NOT_APPLICABLE,
        )

    def test_non_instant_availability_does_not_authorize_historical_use(self) -> None:
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(RAIN),),
            temporal_facts=(
                TemporalFact(
                    FORECAST_A,
                    TemporalRole.AVAILABLE_TO_CONTEXT,
                    TemporalMarker.NOT_APPLICABLE,
                ),
            ),
        )

        self.assertIn(FORECAST_A, context.reference_roots(RAIN))
        self.assertNotIn(
            FORECAST_A,
            context.available_reference_roots(RAIN, instant(4)),
        )

    def test_unmodeled_temporal_value_differs_from_both_markers(self) -> None:
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(RAIN),),
        )

        value = context.temporal_value(RAIN, TemporalRole.TARGET_EVENT)

        self.assertIsNone(value)
        self.assertIsNot(value, TemporalMarker.UNKNOWN)
        self.assertIsNot(value, TemporalMarker.NOT_APPLICABLE)

    def test_observed_at_is_not_automatically_reinterpreted(self) -> None:
        model = make_valid_input()
        model = replace(
            model,
            observation=replace(
                model.observation,
                observed_at="2026-01-01T00:00:00Z",
            ),
        )
        context = ReferenceContext(
            validator_input=model,
            claims=(ClaimAnchor(OBSERVATION),),
        )

        self.assertIsNone(
            context.temporal_value(OBSERVATION, TemporalRole.TARGET_EVENT)
        )
        self.assertIsNone(
            context.temporal_value(OBSERVATION, TemporalRole.CREATION_DERIVATION)
        )
        self.assertIsNone(
            context.temporal_value(OBSERVATION, TemporalRole.AVAILABLE_TO_CONTEXT)
        )


class LifecycleDeterminismTests(unittest.TestCase):
    def _assertions(self) -> tuple[AdmissibilityAssertion, ...]:
        return (
            AdmissibilityAssertion(
                FORECAST_A,
                True,
                effective_at=instant(1),
                known_at=instant(1),
                rationale="Initially admitted.",
            ),
            AdmissibilityAssertion(
                FORECAST_A,
                False,
                effective_at=instant(2),
                known_at=instant(3),
                rationale="A later check invalidated the source from day two.",
            ),
            AdmissibilityAssertion(
                FORECAST_A,
                True,
                effective_at=instant(4),
                known_at=instant(4),
                rationale="A replacement verification restored admissibility.",
            ),
        )

    def test_multiple_assertions_resolve_by_effective_then_known_time(self) -> None:
        context = ReferenceContext(
            validator_input=make_valid_input(),
            admissibility_assertions=self._assertions(),
        )

        self.assertEqual(
            context.admissibility_at(
                FORECAST_A,
                effective_at=instant(3),
                known_at=instant(2),
            ),
            AdmissibilityStatus.ADMISSIBLE,
        )
        self.assertEqual(
            context.admissibility_at(
                FORECAST_A,
                effective_at=instant(3),
                known_at=instant(3),
            ),
            AdmissibilityStatus.INADMISSIBLE,
        )
        self.assertEqual(
            context.current_admissibility(FORECAST_A, instant(4)),
            AdmissibilityStatus.ADMISSIBLE,
        )

    def test_container_order_does_not_change_lifecycle_result(self) -> None:
        assertions = self._assertions()
        first = ReferenceContext(
            validator_input=make_valid_input(),
            admissibility_assertions=assertions,
        )
        second = ReferenceContext(
            validator_input=make_valid_input(),
            admissibility_assertions=tuple(reversed(assertions)),
        )

        self.assertEqual(
            first.current_admissibility(FORECAST_A, instant(4)),
            second.current_admissibility(FORECAST_A, instant(4)),
        )

    def test_same_time_conflict_is_unresolved_not_order_dependent(self) -> None:
        assertions = (
            AdmissibilityAssertion(
                FORECAST_A,
                True,
                effective_at=instant(2),
                known_at=instant(3),
                rationale="One assessment admits the source.",
            ),
            AdmissibilityAssertion(
                FORECAST_A,
                False,
                effective_at=instant(2),
                known_at=instant(3),
                rationale="Another assessment rejects the source.",
            ),
        )
        forward = ReferenceContext(
            validator_input=make_valid_input(),
            admissibility_assertions=assertions,
        )
        reverse = ReferenceContext(
            validator_input=make_valid_input(),
            admissibility_assertions=tuple(reversed(assertions)),
        )

        self.assertEqual(
            forward.current_admissibility(FORECAST_A, instant(4)),
            AdmissibilityStatus.UNRESOLVED,
        )
        self.assertEqual(
            reverse.current_admissibility(FORECAST_A, instant(4)),
            AdmissibilityStatus.UNRESOLVED,
        )


class ImmutabilityAndCompatibilityTests(unittest.TestCase):
    def test_w1a_structures_are_immutable(self) -> None:
        context = rrc_context()
        impact = context.invalidation_impact(FORECAST_A)

        with self.assertRaises(FrozenInstanceError):
            context.claims = ()  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            context.claims[0].target_id = TargetId("changed")  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            impact.direct_claims = ()  # type: ignore[misc]

    def test_query_results_are_deterministic_across_input_order(self) -> None:
        first = ClaimId.internal("first")
        second = ClaimId.internal("second")
        claims = (ClaimAnchor(RAIN), internal_claim("first"), internal_claim("second"))
        dependencies = (
            ClaimDependency(RAIN, first),
            ClaimDependency(first, second),
        )
        supports = (ReferenceSupport(FORECAST_B, RAIN),)
        forward = ReferenceContext(
            validator_input=make_valid_input(),
            claims=claims,
            reference_supports=supports,
            claim_dependencies=dependencies,
        )
        reverse = ReferenceContext(
            validator_input=make_valid_input(),
            claims=tuple(reversed(claims)),
            reference_supports=tuple(reversed(supports)),
            claim_dependencies=tuple(reversed(dependencies)),
        )

        self.assertEqual(forward.claim_ids, reverse.claim_ids)
        self.assertEqual(
            forward.transitive_dependents(FORECAST_A),
            reverse.transitive_dependents(FORECAST_A),
        )
        self.assertEqual(
            forward.reference_roots(second),
            reverse.reference_roots(second),
        )
        self.assertEqual(
            forward.invalidation_impact(FORECAST_A),
            reverse.invalidation_impact(FORECAST_A),
        )

    def test_w1a_is_not_exported_through_the_public_package(self) -> None:
        self.assertFalse(hasattr(rpf_validator, "ReferenceContext"))
        self.assertNotIn("ReferenceContext", rpf_validator.__all__)

    def test_constructing_w1a_context_does_not_change_public_behavior(self) -> None:
        model = make_valid_input()
        result_before = rpf_validator.evaluate(model)
        trace_before = rpf_validator.run_state_machine(result_before)

        context = ReferenceContext(
            validator_input=model,
            claims=(ClaimAnchor(RAIN),),
            admissibility_assertions=(
                AdmissibilityAssertion(
                    FORECAST_A,
                    False,
                    effective_at=instant(1),
                    known_at=instant(1),
                    rationale="Internal W1A lifecycle fixture.",
                ),
            ),
        )

        self.assertEqual(
            context.current_admissibility(FORECAST_A, instant(2)),
            AdmissibilityStatus.INADMISSIBLE,
        )
        result_after = rpf_validator.evaluate(model)
        self.assertEqual(result_after, result_before)
        self.assertEqual(rpf_validator.run_state_machine(result_after), trace_before)


if __name__ == "__main__":
    unittest.main()
