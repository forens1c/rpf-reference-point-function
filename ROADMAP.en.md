# RPF Development Roadmap

**Languages:** [Deutsch](ROADMAP.md) · English

## Status of this roadmap

This roadmap describes possible next development steps. It is
**non-normative**, makes no schedule commitments, and changes neither
`ARCHIVED_SPEC_1.2` nor `ARCHIVED_RPF-X_IR_0.2`.

Experimental implementation choices, thresholds, and data models do not
automatically become part of the frozen RPF core. Deviations and later changes
must remain traceable.

## Next objective

The next objective is an **experimental Python reference implementation**. Its
first milestone will be a deterministic axiom validator.

The validator will not determine whether a statement is true. It will evaluate
whether a calibration and decision process:

- considers its own competence fit,
- keeps internal confidence separate from external evidence,
- identifies the reference frame before a global revision,
- reports remaining uncertainty explicitly,
- observes termination and resource limits,
- considers consequences across multiple time horizons.

Planned structured result states include `PASS`, `WARN`, `DELEGATE`,
`NO_REFERENCE`, and `STOP`. Triggering a protective rule is not automatically
an axiom violation: delegation under insufficient competence and rule-compliant
termination are intended RPF outcomes.

## Development principles

1. **Deterministic core first:** The fundamental rules should be executable and
   testable without a language model.
2. **Process, not a truth claim:** The implementation evaluates procedural
   quality and traceability, not the objective truth of a conclusion.
3. **Explicit provenance:** Inputs, thresholds, triggered rules, and residual
   uncertainty should remain visible in the output.
4. **Experimental thresholds:** Numerical values must not be presented as a
   canonical part of RPF without justification.
5. **Separation of concerns:** The validator, state machine, reference-frame
   classifier, and optional AI components remain separate modules.
6. **No silent revision:** Code neither overwrites nor retrospectively
   reinterprets the archived specifications.

## Planned stages

### 0 — Technical operationalization

- Define the required inputs, validation rules, and outputs for each axiom.
- Determine which variables are directly measurable and which require declared
  or external assessment.
- Clarify the meaning and scales of competence fit, `C_i`, `C_e`, `ΔK`, time,
  and resources.
- Mark experimental thresholds explicitly as configuration.

### 1 — Data model and result schema

- Define typed inputs for problem context, competence fit, confidence, evidence,
  reference frame, and resources.
- Define structured results containing status, rationale, triggered rules, and
  residual uncertainty.
- Validate ranges and missing required fields.

### 2 — Deterministic axiom validator

- Implement the competence gate with a `DELEGATE` result.
- Verify separation of `C_i` and `C_e`; initially treat notable divergence as a
  calibration signal rather than an automatic error.
- Implement termination based on information gain, iterations, time, and
  resources.
- Represent evaluation across multiple time horizons and reversible action
  options.
- Produce both machine-readable and human-readable rationales.

### 3 — Tests and neutral reference case

- Add unit tests for every rule and result state.
- Test boundaries, invalid inputs, and missing reference points.
- Implement the neutral weather example as the first complete end-to-end case.
- Ensure that identical inputs produce reproducible results.

### 4 — RPF state machine

- Model the existing state space as executable transition logic.
- Test allowed and disallowed transitions.
- Record delegation, `NO_REFERENCE`, termination, and return to `IDLE`.

### 5 — Optional classification and AI experiments

- Evaluate a rule-based reference-frame classifier before an AI-based variant.
- Treat AI outputs as hypotheses and pass them through the same validator.
- Use the AI agent transfer case as a demanding research case without treating
  it as validation of RPF.
- Keep authorization separate from technical reachability in security-related
  experiments.

### 6 — Experimental evaluation

- Document evaluation criteria and comparison conditions before experiments.
- Study false alarms, missed conflicts, termination behavior, and
  explainability.
- Publish results separately from the frozen specification.

## First planned milestone

- [ ] Create an operationalization table for A1–A4 and P1–P4
- [ ] Select a separate software license for new code
- [ ] Create a minimal Python package and result schema
- [ ] Implement the deterministic axiom validator
- [ ] Add automated unit tests
- [ ] Implement the weather example as an end-to-end test
- [ ] Document limitations and experimental assumptions

## Non-goals of the first prototype

The first prototype is explicitly not:

- a truth detector,
- an autonomous authorization system,
- a medical, psychological, or diagnostic tool,
- empirical confirmation of RPF,
- a validated AI safety architecture,
- a substitute for domain expertise or external evidence.

## Contributions and change records

Proposals, test cases, and implementations may later be submitted through
GitHub Issues and pull requests. Contributions should clearly distinguish:

1. the documented RPF core,
2. an experimental implementation choice,
3. an empirical finding,
4. an interpretation or new hypothesis.

Conceptual changes require a separate version identifier. Implementation code
should receive a separate software license; the existing `CC BY-NC-SA 4.0`
documentation license does not automatically apply to future code.
