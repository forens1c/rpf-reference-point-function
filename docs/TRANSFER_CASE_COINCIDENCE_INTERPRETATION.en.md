# Non-clinical Transfer Case: Coincidence Interpretation

**Languages:** [Deutsch](TRANSFER_CASE_COINCIDENCE_INTERPRETATION.md) · English

## Status and purpose

This transfer case examines a **synthetic** salient coincidence as a `WARN`
case for the experimental validator. It is non-normative, empirically
unvalidated, and does not extend the frozen RPF specifications.

The fixture declares only that an internally salient topic and an apparently
similar external event were noticed close together in time. It tests whether
the process keeps personal meaning, observed co-occurrence, and external
causality separate.

It explicitly does not determine:

- whether a real coincidence is random or causal,
- what personal meaning a real event has,
- whether thoughts caused an external event,
- whether a real person's perception or interpretation is appropriate.

The case is neither a psychological test nor a medical or diagnostic model.

## The essential separation

A coincidence may be subjectively meaningful. That significance is not
automatically a measurement of confidence in an external causal claim, nor is
it external evidence for that claim.

| Quantity | Meaning in the fixture | Representation |
| --- | --- | --- |
| subjective salience | why the observation appears personally relevant | text in the observation and reference frame; no score |
| internal confidence `C_i` | confidence in one precisely named causal claim | `null`, because the claim and scale are not sufficiently defined |
| external evidence `C_e` | strength of traceable external evidence for the same claim | `null`, because no such evidence is declared |
| event probability | frequency of a predefined event under a model | not repurposed as `C_e`; statistical context remains open |
| residual uncertainty | open causal, statistical, and frame questions | three structured uncertainty items |

In the current contract, `C_e` is not a substitute for an event probability.
A statistical interpretation would require at least a predefined event class,
an observation window, a count of opportunities or a base rate, and an
appropriate model. The fixture does not invent those inputs.

## Executable representation

The
[coincidence fixture](../examples/coincidence-interpretation-input-0.2.json)
declares three reference-frame classes that have not yet been collapsed:

- `SUBJECTIVE_PERCEPTION` for personal salience,
- `OBJECTIVE_MEASUREMENT` for the recorded temporal co-occurrence,
- `STATISTICAL_EXCEPTION` as an open statistical classification question.

The reference frame therefore deliberately remains `AMBIGUOUS`. No global
model revision is proposed; the revision scope remains `LOCAL`. Multiple
hypotheses are retained without assigning invented numerical weights.

The selected `defer-causal-conclusion` action is reversible: the observation
and its subjective meaning may remain recorded while an external causal claim
is suspended until methodologically defined new evidence becomes available.

## Expected rule trace

```text
overall_status = WARN
A1 = SATISFIED
A2 = SATISFIED
A3 = SATISFIED
A4 = SATISFIED
P1 = SIGNAL    · REFERENCE_FRAME_AMBIGUOUS
P2 = SATISFIED
P3 = NOT_APPLICABLE
P4 = SATISFIED
```

A2 is satisfied because internal confidence and external evidence remain
separate and explicitly unquantified with rationales. The validator neither
creates false precision nor compares subjective salience with external
evidence.

The `WARN` originates only from P1. It means that the reference frame required
for a causal interpretation remains ambiguous. It neither denies the
observation or its personal meaning nor confirms any open causal hypothesis.

## Downstream context feedback

A coincidence may feed more than a causal interpretation. Its perceived
frequency may also be translated into a social norm and then into a personal
deficit or desire. The separate transfer case
[context feedback and reflected desire](TRANSFER_CASE_REFLECTED_DESIRE.en.md)
examines this downstream inference chain through an executable neutral contrast
case.

## Execution

After local installation:

```bash
rpf validate examples/coincidence-interpretation-input-0.2.json
```

The command technically exits with code `0`, because `WARN` is a valid
validator result rather than an input failure.

## Historical term and methodological boundary

In 1952, C. G. Jung published a philosophical and psychological account of
meaningful coincidences under the term *synchronicity*, describing it as an
“acausal connecting principle.” The fixture deliberately retains a neutral
technical name. The historical term is context, not scientific confirmation
and not a validator assumption.

A statistical study of coincidences requires its own data collection, event
definition, and probability model. The validator does not perform that study;
it preserves the absent prerequisites as residual uncertainty.

Further context:

- [C. G. Jung: *Synchronicity: An Acausal Connecting Principle*](https://doi.org/10.2307/j.ctt7s94k.8)
- [Persi Diaconis and Frederick Mosteller: *Methods for Studying Coincidences*](https://doi.org/10.1080/01621459.1989.10478847)

The sources provide historical context and statistical study methods,
respectively. They validate neither RPF nor the synthetic fixture.
