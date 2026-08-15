# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import unittest
from pathlib import Path

from rpf_validator import (
    ProcessStatus,
    ReasonCode,
    RuleId,
    RuleStatus,
    evaluate,
    load_input,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "wave-tank-no-reference-input-0.2.json"


def rule(result, rule_id: RuleId):
    return next(item for item in result.rule_results if item.rule_id is rule_id)


class WaveTankNoReferenceExampleTests(unittest.TestCase):
    def test_undefined_display_frames_return_no_reference(self) -> None:
        result = evaluate(load_input(FIXTURE))

        self.assertEqual(result.overall_status, ProcessStatus.NO_REFERENCE)
        self.assertEqual(rule(result, RuleId.A1).status, RuleStatus.SATISFIED)
        self.assertEqual(rule(result, RuleId.A2).status, RuleStatus.SATISFIED)
        self.assertEqual(rule(result, RuleId.A3).status, RuleStatus.SATISFIED)
        self.assertEqual(rule(result, RuleId.A4).status, RuleStatus.SATISFIED)
        self.assertEqual(rule(result, RuleId.P1).status, RuleStatus.TRIGGERED)
        self.assertEqual(
            rule(result, RuleId.P1).reason_codes,
            (ReasonCode.REFERENCE_FRAME_MISSING,),
        )
        self.assertEqual(rule(result, RuleId.P2).status, RuleStatus.SATISFIED)
        self.assertEqual(
            rule(result, RuleId.P3).status,
            RuleStatus.NOT_APPLICABLE,
        )
        self.assertEqual(rule(result, RuleId.P4).status, RuleStatus.SATISFIED)
        self.assertEqual(
            result.next_step,
            "Establish a traceable reference frame before revising the model "
            "or acting on the conflict.",
        )


if __name__ == "__main__":
    unittest.main()
