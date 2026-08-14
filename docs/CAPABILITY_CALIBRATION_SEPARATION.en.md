# Experimental Implementation Principle: Capability–Calibration Separation

**Languages:** [Deutsch](CAPABILITY_CALIBRATION_SEPARATION.md) · English

## Status

This document defines a **non-normative design rule** for the planned
experimental RPF validator. It changes neither `ARCHIVED_SPEC_1.2` nor
`ARCHIVED_RPF-X_IR_0.2` and does not constitute empirical or clinical
validation of RPF.

## Core statement

> Capability is not the same as calibration, and calibration is not the same
> as reference-frame fit.

The implementation should therefore preserve the following distinction:

```text
competence fit ≠ internal confidence ≠ external evidence
               ≠ reference-frame fit ≠ temporal adaptivity
```

These variables may interact, but the validator must not treat them as
synonyms or silently collapse them into a single trust score. High capability
may also enable efficient optimization of an unsuitable local objective. It is
therefore not, by itself, sufficient for `PASS`.

## Separate evaluation dimensions

| Dimension | Guiding question | Boundary |
| --- | --- | --- |
| Competence fit | Are the task-specific capabilities sufficient for this assessment? | This is not a statement about general intelligence or a person's value. |
| Internal confidence (`C_i`) | How certain is the system about its own assessment? | Confidence is neither competence nor proof. |
| External evidence (`C_e`) | How well is the assessment supported by traceable external data or methods? | Evidence remains linked to its provenance, quality, and limitations. |
| Reference-frame fit | Are the objective, level, scope, and governing constraints identified? | A technically reachable objective is not automatically permitted or appropriate within the relevant frame. |
| Temporal adaptivity | Does the action remain viable across the defined time horizons? | Short-term success may conflict with medium- or long-term costs. |
| Reversibility | How well can consequences be limited or reversed if an assumption is wrong? | Reversibility does not replace evidence, but it affects the proportionality of an action. |

## Consequences for the validator

1. Every evaluation dimension receives its own field, provenance, and
   rationale.
2. An overall status must not be derived solely from high competence or high
   confidence.
3. Insufficient competence should produce `DELEGATE`, not a claim that an axiom
   was violated.
4. A missing or insufficiently identified reference frame should produce
   `NO_REFERENCE`.
5. Notable divergence between `C_i` and `C_e` is initially a calibration
   signal. It produces `WARN` or renewed calibration unless another stop rule
   applies.
6. A conflict with previously declared constraints or the required
   multi-horizon evaluation may produce `STOP`.
7. `PASS` is permitted only after all dimensions required for the case have
   been evaluated and residual uncertainty has been reported.

The implementation must define and test the precedence of simultaneously
triggered states explicitly. These status mappings are prototype design
choices, not a retroactive extension of the archived specification.

## Illustrative result patterns

| Finding | Example status |
| --- | --- |
| Insufficient competence fit | `DELEGATE` |
| High competence but no identified reference frame | `NO_REFERENCE` |
| High confidence with weak external evidence | `WARN` |
| A local objective conflicts with a declared higher-order constraint | `STOP` |
| Required dimensions evaluated and residual uncertainty reported | `PASS` |

These patterns evaluate the procedural compliance of a process. They do not
determine whether a statement is objectively true.

## Safety and application boundary

This principle is intended for modeling technical decision processes. The
experimental validator must not be used to evaluate, diagnose, or classify
people, mental states, or substance-related behavior. Analogies from such
domains may illustrate ideas, but they are not part of the technical validation
logic and do not provide empirical evidence for RPF.

## Candidate for a future revision

Only implementation, tests, and documented evaluation can show whether
capability–calibration separation should be proposed as a distinct principle in
a future RPF version. Until then, it remains an experimental implementation
rule.
