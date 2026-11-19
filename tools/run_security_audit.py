#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KTT Security Audit Runner - Entry Point Wrapper
Trỏ trực tiếp tới bộ công cụ: doc/Skill/cyber-security-expert/scripts/run_security_audit.py
"""
import sys
import subprocess
from pathlib import Path

SCRIPT_TARGET = Path(__file__).resolve().parent.parent / "doc" / "Skill" / "cyber-security-expert" / "scripts" / "run_security_audit.py"

if __name__ == "__main__":
    if not SCRIPT_TARGET.exists():
        print(f"Lỗi: Không tìm thấy file script bảo mật tại {SCRIPT_TARGET}")
        sys.exit(1)

    result = subprocess.run([sys.executable, str(SCRIPT_TARGET), *sys.argv[1:]])
    sys.exit(result.returncode)
