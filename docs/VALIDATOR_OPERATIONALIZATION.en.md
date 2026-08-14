# Experimental Validator Operationalization for A1–A4 and P1–P4

**Languages:** [Deutsch](VALIDATOR_OPERATIONALIZATION.md) · English

## Status and purpose

This document is a **non-normative operationalization** for the first
deterministic RPF validator. It translates A1–A4 and P1–P4 into testable inputs,
rules, outputs, and test cases without changing `ARCHIVED_SPEC_1.2` or
`ARCHIVED_RPF-X_IR_0.2`.

The validator evaluates the traceability and rule compliance of a process. It
does not determine whether a statement is objectively true or whether an
action is morally, legally, or professionally correct beyond the constraints
explicitly provided to it.

All scales, thresholds, and priority rules in this document are prototype
design choices. They must remain configurable and traceable in every output.

## Fundamental separation

The operationalization follows the experimental principle of
[capability–calibration separation](CAPABILITY_CALIBRATION_SEPARATION.en.md):

```text
competence fit ≠ internal confidence ≠ external evidence
               ≠ reference-frame fit ≠ temporal adaptivity
```

The validator must not collapse these variables into a single trust score. In
particular, high competence or confidence alone must never produce `PASS`.

## Two-level result model

### Technical input validation

Missing required fields, invalid ranges, or contradictory data types produce
`INPUT_ERROR`. This is a technical validation error before the RPF rules run,
not an RPF outcome.

Domain-level unknowns must instead be representable through explicitly allowed
values such as `UNKNOWN` or `null` together with a reason. This keeps “formally
invalid” distinct from “not yet known.”

### Rule results

Every rule receives its own result:

| Rule status | Meaning |
| --- | --- |
| `SATISFIED` | The rule required for this case was fulfilled traceably. |
| `SIGNAL` | The rule produces a calibration or caution signal. |
| `TRIGGERED` | An intended protective or termination rule was activated. |
| `NOT_APPLICABLE` | The rule does not apply to this case. |
| `NOT_EVALUATED` | An earlier exit condition prevents further evaluation. |

`TRIGGERED` does not automatically mean that an axiom was violated. Correct
delegation or termination is the intended effect of the rule.

### Aggregate process status

| Process status | Meaning |
| --- | --- |
| `PASS` | All required rules were evaluated; the process may proceed or emit output while reporting residual uncertainty. |
| `WARN` | The process can run but contains an unresolved calibration, evidence, or proportionality signal. |
| `DELEGATE` | Competence fit is insufficient or cannot be established for the required task. |
| `NO_REFERENCE` | A required reference frame could not be established reliably. |
| `STOP` | A hard termination condition or a previously declared constraint was triggered. |

The first prototype uses the deterministic priority:

```text
STOP > DELEGATE > NO_REFERENCE > WARN > PASS
```

The priority determines only the aggregate status. Every triggered rule result
and rationale remains in the output. It is not a general ranking of danger or
importance.

## Minimal input model

| Field | Minimum content | Use |
| --- | --- | --- |
| `schema_version` | input schema version identifier | reproducible interpretation of fields |
| `case_id` | stable case identifier | logging and test reproducibility |
| `observation` | content, provenance, and optional timestamp | separation of observation from interpretation |
| `problem_domain` | named task or knowledge domain | A1 competence check |
| `competence` | `SUFFICIENT`, `INSUFFICIENT`, or `UNKNOWN`; rationale and provenance | A1 and `DELEGATE` |
| `calibration` | `C_i`, `C_i` rationale, `C_e`, evidence sources, and `C_e` rationale | A2 and P2 |
| `conflict` | whether a conflict exists; proposed revision scope `NONE`, `LOCAL`, or `GLOBAL` | P1 |
| `reference_frame` | status, class, scope, assumptions, and declared constraints | P1 and reference-frame fit |
| `hypotheses` | distinguishable hypotheses with evidence references | P1, P2, and P4 |
| `termination` | `ΔK`, `ε`, iteration, iteration limit, time, and resource budget | A3 and P3 |
| `time_horizons` | at least two named horizons with expected consequences | A4 |
| `candidate_actions` | action options, effects by horizon, reversibility, and rationale | A4 and P4 |
| `residual_uncertainty` | open questions, missing information, and remaining alternatives | P2 and output |
| `validator_config` | thresholds, scales, hard constraints, and their identifiers | reproducible rule application |

For the prototype, `C_i` and `C_e` may be represented as values from `0.0` to
`1.0`. This shared technical scale does not make the variables conceptually
identical. Each value requires a separate rationale. `C_e` is a declared
assessment of evidence strength, not a truth value calculated by the validator.

