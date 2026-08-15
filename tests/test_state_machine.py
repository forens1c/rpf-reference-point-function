# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, replace
from unittest.mock import patch

from rpf_validator import (
    ALLOWED_TRANSITIONS,
    DeclaredConstraint,
    InconsistentResultStatusError,
    InvalidTransitionError,
    ProcessStatus,
    RPFState,
    ReferenceFrame,
    ReferenceFrameStatus,
    STATE_MACHINE_MAX_TRANSITIONS,
    STATE_MACHINE_TRACE_VERSION,
    StateMachineErrorCode,
    StateMachineStepLimitError,
    TransitionEvent,
    UnsupportedResultContractError,
    evaluate,
    run_state_machine,
    to_json,
    transition,
)
from tests.test_models import make_valid_input


def state_values(trace) -> tuple[str, ...]:
    return tuple(state.value for state in trace.visited_states)


class TransitionTableTests(unittest.TestCase):
    def test_declared_transition_is_pure_and_deterministic(self) -> None:
        first = transition(RPFState.IDLE, TransitionEvent.BEGIN)
        second = transition(RPFState.IDLE, TransitionEvent.BEGIN)

        self.assertIs(first, RPFState.ISOLATION)
        self.assertIs(second, first)

    def test_invalid_transition_is_rejected_with_stable_code(self) -> None:
        with self.assertRaises(InvalidTransitionError) as caught:
            transition(RPFState.IDLE, TransitionEvent.STOP)

        self.assertIs(
            caught.exception.code,
            StateMachineErrorCode.INVALID_TRANSITION,
        )
        self.assertIs(caught.exception.state, RPFState.IDLE)
        self.assertIs(caught.exception.event, TransitionEvent.STOP)

    def test_transition_table_is_immutable(self) -> None:
        with self.assertRaises(TypeError):
            ALLOWED_TRANSITIONS[(RPFState.IDLE, TransitionEvent.STOP)] = (
                RPFState.OUTPUT_INTERFACE
            )  # type: ignore[index]


