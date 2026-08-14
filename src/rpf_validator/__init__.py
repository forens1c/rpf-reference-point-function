# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Public API for the experimental deterministic RPF process validator."""

from rpf_validator.enums import (
    PROCESS_STATUS_PRIORITY,
    CompetenceStatus,
    ProcessStatus,
    ReasonCode,
    ReferenceFrameClass,
    ReferenceFrameStatus,
    RevisionScope,
    RuleId,
    RuleStatus,
)
from rpf_validator.errors import InputValidationError
from rpf_validator.models import (
    INPUT_SCHEMA_VERSION,
    RESULT_SCHEMA_VERSION,
    Calibration,
    CandidateAction,
    CompetenceAssessment,
    Conflict,
    DeclaredConstraint,
    EvidenceSource,
    ExpectedEffect,
    Hypothesis,
    Observation,
    ReferenceFrame,
    RuleResult,
    TerminationState,
    TimeHorizon,
    UncertaintyItem,
    UncertaintyReport,
    ValidatorConfig,
    ValidatorInput,
    ValidatorResult,
)
from rpf_validator.evaluator import evaluate
from rpf_validator.parsing import load_input, parse_input, parse_json
from rpf_validator.schema import INPUT_SCHEMA_RESOURCE, load_input_schema
from rpf_validator.serialization import to_json, to_primitive

__version__ = "0.3.0.dev0"

__all__ = [
    "INPUT_SCHEMA_VERSION",
    "INPUT_SCHEMA_RESOURCE",
    "PROCESS_STATUS_PRIORITY",
    "RESULT_SCHEMA_VERSION",
    "__version__",
    "Calibration",
    "CandidateAction",
    "CompetenceAssessment",
    "CompetenceStatus",
    "Conflict",
    "DeclaredConstraint",
    "EvidenceSource",
    "ExpectedEffect",
    "Hypothesis",
    "InputValidationError",
    "Observation",
    "ProcessStatus",
    "ReasonCode",
    "ReferenceFrame",
    "ReferenceFrameClass",
    "ReferenceFrameStatus",
    "RevisionScope",
    "RuleId",
    "RuleResult",
    "RuleStatus",
    "TerminationState",
    "TimeHorizon",
    "UncertaintyItem",
    "UncertaintyReport",
    "ValidatorConfig",
    "ValidatorInput",
    "ValidatorResult",
    "evaluate",
    "load_input",
    "load_input_schema",
    "parse_input",
    "parse_json",
    "to_json",
    "to_primitive",
]
