# -*- coding: utf-8 -*-
"""
Test Automated Source Code Security Scan (SAST & Anti-Hardcode Gate)
Chạy bộ quét bảo mật tĩnh scan_source.py:
- Kiểm tra 0 Secrets / Tokens / Passwords
- Kiểm tra 0 Hardcoded Absolute Paths
- Kiểm tra 0 Unsafe Code / Command Injections
- Đảm bảo 100% UTF-8 & Unicode NFC
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from scan_source import run_full_security_scan

def test_automated_source_security_and_no_hardcode():
    report = run_full_security_scan()
    assert report["passed"] is True, f"Phát hiện lỗi bảo mật hoặc hardcode trong mã nguồn: {report['issues']}"
    assert report["critical"] == 0, "Không được phép có lỗi mức CRITICAL"
    assert report["high"] == 0, "Không được phép có lỗi mức HIGH"
