# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path

from rpf_validator.cli import (
    EXIT_INPUT_ERROR,
    EXIT_IO_ERROR,
    EXIT_SUCCESS,
    main,
)

ROOT = Path(__file__).resolve().parents[1]
WEATHER_EXAMPLE = ROOT / "examples" / "weather-input-0.2.json"


def run_cli(
    *args: str,
    stdin_text: str = "",
) -> tuple[int, str, str]:
    stdin = StringIO(stdin_text)
    stdout = StringIO()
    stderr = StringIO()
    code = main(args, stdin=stdin, stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()


class CliTests(unittest.TestCase):
    def test_validate_public_example_emits_pass_result(self) -> None:
        code, stdout, stderr = run_cli("validate", str(WEATHER_EXAMPLE))

        self.assertEqual(code, EXIT_SUCCESS)
        self.assertEqual(stderr, "")
        self.assertEqual(json.loads(stdout)["overall_status"], "PASS")

    def test_validate_can_read_standard_input(self) -> None:
        source = WEATHER_EXAMPLE.read_text(encoding="utf-8")

        code, stdout, stderr = run_cli("validate", "-", stdin_text=source)

        self.assertEqual(code, EXIT_SUCCESS)
        self.assertEqual(stderr, "")
        self.assertEqual(json.loads(stdout)["case_id"], "weather-001")

    def test_compact_output_is_one_line(self) -> None:
        code, stdout, _ = run_cli(
            "validate",
            str(WEATHER_EXAMPLE),
            "--compact",
        )

        self.assertEqual(code, EXIT_SUCCESS)
        self.assertEqual(len(stdout.splitlines()), 1)

    def test_stop_is_a_valid_evaluation_not_a_cli_failure(self) -> None:
        value = json.loads(WEATHER_EXAMPLE.read_text(encoding="utf-8"))
        value["termination"]["iteration"] = 5
        stdin_text = json.dumps(value)

        code, stdout, stderr = run_cli(
            "validate",
            "-",
            stdin_text=stdin_text,
        )

        self.assertEqual(code, EXIT_SUCCESS)
        self.assertEqual(stderr, "")
        self.assertEqual(json.loads(stdout)["overall_status"], "STOP")

    def test_invalid_input_emits_machine_readable_error(self) -> None:
        code, stdout, stderr = run_cli(
            "validate",
            "-",
            stdin_text='{ "case_id": ',
        )

        self.assertEqual(code, EXIT_INPUT_ERROR)
        self.assertEqual(stdout, "")
        payload = json.loads(stderr)["error"]
        self.assertEqual(payload["code"], "INPUT_SCHEMA_INVALID")
        self.assertEqual(payload["path"], "$")
        self.assertIn("invalid JSON", payload["message"])

    def test_missing_file_emits_machine_readable_io_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "absent.json"
            code, stdout, stderr = run_cli("validate", str(missing))

        self.assertEqual(code, EXIT_IO_ERROR)
        self.assertEqual(stdout, "")
        payload = json.loads(stderr)["error"]
        self.assertEqual(payload["code"], "INPUT_FILE_ERROR")
        self.assertEqual(payload["path"], str(missing))

    def test_schema_command_emits_bundled_contract(self) -> None:
        code, stdout, stderr = run_cli("schema", "--compact")

        self.assertEqual(code, EXIT_SUCCESS)
        self.assertEqual(stderr, "")
        self.assertEqual(
            json.loads(stdout)["properties"]["schema_version"]["const"],
            "rpf-validator-input-0.2",
        )
        self.assertEqual(len(stdout.splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
