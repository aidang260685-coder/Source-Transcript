# -*- coding: utf-8 -*-
"""
Test Harness Architecture:
1. Audits 5 phases: GATHER -> CURATE -> ACT -> VERIFY -> RETRY.
2. Checks guards: trace/logging, cost bounds, test, publication gate.
3. Ensures verdict is COMPLETE.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "doc" / "Skill" / "harness-engineering" / "scripts"))

from audit_harness import scan

def test_harness_five_phases_complete():
    files, hits, guards = scan(str(ROOT))
    missing = [p for p, f in hits.items() if not f]
    weak = [g for g, ok in guards.items() if not ok]
    
    assert len(missing) == 0, f"Harness thiếu các pha sau: {missing}"
    assert len(weak) == 0, f"Harness thiếu các chốt chặn sau: {weak}"

def test_harness_runner_exists():
    runner = ROOT / "harness" / "run_ktt_harness.py"
    assert runner.exists(), "run_ktt_harness.py phải tồn tại"
