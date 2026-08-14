# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Access to the machine-readable JSON Schema bundled with the package."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

INPUT_SCHEMA_RESOURCE = "schemas/rpf-validator-input-0.2.schema.json"


def load_input_schema() -> dict[str, Any]:
    """Load and return a fresh copy of the bundled input JSON Schema."""

    resource = files("rpf_validator").joinpath(INPUT_SCHEMA_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise RuntimeError("bundled input schema must be a JSON object")
    return value
