# JSON Interface and CLI 0.3

**Languages:** [Deutsch](JSON_CLI_0.3.md) · English

## Status and boundary

`rpf-validator 0.3.0.dev0` makes the experimental validator directly usable
through a strict JSON interface and the `rpf` command. This version does not
change any evaluation rule in
[validator implementation 0.2](VALIDATOR_IMPLEMENTATION_0.2.en.md).

The package version and data-contract versions are intentionally independent:

| Component | Identifier |
| --- | --- |
| Python package and CLI | `0.3.0.dev0` |
| Input contract | `rpf-validator-input-0.2` |
| Result contract | `rpf-validator-result-0.2` |

A `PASS` still means only that the supplied process description satisfies the
implemented rules. It does not confirm its facts, sources, or action.

## Included interfaces

| Artifact | Function |
| --- | --- |
| [`parse_json`](../src/rpf_validator/parsing.py) | convert strict JSON into an immutable `ValidatorInput` |
| [JSON Schema](../src/rpf_validator/schemas/rpf-validator-input-0.2.schema.json) | machine-readable description of the input contract |
| [`rpf validate`](../src/rpf_validator/cli.py) | evaluate a file or standard input |
| [`rpf schema`](../src/rpf_validator/cli.py) | print the bundled input schema |
| [Weather example](../examples/weather-input-0.2.json) | public neutral end-to-end case |
| [Coincidence interpretation](../examples/coincidence-interpretation-input-0.2.json) | ambiguous reference frame producing `WARN` |
| [Reflected desire](../examples/reflected-desire-input-0.2.json) | ambiguous source of an action impulse producing `WARN` |
| [Source Echo](../examples/source-echo-input-0.2.json) | claim-relative source ambiguity producing `WARN` |
| [Loop-collapse self-assessment](../examples/loop-collapse-self-input-0.2.json) | A1 gate producing `DELEGATE` |
| [Externally documented loop-collapse mechanics case](../examples/loop-collapse-external-input-0.2.json) | retained signal path producing `STOP` |

The parser and CLI use only the Python standard library at runtime.

## Installation and use

With Python 3.11 or newer, install the package locally without runtime
dependencies:

```bash
python -m pip install --no-deps .
```

Evaluate the public example:

```bash
rpf validate examples/weather-input-0.2.json
```

Produce compact output or read JSON from standard input:

```bash
rpf validate examples/weather-input-0.2.json --compact
rpf validate - --compact < examples/weather-input-0.2.json
```

Print the schema:

```bash
rpf schema
```

The same interface is available without an installed console script as:

```bash
python -m rpf_validator validate examples/weather-input-0.2.json
```

## Strict input validation

Before evaluation, the parser checks among other things:

- valid UTF-8 JSON without `NaN`, `Infinity`, or duplicate object keys,
- known and required fields plus the declared schema identifier,
- data types, enums, ranges, and non-empty text,
- unique model identifiers,
- references to evidence sources, time horizons, constraints, and the selected
  action.

Structural failures contain the stable reason code `INPUT_SCHEMA_INVALID`, a
JSONPath-like path, and a rationale. The JSON Schema helps editors and external
tools perform preliminary validation. The Python parser remains authoritative,
however, because JSON Schema cannot express every cross-object reference and
identifier uniqueness rule.

## Output and exit codes

For valid input, `rpf validate` always emits a complete
`rpf-validator-result-0.2` JSON document.

| Exit code | Meaning |
| --- | --- |
| `0` | Input was evaluated; this also covers `WARN`, `DELEGATE`, `NO_REFERENCE`, and `STOP` |
| `2` | JSON or the input model is invalid; error code `INPUT_SCHEMA_INVALID` |
| `3` | The file could not be read or decoded as UTF-8; error code `INPUT_FILE_ERROR` |

CLI usage errors, such as omitting a required subcommand, are also reported by
`argparse` with exit code `2` and a usage message.

## Neutral reference case

The [weather example](../examples/weather-input-0.2.json) describes two
divergent public forecasts, separate internal confidence and external evidence,
two hypotheses, fixed termination bounds, and a reversible action across two
time horizons. Its expected process result is `PASS`.

This status does not predict whether it will rain. It shows only that the
declared process description satisfies the implemented rules while retaining
its residual uncertainty.

Two additional [loop-collapse fixtures](TRANSFER_CASE_LOOP_COLLAPSE.en.md)
represent a non-clinical negative case. The self-assessment correctly produces
`DELEGATE`; the separate externally documented mechanics case produces `STOP`
while retaining every triggered signal in its rule trace.

The additional
[coincidence interpretation](TRANSFER_CASE_COINCIDENCE_INTERPRETATION.en.md)
keeps personal salience separate from confidence and external evidence for a
causal claim. Its unquantified calibration values create no false precision;
the explicitly ambiguous reference frame correctly produces `WARN`.

The downstream
[reflected-desire transfer case](TRANSFER_CASE_REFLECTED_DESIRE.en.md) tests
whether an external cue, a perceived collective preference, deficit
attribution, and personal desire silently collapse into one inference. The
neutral executable fixture leaves the source of the spontaneous impulse open
and therefore also produces `WARN`.

The additional
[Source Echo and Reference-Frame Drift transfer case](TRANSFER_CASE_SOURCE_ECHO.en.md)
separates the number of texts from the number of independent evidence roots for
one atomic target claim. The fixture therefore records only one synthetic
primary observation as an evidence source and retains claim equivalence,
derivation edges, and semantic drift as residual uncertainty. The current
contract does not infer these features; the `WARN` comes from the declared
ambiguous reference frame.

## Public scenario matrix

| Input | Focus | Leading rule trace | Result |
| --- | --- | --- | --- |
| [Weather](../examples/weather-input-0.2.json) | neutral reference process | no triggered rule | `PASS` |
| [Coincidence](../examples/coincidence-interpretation-input-0.2.json) | keep meaning and causality separate | P1 · `REFERENCE_FRAME_AMBIGUOUS` | `WARN` |
| [Reflected desire](../examples/reflected-desire-input-0.2.json) | keep norm, deficit, and personal desire separate | P1 · `REFERENCE_FRAME_AMBIGUOUS` | `WARN` |
| [Source Echo](../examples/source-echo-input-0.2.json) | keep texts, claims, and evidence roots separate | P1 · `REFERENCE_FRAME_AMBIGUOUS` | `WARN` |
| [Loop self-assessment](../examples/loop-collapse-self-input-0.2.json) | competence gate | A1 · `COMPETENCE_INSUFFICIENT` | `DELEGATE` |
| [Loop mechanics](../examples/loop-collapse-external-input-0.2.json) | termination and reflexivity bounds | A3/P3 · reached bounds | `STOP` |

The `NO_REFERENCE` path is covered by unit tests but does not yet have a
complete public fixture.

## Verification and limitations

The interface is covered by 63 automated tests, including roundtrips, invalid
and duplicate JSON fields, precise error paths, cross-references, standard
input, compact output, schema output, and CLI exit codes.

The CLI:

- does not verify facts or sources outside the supplied input,
- does not authorize an action,
- is not a safety, medical, or diagnostic system,
- does not currently localize the English result rationales,
- does not change the frozen RPF specifications.

The next planned technical step is executable transition logic for the RPF
state machine. Compatibility rules for later pre-release schemas remain a
separate open task.
