# Non-clinical Transfer Case: Loop Collapse

**Languages:** [Deutsch](TRANSFER_CASE_LOOP_COLLAPSE.md) · English

## Status and purpose

This transfer case examines a **synthetic** cognitive loop as a negative case
for the experimental validator. It is non-normative, empirically unvalidated,
and does not extend the frozen RPF specifications.

The analogy was prompted by a scenario in which an impaired decision process
confuses an internal alarm signal with an external threat and considers another
state-changing input. The executable fixtures deliberately express this in
abstract, non-clinical terms.

They specifically do not establish:

- whether a real environment is safe or dangerous,
- what causes a real physical or psychological signal,
- whether a person is competent, intoxicated, or ill,
- which medical, psychological, or practical action is correct.

## Why two fixtures are required

A1 is a real competence gate in the current validator. Insufficient competence
produces `DELEGATE`, after which later rules are deliberately recorded as
`NOT_EVALUATED`. One run therefore cannot claim both insufficient A1 competence
and evaluated A2/A3 violations.

The case is consequently split into two explicit evaluation fixtures:

| Fixture | Evaluated process | Expected result |
| --- | --- | --- |
| [Self-assessment](../examples/loop-collapse-self-input-0.2.json) | The synthetic subject evaluates its own explicitly impaired process. | `DELEGATE` |
| [Externally documented mechanics case](../examples/loop-collapse-external-input-0.2.json) | An external test author supplies a process record in which the evaluated process is declared task-competent. | `STOP` |

The role distinction currently resides in `problem_domain`, rationale, and
provenance. The input contract does not yet have dedicated fields for an
assessment subject and an assessment authority.

## Self-assessment and the A1 gate

The self-assessment fixture declares `competence.status` as `INSUFFICIENT`.
The validator therefore emits:

```text
overall_status = DELEGATE
A1 = TRIGGERED · COMPETENCE_INSUFFICIENT
A2–A4, P1–P4 = NOT_EVALUATED
```

The notable calibration and termination values remain present as input but are
not evaluated as domain rules. This is the intended protective effect of the
competence gate.

## Externally documented mechanics case and retained signals

The second fixture does not substitute an observer's competence for the
competence of the evaluated process. As a separate mechanics test, it assumes
that the evaluated process is task-competent while currently exhibiting strong
calibration divergence and exceeded bounds. The external test author supplies
only the record and its provenance.

This test precondition assumes no medical or factual authority. With
comparability declared for `C_i = 0.98`, `C_e = 0.02`, and an experimental
divergence threshold of `0.4`, the result is:

```text
overall_status = STOP
A1 = SATISFIED
A2 = SIGNAL    · CONFIDENCE_EVIDENCE_DIVERGENCE
A3 = TRIGGERED · INFORMATION_GAIN_LIMIT
               · ITERATION_LIMIT
               · TIME_LIMIT
               · RESOURCE_LIMIT
A4 = SATISFIED
P1 = SATISFIED
P2 = SATISFIED
P3 = TRIGGERED · REFLEXIVE_DEPTH_LIMIT
P4 = SIGNAL    · IRREVERSIBLE_ACTION_UNJUSTIFIED
```

The aggregate `STOP` does not erase lower-priority signals. The complete rule
trace still shows calibration divergence, reached termination bounds, and an
unjustified irreversible selection in the supplied process.

The fixture is therefore a mechanics demonstration, not a claim that a
particular impaired person is in fact competent. The current contract cannot
yet formally enforce the role and source of each individual declaration.

## Translation into the existing 0.2 contract

| Original idea | Executable representation |
| --- | --- |
| numeric competence `0.15` | `INSUFFICIENT` enum; the validator has no canonical competence threshold |
| `SUBJECTIVE_EMOTIONAL` | existing `SUBJECTIVE_PERCEPTION` and `OBJECTIVE_MEASUREMENT` classes |
| residual uncertainty `0.85` | structured uncertainty items without an invented aggregate score |
| loop depth `412 > 50` | A3 `iteration/max_iterations` and P3 `recursion_depth/max_recursion_depth` |
| `robustness_score` | not implemented; P4 checks selection, reversibility, rationale, and declared constraints |
| `NON_ROBUST_ACTION_SELECTION` | existing `IRREVERSIBLE_ACTION_UNJUSTIFIED` for this fixture |

The alternative `pause-and-delegate` action is an abstract process option. It
is not breathing, vagus-nerve, addiction, or therapy advice.

## Execution

After local installation:

```bash
rpf validate examples/loop-collapse-self-input-0.2.json
rpf validate examples/loop-collapse-external-input-0.2.json
```

Both commands technically exit with code `0`, because `DELEGATE` and `STOP`
are valid validator results rather than input failures.

## Open architecture question

The case exposes a real modeling question: a future contract could explicitly
separate assessment subject, assessment authority, and the provenance of their
respective declarations. Before such a schema change, the project must clarify:

1. Whose competence is being assessed?
2. Who supplies `C_i`, `C_e`, observation, and provenance?
3. When is an external source genuinely independent?
4. How do separate dimensions remain protected from being collapsed into an
   apparently objective person or risk score?

This question is recorded as a possible later schema development. The current
fixtures change neither the 0.2 data contract nor the evaluator rules.
