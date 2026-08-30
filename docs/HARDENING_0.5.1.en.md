# RPF Boundary Hardening 0.5.1

**Languages:** [Deutsch](HARDENING_0.5.1.md) · English

| Field | Value |
| --- | --- |
| Package version | `0.5.1.dev0` |
| Implementation status | non-normative experimental hardening update |
| Input contract | unchanged `rpf-validator-input-0.2` |
| Result contract | unchanged `rpf-validator-result-0.2` |
| Proposal contract | unchanged `rpf-classification-proposal-0.1` |
| State-machine trace | unchanged `rpf-state-machine-trace-0.1` |
| Change to the frozen RPF core | none |

## Purpose

Version 0.5.1 closes four reproducible boundary defects found during a review of
the published 0.5 tree. It does not add a provider, adapter, language model, or
new evaluation rule. Valid public fixtures keep their previous results and
traces.

## Hardened boundaries

### Result consistency before routing

`run_state_machine` now checks the routing-relevant consistency of every
`ValidatorResult` before selecting a transition plan. The result must contain
exactly one entry for A1–A4 and P1–P4, use a status admitted for each rule,
respect the A1 competence gate, and expose the aggregate status implied by the
complete rule trace and the published priority order.

A contradictory direct API object such as `overall_status=PASS` with triggered
A3 is rejected with `INCONSISTENT_RESULT_STATUS`. This check does not re-run the
axioms and does not prove that rationales, reason codes, or source statements
are true.

### Normalized JSON decoder failures

Both public JSON parsers use one shared strict decoder. Duplicate keys,
non-standard constants, syntax failures, and decoder-level numeric range
failures now become `InputValidationError`. The CLI therefore returns the
documented machine-readable `INPUT_SCHEMA_INVALID` response and exit code `2`
instead of leaking a Python traceback for an oversized integer token.

### Canonical textual media type

The Python proposal parser now enforces the same `media_type` form already
published by the JSON Schema: `text/<subtype>` with a lowercase `text` prefix,
one non-empty subtype, no whitespace, and no additional slash. Values such as
`text/`, `TEXT/PLAIN`, and `text/plain/extra` are rejected consistently.

### UTF-8-aligned evidence fragments

Every evidence-fragment start and exclusive end offset must now fall on a
UTF-8 code-point boundary, even when the optional `excerpt` is absent. A digest
of a byte range that cuts through a multi-byte character no longer makes that
range acceptable.

## Compatibility

No public data-contract identifier changed. The update intentionally rejects
objects that were already invalid according to the published schema or
evaluator semantics but slipped through one Python boundary. Consumers relying
on those malformed objects must correct them; schema-valid public examples need
no migration.

## Verification and limit

The full suite now contains 114 automated tests. New regression cases cover
contradictory and incomplete result traces, the A1 gate, oversized JSON
integers through both parsers and the CLI, parser/schema media-type parity, and
misaligned UTF-8 fragments without excerpts.

This is a targeted hardening update, not a formal security proof or penetration
test.
