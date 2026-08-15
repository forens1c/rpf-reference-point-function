# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Access to the machine-readable JSON Schema bundled with the package."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

INPUT_SCHEMA_RESOURCE = "schemas/rpf-validator-input-0.2.schema.json"
CLASSIFICATION_PROPOSAL_SCHEMA_RESOURCE = (
    "schemas/rpf-classification-proposal-0.1.schema.json"
)


def _load_schema(resource_name: str) -> dict[str, Any]:
    resource = files("rpf_validator").joinpath(resource_name)
    with resource.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise RuntimeError("bundled schema must be a JSON object")
    return value


def load_input_schema() -> dict[str, Any]:
    """Load and return a fresh copy of the bundled input JSON Schema."""

    return _load_schema(INPUT_SCHEMA_RESOURCE)


def load_classification_proposal_schema() -> dict[str, Any]:
    """Load a fresh copy of classification proposal contract 0.1."""

    return _load_schema(CLASSIFICATION_PROPOSAL_SCHEMA_RESOURCE)
