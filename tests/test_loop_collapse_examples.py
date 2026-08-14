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
EXTERNAL_FIXTURE = ROOT / "examples" / "loop-collapse-external-input-0.2.json"
SELF_FIXTURE = ROOT / "examples" / "loop-collapse-self-input-0.2.json"


def rule(result, rule_id: RuleId):
    return next(item for item in result.rule_results if item.rule_id is rule_id)


class LoopCollapseExampleTests(unittest.TestCase):
    def test_compromised_self_assessment_delegates_at_a1(self) -> None:
        result = evaluate(load_input(SELF_FIXTURE))

        self.assertEqual(result.overall_status, ProcessStatus.DELEGATE)
        self.assertEqual(rule(result, RuleId.A1).status, RuleStatus.TRIGGERED)
        self.assertEqual(
            rule(result, RuleId.A1).reason_codes,
            (ReasonCode.COMPETENCE_INSUFFICIENT,),
        )
        self.assertTrue(
            all(
                item.status is RuleStatus.NOT_EVALUATED
                for item in result.rule_results[1:]
            )
        )

    def test_external_mechanics_case_retains_all_loop_signals(self) -> None:
        result = evaluate(load_input(EXTERNAL_FIXTURE))

        self.assertEqual(result.overall_status, ProcessStatus.STOP)
        self.assertEqual(rule(result, RuleId.A1).status, RuleStatus.SATISFIED)
        self.assertEqual(rule(result, RuleId.A2).status, RuleStatus.SIGNAL)
        self.assertEqual(
            rule(result, RuleId.A2).reason_codes,
            (ReasonCode.CONFIDENCE_EVIDENCE_DIVERGENCE,),
        )
        self.assertEqual(
            rule(result, RuleId.A3).reason_codes,
            (
                ReasonCode.INFORMATION_GAIN_LIMIT,
                ReasonCode.ITERATION_LIMIT,
                ReasonCode.TIME_LIMIT,
                ReasonCode.RESOURCE_LIMIT,
            ),
        )
        self.assertEqual(rule(result, RuleId.A4).status, RuleStatus.SATISFIED)
        self.assertEqual(
            rule(result, RuleId.P3).reason_codes,
            (ReasonCode.REFLEXIVE_DEPTH_LIMIT,),
        )
        self.assertEqual(
            rule(result, RuleId.P4).reason_codes,
            (ReasonCode.IRREVERSIBLE_ACTION_UNJUSTIFIED,),
        )


if __name__ == "__main__":
    unittest.main()
