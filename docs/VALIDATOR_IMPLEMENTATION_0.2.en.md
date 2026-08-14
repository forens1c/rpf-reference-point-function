# Experimental Validator Implementation 0.2

**Languages:** [Deutsch](VALIDATOR_IMPLEMENTATION_0.2.md) · English

## Status and boundary

This document describes the executable Python prototype
`rpf-validator 0.2.0.dev0`. Its schema identifiers are:

| Contract | Identifier |
| --- | --- |
| Input | `rpf-validator-input-0.2` |
| Result | `rpf-validator-result-0.2` |

The implementation is **experimental and non-normative**. It translates the
[validator operationalization](VALIDATOR_OPERATIONALIZATION.en.md) into
deterministic rules but changes neither `ARCHIVED_SPEC_1.2` nor
`ARCHIVED_RPF-X_IR_0.2`.

A `PASS` confirms only that the supplied process description satisfies the
implemented rules. It confirms neither the truth of a statement nor the
professional, legal, moral, or practical correctness of an action.

## Public Python API

A fully constructed and structurally valid `ValidatorInput` is evaluated with
`evaluate`:

```python
from rpf_validator import evaluate, to_json

result = evaluate(case)
print(to_json(result))
```

Here, `case` is an immutable `ValidatorInput` object. A JSON input file, JSON
Schema, and command-line interface are not part of version 0.2 yet.

## Execution contract

1. The dataclasses validate types, ranges, unique identifiers, and references
   when the input object is constructed.
2. `evaluate` uses no network, language model, randomness, file access, or
   system clock. Time values come exclusively from the input.
3. A1 is a competence gate. `INSUFFICIENT` or `UNKNOWN` produces `DELEGATE`;
   A2–A4 and P1–P4 are recorded as `NOT_EVALUATED`.
4. With sufficient competence, all eight rules are emitted in stable A1–A4,
   P1–P4 order.
5. The aggregate status follows only the documented priority:

   ```text
   STOP > DELEGATE > NO_REFERENCE > WARN > PASS
   ```

6. Every triggered rule result is retained even when a higher-priority status
   determines the aggregate result.

## Deterministic rule semantics in 0.2

| Rule | Current technical check | Process effect |
| --- | --- | --- |
| A1 | Uses the declared competence status; the validator does not measure competence itself. | `INSUFFICIENT` or `UNKNOWN` → `DELEGATE`. |
| A2 | `C_i` and `C_e` remain separate fields. Numeric `C_e` without an evidence source produces a signal. Divergence is checked only when comparability and a threshold are explicitly configured; it triggers when `abs(C_i - C_e) > threshold`. | Signal → `WARN`; no truth decision. |
| A3 | At least one hard iteration, time, or resource bound must exist. Reached conditions use inclusive comparisons (`≤` or `≥`) and are reported together. | Missing or reached bound → `STOP`. |
| A4 | The configured minimum number of horizons must exist and be covered by every candidate action. Only a selected action's conflict with a declared hard constraint stops the run. | Incomplete horizons → `WARN`; hard conflict → `STOP`. |
| P1 | A conflict or revision requires an identified reference frame with at least a class and scope. | Missing → `NO_REFERENCE`; ambiguous → `WARN`. |
| P2 | A non-empty uncertainty list, or an explicit rationale for an empty list, counts as explicit uncertainty. | Empty list without rationale → `WARN`. |
| P3 | Reflexive runs require both a hard termination bound and a recursion-depth bound. `recursion_depth >= max_recursion_depth` terminates the run. | Missing or reached bound → `STOP`. |
| P4 | Applies to a selected action under at least two explicit hypotheses. An irreversible selection without its own selection rationale produces a signal. | Signal → `WARN`; hard conflict → `STOP`. |

## Action selection

Version 0.2 adds two optional input fields:

- `selected_action_id` references exactly one existing candidate action.
- `selection_rationale` explains the concrete selection separately from the
  candidate action's general rationale.

A selection rationale without a selected action is a technical input error. An
irreversible selection may remain formally representable without a rationale
so that P4 can emit `IRREVERSIBLE_ACTION_UNJUSTIFIED`.

## Neutral end-to-end case

The automated weather case contains two divergent forecasts, two hypotheses,
declared termination bounds, two time horizons, explicit residual uncertainty,
and the reversible selection “carry an umbrella.”

It reproducibly yields:

```text
overall_status = PASS
A1 = SATISFIED
A2 = SATISFIED
A3 = SATISFIED
A4 = SATISFIED
P1 = SATISFIED
P2 = SATISFIED
P3 = NOT_APPLICABLE
P4 = SATISFIED
```

This test does not predict whether rain will occur. It confirms only the rule
compliance of the described process.

## Verification state

Version 0.2 is covered by 37 automated tests, including minimum cases for:

- competence delegation and A1 gating,
- separate calibration and configurable divergence,
- information-gain, iteration, time, and resource limits,
- status priority under simultaneous signals,
- missing and ambiguous reference frames,
- explicit residual uncertainty,
- time horizons and hard declared constraints,
- reflexive depth and reversibility,
- identical outputs for identical inputs.

## Known limitations

- The validator does not verify whether supplied values, competence claims, or
  provenance statements are factually correct.
- There is no parser for untrusted JSON input yet.
- There is no universal utility function or automatic action selection.
- Free-text rationales are checked for presence, not substantive quality.
- Machine-readable reason codes are language-neutral; generated prose
  rationales are currently English.
- The implementation is not an authorization, medical, diagnostic, or therapy
  system and is not empirical confirmation of RPF.

## Next technical slice

A future version 0.3 could add a versioned JSON parser, a public scenario file,
and a command such as `rpf validate scenario.json`. The executable RPF state
machine should be connected only after that interface is stable.