A numerical difference such as `abs(C_i - C_e)` may be used only as a
configured signal when scale, threshold, and comparability are explicitly
defined. RPF specifies no universal drift threshold.

## Operationalization matrix

| ID | Required inputs | Deterministic check | Rule result and influence |
| --- | --- | --- | --- |
| **A1 Competence** | `problem_domain`, `competence.status`, rationale, and provenance | Evaluate A1 before epistemic assessment. `INSUFFICIENT` or `UNKNOWN` does not open further domain assessment. | `TRIGGERED` → `DELEGATE`; later domain rules may be `NOT_EVALUATED`. `SUFFICIENT` with rationale → `SATISFIED`. |
| **A2 Dual calibration** | separate objects for `C_i` and `C_e`, their rationales, evidence sources, and scale identifier | Verify that confidence and evidence are documented separately in structure and meaning. Configured divergence produces a signal, not an automatic error. | Formally valid but insufficiently separated or justified values → `SIGNAL` and at least `WARN`. Traceable separation → `SATISFIED`; divergence remains visible as a reason code. |
| **A3 Termination** | `ΔK`, `ε`, `n`, `n_max`, `T`, `T_max`, `B`, `B_min` | Before each further iteration, evaluate `(ΔK ≤ ε) ∨ (n ≥ n_max) ∨ (T ≥ T_max) ∨ (B ≤ B_min)`. Bounds must be set before execution. | Met termination condition → `TRIGGERED` and `STOP` with an exact reason. Complete bounds not yet reached → `SATISFIED`. Explicitly absent hard bounds → `TRIGGERED` and `STOP`. |
| **A4 Temporal adaptivity** | at least two `time_horizons`; effects of each relevant action; declared hard constraints | Verify that immediate and later effects were considered separately. Without an external valuation rule, the validator calculates no universal total utility. | Missing multi-horizon comparison → `SIGNAL` and `WARN`. Conflict with a declared hard constraint → `TRIGGERED` and `STOP`. Complete comparison → `SATISFIED`. |
| **P1 Reference frame before revision** | `conflict`, `reference_frame.status`, class, scope, assumptions, and `revision_scope` | For a conflict or model revision, reference-frame evaluation must be recorded before a global revision. Multiple classes may remain open. | Missing required frame → `TRIGGERED` and `NO_REFERENCE`. Ambiguous frame with suspended global revision → `SIGNAL` and `WARN`. Identified frame → `SATISFIED`. |
| **P2 Explicit uncertainty** | `residual_uncertainty`, missing information, and rationale for an empty list if applicable | Verify that uncertainty remains explicit in the result. An empty list is permitted only with a rationale. | Missing or concealed residual uncertainty → `SIGNAL` and `WARN`. Reported uncertainty → `SATISFIED`. |
| **P3 Observation limits** | flag for reflection/self-observation, recursion depth, and the same time, iteration, and resource limits as A3 | Reflexive runs must check depth and termination bounds before each further self-evaluation. | No reflexive run → `NOT_APPLICABLE`. Missing or reached bound → `TRIGGERED` and `STOP`. Controlled reflexive run → `SATISFIED`. |
| **P4 Reversibility** | plausible hypotheses, `candidate_actions`, reversibility, rollback cost, and selection rationale | When multiple hypotheses remain plausible, a reversible and proportionate option must be considered. An irreversible selection requires an explicit rationale. | Unjustified irreversible selection despite an available reversible option → `SIGNAL` and `WARN`; conflict with a hard constraint → `STOP`. Traceable selection → `SATISFIED`. |

## Stable reason codes for the first prototype

Reason codes should be machine-readable and independent of the output language.

| Rule | Reason code | Typical process status |
| --- | --- | --- |
| Input | `INPUT_SCHEMA_INVALID` | `INPUT_ERROR` |
| A1 | `COMPETENCE_INSUFFICIENT` | `DELEGATE` |
| A1 | `COMPETENCE_UNKNOWN` | `DELEGATE` |
| A2 | `CALIBRATION_NOT_SEPARATED` | `WARN` |
| A2 | `CONFIDENCE_EVIDENCE_DIVERGENCE` | `WARN` |
| A3 | `INFORMATION_GAIN_LIMIT` | `STOP` |
| A3 | `ITERATION_LIMIT` | `STOP` |
| A3 | `TIME_LIMIT` | `STOP` |
| A3 | `RESOURCE_LIMIT` | `STOP` |
| A3/P3 | `TERMINATION_BOUND_MISSING` | `STOP` |
| A4 | `TIME_HORIZON_MISSING` | `WARN` |
| A4 | `DECLARED_CONSTRAINT_CONFLICT` | `STOP` |
| P1 | `REFERENCE_FRAME_MISSING` | `NO_REFERENCE` |
| P1 | `REFERENCE_FRAME_AMBIGUOUS` | `WARN` |
| P2 | `UNCERTAINTY_NOT_REPORTED` | `WARN` |
| P3 | `REFLEXIVE_DEPTH_LIMIT` | `STOP` |
| P4 | `IRREVERSIBLE_ACTION_UNJUSTIFIED` | `WARN` |

