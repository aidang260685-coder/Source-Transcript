# -*- coding: utf-8 -*-
"""
Test 6 Deterministic Verification Gates:
Kiểm chứng toàn diện 6 Gate kiểm định trên file output đã niêm phong VERIFIED.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))

from verify_strict import run_strict_audit

def test_six_deterministic_gates():
    passed = run_strict_audit()
    assert passed is True, "6 Deterministic Gates phải đạt 100% trước khi release!"
