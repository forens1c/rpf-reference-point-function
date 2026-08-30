# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Shared strict JSON decoding for public RPF text contracts."""

from __future__ import annotations

import json

from rpf_validator.errors import InputValidationError


class _DuplicateKeyError(ValueError):
    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(key)


class _NonStandardConstantError(ValueError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__(value)


def _reject_duplicate_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _reject_non_standard_constant(value: str) -> object:
    raise _NonStandardConstantError(value)


def decode_json(text: str) -> object:
    """Decode RFC-compatible JSON or raise one normalized contract error."""

    if not isinstance(text, str):
        raise InputValidationError("$", "must be JSON text")
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_standard_constant,
        )
    except json.JSONDecodeError as exc:
        raise InputValidationError(
            "$",
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        ) from exc
    except _DuplicateKeyError as exc:
        raise InputValidationError(
            "$",
            f"contains duplicate object key {exc.key!r}",
        ) from exc
    except _NonStandardConstantError as exc:
        raise InputValidationError(
            "$",
            f"contains non-standard numeric constant {exc.value!r}",
        ) from exc
    except ValueError as exc:
        raise InputValidationError(
            "$",
            "contains a numeric value outside the supported JSON decoder range",
        ) from exc
