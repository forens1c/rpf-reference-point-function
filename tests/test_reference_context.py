# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from zoneinfo import ZoneInfo

import rpf_validator
from rpf_validator._reference_context import (
    AccessFinding,
    AccessStatus,
    AdmissibilityAssertion,
    AdmissibilityStatus,
    AgentId,
    ClaimAnchor,
    ClaimDependency,
    ClaimId,
    ClaimReferenceRoots,
    ClaimScope,
    PresenceFinding,
    PresenceStatus,
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


W1B_REFERENCE = ReferenceId.candidate("archive-entry")
W1B_SCOPE = ClaimScope.local("declared archive S1")
W1B_AGENT = AgentId("agent-a")
W1B_PRESENCE_CLAIM = ClaimId.internal("presence-assessment")
W1B_ACCESS_CLAIM = ClaimId.internal("access-assessment")


def w1b_context(
    presence: tuple[PresenceFinding, ...] = (),
    access: tuple[AccessFinding, ...] = (),
) -> ReferenceContext:
    """Synthetic declared findings; no semantic evidence assessment is implied."""

    findings = (*presence, *access)
    claims = tuple(
        sorted({f.claim_id for f in findings}, key=lambda c: c.local_id)
    )
    candidates = {W1B_REFERENCE} | {
        f.reference_id for f in findings
        if f.reference_id.namespace is W1B_REFERENCE.namespace
    }
    return ReferenceContext(
        validator_input=make_valid_input(),
        claims=tuple(
            ClaimAnchor(
                claim,
                internal_statement=f"Declared fixture assessment: {claim.local_id}",
                scope=W1B_SCOPE,
            )
            for claim in claims
        ),
        reference_candidates=tuple(
            ReferenceCandidate(r, "A represented reference, without implied presence.")
            for r in sorted(candidates, key=lambda r: r.local_id)
        ),
        reference_supports=tuple(ReferenceSupport(FORECAST_A, c) for c in claims),
        temporal_facts=tuple(
            fact for c in claims
            for fact in (
                TemporalFact(c, TemporalRole.TARGET_EVENT, instant(1)),
                TemporalFact(c, TemporalRole.AVAILABLE_TO_CONTEXT, instant(2)),
            )
        ),
        presence_findings=presence,
        access_findings=access,
    )


def w1b_time(
    context: ReferenceContext,
    claim_id: ClaimId,
    role: TemporalRole,
    value: datetime | TemporalMarker | None,
) -> ReferenceContext:
    facts = tuple(
        f for f in context.temporal_facts
        if (f.subject, f.role) != (claim_id, role)
    )
    if value is not None:
        facts += (TemporalFact(claim_id, role, value),)
    return replace(context, temporal_facts=facts)


def w1b_present() -> PresenceFinding:
    return PresenceFinding(
        W1B_REFERENCE, PresenceStatus.KNOWN_PRESENT, W1B_PRESENCE_CLAIM
    )


def w1b_access(status: AccessStatus = AccessStatus.AVAILABLE) -> AccessFinding:
    return AccessFinding(W1B_REFERENCE, W1B_AGENT, status, W1B_ACCESS_CLAIM)


def w1b_presence_view(
    context: ReferenceContext,
    *,
    scope: ClaimScope = W1B_SCOPE,
    target_time: datetime = instant(1),
    knowledge_cutoff: datetime = instant(5),
) -> PresenceStatus:
    return context.presence_at(
        W1B_REFERENCE, scope=scope, target_time=target_time,
        knowledge_cutoff=knowledge_cutoff,
    )


def w1b_access_view(
    context: ReferenceContext,
    agent_id: AgentId = W1B_AGENT,
    *,
    target_time: datetime = instant(1),
    knowledge_cutoff: datetime = instant(5),
) -> AccessStatus:
    return context.access_at(
        W1B_REFERENCE, agent_id, target_time=target_time,
        knowledge_cutoff=knowledge_cutoff,
    )


def w1b_determinism_snapshot(reverse: bool = False) -> tuple:
    """Construct from hash-ordered sets, then expose only query observations."""

    present = w1b_present()
    absent = PresenceFinding(
        W1B_REFERENCE, PresenceStatus.KNOWN_ABSENT, ClaimId.internal("absence")
    )
    available = w1b_access()
    unavailable = AccessFinding(
        W1B_REFERENCE, W1B_AGENT, AccessStatus.UNAVAILABLE,
        ClaimId.internal("unavailable"),
    )
    context = w1b_context(tuple({present, absent}), tuple({available, unavailable}))
    context = w1b_time(
        context, absent.claim_id, TemporalRole.AVAILABLE_TO_CONTEXT, instant(4)
    )
    context = w1b_time(
        context, unavailable.claim_id, TemporalRole.AVAILABLE_TO_CONTEXT, instant(4)
    )
    context = replace(
        context,
        claim_dependencies=(ClaimDependency(present.claim_id, available.claim_id),),
    )
    if reverse:
        context = replace(
            context,
            claims=tuple(reversed(context.claims)),
            reference_candidates=tuple(reversed(context.reference_candidates)),
            reference_supports=tuple(reversed(context.reference_supports)),
            temporal_facts=tuple(reversed(context.temporal_facts)),
            presence_findings=tuple(reversed(context.presence_findings)),
            access_findings=tuple(reversed(context.access_findings)),
        )
    return (
        tuple(
            (
                w1b_presence_view(context, knowledge_cutoff=cutoff).value,
                tuple(
                    (f.claim_id.local_id, f.status.value)
                    for f in context.presence_findings_at(
                        W1B_REFERENCE, scope=W1B_SCOPE, target_time=instant(1),
                        knowledge_cutoff=cutoff,
                    )
                ),
                w1b_access_view(context, knowledge_cutoff=cutoff).value,
                tuple(
                    (f.claim_id.local_id, f.status.value)
                    for f in context.access_findings_at(
                        W1B_REFERENCE, W1B_AGENT, target_time=instant(1),
                        knowledge_cutoff=cutoff,
                    )
                ),
            )
            for cutoff in (instant(1), instant(2), instant(5))
        ),
        tuple((f.claim_id.local_id, f.status.value)
              for f in context.presence_findings_for(W1B_REFERENCE)),
        tuple((f.claim_id.local_id, f.status.value)
              for f in context.access_findings_for(W1B_REFERENCE, W1B_AGENT)),
        tuple(c.local_id for c in context.invalidation_impact(FORECAST_A).affected_claims),
    )


class W1BFailureTests(unittest.TestCase):
    def test_f1_known_present_and_agent_inaccessible_coexist(self) -> None:
        context = w1b_context((w1b_present(),), (w1b_access(AccessStatus.UNAVAILABLE),))
        self.assertIs(w1b_presence_view(context), PresenceStatus.KNOWN_PRESENT)
        self.assertIs(w1b_access_view(context), AccessStatus.UNAVAILABLE)
        self.assertIs(
            context.current_admissibility(W1B_REFERENCE, instant(5)),
            AdmissibilityStatus.UNRESOLVED,
        )

    def test_f2_failed_search_does_not_create_absence(self) -> None:
        search = ClaimId.internal("limited-search")
        context = replace(
            w1b_context(),
            claims=(ClaimAnchor(
                search, internal_statement="Not found in an incomplete search.",
                scope=W1B_SCOPE,
            ),),
            reference_supports=(ReferenceSupport(FORECAST_A, search),),
            temporal_facts=(
                TemporalFact(search, TemporalRole.TARGET_EVENT, instant(1)),
                TemporalFact(search, TemporalRole.AVAILABLE_TO_CONTEXT, instant(2)),
            ),
        )
        self.assertEqual(context.presence_findings_for(W1B_REFERENCE), ())
        self.assertIs(w1b_presence_view(context), PresenceStatus.UNRESOLVED)

    def test_f3_known_absence_is_limited_to_declared_scope_and_instant(self) -> None:
        finding = replace(w1b_present(), status=PresenceStatus.KNOWN_ABSENT)
        context = w1b_context((finding,))
        context = replace(context, claims=(replace(
            context.claims[0],
            internal_statement=(
                "The supplied inventory assessment declares the bounded S1 "
                "fully inspected at t1 and reports no matching entry."
            ),
        ),))
        self.assertIs(w1b_presence_view(context), PresenceStatus.KNOWN_ABSENT)
        self.assertIs(
            w1b_presence_view(context, scope=ClaimScope.local("archive S2")),
            PresenceStatus.UNRESOLVED,
        )
        self.assertIs(
            w1b_presence_view(context, target_time=instant(2)),
            PresenceStatus.UNRESOLVED,
        )
        self.assertEqual(context.presence_findings_for(W1B_REFERENCE), (finding,))

    def test_f4_access_is_agent_specific_with_no_global_default(self) -> None:
        other = AgentId("agent-b")
        context = w1b_context(access=(
            w1b_access(),
            AccessFinding(W1B_REFERENCE, other, AccessStatus.UNAVAILABLE,
                          ClaimId.internal("other-agent")),
        ))
        self.assertIs(w1b_access_view(context, AgentId("agent-a")), AccessStatus.AVAILABLE)
        self.assertIs(w1b_access_view(context, other), AccessStatus.UNAVAILABLE)
        self.assertIs(w1b_access_view(context, AgentId("agent-c")), AccessStatus.UNRESOLVED)

    def test_f5_access_change_has_no_forward_or_backward_projection(self) -> None:
        early = w1b_access(AccessStatus.UNAVAILABLE)
        late = replace(early, status=AccessStatus.AVAILABLE,
                       claim_id=ClaimId.internal("later-access"))
        context = w1b_context(access=(early, late))
        context = w1b_time(context, late.claim_id, TemporalRole.TARGET_EVENT, instant(3))
        context = w1b_time(
            context, late.claim_id, TemporalRole.AVAILABLE_TO_CONTEXT, instant(4)
        )
        for day, expected in ((1, AccessStatus.UNAVAILABLE),
                              (2, AccessStatus.UNRESOLVED),
                              (3, AccessStatus.AVAILABLE),
                              (4, AccessStatus.UNRESOLVED)):
            with self.subTest(day=day):
                self.assertIs(w1b_access_view(context, target_time=instant(day)), expected)
        self.assertIs(
            w1b_access_view(context, target_time=instant(3), knowledge_cutoff=instant(3)),
            AccessStatus.UNRESOLVED,
        )

    def test_f6_cue_and_reference_are_not_aliased_by_target_or_dependency(self) -> None:
        cue = ReferenceId.candidate("correlated-cue")
        finding = replace(w1b_access(), reference_id=cue)
        other = internal_claim("same-target", target_id=TargetId("common-referent"))
        context = w1b_context(access=(finding,))
        context = replace(
            context,
            claims=(replace(context.claims[0], target_id=other.target_id), other),
            claim_dependencies=(ClaimDependency(finding.claim_id, other.claim_id),),
            reference_supports=context.reference_supports + (
                ReferenceSupport(W1B_REFERENCE, other.claim_id),
            ),
        )
        self.assertIs(context.access_at(
            cue, W1B_AGENT, target_time=instant(1), knowledge_cutoff=instant(5),
        ), AccessStatus.AVAILABLE)
        self.assertIs(w1b_access_view(context), AccessStatus.UNRESOLVED)

    def test_f7_multiple_paths_do_not_create_modality_or_more_evidence(self) -> None:
        first = w1b_access()
        second = replace(first, claim_id=ClaimId.internal("second-path"))
        context = w1b_context(access=(first, second))
        original_calibration = context.validator_input.calibration
        context = replace(context, claims=tuple(
            replace(c, internal_statement=text)
            for c, text in zip(context.claims, (
                "A visual delivery path is explicitly bound to R.",
                "An audio delivery path is explicitly bound to the same R.",
            ))
        ))
        self.assertIs(w1b_access_view(context), AccessStatus.AVAILABLE)
        self.assertEqual(context.reference_roots(first.claim_id), (FORECAST_A,))
        self.assertEqual(context.reference_roots(second.claim_id), (FORECAST_A,))
        self.assertIs(context.validator_input.calibration, original_calibration)
        self.assertNotIn("modality", {f.name for f in fields(first)})
        self.assertEqual(len(context.access_findings_for(W1B_REFERENCE, W1B_AGENT)), 2)

    def test_f8_content_conflict_does_not_mean_access_conflict(self) -> None:
        first = w1b_access()
        second = replace(first, claim_id=ClaimId.internal("opposing-content"))
        context = w1b_context(access=(first, second))
        context = replace(context, claims=tuple(
            replace(c, internal_statement=text)
            for c, text in zip(context.claims, (
                "The delivered account says the indicator is on.",
                "The delivered account says the indicator is off.",
            ))
        ))
        self.assertIs(w1b_access_view(context), AccessStatus.AVAILABLE)
        contents = tuple(context.claim_content(c.claim_id) for c in context.claims)
        self.assertNotEqual(*contents)
        conflicting = replace(second, status=AccessStatus.UNAVAILABLE)
        conflict_context = replace(context, access_findings=(first, conflicting))
        self.assertIs(w1b_access_view(conflict_context), AccessStatus.UNRESOLVED)
        self.assertEqual(len(conflict_context.access_findings_at(
            W1B_REFERENCE, W1B_AGENT, target_time=instant(1), knowledge_cutoff=instant(5),
        )), 2)
        self.assertEqual(
            tuple(conflict_context.claim_content(c.claim_id) for c in context.claims),
            contents,
        )

    def test_f9_access_does_not_add_control_or_operation_claims(self) -> None:
        context = w1b_context(access=(w1b_access(),))
        before = context.claims
        self.assertIs(w1b_access_view(context), AccessStatus.AVAILABLE)
        self.assertEqual(context.claims, before)
        self.assertEqual(context.claim_ids, (W1B_ACCESS_CLAIM,))
        self.assertFalse(hasattr(context.access_findings[0], "control"))

    def test_f10_operation_on_opaque_object_does_not_grant_content_access(self) -> None:
        operation = ClaimId.internal("delete-opaque-object")
        container = ReferenceId.candidate("encrypted-container")
        context = w1b_context(access=(w1b_access(AccessStatus.UNAVAILABLE),))
        context = replace(
            context,
            claims=context.claims + (ClaimAnchor(
                operation, internal_statement="A can delete the opaque container at t1.",
            ),),
            reference_candidates=context.reference_candidates + (
                ReferenceCandidate(container, "Opaque container, not its cleartext content."),
            ),
            reference_supports=context.reference_supports + (
                ReferenceSupport(container, operation),
            ),
        )
        self.assertIs(w1b_access_view(context), AccessStatus.UNAVAILABLE)
        self.assertIs(context.access_at(
            container, W1B_AGENT, target_time=instant(1), knowledge_cutoff=instant(5),
        ), AccessStatus.UNRESOLVED)
        self.assertEqual(context.reference_roots(operation), (container,))


class W1BStructureTests(unittest.TestCase):
    def test_opposite_presence_findings_in_different_scopes_do_not_conflict(self) -> None:
        present = w1b_present()
        absent = replace(present, status=PresenceStatus.KNOWN_ABSENT,
                         claim_id=ClaimId.internal("absent-in-S2"))
        scope2 = ClaimScope.local("declared archive S2")
        context = w1b_context((present, absent))
        context = replace(context, claims=tuple(
            replace(c, scope=scope2) if c.claim_id == absent.claim_id else c
            for c in context.claims
        ))
        self.assertIs(w1b_presence_view(context), PresenceStatus.KNOWN_PRESENT)
        self.assertIs(w1b_presence_view(context, scope=scope2), PresenceStatus.KNOWN_ABSENT)
        self.assertEqual(len(context.presence_findings_for(W1B_REFERENCE)), 2)

    def test_same_referent_does_not_merge_different_reference_states(self) -> None:
        other_state = ReferenceId.candidate("archive-entry-later-state")
        first = w1b_access()
        second = replace(first, reference_id=other_state, status=AccessStatus.UNAVAILABLE,
                         claim_id=ClaimId.internal("access-to-other-state"))
        context = w1b_context(access=(first, second))
        context = replace(context, claims=tuple(
            replace(c, target_id=TargetId("same-referent")) for c in context.claims
        ))
        self.assertIs(w1b_access_view(context), AccessStatus.AVAILABLE)
        self.assertIs(context.access_at(
            other_state, W1B_AGENT, target_time=instant(1), knowledge_cutoff=instant(5),
        ), AccessStatus.UNAVAILABLE)

    def test_registration_does_not_imply_presence_or_access(self) -> None:
        context = w1b_context()
        for reference in (W1B_REFERENCE, FORECAST_A):
            with self.subTest(reference=reference):
                self.assertEqual(context.presence_findings_for(reference), ())
                self.assertIs(context.presence_at(
                    reference, scope=W1B_SCOPE, target_time=instant(1),
                    knowledge_cutoff=instant(5),
                ), PresenceStatus.UNRESOLVED)
                self.assertIs(context.access_at(
                    reference, W1B_AGENT, target_time=instant(1),
                    knowledge_cutoff=instant(5),
                ), AccessStatus.UNRESOLVED)

    def test_positive_presence_does_not_promote_candidate_to_source(self) -> None:
        context = w1b_context((w1b_present(),))
        sources = context.validator_input.calibration.evidence_sources
        self.assertIs(w1b_presence_view(context), PresenceStatus.KNOWN_PRESENT)
        self.assertIn(W1B_REFERENCE, context.reference_ids)
        self.assertNotIn(W1B_REFERENCE.local_id, {s.source_id for s in sources})
        self.assertIsNone(context.availability_at(W1B_REFERENCE, instant(5)))
        self.assertIs(w1b_access_view(context), AccessStatus.UNRESOLVED)

    def test_determinate_presence_requires_explicit_scope(self) -> None:
        for status in (PresenceStatus.KNOWN_PRESENT, PresenceStatus.KNOWN_ABSENT):
            with self.subTest(status=status):
                context = w1b_context((replace(w1b_present(), status=status),))
                with self.assertRaisesRegex(ReferenceContextError, "explicit claim scope"):
                    replace(context, claims=(replace(context.claims[0], scope=None),))

    def test_unresolved_without_scope_or_basis_is_retained(self) -> None:
        finding = replace(w1b_present(), status=PresenceStatus.UNRESOLVED)
        context = w1b_context((finding,))
        context = replace(context, claims=(replace(context.claims[0], scope=None),),
                          reference_supports=())
        self.assertIs(w1b_presence_view(context), PresenceStatus.UNRESOLVED)
        self.assertEqual(context.presence_findings_for(W1B_REFERENCE), (finding,))

    def test_frame_scope_reuse_is_explicit_and_not_text_aliasing(self) -> None:
        context = w1b_context((w1b_present(),))
        frame_scope = ClaimScope.reference_frame()
        context = replace(context, claims=(replace(context.claims[0], scope=frame_scope),))
        self.assertIs(w1b_presence_view(context, scope=frame_scope), PresenceStatus.KNOWN_PRESENT)
        same_text = ClaimScope.local(context.validator_input.reference_frame.scope)
        self.assertIs(w1b_presence_view(context, scope=same_text), PresenceStatus.UNRESOLVED)
        self.assertEqual(context.scope_text(W1B_PRESENCE_CLAIM), same_text.text)

    def test_presence_needs_a_binding_beyond_examined_reference(self) -> None:
        context = w1b_context((w1b_present(),))
        for supports in ((), (ReferenceSupport(W1B_REFERENCE, W1B_PRESENCE_CLAIM),)):
            with self.subTest(supports=supports):
                with self.assertRaisesRegex(ReferenceContextError, "support path"):
                    replace(context, reference_supports=supports)

    def test_ordinary_support_never_generates_a_presence_finding(self) -> None:
        context = w1b_context((w1b_present(),))
        context = replace(context, presence_findings=())
        self.assertTrue(context.reference_roots(W1B_PRESENCE_CLAIM))
        self.assertIs(w1b_presence_view(context), PresenceStatus.UNRESOLVED)

    def test_absence_declaration_is_not_a_search_completeness_assessment(self) -> None:
        context = w1b_context((replace(w1b_present(), status=PresenceStatus.KNOWN_ABSENT),))
        context = replace(context, claims=(replace(
            context.claims[0],
            internal_statement="A supplied assessment whose method W1B cannot evaluate.",
        ),))
        # Only structural binding is checked. This is no certification of the assertion.
        self.assertIs(w1b_presence_view(context), PresenceStatus.KNOWN_ABSENT)
        self.assertEqual(context.reference_roots(W1B_PRESENCE_CLAIM), (FORECAST_A,))

    def test_observation_provenance_can_anchor_presence_directly_or_upstream(self) -> None:
        for direct in (True, False):
            with self.subTest(direct=direct):
                claim_id = OBSERVATION if direct else W1B_PRESENCE_CLAIM
                finding = replace(w1b_present(), claim_id=claim_id)
                claims = (ClaimAnchor(OBSERVATION, scope=W1B_SCOPE),)
                dependencies = ()
                if not direct:
                    claims += (internal_claim(claim_id.local_id, scope=W1B_SCOPE),)
                    dependencies = (ClaimDependency(OBSERVATION, claim_id),)
                context = ReferenceContext(
                    validator_input=make_valid_input(), claims=claims,
                    reference_candidates=(ReferenceCandidate(W1B_REFERENCE, "Candidate R."),),
                    claim_dependencies=dependencies,
                    presence_findings=(finding,),
                    temporal_facts=(
                        TemporalFact(claim_id, TemporalRole.TARGET_EVENT, instant(1)),
                        TemporalFact(claim_id, TemporalRole.AVAILABLE_TO_CONTEXT, instant(2)),
                    ),
                )
                self.assertIs(w1b_presence_view(context), PresenceStatus.KNOWN_PRESENT)
                self.assertEqual(context.claim_content(OBSERVATION),
                                 context.validator_input.observation.content)

    def test_hypothesis_anchor_reuses_implicit_evidence_bindings(self) -> None:
        context = ReferenceContext(
            validator_input=make_valid_input(),
            claims=(ClaimAnchor(RAIN, scope=W1B_SCOPE),),
            reference_candidates=(ReferenceCandidate(W1B_REFERENCE, "Candidate R."),),
            presence_findings=(replace(w1b_present(), claim_id=RAIN),),
        )
        self.assertEqual(context.reference_supports, ())
        self.assertEqual(context.reference_roots(RAIN), (FORECAST_A,))
        self.assertIs(w1b_presence_view(context), PresenceStatus.UNRESOLVED)  # Undated.

    def test_cycles_are_safe_but_do_not_supply_their_own_evidence(self) -> None:
        context = w1b_context((w1b_present(),))
        upstream = internal_claim("upstream")
        dependencies = (
            ClaimDependency(upstream.claim_id, W1B_PRESENCE_CLAIM),
            ClaimDependency(W1B_PRESENCE_CLAIM, upstream.claim_id),
        )
        context = replace(
            context, claims=context.claims + (upstream,),
            claim_dependencies=dependencies,
            reference_supports=(ReferenceSupport(FORECAST_A, upstream.claim_id),),
        )
        self.assertIs(w1b_presence_view(context), PresenceStatus.KNOWN_PRESENT)
        with self.assertRaisesRegex(ReferenceContextError, "support path"):
            replace(context, reference_supports=())

    def test_agent_identity_is_opaque_distinct_and_registry_free(self) -> None:
        agent = AgentId("shared-name")
        self.assertEqual(agent, AgentId("shared-name"))
        self.assertEqual(hash(agent), hash(AgentId("shared-name")))
        for other in (ClaimId.internal("shared-name"),
                      ReferenceId.candidate("shared-name"), TargetId("shared-name")):
            self.assertNotEqual(agent, other)
        self.assertIs(w1b_access_view(w1b_context(), agent), AccessStatus.UNRESOLVED)
        for bad in ("", "  ", None, 7):
            with self.subTest(bad=bad), self.assertRaises(ReferenceContextError):
                AgentId(bad)

    def test_finding_types_and_containers_are_strict(self) -> None:
        for finding, changes in (
            (w1b_present(), ({"status": "known_present"}, {"status": AccessStatus.UNRESOLVED},
                             {"reference_id": "archive-entry"}, {"claim_id": "claim"})),
            (w1b_access(), ({"status": "available"}, {"status": PresenceStatus.UNRESOLVED},
                           {"reference_id": W1B_ACCESS_CLAIM}, {"claim_id": W1B_REFERENCE},
                           {"agent_id": "agent-a"})),
        ):
            for change in changes:
                with self.subTest(change=change), self.assertRaises(ReferenceContextError):
                    replace(finding, **change)
        for change in ({"presence_findings": [w1b_present()]},
                       {"access_findings": [w1b_access()]},
                       {"presence_findings": (w1b_access(),)},
                       {"access_findings": (w1b_present(),)}):
            with self.subTest(change=change), self.assertRaises(ReferenceContextError):
                replace(w1b_context(), **change)

    def test_findings_must_bind_registered_references_and_enrolled_claims(self) -> None:
        context = w1b_context((w1b_present(),), (w1b_access(),))
        for field in ("presence_findings", "access_findings"):
            finding = getattr(context, field)[0]
            for change in ({"reference_id": ReferenceId.candidate("unknown")},
                           {"claim_id": ClaimId.internal("unknown")}):
                with (
                    self.subTest(field=field, change=change),
                    self.assertRaises(ReferenceContextError),
                ):
                    replace(context, **{field: (replace(finding, **change),)})

    def test_each_finding_uses_one_distinct_claim_anchor(self) -> None:
        context = w1b_context((w1b_present(),), (w1b_access(),))
        for change in (
            {"presence_findings": (w1b_present(), w1b_present())},
            {"access_findings": (w1b_access(), w1b_access())},
            {"access_findings": (replace(w1b_access(), claim_id=W1B_PRESENCE_CLAIM),)},
            {"access_findings": (w1b_access(), replace(w1b_access(), agent_id=AgentId("b")))},
        ):
            with (
                self.subTest(change=change),
                self.assertRaisesRegex(ReferenceContextError, "own claim"),
            ):
                replace(context, **change)

    def test_queries_reject_invalid_ids_scopes_and_naive_times(self) -> None:
        context = w1b_context()
        for query, keywords in (
            (w1b_presence_view, {"scope": None}),
            (w1b_presence_view, {"target_time": datetime(2026, 1, 1)}),
            (w1b_presence_view, {"knowledge_cutoff": datetime(2026, 1, 5)}),
            (w1b_access_view, {"target_time": datetime(2026, 1, 1)}),
            (w1b_access_view, {"knowledge_cutoff": datetime(2026, 1, 5)}),
            (w1b_access_view, {"agent_id": "agent-a"}),
        ):
            with self.subTest(keywords=keywords), self.assertRaises(ReferenceContextError):
                query(context, **keywords)
        for query in (context.presence_findings_for,
                      lambda r: context.access_findings_for(r, W1B_AGENT)):
            with self.assertRaises(ReferenceContextError):
                query(ReferenceId.candidate("not-registered"))
        model = replace(context.validator_input, reference_frame=replace(
            context.validator_input.reference_frame, scope=None,
        ))
        with self.assertRaises(ReferenceContextError):
            w1b_presence_view(replace(context, validator_input=model),
                              scope=ClaimScope.reference_frame())


class W1BHistoryTests(unittest.TestCase):
    def test_upper_bound_cutoff_with_negative_offset_includes_known_findings(self) -> None:
        context = w1b_context((w1b_present(),), (w1b_access(),))
        for offset in (-timedelta(hours=1), -timedelta(days=1, microseconds=-1)):
            cutoff = datetime.max.replace(tzinfo=timezone(offset))
            with self.subTest(offset=offset):
                self.assertIs(
                    w1b_presence_view(context, knowledge_cutoff=cutoff),
                    PresenceStatus.KNOWN_PRESENT,
                )
                self.assertIs(
                    w1b_access_view(context, knowledge_cutoff=cutoff),
                    AccessStatus.AVAILABLE,
                )

    def test_lower_bound_cutoff_with_positive_offset_excludes_later_findings(self) -> None:
        context = w1b_context((w1b_present(),), (w1b_access(),))
        for offset in (timedelta(hours=1), timedelta(days=1, microseconds=-1)):
            cutoff = datetime.min.replace(tzinfo=timezone(offset))
            with self.subTest(offset=offset):
                self.assertIs(
                    w1b_presence_view(context, knowledge_cutoff=cutoff),
                    PresenceStatus.UNRESOLVED,
                )
                self.assertIs(
                    w1b_access_view(context, knowledge_cutoff=cutoff),
                    AccessStatus.UNRESOLVED,
                )

    def _assert_boundary_instants(self, query, unresolved, resolved) -> None:
        for event, equivalent in (
            (
                datetime.min.replace(tzinfo=timezone(timedelta(hours=1))),
                datetime.min.replace(hour=1, tzinfo=timezone(timedelta(hours=2))),
            ),
            (
                datetime.max.replace(tzinfo=timezone(-timedelta(hours=1))),
                datetime.max.replace(hour=22, tzinfo=timezone(-timedelta(hours=2))),
            ),
        ):
            context = w1b_context((w1b_present(),), (w1b_access(),))
            for claim in (W1B_PRESENCE_CLAIM, W1B_ACCESS_CLAIM):
                context = w1b_time(context, claim, TemporalRole.TARGET_EVENT, event)
                context = w1b_time(
                    context, claim, TemporalRole.AVAILABLE_TO_CONTEXT, event
                )
            with self.subTest(event=event):
                self.assertIs(
                    query(context, target_time=equivalent, knowledge_cutoff=equivalent),
                    resolved,
                )
                self.assertIs(
                    query(context, target_time=equivalent,
                          knowledge_cutoff=equivalent - timedelta(microseconds=1)),
                    unresolved,
                )
                later = equivalent + timedelta(microseconds=1)
                self.assertIs(
                    query(context, target_time=later, knowledge_cutoff=later),
                    unresolved,
                )

    def test_presence_boundary_instants_preserve_exact_equality_and_order(self) -> None:
        self._assert_boundary_instants(
            w1b_presence_view, PresenceStatus.UNRESOLVED, PresenceStatus.KNOWN_PRESENT
        )

    def test_access_boundary_instants_preserve_exact_equality_and_order(self) -> None:
        self._assert_boundary_instants(
            w1b_access_view, AccessStatus.UNRESOLVED, AccessStatus.AVAILABLE
        )

    def test_repeated_local_times_remain_distinct_event_and_knowledge_instants(self) -> None:
        zone = ZoneInfo("Europe/Berlin")
        early = datetime(2026, 10, 25, 2, 30, tzinfo=zone, fold=0)
        late = datetime(2026, 10, 25, 2, 30, tzinfo=zone, fold=1)
        context = w1b_context((w1b_present(),), (w1b_access(),))
        for claim in (W1B_PRESENCE_CLAIM, W1B_ACCESS_CLAIM):
            context = w1b_time(context, claim, TemporalRole.TARGET_EVENT, early)
            context = w1b_time(context, claim, TemporalRole.AVAILABLE_TO_CONTEXT, late)
        for query, unresolved, resolved in (
            (w1b_presence_view, PresenceStatus.UNRESOLVED, PresenceStatus.KNOWN_PRESENT),
            (w1b_access_view, AccessStatus.UNRESOLVED, AccessStatus.AVAILABLE),
        ):
            with self.subTest(query=query.__name__):
                self.assertIs(query(context, target_time=early, knowledge_cutoff=early), unresolved)
                self.assertIs(query(context, target_time=late, knowledge_cutoff=late), unresolved)
                self.assertIs(query(context, target_time=early, knowledge_cutoff=late), resolved)

    def test_finding_knowledge_time_is_separate_from_target_creation_and_roots(self) -> None:
        context = w1b_context((w1b_present(),), (w1b_access(),))
        for claim in (W1B_PRESENCE_CLAIM, W1B_ACCESS_CLAIM):
            context = w1b_time(context, claim, TemporalRole.AVAILABLE_TO_CONTEXT, instant(4))
            context = w1b_time(context, claim, TemporalRole.CREATION_DERIVATION, instant(1))
        context = replace(context, temporal_facts=context.temporal_facts + (
            TemporalFact(FORECAST_A, TemporalRole.AVAILABLE_TO_CONTEXT, instant(1)),
        ))
        self.assertEqual(context.available_reference_roots(W1B_PRESENCE_CLAIM, instant(2)),
                         (FORECAST_A,))
        for query, unresolved, resolved in (
            (w1b_presence_view, PresenceStatus.UNRESOLVED, PresenceStatus.KNOWN_PRESENT),
            (w1b_access_view, AccessStatus.UNRESOLVED, AccessStatus.AVAILABLE),
        ):
            with self.subTest(query=query.__name__):
                self.assertIs(query(context, knowledge_cutoff=instant(2)), unresolved)
                self.assertIs(query(context, knowledge_cutoff=instant(4)), resolved)
                self.assertIs(query(context, knowledge_cutoff=instant(2)), unresolved)
        self.assertEqual(context.presence_findings_at(
            W1B_REFERENCE, scope=W1B_SCOPE, target_time=instant(1), knowledge_cutoff=instant(2),
        ), ())
        self.assertEqual(context.access_findings_at(
            W1B_REFERENCE, W1B_AGENT, target_time=instant(1), knowledge_cutoff=instant(2),
        ), ())
        self.assertEqual(len(context.presence_findings_for(W1B_REFERENCE)), 1)
        self.assertEqual(len(context.access_findings_for(W1B_REFERENCE, W1B_AGENT)), 1)

    def _assert_noninstant_times(self, marker: TemporalMarker | None) -> None:
        original = w1b_context((w1b_present(),), (w1b_access(),))
        for role in (TemporalRole.TARGET_EVENT, TemporalRole.AVAILABLE_TO_CONTEXT):
            context = original
            for claim in (W1B_PRESENCE_CLAIM, W1B_ACCESS_CLAIM):
                context = w1b_time(context, claim, role, marker)
                self.assertIs(context.temporal_value(claim, role), marker)
            with self.subTest(role=role):
                self.assertIs(w1b_presence_view(context), PresenceStatus.UNRESOLVED)
                self.assertIs(w1b_access_view(context), AccessStatus.UNRESOLVED)
                self.assertEqual(context.presence_findings_for(W1B_REFERENCE), (w1b_present(),))
                self.assertEqual(
                    context.access_findings_for(W1B_REFERENCE, W1B_AGENT),
                    (w1b_access(),),
                )

    def test_unknown_time_is_preserved_but_does_not_match(self) -> None:
        self._assert_noninstant_times(TemporalMarker.UNKNOWN)

    def test_not_applicable_time_is_preserved_but_does_not_match(self) -> None:
        self._assert_noninstant_times(TemporalMarker.NOT_APPLICABLE)

    def test_unmodeled_time_remains_distinct_and_does_not_match(self) -> None:
        self._assert_noninstant_times(None)

    def test_timezone_aware_equivalent_instants_match(self) -> None:
        context = w1b_context((w1b_present(),), (w1b_access(),))
        equivalent = datetime(2026, 1, 1, 2, tzinfo=timezone(timedelta(hours=2)))
        self.assertIs(
            w1b_presence_view(context, target_time=equivalent),
            PresenceStatus.KNOWN_PRESENT,
        )
        self.assertIs(w1b_access_view(context, target_time=equivalent), AccessStatus.AVAILABLE)

    def test_empty_explicit_unresolved_and_conflict_retain_different_records(self) -> None:
        unknown_presence = replace(w1b_present(), status=PresenceStatus.UNRESOLVED)
        opposite_presence = replace(w1b_present(), status=PresenceStatus.KNOWN_ABSENT,
                                    claim_id=ClaimId.internal("opposite-presence"))
        unknown_access = replace(w1b_access(), status=AccessStatus.UNRESOLVED)
        opposite_access = replace(w1b_access(), status=AccessStatus.UNAVAILABLE,
                                  claim_id=ClaimId.internal("opposite-access"))
        for presence, access, count in (
            ((), (), 0),
            ((unknown_presence,), (unknown_access,), 1),
            ((w1b_present(), opposite_presence), (w1b_access(), opposite_access), 2),
        ):
            with self.subTest(count=count):
                context = w1b_context(presence, access)
                self.assertIs(w1b_presence_view(context), PresenceStatus.UNRESOLVED)
                self.assertIs(w1b_access_view(context), AccessStatus.UNRESOLVED)
                self.assertEqual(len(context.presence_findings_at(
                    W1B_REFERENCE, scope=W1B_SCOPE, target_time=instant(1),
                    knowledge_cutoff=instant(5),
                )), count)
                self.assertEqual(len(context.access_findings_at(
                    W1B_REFERENCE, W1B_AGENT, target_time=instant(1),
                    knowledge_cutoff=instant(5),
                )), count)

    def test_later_arrival_and_majority_do_not_override_conflict(self) -> None:
        p = w1b_present()
        a = w1b_access()
        opposite_p = replace(p, status=PresenceStatus.KNOWN_ABSENT,
                             claim_id=ClaimId.internal("opposite-presence"))
        opposite_a = replace(a, status=AccessStatus.UNAVAILABLE,
                             claim_id=ClaimId.internal("opposite-access"))
        context = w1b_context(
            (p, replace(p, claim_id=ClaimId.internal("another-present")), opposite_p),
            (a, replace(a, claim_id=ClaimId.internal("another-available")), opposite_a),
        )
        for claim in (opposite_p.claim_id, opposite_a.claim_id):
            context = w1b_time(context, claim, TemporalRole.AVAILABLE_TO_CONTEXT, instant(4))
        self.assertIs(
            w1b_presence_view(context, knowledge_cutoff=instant(2)),
            PresenceStatus.KNOWN_PRESENT,
        )
        self.assertIs(w1b_access_view(context, knowledge_cutoff=instant(2)), AccessStatus.AVAILABLE)
        self.assertIs(w1b_presence_view(context), PresenceStatus.UNRESOLVED)
        self.assertIs(w1b_access_view(context), AccessStatus.UNRESOLVED)
        reverse = replace(context, presence_findings=tuple(reversed(context.presence_findings)),
                          access_findings=tuple(reversed(context.access_findings)))
        self.assertEqual(context.presence_findings_for(W1B_REFERENCE),
                         reverse.presence_findings_for(W1B_REFERENCE))
        self.assertEqual(context.access_findings_for(W1B_REFERENCE, W1B_AGENT),
                         reverse.access_findings_for(W1B_REFERENCE, W1B_AGENT))
        self.assertIs(w1b_presence_view(reverse), PresenceStatus.UNRESOLVED)
        self.assertIs(w1b_access_view(reverse), AccessStatus.UNRESOLVED)

    def test_explicit_unresolved_is_not_silently_discarded(self) -> None:
        p = replace(w1b_present(), status=PresenceStatus.UNRESOLVED,
                    claim_id=ClaimId.internal("open-presence"))
        a = replace(w1b_access(), status=AccessStatus.UNRESOLVED,
                    claim_id=ClaimId.internal("open-access"))
        context = w1b_context((w1b_present(), p), (w1b_access(), a))
        self.assertIs(w1b_presence_view(context), PresenceStatus.UNRESOLVED)
        self.assertIs(w1b_access_view(context), AccessStatus.UNRESOLVED)
        self.assertIn(p, context.presence_findings_for(W1B_REFERENCE))
        self.assertIn(a, context.access_findings_for(W1B_REFERENCE, W1B_AGENT))


class W1BCompatibilityTests(unittest.TestCase):
    def test_root_invalidation_finds_claims_without_inverting_findings(self) -> None:
        context = w1b_context((w1b_present(),), (w1b_access(),))
        context = replace(
            context,
            reference_supports=(ReferenceSupport(FORECAST_A, W1B_PRESENCE_CLAIM),
                                ReferenceSupport(FORECAST_B, W1B_PRESENCE_CLAIM)),
            claim_dependencies=(ClaimDependency(W1B_PRESENCE_CLAIM, W1B_ACCESS_CLAIM),),
        )
        invalidated = replace(context, admissibility_assertions=(AdmissibilityAssertion(
            FORECAST_A, False, effective_at=instant(1), known_at=instant(4),
            rationale="A later audit invalidates the declared supporting source.",
        ),))
        impact = invalidated.invalidation_impact(FORECAST_A)
        self.assertEqual(impact.direct_claims, (W1B_PRESENCE_CLAIM,))
        self.assertEqual(impact.transitive_dependents, (W1B_ACCESS_CLAIM,))
        self.assertTrue(all(r.reference_ids == (FORECAST_B,) for r in impact.remaining_roots))
        self.assertEqual(invalidated.reference_supports, context.reference_supports)
        self.assertEqual(invalidated.claims, context.claims)
        self.assertEqual(invalidated.presence_findings, context.presence_findings)
        self.assertEqual(invalidated.access_findings, context.access_findings)
        self.assertIs(w1b_presence_view(invalidated), PresenceStatus.KNOWN_PRESENT)
        self.assertIs(w1b_access_view(invalidated), AccessStatus.AVAILABLE)
        self.assertIs(invalidated.current_admissibility(FORECAST_A, instant(5)),
                      AdmissibilityStatus.INADMISSIBLE)

    def test_presence_access_and_admissibility_do_not_override_each_other(self) -> None:
        context = w1b_context((w1b_present(),), (w1b_access(),))
        context = replace(context, admissibility_assertions=(AdmissibilityAssertion(
            W1B_REFERENCE, False, instant(1), instant(2), "Declared inadmissible.",
        ),))
        self.assertIs(w1b_presence_view(context), PresenceStatus.KNOWN_PRESENT)
        self.assertIs(w1b_access_view(context), AccessStatus.AVAILABLE)
        self.assertIs(context.current_admissibility(W1B_REFERENCE, instant(5)),
                      AdmissibilityStatus.INADMISSIBLE)

    def test_w1b_structures_and_query_records_are_immutable(self) -> None:
        context = w1b_context((w1b_present(),), (w1b_access(),))
        for obj, attribute, value in (
            (context, "presence_findings", ()),
            (context, "access_findings", ()),
            (W1B_AGENT, "local_id", "changed"),
            (context.presence_findings_for(W1B_REFERENCE)[0],
             "status", PresenceStatus.KNOWN_ABSENT),
            (context.access_findings_for(W1B_REFERENCE, W1B_AGENT)[0],
             "status", AccessStatus.UNAVAILABLE),
        ):
            with self.subTest(attribute=attribute), self.assertRaises(FrozenInstanceError):
                setattr(obj, attribute, value)
        self.assertIsInstance(context.presence_findings_for(W1B_REFERENCE), tuple)
        self.assertIsInstance(context.access_findings_for(W1B_REFERENCE, W1B_AGENT), tuple)

    def test_queries_are_deterministic_under_insertion_order_changes(self) -> None:
        self.assertEqual(w1b_determinism_snapshot(), w1b_determinism_snapshot(reverse=True))

    def test_queries_are_deterministic_across_hash_seeds(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = (
            "import json; from tests.test_reference_context import w1b_determinism_snapshot; "
            "print(json.dumps(w1b_determinism_snapshot(), sort_keys=True))"
        )
        expected = json.dumps(w1b_determinism_snapshot(), sort_keys=True)
        for seed in ("0", "1", "42", "8675309"):
            with self.subTest(seed=seed):
                result = subprocess.run(
                    [sys.executable, "-B", "-c", script], cwd=root,
                    env={**os.environ, "PYTHONHASHSEED": seed,
                         "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(root / "src")},
                    capture_output=True, text=True, check=True, timeout=20,
                )
                self.assertEqual(result.stdout.strip(), expected)

    def test_new_types_stay_private_and_have_no_promoted_dimensions(self) -> None:
        for name in (
            "AgentId", "PresenceStatus", "AccessStatus", "PresenceFinding", "AccessFinding"
        ):
            self.assertFalse(hasattr(rpf_validator, name))
            self.assertNotIn(name, rpf_validator.__all__)
        forbidden = {"modality", "control", "authority", "exclusivity", "valuation",
                     "interpretability", "sufficiency", "confidence", "independence",
                     "truth", "causality", "finding_id"}
        for obj in (w1b_present(), w1b_access(), W1B_AGENT):
            self.assertFalse(forbidden & {f.name for f in fields(obj)})
        self.assertEqual(
            {s.value for s in AccessStatus}, {"available", "unavailable", "unresolved"}
        )

    def test_existing_public_fixture_outputs_and_traces_do_not_change(self) -> None:
        examples = Path(__file__).resolve().parents[1] / "examples"
        paths = sorted(examples.glob("*-input-0.2.json"))
        self.assertEqual(len(paths), 7)
        for path in paths:
            with self.subTest(path=path.name):
                model = rpf_validator.load_input(path)
                result = rpf_validator.evaluate(model)
                output_before = rpf_validator.to_json(result)
                trace_before = rpf_validator.to_json(rpf_validator.run_state_machine(result))
                template = w1b_context((w1b_present(),), (w1b_access(),))
                context = replace(
                    template, validator_input=model,
                    claims=template.claims + (ClaimAnchor(OBSERVATION),),
                    reference_supports=(),
                    claim_dependencies=(ClaimDependency(OBSERVATION, W1B_PRESENCE_CLAIM),),
                )
                self.assertIs(context.validator_input, model)
                self.assertIs(w1b_presence_view(context), PresenceStatus.KNOWN_PRESENT)
                self.assertIs(w1b_access_view(context), AccessStatus.AVAILABLE)
                result_after = rpf_validator.evaluate(model)
                self.assertEqual(rpf_validator.to_json(result_after), output_before)
                self.assertEqual(
                    rpf_validator.to_json(rpf_validator.run_state_machine(result_after)),
                    trace_before,
                )


if __name__ == "__main__":
    unittest.main()