class ResultRoutingTests(unittest.TestCase):
    def test_pass_runs_full_path_and_returns_to_idle(self) -> None:
        trace = run_state_machine(evaluate(make_valid_input()))

        self.assertEqual(trace.schema_version, STATE_MACHINE_TRACE_VERSION)
        self.assertEqual(trace.result_schema_version, "rpf-validator-result-0.2")
        self.assertEqual(trace.overall_status, ProcessStatus.PASS)
        self.assertEqual(
            state_values(trace),
            (
                "IDLE",
                "ISOLATION",
                "OPERATOR_APPL",
                "DELTA_EVAL",
                "HYPOTHESIS_GEN",
                "ADAPTIVE_VAL",
                "OUTPUT_INTERFACE",
                "IDLE",
            ),
        )
        self.assertIs(trace.final_state, RPFState.IDLE)
        self.assertLessEqual(len(trace.transitions), STATE_MACHINE_MAX_TRANSITIONS)

    def test_warn_uses_full_path_without_becoming_a_truth_decision(self) -> None:
        model = make_valid_input()
        frame = replace(
            model.reference_frame,
            status=ReferenceFrameStatus.AMBIGUOUS,
        )

        trace = run_state_machine(evaluate(replace(model, reference_frame=frame)))

        self.assertEqual(trace.overall_status, ProcessStatus.WARN)
        self.assertIn(RPFState.ADAPTIVE_VAL, trace.visited_states)
        self.assertIs(trace.final_state, RPFState.IDLE)

    def test_delegate_is_an_explicit_short_path(self) -> None:
        from rpf_validator import CompetenceStatus

        result = evaluate(
            make_valid_input(competence_status=CompetenceStatus.INSUFFICIENT)
        )

        trace = run_state_machine(result)

        self.assertEqual(trace.overall_status, ProcessStatus.DELEGATE)
        self.assertEqual(
            state_values(trace),
            ("IDLE", "ISOLATION", "DELEGIERT", "IDLE"),
        )
        self.assertEqual(
            tuple(record.event for record in trace.transitions),
            (
                TransitionEvent.BEGIN,
                TransitionEvent.DELEGATE,
                TransitionEvent.RESET,
            ),
        )

    def test_no_reference_is_emitted_before_return_to_idle(self) -> None:
        model = make_valid_input()
        result = evaluate(
            replace(
                model,
                reference_frame=ReferenceFrame(
                    status=ReferenceFrameStatus.MISSING
                ),
            )
        )

        trace = run_state_machine(result)

        self.assertEqual(trace.overall_status, ProcessStatus.NO_REFERENCE)
        self.assertEqual(
            state_values(trace),
            (
                "IDLE",
                "ISOLATION",
                "NO_REFERENCE",
                "OUTPUT_INTERFACE",
                "IDLE",
            ),
        )

    def test_termination_stop_is_recorded_at_delta_eval(self) -> None:
        model = make_valid_input()
        result = evaluate(
            replace(
                model,
                termination=replace(model.termination, iteration=5),
            )
        )

        trace = run_state_machine(result)

        self.assertEqual(trace.overall_status, ProcessStatus.STOP)
        self.assertEqual(
            state_values(trace),
            (
                "IDLE",
                "ISOLATION",
                "OPERATOR_APPL",
                "DELTA_EVAL",
                "OUTPUT_INTERFACE",
                "IDLE",
            ),
        )
        self.assertIs(trace.transitions[3].event, TransitionEvent.STOP)

    def test_constraint_stop_is_recorded_at_adaptive_val(self) -> None:
        model = make_valid_input()
        hard_constraint = DeclaredConstraint(
            code="DO_NOT_PROCEED",
            description="Fixture hard stop.",
            hard=True,
        )
        frame = replace(
            model.reference_frame,
            constraints=(*model.reference_frame.constraints, hard_constraint),
        )
        first_effect = replace(
            model.candidate_actions[0].effects[0],
            constraint_conflicts=(hard_constraint.code,),
        )
        action = replace(
            model.candidate_actions[0],
            effects=(first_effect, model.candidate_actions[0].effects[1]),
        )
        result = evaluate(
            replace(model, reference_frame=frame, candidate_actions=(action,))
        )

        trace = run_state_machine(result)

        self.assertEqual(trace.overall_status, ProcessStatus.STOP)
        self.assertEqual(trace.transitions[-2].source_state, RPFState.ADAPTIVE_VAL)
        self.assertIs(trace.transitions[-2].event, TransitionEvent.STOP)
        self.assertIs(trace.final_state, RPFState.IDLE)

    def test_identical_result_produces_identical_trace_and_json(self) -> None:
        result = evaluate(make_valid_input())

        first = run_state_machine(result)
        second = run_state_machine(result)

        self.assertEqual(first, second)
        self.assertEqual(to_json(first), to_json(second))


class StateMachineBoundaryTests(unittest.TestCase):
    def test_non_result_input_is_rejected(self) -> None:
        with self.assertRaises(UnsupportedResultContractError) as caught:
            run_state_machine({"overall_status": "PASS"})  # type: ignore[arg-type]

        self.assertIs(
            caught.exception.code,
            StateMachineErrorCode.UNSUPPORTED_RESULT_CONTRACT,
        )

    def test_stop_without_a_triggered_stop_rule_is_rejected(self) -> None:
        result = replace(
            evaluate(make_valid_input()),
            overall_status=ProcessStatus.STOP,
        )

        with self.assertRaises(InconsistentResultStatusError) as caught:
            run_state_machine(result)

        self.assertIs(
            caught.exception.code,
            StateMachineErrorCode.INCONSISTENT_RESULT_STATUS,
        )

    def test_fixed_transition_bound_is_enforced(self) -> None:
        result = evaluate(make_valid_input())

        with patch("rpf_validator.state_machine.STATE_MACHINE_MAX_TRANSITIONS", 1):
            with self.assertRaises(StateMachineStepLimitError) as caught:
                run_state_machine(result)

        self.assertIs(
            caught.exception.code,
            StateMachineErrorCode.STATE_MACHINE_STEP_LIMIT,
        )

    def test_trace_is_immutable(self) -> None:
        trace = run_state_machine(evaluate(make_valid_input()))

        with self.assertRaises(FrozenInstanceError):
            trace.final_state = RPFState.ISOLATION  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
