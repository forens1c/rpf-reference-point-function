# Executable RPF State Machine 0.4

**Languages:** [Deutsch](STATE_MACHINE_RUNTIME_0.4.md) · English

| Field | Value |
| --- | --- |
| Implementation status | non-normative experimental prototype |
| Package version | `0.4.0.dev0` |
| Runtime input contract | `rpf-validator-result-0.2` |
| Runtime output contract | `rpf-state-machine-trace-0.1` |
| Fixed transition bound | 7 |
| Change to the frozen RPF core | none |

## Purpose

Version 0.4 implements the documented RPF state space as executable transition
logic for the first time. The runtime accepts only an already produced,
versioned `ValidatorResult`. It does not evaluate the axioms again, interpret
text, or determine whether a claim is true.

```text
ValidatorInput
  → evaluate(...)
  → ValidatorResult · rpf-validator-result-0.2
  → run_state_machine(...)
  → StateMachineTrace · rpf-state-machine-trace-0.1
```

The validator and state machine therefore remain separate modules. Their only
direct coupling is the published result contract.

## Implementation form

The runtime uses a deliberately small hybrid architecture:

- `RPFState` and `TransitionEvent` are typed enums.
- `ALLOWED_TRANSITIONS` is an immutable declarative table.
- `transition(state, event)` is a pure function.
- `TransitionRecord` and `StateMachineTrace` are immutable dataclasses.
- no transition plan may exceed seven steps.
- every successful run returns to `IDLE`.

There is neither a mutable global state object nor one class per state. The
table consequently remains directly inspectable and auditable.

## Declared transitions

| Source | Event | Target |
| --- | --- | --- |
| `IDLE` | `BEGIN` | `ISOLATION` |
| `ISOLATION` | `APPLY_OPERATORS` | `OPERATOR_APPL` |
| `ISOLATION` | `DELEGATE` | `DELEGIERT` |
| `ISOLATION` | `NO_REFERENCE` | `NO_REFERENCE` |
| `OPERATOR_APPL` | `EVALUATE_DELTA` | `DELTA_EVAL` |
| `DELTA_EVAL` | `GENERATE_HYPOTHESES` | `HYPOTHESIS_GEN` |
| `DELTA_EVAL` | `STOP` | `OUTPUT_INTERFACE` |
| `HYPOTHESIS_GEN` | `EVALUATE_ADAPTIVELY` | `ADAPTIVE_VAL` |
| `ADAPTIVE_VAL` | `EMIT` | `OUTPUT_INTERFACE` |
| `ADAPTIVE_VAL` | `STOP` | `OUTPUT_INTERFACE` |
| `NO_REFERENCE` | `EMIT` | `OUTPUT_INTERFACE` |
| `OUTPUT_INTERFACE` | `RESET` | `IDLE` |
| `DELEGIERT` | `RESET` | `IDLE` |

Competence and reference checks are not invented as new canonical states.
Their outcomes appear as explicit transitions from `ISOLATION`, preserving the
state space of the frozen draft.

## Process-status routing

| Validator result | Recorded path |
| --- | --- |
| `PASS` or `WARN` | `IDLE → ISOLATION → OPERATOR_APPL → DELTA_EVAL → HYPOTHESIS_GEN → ADAPTIVE_VAL → OUTPUT_INTERFACE → IDLE` |
| `DELEGATE` | `IDLE → ISOLATION → DELEGIERT → IDLE` |
| `NO_REFERENCE` | `IDLE → ISOLATION → NO_REFERENCE → OUTPUT_INTERFACE → IDLE` |
| A3/P3 `STOP` | `IDLE → ISOLATION → OPERATOR_APPL → DELTA_EVAL → OUTPUT_INTERFACE → IDLE` |
| A4/P4 `STOP` | `IDLE → ISOLATION → OPERATOR_APPL → DELTA_EVAL → HYPOTHESIS_GEN → ADAPTIVE_VAL → OUTPUT_INTERFACE → IDLE` |

The `STOP` event remains visible in the transition trace. If several stop
signals exist, a termination bound already reached in A3 or P3 ends the path
at `DELTA_EVAL`; a later A4/P4 finding is not required to continue the control
flow. The preceding `ValidatorResult` still retains every rule result.

## Command line

A public JSON scenario can now run through both validator and runtime:

```bash
rpf trace examples/weather-input-0.2.json
```

Compact output:

```bash
rpf trace examples/wave-tank-no-reference-input-0.2.json --compact
```

The trace includes:

- its own schema version,
- the consumed result schema version,
- case identifier and process status,
- every numbered transition with source, event, and target,
- the final `IDLE` state,
- the fixed maximum transition count.

Exit codes remain separate from domain-level process statuses:

| Code | Meaning |
| --- | --- |
| `0` | valid evaluation and trace, including a `STOP` result |
| `2` | invalid JSON or input structure |
| `3` | file or decoding failure |
| `4` | technical state-machine contract failure |

## Python API

```python
from rpf_validator import evaluate, run_state_machine, to_json

result = evaluate(case)
trace = run_state_machine(result)
print(to_json(trace))
```

One transition can also be inspected independently:

```python
from rpf_validator import RPFState, TransitionEvent, transition

next_state = transition(RPFState.IDLE, TransitionEvent.BEGIN)
assert next_state is RPFState.ISOLATION
```

An undeclared transition is rejected deterministically with
`INVALID_TRANSITION`. Unsupported result contracts, inconsistent `STOP`
traces, and an exceeded fixed step bound have separate technical error codes.
These codes deliberately remain outside the domain-level A1–A4/P1–P4 reason
codes.

## Safety and epistemic boundary

The state machine controls the flow of an already structured result. It can
reject forbidden transitions, unsupported contracts, and incomplete stop
traces. It cannot determine whether plausible, internally consistent source
data is factually false.

A later language model or semantic module may therefore supply structured
proposals only. Provenance, assessment authority, and external evidence remain
separate requirements. The deterministic runtime is control flow, not a truth
detector or an authorization authority.

## Verification

The technical slice is covered by 80 automated tests. They include:

- all five public process statuses,
- early and adaptive `STOP` paths,
- immutable transition table and traces,
- deterministic repetition of identical runs,
- rejection of invalid transitions and inconsistent stop traces,
- the fixed transition bound and return to `IDLE`,
- `rpf trace` for normal and `NO_REFERENCE` scenarios.
