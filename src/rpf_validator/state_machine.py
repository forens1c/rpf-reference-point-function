# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Deterministic runtime for the experimental RPF state machine.

The runtime consumes only an already versioned :class:`ValidatorResult`.  It
does not repeat rule evaluation, infer semantic meaning, or consult external
state.  A declarative transition table is the sole source of allowed state
changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final, Mapping

from rpf_validator.enums import ProcessStatus, RuleId, RuleStatus
from rpf_validator.models import RESULT_SCHEMA_VERSION, ValidatorResult

STATE_MACHINE_TRACE_VERSION: Final = "rpf-state-machine-trace-0.1"
STATE_MACHINE_MAX_TRANSITIONS: Final = 7
SUPPORTED_RESULT_SCHEMA_VERSIONS: Final = frozenset({RESULT_SCHEMA_VERSION})


class RPFState(StrEnum):
    """Canonical states retained from the frozen RPF draft."""

    IDLE = "IDLE"
    ISOLATION = "ISOLATION"
    OPERATOR_APPL = "OPERATOR_APPL"
    DELTA_EVAL = "DELTA_EVAL"
    HYPOTHESIS_GEN = "HYPOTHESIS_GEN"
    ADAPTIVE_VAL = "ADAPTIVE_VAL"
    OUTPUT_INTERFACE = "OUTPUT_INTERFACE"
    DELEGIERT = "DELEGIERT"
    NO_REFERENCE = "NO_REFERENCE"


class TransitionEvent(StrEnum):
    """Explicit events that may advance the runtime."""

    BEGIN = "BEGIN"
    APPLY_OPERATORS = "APPLY_OPERATORS"
    EVALUATE_DELTA = "EVALUATE_DELTA"
    GENERATE_HYPOTHESES = "GENERATE_HYPOTHESES"
    EVALUATE_ADAPTIVELY = "EVALUATE_ADAPTIVELY"
    EMIT = "EMIT"
    DELEGATE = "DELEGATE"
    NO_REFERENCE = "NO_REFERENCE"
    STOP = "STOP"
    RESET = "RESET"


class StateMachineErrorCode(StrEnum):
    """Stable technical error codes outside the RPF rule-result contract."""

    INVALID_TRANSITION = "INVALID_TRANSITION"
    UNSUPPORTED_RESULT_CONTRACT = "UNSUPPORTED_RESULT_CONTRACT"
    INCONSISTENT_RESULT_STATUS = "INCONSISTENT_RESULT_STATUS"
    STATE_MACHINE_STEP_LIMIT = "STATE_MACHINE_STEP_LIMIT"


class StateMachineError(ValueError):
    """Base class for deterministic state-machine contract failures."""

    def __init__(
        self,
        code: StateMachineErrorCode,
        message: str,
        *,
        path: str = "state_machine",
    ) -> None:
        self.code = code
        self.message = message
        self.path = path
        super().__init__(f"{path}: {message}")


class InvalidTransitionError(StateMachineError):
    """Raised when an event is not allowed from the supplied state."""

    def __init__(self, state: object, event: object) -> None:
        state_value = state.value if isinstance(state, RPFState) else repr(state)
        event_value = (
            event.value if isinstance(event, TransitionEvent) else repr(event)
        )
        super().__init__(
            StateMachineErrorCode.INVALID_TRANSITION,
            f"event {event_value} is not allowed from state {state_value}",
            path="state_machine.transition",
        )
        self.state = state
        self.event = event


class UnsupportedResultContractError(StateMachineError):
    """Raised when the runtime cannot consume the supplied result contract."""

    def __init__(self, message: str) -> None:
        super().__init__(
            StateMachineErrorCode.UNSUPPORTED_RESULT_CONTRACT,
            message,
            path="state_machine.result",
        )


class InconsistentResultStatusError(StateMachineError):
    """Raised when a process status cannot be routed from its rule trace."""

    def __init__(self, message: str) -> None:
        super().__init__(
            StateMachineErrorCode.INCONSISTENT_RESULT_STATUS,
            message,
            path="state_machine.result.overall_status",
        )


