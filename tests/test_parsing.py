# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from rpf_validator import (
    INPUT_SCHEMA_RESOURCE,
    INPUT_SCHEMA_VERSION,
    InputValidationError,
    ProcessStatus,
    evaluate,
    load_input,
    load_input_schema,
    parse_input,
    parse_json,
    to_json,
    to_primitive,
)
from tests.test_models import make_valid_input

ROOT = Path(__file__).resolve().parents[1]
WEATHER_EXAMPLE = ROOT / "examples" / "weather-input-0.2.json"


class JsonParserTests(unittest.TestCase):
    def test_public_weather_example_loads_and_passes(self) -> None:
        model = load_input(WEATHER_EXAMPLE)

        self.assertEqual(model.schema_version, INPUT_SCHEMA_VERSION)
        self.assertEqual(evaluate(model).overall_status, ProcessStatus.PASS)

    def test_serialized_model_round_trips_without_loss(self) -> None:
        expected = make_valid_input()

        parsed = parse_json(to_json(expected))

        self.assertEqual(parsed, expected)
        self.assertEqual(parse_input(to_primitive(expected)), expected)

    def test_unknown_top_level_field_is_rejected(self) -> None:
        value = to_primitive(make_valid_input())
        value["invented"] = True

        with self.assertRaises(InputValidationError) as caught:
            parse_input(value)

        self.assertEqual(caught.exception.path, "$")
        self.assertIn("unknown fields: invented", caught.exception.message)

    def test_missing_required_field_is_rejected(self) -> None:
        value = to_primitive(make_valid_input())
        del value["observation"]

        with self.assertRaises(InputValidationError) as caught:
            parse_input(value)

        self.assertEqual(caught.exception.path, "$")
        self.assertIn("missing required fields: observation", caught.exception.message)

    def test_bad_enum_reports_precise_json_path(self) -> None:
        value = to_primitive(make_valid_input())
        value["competence"]["status"] = "CERTAIN"

        with self.assertRaises(InputValidationError) as caught:
            parse_input(value)

        self.assertEqual(caught.exception.path, "$.competence.status")
        self.assertIn("SUFFICIENT", caught.exception.message)

    def test_nested_model_error_reports_precise_json_path(self) -> None:
        value = to_primitive(make_valid_input())
        value["candidate_actions"][0]["effects"][0]["expected_cost"] = ""

        with self.assertRaises(InputValidationError) as caught:
            parse_input(value)

        self.assertEqual(
            caught.exception.path,
            "$.candidate_actions[0].effects[0].expected_cost",
        )

    def test_cross_reference_error_reports_precise_json_path(self) -> None:
        value = to_primitive(make_valid_input())
        value["hypotheses"][0]["evidence_source_ids"] = ["absent"]

        with self.assertRaises(InputValidationError) as caught:
            parse_input(value)

        self.assertEqual(
            caught.exception.path,
            "$.hypotheses[0].evidence_source_ids",
        )
        self.assertIn("unknown source identifiers", caught.exception.message)

    def test_invalid_json_syntax_is_rejected(self) -> None:
        with self.assertRaises(InputValidationError) as caught:
            parse_json('{"case_id":')

        self.assertEqual(caught.exception.path, "$")
        self.assertIn("invalid JSON at line 1", caught.exception.message)

    def test_duplicate_json_key_is_rejected(self) -> None:
        with self.assertRaises(InputValidationError) as caught:
            parse_json('{"case_id": "a", "case_id": "b"}')

        self.assertEqual(caught.exception.path, "$")
        self.assertIn("duplicate object key 'case_id'", caught.exception.message)

    def test_non_standard_json_number_is_rejected(self) -> None:
        with self.assertRaises(InputValidationError) as caught:
            parse_json('{"value": NaN}')

        self.assertEqual(caught.exception.path, "$")
        self.assertIn("non-standard numeric constant 'NaN'", caught.exception.message)

    def test_non_text_input_is_rejected(self) -> None:
        with self.assertRaises(InputValidationError) as caught:
            parse_json(b"{}")  # type: ignore[arg-type]

        self.assertEqual(caught.exception.path, "$")
        self.assertEqual(caught.exception.message, "must be JSON text")


class BundledSchemaTests(unittest.TestCase):
    def test_schema_identifies_the_published_input_contract(self) -> None:
        schema = load_input_schema()

        self.assertEqual(
            INPUT_SCHEMA_RESOURCE,
            "schemas/rpf-validator-input-0.2.schema.json",
        )
        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            INPUT_SCHEMA_VERSION,
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertIn("validator_config", schema["required"])

    def test_schema_loader_returns_a_fresh_object(self) -> None:
        first = load_input_schema()
        original = deepcopy(first)
        first["title"] = "Changed locally"

        self.assertEqual(load_input_schema(), original)

    def test_public_example_uses_only_declared_top_level_properties(self) -> None:
        schema = load_input_schema()
        value = json.loads(WEATHER_EXAMPLE.read_text(encoding="utf-8"))

        self.assertEqual(set(value), set(schema["properties"]))
        self.assertTrue(set(schema["required"]).issubset(value))


if __name__ == "__main__":
    unittest.main()
