# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import unittest

from rpf_validator import (
    CLASSIFICATION_PROPOSAL_SCHEMA_VERSION,
    PROVIDER_CONFIDENCE_SCALE_ID,
    ClassificationProposal,
    DigestAlgorithm,
    DigestCanonicalization,
    InputValidationError,
    ProposalRole,
    ProviderKind,
    ReferenceFrameClass,
    ReferenceFrameStatus,
    load_classification_proposal,
    load_classification_proposal_schema,
    parse_classification_proposal,
    parse_classification_proposal_json,
    to_json,
    verify_source_payload,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
INVALID_CASES = (
    ROOT
    / "tests"
    / "fixtures"
    / "classification-proposal-invalid-cases-0.1.json"
)
PROPOSAL_SOURCES = {
    "classification-proposal-identified-0.1.json": (
        "classification-source-identified.txt"
    ),
    "classification-proposal-ambiguous-0.1.json": (
        "classification-source-ambiguous.txt"
    ),
    "classification-proposal-missing-0.1.json": (
        "classification-source-missing.txt"
    ),
}


def _set_path(value: object, dotted_path: str, replacement: object) -> None:
    current = value
    parts = dotted_path.split(".")
    for part in parts[:-1]:
        if isinstance(current, list):
            current = current[int(part)]
        else:
            assert isinstance(current, dict)
            current = current[part]
    final = parts[-1]
    if isinstance(current, list):
        current[int(final)] = replacement
    else:
        assert isinstance(current, dict)
        current[final] = replacement


class PublicClassificationProposalTests(unittest.TestCase):
    def test_all_public_proposals_parse_and_bind_to_their_sources(self) -> None:
        for proposal_name, source_name in PROPOSAL_SOURCES.items():
            with self.subTest(proposal=proposal_name):
                proposal = load_classification_proposal(EXAMPLES / proposal_name)
                source = (EXAMPLES / source_name).read_text(encoding="utf-8")

                self.assertEqual(
                    proposal.schema_version,
                    CLASSIFICATION_PROPOSAL_SCHEMA_VERSION,
                )
                self.assertIs(
                    proposal.proposal_role,
                    ProposalRole.NON_AUTHORITATIVE_SUGGESTION,
                )
                verify_source_payload(proposal, source)

    def test_identified_fixture_keeps_status_and_class_separate(self) -> None:
        proposal = load_classification_proposal(
            EXAMPLES / "classification-proposal-identified-0.1.json"
        )
        candidate = proposal.candidates[0]

        self.assertIs(candidate.status, ReferenceFrameStatus.IDENTIFIED)
        self.assertEqual(
            candidate.classes,
            (ReferenceFrameClass.OBJECTIVE_MEASUREMENT,),
        )
        self.assertFalse(hasattr(proposal, "overall_status"))
        self.assertFalse(hasattr(proposal.provider, "authority_level"))

    def test_ambiguous_fixture_preserves_alternative_candidates(self) -> None:
        proposal = load_classification_proposal(
            EXAMPLES / "classification-proposal-ambiguous-0.1.json"
        )

        self.assertEqual(len(proposal.candidates), 2)
        self.assertEqual(
            proposal.preferred_candidate_id,
            "frame-label-semantics",
        )
        self.assertIs(
            proposal.candidates[0].status,
            ReferenceFrameStatus.AMBIGUOUS,
        )
        self.assertEqual(len(proposal.uncertainties), 1)

    def test_missing_fixture_has_no_class_or_scope(self) -> None:
        proposal = load_classification_proposal(
            EXAMPLES / "classification-proposal-missing-0.1.json"
        )
        candidate = proposal.candidates[0]

        self.assertIs(candidate.status, ReferenceFrameStatus.MISSING)
        self.assertEqual(candidate.classes, ())
        self.assertIsNone(candidate.scope)

    def test_serialization_is_deterministic_and_round_trips(self) -> None:
        proposal = load_classification_proposal(
            EXAMPLES / "classification-proposal-ambiguous-0.1.json"
        )

        first = to_json(proposal)
        second = to_json(proposal)
        reparsed = parse_classification_proposal_json(first)

        self.assertEqual(first, second)
        self.assertEqual(reparsed, proposal)

    def test_models_are_immutable(self) -> None:
        proposal = load_classification_proposal(
            EXAMPLES / "classification-proposal-identified-0.1.json"
        )

        with self.assertRaises(FrozenInstanceError):
            proposal.proposal_id = "changed"  # type: ignore[misc]


class ProposalBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base_value = json.loads(
            (
                EXAMPLES / "classification-proposal-missing-0.1.json"
            ).read_text(encoding="utf-8")
        )

    def test_public_negative_case_catalog_is_rejected_as_declared(self) -> None:
        catalog = json.loads(INVALID_CASES.read_text(encoding="utf-8"))

        for case in catalog["cases"]:
            with self.subTest(case=case["case_id"]):
                value = deepcopy(self.base_value)
                _set_path(value, case["mutation_path"], case["value"])

                with self.assertRaises(InputValidationError) as caught:
                    parse_classification_proposal(value)

                self.assertEqual(
                    caught.exception.path,
                    case["expected_error_path"],
                )
                self.assertIn(
                    case["expected_message_fragment"],
                    caught.exception.message,
                )

    def test_provider_confidence_is_not_external_evidence(self) -> None:
        candidate = self.base_value["candidates"][0]
        self.assertIn("provider_confidence", candidate)
        self.assertNotIn("external_evidence", candidate)
        self.assertNotIn("internal_confidence", candidate)

    def test_duplicate_candidate_ids_are_rejected(self) -> None:
        value = json.loads(
            (
                EXAMPLES / "classification-proposal-ambiguous-0.1.json"
            ).read_text(encoding="utf-8")
        )
        value["candidates"][1]["candidate_id"] = value["candidates"][0][
            "candidate_id"
        ]

        with self.assertRaises(InputValidationError) as caught:
            parse_classification_proposal(value)

        self.assertEqual(caught.exception.path, "$.candidates")
        self.assertIn("unique", caught.exception.message)

    def test_unknown_evidence_reference_is_rejected(self) -> None:
        value = deepcopy(self.base_value)
        value["candidates"][0]["evidence_ids"] = ["absent-evidence"]

        with self.assertRaises(InputValidationError) as caught:
            parse_classification_proposal(value)

        self.assertIn("unknown evidence", caught.exception.message)

    def test_unknown_uncertainty_candidate_is_rejected(self) -> None:
        value = deepcopy(self.base_value)
        value["uncertainties"][0]["affects_candidate_ids"] = [
            "absent-candidate"
        ]

        with self.assertRaises(InputValidationError) as caught:
            parse_classification_proposal(value)

        self.assertIn("unknown candidates", caught.exception.message)

    def test_model_provider_requires_explicit_model_identity(self) -> None:
        value = deepcopy(self.base_value)
        value["provider"]["provider_kind"] = "MODEL_BASED"

        with self.assertRaises(InputValidationError) as caught:
            parse_classification_proposal(value)

        self.assertEqual(caught.exception.path, "$.provider")
        self.assertIn("model_id", caught.exception.message)

    def test_rule_provider_rejects_model_identity(self) -> None:
        value = deepcopy(self.base_value)
        value["provider"]["model_id"] = "example-model"
        value["provider"]["model_version"] = "1"

        with self.assertRaises(InputValidationError) as caught:
            parse_classification_proposal(value)

        self.assertEqual(caught.exception.path, "$.provider")
        self.assertIn("must not declare", caught.exception.message)

    def test_generated_at_requires_strict_rfc3339_with_timezone(self) -> None:
        invalid_values = (
            "2026-08-15T17:00:00",
            "2026-08-15 17:00:00+00:00",
            "2026-08-15T17:00:00+0000",
        )
        for invalid in invalid_values:
            with self.subTest(value=invalid):
                value = deepcopy(self.base_value)
                value["generated_at"] = invalid

                with self.assertRaises(InputValidationError) as caught:
                    parse_classification_proposal(value)

                self.assertEqual(caught.exception.path, "$.generated_at")
                self.assertIn("RFC 3339", caught.exception.message)

    def test_confidence_scale_is_fixed_by_the_contract(self) -> None:
        value = deepcopy(self.base_value)
        value["candidates"][0]["confidence_scale_id"] = "private-scale"

        with self.assertRaises(InputValidationError) as caught:
            parse_classification_proposal(value)

        self.assertEqual(
            caught.exception.path,
            "$.candidates[0].confidence_scale_id",
        )
        self.assertIn("provider-self-report", caught.exception.message)

    def test_assumptions_must_be_unique(self) -> None:
        value = deepcopy(self.base_value)
        value["candidates"][0]["assumptions"] = ["same", "same"]

        with self.assertRaises(InputValidationError) as caught:
            parse_classification_proposal(value)

        self.assertEqual(caught.exception.path, "$.candidates[0].assumptions")
        self.assertIn("unique", caught.exception.message)

    def test_fragment_source_must_match_bound_input_source(self) -> None:
        value = deepcopy(self.base_value)
        value["evidence_fragments"][0]["source_id"] = "different-source"

        with self.assertRaises(InputValidationError) as caught:
            parse_classification_proposal(value)

        self.assertIn("source_id", caught.exception.path)
        self.assertIn("must match", caught.exception.message)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        with self.assertRaises(InputValidationError) as caught:
            parse_classification_proposal_json(
                '{"schema_version":"a","schema_version":"b"}'
            )

        self.assertIn("duplicate", caught.exception.message)

    def test_non_standard_numeric_constants_are_rejected(self) -> None:
        with self.assertRaises(InputValidationError) as caught:
            parse_classification_proposal_json('{"value": NaN}')

        self.assertIn("non-standard", caught.exception.message)

    def test_source_payload_hash_mismatch_is_rejected(self) -> None:
        proposal = load_classification_proposal(
            EXAMPLES / "classification-proposal-identified-0.1.json"
        )

        with self.assertRaises(InputValidationError) as caught:
            verify_source_payload(proposal, "different source text")

        self.assertEqual(
            caught.exception.path,
            "classification_proposal.input_reference.payload_digest.value",
        )

    def test_fragment_digest_mismatch_is_rejected(self) -> None:
        proposal = load_classification_proposal(
            EXAMPLES / "classification-proposal-identified-0.1.json"
        )
        fragment = proposal.evidence_fragments[0]
        wrong_digest = replace(
            fragment.fragment_digest,
            value="0" * 64,
        )
        changed_fragment = replace(fragment, fragment_digest=wrong_digest)
        changed = replace(proposal, evidence_fragments=(changed_fragment,))
        source = (
            EXAMPLES / "classification-source-identified.txt"
        ).read_text(encoding="utf-8")

        with self.assertRaises(InputValidationError) as caught:
            verify_source_payload(changed, source)

        self.assertIn("fragment_digest.value", caught.exception.path)


class ClassificationProposalSchemaTests(unittest.TestCase):
    def test_bundled_schema_exposes_the_versioned_non_authoritative_contract(
        self,
    ) -> None:
        schema = load_classification_proposal_schema()

        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            CLASSIFICATION_PROPOSAL_SCHEMA_VERSION,
        )
        self.assertEqual(
            schema["properties"]["proposal_role"]["const"],
            "NON_AUTHORITATIVE_SUGGESTION",
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertNotIn("overall_status", schema["properties"])
        self.assertEqual(
            schema["$defs"]["frameCandidate"]["properties"][
                "confidence_scale_id"
            ]["const"],
            PROVIDER_CONFIDENCE_SCALE_ID,
        )

    def test_schema_loader_returns_a_fresh_copy(self) -> None:
        first = load_classification_proposal_schema()
        first["title"] = "changed"

        second = load_classification_proposal_schema()

        self.assertEqual(second["title"], "RPF Classification Proposal 0.1")

    def test_digest_enums_match_the_public_contract(self) -> None:
        self.assertEqual(DigestAlgorithm.SHA_256.value, "sha-256")
        self.assertEqual(DigestCanonicalization.RAW_UTF8.value, "raw-utf8")
        self.assertIs(ProviderKind.RULE_BASED, ProviderKind("RULE_BASED"))


if __name__ == "__main__":
    unittest.main()
