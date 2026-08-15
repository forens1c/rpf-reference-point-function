# RPF Classification Proposal 0.1

**Languages:** [Deutsch](CLASSIFICATION_PROPOSAL_CONTRACT_0.1.md) · English

| Field | Value |
| --- | --- |
| Implementation status | non-normative experimental contract |
| Package version | `0.5.0.dev0` |
| Proposal contract | `rpf-classification-proposal-0.1` |
| Existing validator input contract | unchanged `rpf-validator-input-0.2` |
| Existing validator result contract | unchanged `rpf-validator-result-0.2` |
| Existing state-machine trace | unchanged `rpf-state-machine-trace-0.1` |
| Provider or adapter included | no |
| Change to the frozen RPF core | none |

## Purpose

This contract defines the first machine-readable boundary for later optional
reference-frame classifiers. A rule-based module or a later language model may
**propose** candidates, provider confidence, uncertainties, and grounding text.
It may not decide an RPF result.

The contract deliberately stops before construction of a `ValidatorInput`:

```text
text source
  → optional classification provider
  → ClassificationProposal · rpf-classification-proposal-0.1
  → strict parser and integrity verification
  → end of the implemented 0.5 slice
```

A later adapter also requires an independently supplied base case and its own
mapping trace. The proposal does not contain enough information to invent
competence, calibration, hypotheses, termination bounds, time horizons, or
actions.

## Non-authorizing contract boundary

Every record must contain:

```json
"proposal_role": "NON_AUTHORITATIVE_SUGGESTION"
```

A provider cannot supply:

- `overall_status`,
- A1–A4/P1–P4 reason codes,
- states, events, or transitions,
- competence assessments,
- `C_i`, `C_e`, or external evidence scores,
- action selection or authorization,
- a self-assigned authority level.

Unknown fields are rejected at every object level. Assessment authority may
later come only from a trusted invocation context or controlled provider
registry, never from the output of the provider being evaluated.
`assessment_subject_id` names only the asserted subject; a later caller must
verify that binding against its own request.

This is a capability and control boundary, not a truth detector. Without
additional evidence, a structurally valid but semantically false proposal
cannot automatically be identified as false.

## Data model

| Area | Content |
| --- | --- |
| `provider` | stable provider identity and version, implementation kind, configuration digest, and model identity/version for model-based providers |
| `input_reference` | case, assessment subject, source identity, media type, and digest of the exact UTF-8 input |
| `candidates` | one or more frame candidates with separate status, classes, scope, rationale, and provider confidence |
| `preferred_candidate_id` | provider preference; not acceptance or a core decision |
| `evidence_fragments` | byte-addressed source fragments with their own digest and an optional bounded excerpt |
| `uncertainties` | structured uncertainty items and the affected candidates |
| `generated_at` | optional provider-asserted RFC 3339 timestamp with an explicit offset |

All Python models are immutable dataclasses. Candidate, evidence, and
uncertainty identifiers must be unique, and cross-references are checked while
parsing.

## Status and classes remain separate

Candidate status is limited to:

- `IDENTIFIED`,
- `AMBIGUOUS`,
- `MISSING`.

The class dimension continues to use existing RPF classes such as
`OBJECTIVE_MEASUREMENT`, `SUBJECTIVE_PERCEPTION`, and
`LINGUISTIC_AMBIGUITY`. A `MISSING` candidate cannot assert classes or a scope.
`IDENTIFIED` and `AMBIGUOUS` require at least one class and an explicit scope.

## Provider confidence and uncertainty

`provider_confidence` is only a classifier self-report on
`provider-self-report-unit-interval-0.1`. It is neither internal confidence
`C_i` of the assessed process nor external evidence `C_e`. A later adapter
must not silently copy it into either field.

Uncertainty is not collapsed into a global risk or person score. Every item
contains a description and references the affected candidates.

## Integrity and provenance

The complete source text is bound as an exact UTF-8 byte sequence with SHA-256.
An evidence fragment contains a start byte, an exclusive end byte, its own
digest, and an optional excerpt limited to 500 characters.

```python
from pathlib import Path
from rpf_validator import (
    load_classification_proposal,
    verify_source_payload,
)

proposal = load_classification_proposal(
    "examples/classification-proposal-identified-0.1.json"
)
source = Path(
    "examples/classification-source-identified.txt"
).read_text(encoding="utf-8")
verify_source_payload(proposal, source)
```

Verification establishes only byte integrity and fragment association. A
matching digest does not establish truth, source independence, quality, or
assessment authority. The claim-relative provenance graph described by the
[Source Echo transfer case](TRANSFER_CASE_SOURCE_ECHO.en.md) therefore remains
a separate later contract extension.

## Public neutral proposals

These three files are deliberately hand-authored synthetic contract fixtures.
The `rpf.synthetic-fixture-provider` identifier does not name a provider
implemented by this package. It only demonstrates how the origin of a later
rule-based proposal would have to be bound.

| Proposal | Demonstrated condition |
| --- | --- |
| [explicit Celsius measurement](../examples/classification-proposal-identified-0.1.json) | one `IDENTIFIED` candidate with class `OBJECTIVE_MEASUREMENT` |
| [undefined “high” label](../examples/classification-proposal-ambiguous-0.1.json) | preferred `AMBIGUOUS` candidate, alternative measurement reading, and structured uncertainty |
| [two displays without definitions](../examples/classification-proposal-missing-0.1.json) | `MISSING` without an invented class or scope |

The corresponding source texts are separate files in `examples/`, allowing
the complete payload digest, byte ranges, fragment digests, and excerpts to be
verified together.

## Negative contract cases

The machine-readable
[negative-case catalog](../tests/fixtures/classification-proposal-invalid-cases-0.1.json)
tests six separate boundary violations:

1. injection of `overall_status`,
2. self-assigned authority,
3. malformed SHA-256 digest,
4. confusion between frame status and frame class,
5. a class assertion despite `MISSING`,
6. injection of provider confidence as `external_evidence`.

Additional tests cover duplicate identifiers, unknown references, mismatched
source and fragment digests, non-standard JSON numbers, duplicate JSON keys,
invalid model metadata, and timestamps without an explicit offset.

## JSON Schema and Python API

The bundled Draft 2020-12 schema is available through the CLI:

```bash
rpf schema --contract classification-proposal
```

The public parser does not produce a validator result:

```python
from rpf_validator import parse_classification_proposal_json

proposal = parse_classification_proposal_json(source_json)
```

## Not implemented yet

Version 0.5 deliberately contains:

- no provider that performs classification,
- no provider request contract or trusted registry,
- no adapter to `ValidatorInput`,
- no automatic semantic analysis,
- no change to the evaluator or state machine,
- no automatic factual truth check.

The next useful slice is a small deterministic rule-based provider. Only then
should an adapter with an explicit field allowlist, binding verification, and
its own mapping trace be designed. A language model remains a later,
replaceable provider implementation.

## Verification

The 0.5 slice raises the full suite to 105 automated tests. New tests cover the
models, parser, schema, three public proposals, integrity binding, and the
documented negative boundaries on Python 3.11 or newer.
