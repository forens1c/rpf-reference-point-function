# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Command-line interface for the RPF validator and state-machine runtime."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence, TextIO

from rpf_validator.errors import InputValidationError
from rpf_validator.evaluator import evaluate
from rpf_validator.parsing import parse_json
from rpf_validator.schema import load_input_schema
from rpf_validator.serialization import to_json
from rpf_validator.state_machine import StateMachineError, run_state_machine

EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_IO_ERROR = 3
EXIT_STATE_MACHINE_ERROR = 4


def _build_parser(version: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rpf",
        description=(
            "Validate or trace a declared reasoning process against the "
            "experimental RPF rules. This does not determine factual truth."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"rpf-validator {version}",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser(
        "validate",
        help="validate one versioned JSON input file",
    )
    validate.add_argument(
        "input",
        help="path to the JSON input file, or '-' to read standard input",
    )
    validate.add_argument(
        "--compact",
        action="store_true",
        help="emit the result on one line",
    )

    trace = commands.add_parser(
        "trace",
        help="validate one input and emit its bounded state-machine trace",
    )
    trace.add_argument(
        "input",
        help="path to the JSON input file, or '-' to read standard input",
    )
    trace.add_argument(
        "--compact",
        action="store_true",
        help="emit the trace on one line",
    )

    schema = commands.add_parser(
        "schema",
        help="print the bundled input JSON Schema",
    )
    schema.add_argument(
        "--compact",
        action="store_true",
        help="emit the schema on one line",
    )
    return parser


def _write_json(stream: TextIO, value: object, *, compact: bool) -> None:
    stream.write(to_json(value, indent=None if compact else 2))
    stream.write("\n")


def _read_input(source: str, stdin: TextIO) -> str:
    if source == "-":
        return stdin.read()
    return Path(source).read_text(encoding="utf-8")


def _error_payload(code: str, path: str, message: str) -> dict[str, object]:
    return {
        "error": {
            "code": code,
            "message": message,
            "path": path,
        }
    }


def main(
    argv: Sequence[str] | None = None,
    *,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the CLI and return a process exit code."""

    from rpf_validator import __version__

    input_stream = sys.stdin if stdin is None else stdin
    output_stream = sys.stdout if stdout is None else stdout
    error_stream = sys.stderr if stderr is None else stderr
    args = _build_parser(__version__).parse_args(argv)

    if args.command == "schema":
        _write_json(output_stream, load_input_schema(), compact=args.compact)
        return EXIT_SUCCESS

    try:
        text = _read_input(args.input, input_stream)
    except (OSError, UnicodeError) as exc:
        _write_json(
            error_stream,
            _error_payload("INPUT_FILE_ERROR", args.input, str(exc)),
            compact=True,
        )
        return EXIT_IO_ERROR

    try:
        model = parse_json(text)
        result = evaluate(model)
    except InputValidationError as exc:
        _write_json(
            error_stream,
            _error_payload(exc.reason_code.value, exc.path, exc.message),
            compact=True,
        )
        return EXIT_INPUT_ERROR

    if args.command == "trace":
        try:
            output = run_state_machine(result)
        except StateMachineError as exc:
            _write_json(
                error_stream,
                _error_payload(exc.code.value, exc.path, exc.message),
                compact=True,
            )
            return EXIT_STATE_MACHINE_ERROR
    else:
        output = result

    _write_json(output_stream, output, compact=args.compact)
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
