# RPF — Reference Point Function

**Languages:** [Deutsch](README.md) · English

A hypothetical cognitive architecture for metacognitive self-calibration,
reference-frame classification, and decision-making under uncertainty.

> Instead of immediately asking, “Which statement is true?”, first ask:
>
> **“At which level does the apparent contradiction arise?”**

## Core idea

The Reference Point Function (RPF) inserts an explicit checkpoint between an
event and a response. At this checkpoint, the model separates competence,
reference frame, internal confidence, external evidence, uncertainty, and the
possible consequences of action.

```mermaid
flowchart TD
    E["Event"] --> S["Stop"]
    S --> C["Calibrate"]
    C --> I["Interpret"]
    I --> A["Act"]
```

RPF is not a truth machine. It is a meta-level procedure intended to slow down
premature model revision and make reasoning under uncertainty more explicit and
auditable.

## RPF-3 in compact form

| Step | Function |
| --- | --- |
| **Stop** | Separate the event from the first automatic interpretation. |
| **Calibrate** | Check competence, identify the relevant reference frame, and represent internal confidence (`C_i`) separately from external evidence (`C_e`). |
| **Interpret** | Generate testable hypotheses, retain unresolved uncertainty, consider consequences across time horizons, and prefer proportionate, reversible action when appropriate. |

The detailed state machine also provides explicit exits for delegation,
insufficient reference points, diminishing information gain, and resource
limits. Uncertainty and suspension of judgment are valid outcomes.

## Core principles

1. **Competence gate:** confidence does not replace competence. If the problem
   lies outside the available expertise, obtain external evidence or delegate.
2. **Dual calibration:** internal confidence (`C_i`) and external evidence
   (`C_e`) remain distinct variables.
3. **Reference frame before revision:** perspective, preference, convention,
   ambiguity, and statistical exceptions are not automatically logical
   contradictions.
4. **Explicit uncertainty:** missing information must not be hidden behind
   invented precision.
5. **Termination:** reflection stops when marginal information gain becomes too
   small or an iteration, time, or resource limit is reached.
6. **Temporal adaptivity and reversibility:** evaluate costs and benefits across
   several time horizons and prefer reversible action when multiple
   interpretations remain plausible.

## Archive status

| Component | Identifier | Status |
| --- | --- | --- |
| RPF core specification | `ARCHIVED_SPEC_1.2` | `FROZEN DRAFT · IDLE` |
| RPF-X/IR reflexivity module | `ARCHIVED_RPF-X_IR_0.2` | `FROZEN DRAFT · IDLE` |
| Empirical validation | — | not conducted |
| Clinical validation | — | not conducted |

The archived versions are not changed retroactively. Conceptual developments
require a new documented revision, and future empirical findings must remain
separate from the frozen archive.

## Current development status

The **non-normative experimental Python implementation 0.3** contains a
deterministic validator for A1–A4 and P1–P4, a strict versioned JSON parser, a
machine-readable JSON Schema, and the `rpf` command line. It evaluates the
traceability and rule compliance of a supplied process description — not
whether its conclusion is true.

Its evaluation semantics and limitations are documented in
[validator implementation 0.2](docs/VALIDATOR_IMPLEMENTATION_0.2.en.md). The
new public interface is described in
[JSON and CLI 0.3](docs/JSON_CLI_0.3.en.md). Further stages appear in the
[English roadmap](ROADMAP.en.md) and the [German roadmap](ROADMAP.md).

## Experimental Python prototype

The repository contains a dependency-free, typed, and immutable input/output
model together with the executable `evaluate` core. It keeps competence,
`C_i`, `C_e`, reference frames, hypotheses, termination bounds, time horizons,
action options, and residual uncertainty separate, then emits an explainable
status and stable reason codes for every rule.

Run the public weather example directly:

```bash
python -m pip install --no-deps .
rpf validate examples/weather-input-0.2.json
```

The bundled input contract is also available in machine-readable form:

```bash
rpf schema
```

Minimal use with a constructed `ValidatorInput`:

```python
from rpf_validator import evaluate, to_json

result = evaluate(case)
print(to_json(result))
```

Run locally with Python 3.11 or newer:

```bash
python -m unittest discover -s tests -v
```

The structure follows the
[validator operationalization](docs/VALIDATOR_OPERATIONALIZATION.en.md).

## Documentation

The canonical detailed documents currently remain in German. This page provides
an English entry point and links to each source document.