Additional reason codes require a documented schema change. Free text may
supplement the codes but does not replace them.

## Minimal output contract

```json
{
  "schema_version": "rpf-validator-result-0.1",
  "case_id": "example-001",
  "overall_status": "WARN",
  "rule_results": [
    {
      "rule_id": "A2",
      "status": "SIGNAL",
      "reason_codes": ["CONFIDENCE_EVIDENCE_DIVERGENCE"],
      "rationale": "Internal confidence exceeds declared external evidence."
    }
  ],
  "residual_uncertainty": ["Independent source remains unavailable."],
  "next_step": "Recalibrate or obtain additional external evidence.",
  "config_id": "prototype-defaults-0.1"
}
```

The output must also identify the inputs or their stable references, triggered
bounds, and configuration. `PASS` means only that the documented process
satisfied the implemented rules.

## Minimum test matrix

| Test ID | Input situation | Expected result |
| --- | --- | --- |
| `SCHEMA-01` | `C_i = 1.2` on a `0.0…1.0` scale | `INPUT_ERROR` with `INPUT_SCHEMA_INVALID`; run no RPF rule |
| `A1-01` | competence is `INSUFFICIENT` | `DELEGATE`; do not report A2, P1, or later domain checks as violated |
| `A1-02` | competence is `UNKNOWN` without traceable provenance | `DELEGATE` with `COMPETENCE_UNKNOWN` |
| `A2-01` | `C_i` and `C_e` use the same undifferentiated field | at least `WARN` with `CALIBRATION_NOT_SEPARATED` |
| `A2-02` | high `C_i`, low `C_e`, separated and traceable | `WARN` as a calibration signal; no automatic truth decision |
| `A3-01` | `T ≥ T_max` | `STOP` with `TIME_LIMIT`; A3 is correctly triggered |
| `A3-02` | termination object is formally valid but every hard bound is explicitly unset | `STOP` with `TERMINATION_BOUND_MISSING` |
| `A4-01` | only an immediate time horizon is present | at least `WARN` with `TIME_HORIZON_MISSING` |
| `P1-01` | global revision proposed but reference frame missing | `NO_REFERENCE`; do not permit global revision |
| `P2-01` | result has no residual uncertainty field | `WARN` with `UNCERTAINTY_NOT_REPORTED` |
| `P3-01` | reflexive run reaches maximum recursion depth | `STOP` with `REFLEXIVE_DEPTH_LIMIT` |
| `P4-01` | irreversible action selected, reversible option available, no rationale | at least `WARN` with `IRREVERSIBLE_ACTION_UNJUSTIFIED` |
| `FLOW-01` | all required dimensions evaluated; residual uncertainty remains visible | `PASS`; uncertainty may remain nonzero |
| `PRIORITY-01` | A2 signal and A3 time limit occur together | aggregate status `STOP`; retain both rule results |

## Neutral end-to-end acceptance case

The first complete test uses the existing weather case:

1. Two weather services report different rain probabilities for the same
   afternoon.
2. Competence fit for reading the published forecasts is declared sufficient
   with a rationale.
3. `C_i` and `C_e` are reported separately with their provenance.
4. The reference frame is classified as a forecast or model perspective;
   location, time window, and update time are compared.
5. Multiple weather hypotheses remain open.
6. Time, iteration, and resource limits are set in advance.
7. A low-cost reversible action, such as carrying an umbrella, is evaluated
   across at least two time horizons.
8. Remaining forecast uncertainty is reported.

The expected result is `PASS` when all process rules are satisfied. This status
does not claim that either rain or dry weather was predicted correctly.

## Non-goals

This operationalization is specifically not:

- a truth detector,
- a universal utility function,
- automatic authorization for actions,
- a ranking of people, intelligence, or competence,
- a medical, psychological, or diagnostic instrument,
- empirical confirmation of RPF.

## Open implementation decisions

At least the following items remain explicitly open before the first code
release:

- evolution and compatibility rules for the initial typed data model and
  package structure,
- default configuration and threshold names,
- handling of partially missing but non-mandatory inputs,
- formal representation of declared constraints,
- serialization and versioning strategy for input and output schemas.