class StateMachineStepLimitError(StateMachineError):
    """Raised before a transition would exceed the fixed runtime bound."""

    def __init__(self, maximum: int) -> None:
        super().__init__(
            StateMachineErrorCode.STATE_MACHINE_STEP_LIMIT,
            f"transition plan exceeds the fixed maximum of {maximum}",
            path="state_machine.transitions",
        )


ALLOWED_TRANSITIONS: Final[
    Mapping[tuple[RPFState, TransitionEvent], RPFState]
] = MappingProxyType(
    {
        (RPFState.IDLE, TransitionEvent.BEGIN): RPFState.ISOLATION,
        (
            RPFState.ISOLATION,
            TransitionEvent.APPLY_OPERATORS,
        ): RPFState.OPERATOR_APPL,
        (RPFState.ISOLATION, TransitionEvent.DELEGATE): RPFState.DELEGIERT,
        (
            RPFState.ISOLATION,
            TransitionEvent.NO_REFERENCE,
        ): RPFState.NO_REFERENCE,
        (
            RPFState.OPERATOR_APPL,
            TransitionEvent.EVALUATE_DELTA,
        ): RPFState.DELTA_EVAL,
        (
            RPFState.DELTA_EVAL,
            TransitionEvent.GENERATE_HYPOTHESES,
        ): RPFState.HYPOTHESIS_GEN,
        (
            RPFState.DELTA_EVAL,
            TransitionEvent.STOP,
        ): RPFState.OUTPUT_INTERFACE,
        (
            RPFState.HYPOTHESIS_GEN,
            TransitionEvent.EVALUATE_ADAPTIVELY,
        ): RPFState.ADAPTIVE_VAL,
        (
            RPFState.ADAPTIVE_VAL,
            TransitionEvent.EMIT,
        ): RPFState.OUTPUT_INTERFACE,
        (
            RPFState.ADAPTIVE_VAL,
            TransitionEvent.STOP,
        ): RPFState.OUTPUT_INTERFACE,
        (
            RPFState.NO_REFERENCE,
            TransitionEvent.EMIT,
        ): RPFState.OUTPUT_INTERFACE,
        (
            RPFState.OUTPUT_INTERFACE,
            TransitionEvent.RESET,
        ): RPFState.IDLE,
        (RPFState.DELEGIERT, TransitionEvent.RESET): RPFState.IDLE,
    }
)
"""Immutable transition table for the executable prototype."""


@dataclass(frozen=True, slots=True)
class TransitionRecord:
    """One immutable, ordered state change in an audit trace."""

    step: int
    source_state: RPFState
    event: TransitionEvent
    target_state: RPFState


@dataclass(frozen=True, slots=True)
class StateMachineTrace:
    """Versioned, deterministic trace produced for one validator result."""

    schema_version: str
    result_schema_version: str
    case_id: str
    overall_status: ProcessStatus
    transitions: tuple[TransitionRecord, ...]
    final_state: RPFState
    max_transitions: int

    @property
    def visited_states(self) -> tuple[RPFState, ...]:
        """Return the complete state sequence, including the initial state."""

        if not self.transitions:
            return (self.final_state,)
        return (
            self.transitions[0].source_state,
            *(record.target_state for record in self.transitions),
        )


