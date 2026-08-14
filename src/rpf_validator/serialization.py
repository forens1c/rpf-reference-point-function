# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Deterministic conversion of RPF schema dataclasses to JSON primitives."""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any


def to_primitive(value: Any) -> Any:
    """Recursively convert schema values to JSON-compatible primitives."""

    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            item.name: to_primitive(getattr(value, item.name))
            for item in fields(value)
        }
    if isinstance(value, tuple):
        return [to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_primitive(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_primitive(item) for item in value]
    return value


def to_json(value: Any, *, indent: int | None = 2) -> str:
    """Serialize a schema object with stable key ordering and UTF-8 output."""

    return json.dumps(
        to_primitive(value),
        ensure_ascii=False,
        indent=indent,
        sort_keys=True,
    )
