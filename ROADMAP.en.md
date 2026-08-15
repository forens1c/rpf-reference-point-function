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

The **experimental Python reference implementation** now has a deterministic
axiom validator, a public JSON/CLI interface, an executable state machine, and
the separate, non-authorizing proposal contract
`rpf-classification-proposal-0.1`.

The next bounded step is a small deterministic rule-based classification
provider. It will only produce the new proposal contract. An adapter to
`ValidatorInput`, automatic semantic analysis, and a language model remain
later, separately versioned steps.

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

An additional experimental implementation principle is
[capability–calibration separation](docs/CAPABILITY_CALIBRATION_SEPARATION.en.md):
competence fit, internal confidence, external evidence, reference-frame fit,
and temporal adaptivity are evaluated independently. High capability alone
must not produce `PASS`.

The initial [operationalization table for A1–A4 and P1–P4](docs/VALIDATOR_OPERATIONALIZATION.en.md)
defines input fields, rule results, process statuses, reason codes, and minimum
tests. It is the provisional working document for the data model and validator,
not a change to the frozen core.

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
7. **Capability is not calibration:** Competence, confidence, evidence,
   reference-frame fit, and temporal adaptivity remain separate evaluation
   dimensions with their own rationale and provenance.

## Planned stages

### 0 — Technical operationalization

- Define the required inputs, validation rules, and outputs for each axiom.
- Determine which variables are directly measurable and which require declared
  or external assessment.
- Clarify the meaning and scales of competence fit, `C_i`, `C_e`, `ΔK`, time,
  and resources.
- Operationalize reference-frame fit and temporal adaptivity as dimensions
  independent of competence and confidence.
- Mark experimental thresholds explicitly as configuration.

### 1 — Data model and result schema

- Define typed inputs for problem context, competence fit, confidence, evidence,
  reference frame, and resources.
- Prevent separate evaluation dimensions from being silently collapsed into a
  single trust score.
- Define structured results containing status, rationale, triggered rules, and
  residual uncertainty.
- Validate ranges and missing required fields.

### 2 — Deterministic axiom validator

- Implement the competence gate with a `DELEGATE` result.
- Ensure that high competence or confidence alone never produces `PASS`.
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

- [x] Model the existing state space as executable transition logic.
- [x] Test allowed and disallowed transitions.
- [x] Record delegation, `NO_REFERENCE`, termination, and return to `IDLE`.

### 5 — Optional classification and AI experiments

- [x] Define a versioned, non-authorizing classification proposal contract.
- [x] Model status, classes, provider confidence, uncertainty, and grounding
  text fragments as separate dimensions.
- [x] Prevent a proposal from setting process status, reason codes, state
  transitions, competence, evidence scores, or actions.
- [x] Publish neutral positive and negative fixtures for the contract boundary.
- Evaluate a rule-based reference-frame classifier before an AI-based variant.
- Treat AI outputs as hypotheses and pass them through the same validator.
- Examine whether a later schema must explicitly separate the assessment
  subject, assessment authority, and provenance of their respective claims.
- Model source independence relative to a claim and across data, analysis,
  method, context, and provenance dimensions.
- Examine evidence roots, derivation edges, scope, epistemic modality, and
  causal status for a later versioned claim contract.
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

- [x] Create an [operationalization table for A1–A4 and P1–P4](docs/VALIDATOR_OPERATIONALIZATION.en.md)
- [x] Represent capability–calibration separation in the data model and tests
- [x] Select a separate software license for new code (`Apache-2.0`)
- [x] Create a minimal Python package and typed input/output schema
- [x] Implement the deterministic axiom validator
- [x] Add automated unit tests
- [x] Implement the weather example as an end-to-end test
- [x] Document limitations and experimental assumptions

The first implementation milestone is therefore complete in experimental
[validator implementation 0.2](docs/VALIDATOR_IMPLEMENTATION_0.2.en.md).

## Completed technical slice 0.3

Version 0.3 makes the public interface directly usable:

- [x] Develop a versioned parser for JSON input.
- [x] Publish a machine-readable JSON Schema.
- [x] Provide the neutral weather case as an executable scenario file.
- [x] Add `rpf validate scenario.json` and `rpf schema`.
- [x] Add parser, CLI, and compatibility tests.

Details appear in
[JSON interface and CLI 0.3](docs/JSON_CLI_0.3.en.md). Package version
`0.3.0.dev0` continues to use the unchanged input and result contracts
`rpf-validator-input-0.2` and `rpf-validator-result-0.2`.

## Completed technical slice 0.4

Version 0.4 implements stage 4 as executable, bounded control flow:

- [x] represent canonical states and events as typed enums,
- [x] publish allowed transitions in an immutable table,
- [x] reject invalid transitions deterministically,
- [x] record `DELEGATE`, `NO_REFERENCE`, and early or adaptive `STOP` paths,
- [x] return every successful run to `IDLE` within at most seven transitions,
- [x] couple validator and runtime only through
  `rpf-validator-result-0.2`,
- [x] add the versioned `rpf-state-machine-trace-0.1` audit trace and
  `rpf trace scenario.json`.

Details appear in
[executable state machine 0.4](docs/STATE_MACHINE_RUNTIME_0.4.en.md). Package
version `0.4.0.dev0` continues to use the unchanged input and result contracts
`rpf-validator-input-0.2` and `rpf-validator-result-0.2`.

## Completed technical slice 0.5

Version 0.5 establishes the first machine-readable boundary for optional
classification providers without granting them assessment authority:

- [x] version the `rpf-classification-proposal-0.1` contract,
- [x] provide immutable Python models, a strict parser, and a Draft 2020-12
  JSON Schema,
- [x] record provider identity, configuration digest, source binding, and
  byte-addressed evidence fragments,
- [x] keep frame status separate from frame classes and provider confidence
  separate from `C_i`/`C_e`,
- [x] reject unknown fields and authorizing interference deterministically,
- [x] publish three neutral public proposals and a negative-case catalog,
- [x] leave validator input, validator result, and state-machine trace
  unchanged.

Details appear in
[classification proposal contract 0.1](docs/CLASSIFICATION_PROPOSAL_CONTRACT_0.1.en.md).
Package version `0.5.0.dev0` deliberately contains no provider and no adapter.

## Next technical slice

The next slice continues stage 5 with a small rule-based provider without
placing a language model or adapter inside the core:

- implement a small deterministic provider behind a narrow Python interface,
- define the trusted invocation context or provider registry separately from
  provider output,
- produce reproducible proposals for a deliberately limited set of rules,
- add contract, provenance, and reproducibility tests,
- continue testing that the provider neither invokes the validator or
  transition table nor sets process status.

Only after that provider slice should an adapter with an explicit field
allowlist, binding verification, and its own mapping trace be designed. Only
that adapter could combine a proposal with an independently supplied base case
and translate it toward `ValidatorInput`.

Automatic semantic analysis remains a later, replaceable variant. The
deterministic core can reject structurally invalid or incomplete proposals, but
without additional evidence it cannot identify internally consistent false
input as untrue.

Compatibility and migration rules for later pre-release schemas remain an open
parallel task. This includes the role distinction between assessment subject
and assessment authority exposed by the
[loop-collapse transfer case](docs/TRANSFER_CASE_LOOP_COLLAPSE.en.md).
The [Source Echo transfer case](docs/TRANSFER_CASE_SOURCE_ECHO.en.md) adds a
claim-relative provenance structure as another parallel task; it will not be
silently added to the existing 0.2 input contract.

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
is separately licensed under `Apache-2.0`; the existing `CC BY-NC-SA 4.0`
documentation license does not apply to that code.