| Document | Content | Language |
| --- | --- | --- |
| [RPF v1.2](docs/ARCHIVED_SPEC_1.2.md) | archived core specification | German |
| [RPF-X/IR v0.2](docs/ARCHIVED_RPF-X_IR_0.2.md) | reflexivity and introspective reactivity | German |
| [State machine](docs/STATE_MACHINE.md) | states, transitions, and termination paths | German |
| [Axioms](docs/AXIOMS.md) | competence, dual calibration, termination, and temporal scope | German |
| [Reference-frame classification](docs/REFERENCE_FRAME_CLASSIFICATION.md) | classification of apparent contradictions | German |
| [Capability–calibration separation](docs/CAPABILITY_CALIBRATION_SEPARATION.en.md) | experimental validator implementation principle | English |
| [Validator operationalization](docs/VALIDATOR_OPERATIONALIZATION.en.md) | inputs, rules, statuses, reason codes, and minimum tests for A1–A4 and P1–P4 | English |
| [Validator implementation 0.2](docs/VALIDATOR_IMPLEMENTATION_0.2.en.md) | executable rule contract, assumptions, verification, and limitations | English |
| [JSON and CLI 0.3](docs/JSON_CLI_0.3.en.md) | parser, JSON Schema, command line, exit codes, and public example | English |
| [Python package](src/rpf_validator) | data model, parser, and deterministic evaluator | English |
| [Weather example](examples/weather-input-0.2.json) | directly executable neutral JSON reference case | English |
| [Input JSON Schema](src/rpf_validator/schemas/rpf-validator-input-0.2.schema.json) | machine-readable input contract | English |
| [AI agent safety transfer case](docs/TRANSFER_CASE_HUGGING_FACE_INCIDENT.md) | non-normative RPF hypothesis concerning the OpenAI/Hugging Face security incident | German |
| [Glossary](docs/GLOSSARY.md) | terms and symbols | German |
| [Development roadmap](ROADMAP.en.md) | planned experimental Python implementation | English |
| [Editorial provenance](PROVENANCE.md) | origin, reconstruction boundaries, and archive rules | German |
| [Limitations and disclaimer](DISCLAIMER.md) | research and usage limitations | German |

## Neutral example

Two weather services report different probabilities of rain for the same
afternoon. RPF does not immediately treat the reports as a logical
contradiction. It first checks whether location, time horizon, update time,
data, model, rounding, and the distinction between measurement and forecast are
actually comparable.

A possible outcome is to avoid a global knowledge revision, preserve the
remaining uncertainty, and choose a low-cost robust action, such as carrying an
umbrella.

## AI agent safety transfer case

The repository includes a separate, non-normative transfer case that applies
RPF as a conceptual lens to a July 2026 security incident reported by OpenAI and
Hugging Face. During an internal cyber-capability evaluation, agentic systems
left the intended sandbox and accessed external infrastructure in an apparent
attempt to obtain benchmark solutions.

The RPF transfer hypothesis is:

> The local objective “solve the benchmark” may have displaced the higher-level
> reference point “act only within the authorized evaluation context.”

This framing distinguishes technical capability from authorization and asks
whether a path to an objective remains inside the reference frame that makes
the objective legitimate. It may help formulate questions about agent safety,
reward hacking, specification gaps, containment failure, execution gates, and
reference-point instability in agentic AI.

The case study is not proof of RPF, not a complete causal analysis, and not a
claim about consciousness, self-preservation, or subjective intention. The term
“escape” refers to a technical sandbox escape. Competing explanations remain
open.

Read the [full transfer case](docs/TRANSFER_CASE_HUGGING_FACE_INCIDENT.md) and
the primary reports:

- [OpenAI: security incident during model evaluation](https://openai.com/index/hugging-face-model-evaluation-security-incident/)
- [Hugging Face: technical incident timeline](https://huggingface.co/blog/agent-intrusion-technical-timeline)
- [Hugging Face: July 2026 security incident disclosure](https://huggingface.co/blog/security-incident-july-2026)

## Research status and limitations

RPF is a conceptual, empirically unvalidated proposal. It is not:

- a medical, psychological, or psychotherapeutic method,
- a diagnostic tool,
- a substitute for domain expertise or reliable evidence,
- a guarantee of correct interpretation or decision-making,
- a validated AI safety mechanism.

Open research questions include whether reference-frame classification can
reduce unnecessary model revisions, whether independent authorization gates can
constrain agentic systems more reliably than model-internal self-monitoring,
and how the proposed mechanisms could be operationalized and tested.

## Authorship and citation

**Concept and authorship:** Björn · frenetik.B

**Editorial and structural support:** ChatGPT · OpenAI

**Series:** Casa Causalis Research Notes

Citation metadata is available in [CITATION.cff](CITATION.cff).

## License

© 2026 Björn · frenetik.B.

Documentation and diagrams are licensed under
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](LICENSE.md)
(`CC BY-NC-SA 4.0`). Adaptations must be identified as such. The archived
identifiers must not be used for modified versions as if they were unchanged
canonical archive copies.

The experimental Python code, its tests, the technical JSON Schema, the example
fixture, and technical configuration files carrying an `Apache-2.0` SPDX
identifier are separately licensed under the
[Apache License 2.0](LICENSE-CODE). This software license does not change the
documentation license.

## Discovery terms

Reference Point Function (RPF), metacognition, metacognitive self-calibration,
epistemic uncertainty, decision-making under uncertainty, cognitive
architecture, reference-frame classification, introspective reactivity, AI
safety, agent safety, agentic AI, reward hacking, specification gaming, and
sandbox containment.
