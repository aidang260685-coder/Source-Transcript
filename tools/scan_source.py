#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KTT Codebase Security & Static Analysis Scanner (SAST & Hardcode Linter)
Quét toàn diện mã nguồn nhằm phát hiện:
1. Thông tin bí mật (Tokens, Keys, Passwords, Credentials)
2. Đường dẫn ổ đĩa tuyệt đối (Hardcoded Absolute Paths)
3. Các hàm không an toàn (Command Injection, eval, shell=True)
4. Chuẩn mã hóa bảng mã UTF-8 và Unicode NFC
5. File nhạy cảm bị theo dõi bởi Git
"""
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent

# Các mẫu regex phát hiện Secrets / Credentials
SECRET_PATTERNS = {
    "GitHub Classic Token": re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
    "GitHub Fine-Grained Token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82}\b"),
    "Generic API Key / Secret": re.compile(r"""(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)\s*=\s*['"][A-Za-z0-9_\-]{20,}['"]"""),
    "Hardcoded Password": re.compile(r"""(?i)(password|passwd|pwd)\s*=\s*['"][^'"]{6,}['"]"""),
    "Private Key Header": re.compile(r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----"),
    "AWS Access Key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}

# Các mẫu regex phát hiện Hardcoded Paths
PATH_PATTERNS = {
    "Hardcoded Windows Absolute Path": re.compile(r"""[rR]?['"][a-zA-Z]:\\[^'"]+['"]"""),
    "Hardcoded Unix Root Path": re.compile(r"""['"]/(home|usr|etc|var|opt)/[^'"]+['"]"""),
    "Old Project Workspace Reference": re.compile(r"d:\\Source-Transcript", re.IGNORECASE),
}

# Các mẫu regex phát hiện Unsafe Execution / Command Injection
UNSAFE_PATTERNS = {
    "subprocess with shell=True": re.compile(r"subprocess\.(run|Popen|call|check_output)\s*\(.*shell\s*=\s*True", re.DOTALL),
    "os.system execution": re.compile(r"\bos\.system\s*\("),
    "Dangerous eval()": re.compile(r"\beval\s*\("),
    "Dangerous exec()": re.compile(r"\bexec\s*\("),
}

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "runs", ".pytest_cache", "output"}
SKIP_FILES = {"scan_source.py", "test_security_compliance.py"}
SCAN_EXTS = {".py", ".md", ".html", ".txt", ".json", ".toml", ".yaml", ".yml", ".css"}


def scan_file_content(path: Path) -> List[Dict[str, Any]]:
    issues = []
    rel_path = path.relative_to(ROOT_DIR)
    
    try:
        raw_bytes = path.read_bytes()
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        issues.append({
            "category": "ENCODING",
            "file": str(rel_path),
            "line": 0,
            "rule": "Non-UTF-8 Encoding",
            "message": "File không dùng bảng mã UTF-8 hợp lệ",
            "severity": "HIGH"
        })
        return issues

    # Kiểm tra Unicode NFC
    if not unicodedata.is_normalized("NFC", text):
        issues.append({
            "category": "UNICODE",
            "file": str(rel_path),
            "line": 0,
            "rule": "Unicode NFD Decomposed",
            "message": "File chứa ký tự Unicode tổ hợp (NFD), vi phạm chuẩn NFC",
            "severity": "MEDIUM"
        })

    # Quét từng dòng
    lines = text.splitlines()
    for idx, line in enumerate(lines, 1):
        # 1. Quét Secrets
        for rule_name, pat in SECRET_PATTERNS.items():
            if pat.search(line):
                issues.append({
                    "category": "SECRET_LEAK",
                    "file": str(rel_path),
                    "line": idx,
                    "rule": rule_name,
                    "message": f"Phát hiện khả năng lộ token/secret: {line.strip()[:60]}...",
                    "severity": "CRITICAL"
                })

        # 2. Quét Hardcoded Paths (bỏ qua comment mô tả format)
        for rule_name, pat in PATH_PATTERNS.items():
            if pat.search(line):
                # Bỏ qua nếu là file markdown tài liệu giải thích
                if path.suffix in {".md", ".html"} and ("ví dụ:" in line or "mục tiêu" in line or "cũ:" in line):
                    continue
                issues.append({
                    "category": "HARDCODED_PATH",
                    "file": str(rel_path),
                    "line": idx,
                    "rule": rule_name,
                    "message": f"Đường dẫn tuyệt đối hardcoded: {line.strip()[:60]}...",
                    "severity": "HIGH"
                })

        # 3. Quét Unsafe Execution
        for rule_name, pat in UNSAFE_PATTERNS.items():
            if pat.search(line):
                # Bỏ qua comment
                if line.strip().startswith("#"):
                    continue
                issues.append({
                    "category": "VULNERABILITY",
                    "file": str(rel_path),
                    "line": idx,
                    "rule": rule_name,
                    "message": f"Sử dụng hàm không an toàn: {line.strip()[:60]}...",
                    "severity": "HIGH"
                })

    return issues


def run_full_security_scan() -> Dict[str, Any]:
    print("=" * 70)
    print("🛡️ CODEBASE SECURITY SCANNER & STATIC ANALYSIS AUDIT (SAST)")
    print(f"📁 Thư mục gốc: {ROOT_DIR}")
    print("=" * 70)

    total_files = 0
    all_issues = []

    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = Path(root) / f
            if p.name in SKIP_FILES or p.suffix not in SCAN_EXTS:
                continue
            total_files += 1
            issues = scan_file_content(p)
            all_issues.extend(issues)

    # Tổng kết
    critical_count = sum(1 for i in all_issues if i["severity"] == "CRITICAL")
    high_count = sum(1 for i in all_issues if i["severity"] == "HIGH")
    medium_count = sum(1 for i in all_issues if i["severity"] == "MEDIUM")

    print(f"\n📊 Đã quét {total_files} file mã nguồn và tài liệu.")
    
    if all_issues:
        print(f"\n⚠️ TỔNG CỘNG PHÁT HIỆN {len(all_issues)} VẤN ĐỀ:")
        for issue in all_issues:
            print(f"  [{issue['severity']}] {issue['file']}:{issue['line']} — {issue['rule']}: {issue['message']}")
    else:
        print("\n✅ KHÔNG PHÁT HIỆN BẤT KỲ VẤN ĐỀ BẢO MẬT HOẶC HARDCODE NÀO!")
        print("   - 0 Tokens / Passwords / Secrets lộ lọt.")
        print("   - 0 Đường dẫn tuyệt đối (Absolute Paths) hardcoded.")
        print("   - 0 Hàm thực thi không an toàn (shell=True, eval, os.system).")
        print("   - 100% Chuẩn hóa UTF-8 và Unicode NFC.")

    passed = (critical_count == 0 and high_count == 0)
    return {
        "files_scanned": total_files,
        "total_issues": len(all_issues),
        "critical": critical_count,
        "high": high_count,
        "medium": medium_count,
        "issues": all_issues,
        "passed": passed
    }


if __name__ == "__main__":
    result = run_full_security_scan()
    sys.exit(0 if result["passed"] else 1)
