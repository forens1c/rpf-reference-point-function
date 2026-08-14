# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Stable identifiers used by the experimental RPF validator schema."""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final, Mapping


class CompetenceStatus(StrEnum):
    """Declared task-specific competence fit."""

    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class RevisionScope(StrEnum):
    """Requested scope of a proposed model revision."""

    NONE = "NONE"
    LOCAL = "LOCAL"
    GLOBAL = "GLOBAL"


class ReferenceFrameStatus(StrEnum):
    """Availability of a reference frame for the current case."""

    IDENTIFIED = "IDENTIFIED"
    AMBIGUOUS = "AMBIGUOUS"
    MISSING = "MISSING"


class ReferenceFrameClass(StrEnum):
    """Reference-frame classes preserved from the frozen RPF draft."""

    OBJECTIVE_MEASUREMENT = "OBJECTIVE_MEASUREMENT"
    SUBJECTIVE_PERCEPTION = "SUBJECTIVE_PERCEPTION"
    INDIVIDUAL_PREFERENCE = "INDIVIDUAL_PREFERENCE"
    STATISTICAL_EXCEPTION = "STATISTICAL_EXCEPTION"
    CULTURAL_EVALUATION = "CULTURAL_EVALUATION"
    LINGUISTIC_AMBIGUITY = "LINGUISTIC_AMBIGUITY"
    LOGICAL_CONTRADICTION = "LOGICAL_CONTRADICTION"


class RuleId(StrEnum):
    """Identifiers for the four axioms and four derived principles."""

    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    A4 = "A4"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class RuleStatus(StrEnum):
    """Result of evaluating one rule."""

    SATISFIED = "SATISFIED"
    SIGNAL = "SIGNAL"
    TRIGGERED = "TRIGGERED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_EVALUATED = "NOT_EVALUATED"


class ProcessStatus(StrEnum):
    """Aggregate process status, separate from technical input errors."""

    PASS = "PASS"
    WARN = "WARN"
    DELEGATE = "DELEGATE"
    NO_REFERENCE = "NO_REFERENCE"
    STOP = "STOP"


class ReasonCode(StrEnum):
    """Language-independent reason codes defined by the operationalization."""

    INPUT_SCHEMA_INVALID = "INPUT_SCHEMA_INVALID"
    COMPETENCE_INSUFFICIENT = "COMPETENCE_INSUFFICIENT"
    COMPETENCE_UNKNOWN = "COMPETENCE_UNKNOWN"
    CALIBRATION_NOT_SEPARATED = "CALIBRATION_NOT_SEPARATED"
    CONFIDENCE_EVIDENCE_DIVERGENCE = "CONFIDENCE_EVIDENCE_DIVERGENCE"
    INFORMATION_GAIN_LIMIT = "INFORMATION_GAIN_LIMIT"
    ITERATION_LIMIT = "ITERATION_LIMIT"
    TIME_LIMIT = "TIME_LIMIT"
    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    TERMINATION_BOUND_MISSING = "TERMINATION_BOUND_MISSING"
    TIME_HORIZON_MISSING = "TIME_HORIZON_MISSING"
    DECLARED_CONSTRAINT_CONFLICT = "DECLARED_CONSTRAINT_CONFLICT"
    REFERENCE_FRAME_MISSING = "REFERENCE_FRAME_MISSING"
    REFERENCE_FRAME_AMBIGUOUS = "REFERENCE_FRAME_AMBIGUOUS"
    UNCERTAINTY_NOT_REPORTED = "UNCERTAINTY_NOT_REPORTED"
    REFLEXIVE_DEPTH_LIMIT = "REFLEXIVE_DEPTH_LIMIT"
    IRREVERSIBLE_ACTION_UNJUSTIFIED = "IRREVERSIBLE_ACTION_UNJUSTIFIED"


PROCESS_STATUS_PRIORITY: Final[Mapping[ProcessStatus, int]] = MappingProxyType(
    {
        ProcessStatus.PASS: 0,
        ProcessStatus.WARN: 1,
        ProcessStatus.NO_REFERENCE: 2,
        ProcessStatus.DELEGATE: 3,
        ProcessStatus.STOP: 4,
    }
)
"""Prototype priority: STOP > DELEGATE > NO_REFERENCE > WARN > PASS."""
