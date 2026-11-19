#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KTT Unified Cyber Security & SAST Audit Runner
Thuộc bộ công cụ Skill: cyber-security-expert (Harness Edition)

Tự động hóa 6 chốt chặn an ninh mạng (Security Gates):
  Gate 1: Internal SAST & Hardcode Scanner (scan_source.py)
  Gate 2: Git Secret Leak Scanner (gitleaks)
  Gate 3: Python AST Vulnerability Scanner (bandit)
  Gate 4: Python Dependency CVE Vulnerability Audit (pip-audit)
  Gate 5: Large File & Repository Data Guard (check_large_files.py)
  Gate 6: Security Compliance Unit & Regression Suite (test_security_compliance.py)
"""
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SKILL_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = Path(__file__).resolve().parents[4]
PYTHON_EXE = sys.executable


def find_executable(name: str) -> str:
    """Tìm binary thực thi an toàn trong PATH hoặc thư mục .venv."""
    venv_bin = ROOT_DIR / ".venv" / "Scripts" / f"{name}.exe"
    if venv_bin.exists():
        return str(venv_bin)
    system_path = shutil.which(name)
    if system_path:
        return system_path
    return ""


def run_gate(name: str, cmd: List[str]) -> Dict[str, Any]:
    """Thực thi một cổng kiểm tra an ninh bằng danh sách đối số an toàn (shell=False)."""
    print(f"\n▶ Đang kiểm tra {name}...")
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            shell=False,
            timeout=120
        )
        passed = (proc.returncode == 0)
        return {
            "name": name,
            "cmd": " ".join(cmd),
            "passed": passed,
            "returncode": proc.returncode,
            "output": proc.stdout.strip()
        }
    except Exception as e:
        return {
            "name": name,
            "cmd": " ".join(cmd),
            "passed": False,
            "returncode": -1,
            "output": f"Lỗi thực thi: {str(e)}"
        }


def main():
    print("=" * 72)
    print("🛡️  KTT UNIFIED CYBER SECURITY & SAST AUDIT SUITE")
    print(f"📁 Workspace: {ROOT_DIR}")
    print(f"🔧 Python: {PYTHON_EXE}")
    print("=" * 72)

    results = []

    # 1. Gate 1: Internal Codebase Scanner
    scan_source_script = ROOT_DIR / "tools" / "scan_source.py"
    if scan_source_script.exists():
        res1 = run_gate("Gate 1: Internal SAST & Hardcode (scan_source.py)", [PYTHON_EXE, str(scan_source_script)])
        results.append(res1)
    else:
        results.append({"name": "Gate 1: Internal SAST", "passed": False, "output": "Không tìm thấy tools/scan_source.py"})

    # 2. Gate 2: Gitleaks Secret Scanner
    gitleaks_bin = find_executable("gitleaks")
    if gitleaks_bin:
        res2 = run_gate("Gate 2: Git Secret Leak Scanner (gitleaks)", [gitleaks_bin, "detect", "--source", ".", "--no-banner"])
        results.append(res2)
    else:
        results.append({"name": "Gate 2: Gitleaks Secret Scanner", "passed": False, "output": "gitleaks chưa được cài đặt trong hệ thống."})

    # 3. Gate 3: Bandit Python SAST
    bandit_bin = find_executable("bandit")
    if bandit_bin:
        res3 = run_gate("Gate 3: Python SAST Scanner (bandit)", [bandit_bin, "-r", "tools", "harness", "-s", "B101,B404,B603,B607"])
        results.append(res3)
    else:
        results.append({"name": "Gate 3: Bandit SAST", "passed": False, "output": "bandit chưa được cài đặt."})

    # 4. Gate 4: Dependency CVEs Audit
    pip_audit_bin = find_executable("pip-audit")
    if pip_audit_bin:
        res4 = run_gate("Gate 4: Dependency Vulnerability Audit (pip-audit)", [pip_audit_bin])
        results.append(res4)
    else:
        results.append({"name": "Gate 4: pip-audit", "passed": False, "output": "pip-audit chưa được cài đặt."})

    # 5. Gate 5: Large File & Policy Guard
    large_file_script = ROOT_DIR / "tools" / "check_large_files.py"
    if large_file_script.exists():
        res5 = run_gate("Gate 5: Large File Policy Guard (< 45 MB)", [PYTHON_EXE, str(large_file_script)])
        results.append(res5)
    else:
        results.append({"name": "Gate 5: Large File Guard", "passed": False, "output": "Không tìm thấy tools/check_large_files.py"})

    # 6. Gate 6: Security Compliance Pytest Suite
    pytest_bin = find_executable("pytest")
    test_sec_file = ROOT_DIR / "tests" / "test_security_compliance.py"
    if pytest_bin and test_sec_file.exists():
        res6 = run_gate("Gate 6: Automated Security Compliance Tests (pytest)", [pytest_bin, str(test_sec_file), "-q"])
        results.append(res6)

    # Hiển thị kết quả tổng hợp
    print("\n" + "=" * 72)
    print("📊 BẢNG TỔNG KẾT KẾT QUẢ CÁC CỔNG AN NINH MẠNG (CYBER SECURITY AUDIT)")
    print("=" * 72)
    all_passed = True
    for res in results:
        status_icon = "✅ ĐẠT (PASS)" if res["passed"] else "❌ KHÔNG ĐẠT (FAIL)"
        print(f"  {status_icon} | {res['name']}")
        if not res["passed"]:
            all_passed = False
            print(f"    Chi tiết lỗi: {res['output'][:200]}...")

    print("=" * 72)
    if all_passed:
        print("🏆 PHÁN QUYẾT BẢO MẬT: ĐẠT TIÊU CHUẨN AN TOÀN (RELEASE GATE: GO)")
        print("   Tất cả các chốt chặn tĩnh, secret leak và dependency audit đều đã vượt qua!")
        sys.exit(0)
    else:
        print("🚨 PHÁN QUYẾT BẢO MẬT: CÓ CẢNH BÁO / LỖI (RELEASE GATE: NO-GO)")
        print("   Vui lòng rà soát lại các mục thất bại ở trên trước khi tiến hành release.")
        sys.exit(1)


if __name__ == "__main__":
    main()