_FULL_PLAN: Final = (
    TransitionEvent.BEGIN,
    TransitionEvent.APPLY_OPERATORS,
    TransitionEvent.EVALUATE_DELTA,
    TransitionEvent.GENERATE_HYPOTHESES,
    TransitionEvent.EVALUATE_ADAPTIVELY,
    TransitionEvent.EMIT,
    TransitionEvent.RESET,
)
_DELEGATE_PLAN: Final = (
    TransitionEvent.BEGIN,
    TransitionEvent.DELEGATE,
    TransitionEvent.RESET,
)
_NO_REFERENCE_PLAN: Final = (
    TransitionEvent.BEGIN,
    TransitionEvent.NO_REFERENCE,
    TransitionEvent.EMIT,
    TransitionEvent.RESET,
)
_EARLY_STOP_PLAN: Final = (
    TransitionEvent.BEGIN,
    TransitionEvent.APPLY_OPERATORS,
    TransitionEvent.EVALUATE_DELTA,
    TransitionEvent.STOP,
    TransitionEvent.RESET,
)
_ADAPTIVE_STOP_PLAN: Final = (
    TransitionEvent.BEGIN,
    TransitionEvent.APPLY_OPERATORS,
    TransitionEvent.EVALUATE_DELTA,
    TransitionEvent.GENERATE_HYPOTHESES,
    TransitionEvent.EVALUATE_ADAPTIVELY,
    TransitionEvent.STOP,
    TransitionEvent.RESET,
)


def transition(state: RPFState, event: TransitionEvent) -> RPFState:
    """Return the declared target state or reject the pair deterministically."""

    if not isinstance(state, RPFState) or not isinstance(event, TransitionEvent):
        raise InvalidTransitionError(state, event)
    try:
        return ALLOWED_TRANSITIONS[(state, event)]
    except KeyError as exc:
        raise InvalidTransitionError(state, event) from exc


def _stop_plan(result: ValidatorResult) -> tuple[TransitionEvent, ...]:
    triggered_rules = {
        rule.rule_id
        for rule in result.rule_results
        if rule.status is RuleStatus.TRIGGERED
    }
    if triggered_rules & {RuleId.A3, RuleId.P3}:
        return _EARLY_STOP_PLAN
    if triggered_rules & {RuleId.A4, RuleId.P4}:
        return _ADAPTIVE_STOP_PLAN
    raise InconsistentResultStatusError(
        "STOP requires a triggered A3/P3 termination rule or A4/P4 "
        "adaptive constraint rule in result contract 0.2"
    )


def _plan_for(result: ValidatorResult) -> tuple[TransitionEvent, ...]:
    status = result.overall_status
    if status in {ProcessStatus.PASS, ProcessStatus.WARN}:
        return _FULL_PLAN
    if status is ProcessStatus.DELEGATE:
        return _DELEGATE_PLAN
    if status is ProcessStatus.NO_REFERENCE:
        return _NO_REFERENCE_PLAN
    if status is ProcessStatus.STOP:
        return _stop_plan(result)
    raise InconsistentResultStatusError(f"unsupported process status {status!r}")


def run_state_machine(result: ValidatorResult) -> StateMachineTrace:
    """Route one versioned validator result through a bounded state trace."""

    if not isinstance(result, ValidatorResult):
        raise UnsupportedResultContractError("expected ValidatorResult")
    if result.schema_version not in SUPPORTED_RESULT_SCHEMA_VERSIONS:
        raise UnsupportedResultContractError(
            f"unsupported result schema version {result.schema_version!r}"
        )

    plan = _plan_for(result)
    state = RPFState.IDLE
    records: list[TransitionRecord] = []

    for step, event in enumerate(plan, start=1):
        if step > STATE_MACHINE_MAX_TRANSITIONS:
            raise StateMachineStepLimitError(STATE_MACHINE_MAX_TRANSITIONS)
        target = transition(state, event)
        records.append(
            TransitionRecord(
                step=step,
                source_state=state,
                event=event,
                target_state=target,
            )
        )
        state = target

    if state is not RPFState.IDLE:
        raise InconsistentResultStatusError(
            f"transition plan ended in {state.value} instead of IDLE"
        )

    return StateMachineTrace(
        schema_version=STATE_MACHINE_TRACE_VERSION,
        result_schema_version=result.schema_version,
        case_id=result.case_id,
        overall_status=result.overall_status,
        transitions=tuple(records),
        final_state=state,
        max_transitions=STATE_MACHINE_MAX_TRANSITIONS,
    )
