# Synthetic transfer case: Model boat without a reference definition

**Languages:** [Deutsch](TRANSFER_CASE_WAVE_TANK_NO_REFERENCE.md) · English

## Status and purpose

This transfer case closes the `NO_REFERENCE` path that was previously visible
only through unit tests by adding a complete public fixture. It uses a model
boat in a synthetic wave tank and two undocumented displays that output `HIGH`
and `LOW`.

The case is non-normative and changes neither the frozen RPF specification nor
the `rpf-validator-input-0.2` contract. It is not a nautical model, a statement
about the stability of real boats, or navigation or safety guidance.

## Observation and missing reference

The model boat remains at the same **horizontal station** during the experiment.
At one synchronized readout, two laboratory displays show:

```text
display A = HIGH
display B = LOW
```

Only the following is known:

- The horizontal station of the model remains unchanged.
- Vertical motion caused by the wave remains possible and is not denied.
- Both labels were recorded at the same synthetic readout time.
- The displays belong to the test setup but are undocumented.

The following is unknown:

- which quantity each channel measures,
- which axis and datum it uses,
- which unit or threshold underlies the label,
- whether `HIGH` and `LOW` denote measurements, threshold classes, or device
  states.

The unchanged horizontal station therefore does not establish a shared
reference frame for the two outputs.

## Why expertise does not automatically close the gap

A person experienced in nautical systems or metrology can quickly propose
plausible interpretations: boat elevation, wave height, draft, clearance,
water level, a threshold, or device status. That competence improves hypothesis
generation. It does not establish what the particular display actually
measures.

The case therefore distinguishes:

```text
plausible domain convention
≠ documented channel definition
```

If an evaluator treated a familiar convention as given without instrument
documentation, it would perform **implicit reference-frame injection**. Missing
metadata would silently be replaced by prior knowledge.

If a sensor manual or experiment protocol later defines the quantity, datum,
unit, and label semantics in a traceable way, the record must be evaluated
again. Its result may then become `WARN` or `PASS`. Such a change is intended
and is not validator instability.

## Boundary with `WARN`

| State | Available information | Result |
| --- | --- | --- |
| `AMBIGUOUS` | several evidenced reference frames are known but unresolved | `WARN` |
| `MISSING` | information required to construct a reference frame is absent | `NO_REFERENCE` |

The possible nautical or measurement interpretations in this fixture are only
hypotheses. They are not established reference frames. Consequently,
`reference_frame.classes` remains empty and `reference_frame.scope` is `null`.

## Comparability working note

The two labels would require at least a shared comparison key:

```text
K = (quantity, axis, datum, unit, time, label semantics)
```

This notation explains the local transfer case; it is not a new RPF axiom.
Essential parts of `K` are missing from the fixture, so it asserts neither a
numeric evidence comparison nor a logical contradiction.

## Executable representation

The [wave-tank fixture](../examples/wave-tank-no-reference-input-0.2.json)
declares:

- sufficient competence only for structural evaluation of the supplied input,
- a local conflict between two recorded labels,
- unquantified and explicitly non-comparable `C_i` and `C_e` values,
- `reference_frame.status = MISSING`, empty classes, and no scope,
- several possible but unconfirmed channel interpretations,
- one reversible action: suspend comparison and request metadata.

The fixture records a synthetic observation log as its source. The source's
quality note states exactly which channel metadata is absent. The validator
does not verify these statements outside the supplied input.

## Expected rule trace

```text
overall_status = NO_REFERENCE
A1 = SATISFIED
A2 = SATISFIED
A3 = SATISFIED
A4 = SATISFIED
P1 = TRIGGERED · REFERENCE_FRAME_MISSING
P2 = SATISFIED
P3 = NOT_APPLICABLE
P4 = SATISFIED
```

P1 produces `NO_REFERENCE` because a conflict is declared without a complete
reference frame containing a class and scope. The result confirms neither that
the displays contradict one another nor that either display is wrong.

## Robust action

The selected action `suspend-comparison-and-request-metadata` changes neither a
boat nor a device state. It only suspends treating the labels as equivalent and
requests:

- channel definitions,
- measurement quantity and axis,
- datum and unit,
- label thresholds and the experiment protocol.

This is not a failure to decide. The process explicitly decides that model
revision is not yet justified without a shared reference point.

## Running the case

After local installation:

```bash
rpf validate examples/wave-tank-no-reference-input-0.2.json
```

The command exits with code `0` because `NO_REFERENCE` is a valid process result,
not a technical input error.

## Limitations

The example demonstrates only how to retain missing reference metadata. It
evaluates no real instrument, expert, or maritime situation. In particular,
the fixture does not claim that expertise is useless. It separates
domain-informed hypotheses from a demonstrably documented mapping of the
specific measurement channel.
