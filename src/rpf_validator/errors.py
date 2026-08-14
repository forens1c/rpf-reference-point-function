# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Technical schema errors raised before any RPF rule is evaluated."""

from __future__ import annotations

from rpf_validator.enums import ReasonCode


class InputValidationError(ValueError):
    """A structurally invalid input that prevents RPF rule evaluation."""

    reason_code = ReasonCode.INPUT_SCHEMA_INVALID

    def __init__(self, path: str, message: str) -> None:
        self.path = path
        self.message = message
        super().__init__(f"{path}: {message}")
