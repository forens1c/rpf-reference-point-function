# Non-clinical Transfer Case: Context Feedback and Reflected Desire

**Languages:** [Deutsch](TRANSFER_CASE_REFLECTED_DESIRE.md) · English

## Status and purpose

This document extends the
[coincidence transfer case](TRANSFER_CASE_COINCIDENCE_INTERPRETATION.en.md)
with a downstream interpretation question: how can a salient external cue be
translated through perceived social preference and self-comparison into a
personal deficit and, finally, an attributed personal desire?

**Reflected desire attribution** is a non-clinical working label, not an
established psychological term. It denotes a possible inference chain in which
a socially desirable target is reflected back as something personally missing.

The case is non-normative, empirically unvalidated, and does not extend the
frozen RPF specifications. It evaluates no real person and does not decide
whether a concrete desire is authentic, borrowed, right, or wrong.

## The combined chain

```text
salient external cue
→ increased attention or coincidence experience
→ perceived collective preference
→ comparison with one's own state
→ deficit attribution
→ attributed personal desire
→ action impulse
```

Every arrow is a separate, fallible inference. The visibility of something
establishes neither its general popularity nor a personal deficit or need.

The shortest RPF form is:

```text
perceived
≠ directed at me
≠ socially wanted
≠ missing from me
≠ wanted by me
```

## Two deliberately different levels of consequence

The examples form a contrast pair. They are not equated in content; their
formal inference structure is similar, while their meaning and action
consequences explicitly are not.

| Dimension | Lower stakes: large television | Higher stakes: social life path |
| --- | --- | --- |
| external cue | a friend displays a new purchase | families and children become more salient in everyday perception |
| possible norm inference | “Other people own and value this.” | “Many people expect or want this life path.” |
| possible deficit inference | “My device is now inadequate.” | “My own life path is incomplete.” |
| possible desire inference | “Therefore I also need a larger television.” | “Therefore I must want this life path as well.” |
| consequence | bounded purchase, comparatively easy to correct | identity-related, long-term, and not readily reversible |
| RPF weight | a short pause and needs check may be enough | longer horizons, personal values, and strong reversibility requirements become central |

The second example is intentionally more socially consequential. It makes no
claim about the author or any particular person and does not equate children
with a consumer product. It shows that a similar fallible inference form can
have radically different consequences across different domains.

Even a genuinely noticed glance from another person initially remains an
observation. Its intent or meaning is open without additional evidence.
Visible families likewise do not establish what “the majority” wants;
**perceived collective preference** is therefore the more precise term.

## Connection to the coincidence case

The coincidence case and reflected desire attribution examine different
sections of the same process:

1. **Coincidence:** Why does an activated topic suddenly appear repeatedly in
   perception?
2. **Meaning:** What personal meaning may the observation retain without
   thereby proving external causality?
3. **Reflection:** Is a social norm constructed from perceived frequency?
4. **Deficit:** Is that norm interpreted as a deficiency in one's own state?
5. **Desire:** Is the deficiency then attributed back as a stable personal
   desire?

An active topic can guide attention toward matching cues. This does not make
the observation unreal, but it establishes neither an intentional external
message nor that the resulting impulse is a stable personal value.

## Method mini-case: “word missing”

A handwritten project note contained the explicit annotation `Wort fehlt`
(“word missing”). During transcription, the active context of synchronicity
and consciousness led that location to be tentatively read as `not self`. The
hypothetical completion then entered an interpretation before the author
corrected the source.

This real mini-case shows the same feedback form in compact form:

```text
ambiguous source
→ contextually plausible completion
→ completion appears to be source content
→ interpretation builds on its own completion
```

The correct RPF response keeps observation, hypothesis, and confirmation
separate:

| Layer | Content |
| --- | --- |
| source | `Wort fehlt` (“word missing”) |
| hypothesis | an unclear or absent expression |
| invalid shortcut | treating a plausible completion as read source text |
| robust action | mark uncertainty and ask the author |

The final request for confirmation functioned as a safeguard, but the detailed
interpretation of the completion still occurred too early.

## Executable fixture

The [reflected-desire fixture](../examples/reflected-desire-input-0.2.json)
uses the neutral television case. It does not numerically model the higher
consequence requirements of the second example; those remain a documented
transfer boundary.

The fixture separates:

- the observed purchase and subsequently recorded impulse,
- perceived popularity and actual group preference,
- a momentary sense of deficit and stable personal preference,
- desire content and confidence in a claim about its origin.

`C_i` and `C_e` remain `null`: an impulse is not a confidence score, and the
visibility of a purchase is not evidence of a personal need or a population
preference. Four hypotheses preserve pre-existing preference, comparison
effect, attention amplification, and a mixed origin.

The selected `defer-and-test-persistence` action does not suppress the desire.
It only prevents the chain “visible → socially wanted → missing from me →
needed by me” from becoming an automatic decision. Three time horizons cover
the immediate impulse, a pause, and long-term use.

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

The `WARN` originates in P1: `SUBJECTIVE_PERCEPTION`,
`INDIVIDUAL_PREFERENCE`, and `CULTURAL_EVALUATION` have not been reduced to one
unambiguous source of the impulse. The result declares the desire neither true
nor false.

## Execution

After local installation:

```bash
rpf validate examples/reflected-desire-input-0.2.json
```

The command exits with code `0`, because `WARN` is a valid process result
rather than an input failure.

## Research context and boundaries

The literature provides points of contact for individual links, not for the
entire proposed chain:

- Festinger's theory describes social comparison as a source of
  self-evaluation, particularly when objective standards are absent.
- In two experiments, Vogt and colleagues found that activated goals can
  orient attention toward goal-relevant cues.
- In consumption experiments, Wadhwa, Shiv, and Nowlis found that
  high-incentive cues can activate broader reward seeking.

Sources:

- [Leon Festinger: *A Theory of Social Comparison Processes*](https://doi.org/10.1177/001872675400700202)
- [Julia Vogt et al.: *The Automatic Orienting of Attention to Goal-Relevant Stimuli*](https://doi.org/10.1016/j.actpsy.2009.12.006)
- [Monica Wadhwa, Baba Shiv, and Stephen M. Nowlis: *A Bite to Whet the Reward Appetite*](https://doi.org/10.1509/jmkr.45.4.403)

The sources validate neither RPF nor the working label reflected desire
attribution. The fixture is not a psychological test, diagnostic model, or
instruction for a concrete life decision.

## Open architecture question

The existing 0.2 contract can represent the case through observation,
reference frame, hypotheses, residual uncertainty, and time horizons.
Dedicated fields such as `perceived_norm`, `deficit_inference`,
`cue_evoked_impulse`, or `preexisting_preference` are not introduced yet.
Multiple independent cases should first establish whether these distinctions
justify a later schema extension.
