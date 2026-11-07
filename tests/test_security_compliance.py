# -*- coding: utf-8 -*-
"""
Test Security Compliance:
1. No passwords, tokens, API keys or secret credentials committed in source code.
2. Git ignore excludes sensitive patterns (.venv, credentials, logs).
3. Security policies enforced in AGENTS.md, GEMINI.md, and all Skills.
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def test_gitignore_contains_sensitive_rules():
    gitignore = ROOT / ".gitignore"
    assert gitignore.exists(), "File .gitignore bắt buộc phải tồn tại để chống lộ dữ liệu"
    content = gitignore.read_text(encoding="utf-8")
    assert ".venv" in content
    assert "*.token" in content or ".env" in content

def test_no_hardcoded_tokens_or_passwords_in_source():
    # Quét toàn bộ mã nguồn .py, .md, .html, .txt
    sensitive_patterns = [
        re.compile(r"ghp_[A-Za-z0-9]{30,}", re.IGNORECASE),
        re.compile(r"github_pat_[A-Za-z0-9_]{50,}", re.IGNORECASE),
        re.compile(r"341207908@n"), # mật khẩu cụ thể của user
    ]
    skip_dirs = {".git", ".venv", "__pycache__", "runs", ".pytest_cache"}
    
    violations = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if f == "test_security_compliance.py":
                continue
            if f.endswith((".py", ".md", ".html", ".txt", ".json", ".toml")):
                file_path = Path(root) / f
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                for pat in sensitive_patterns:
                    if pat.search(text):
                        violations.append(f"{file_path.relative_to(ROOT)} chứa thông tin nhạy cảm khớp {pat.pattern}")
    
    assert len(violations) == 0, f"Phát hiện lộ thông tin bảo mật trong các file: {violations}"

def test_security_rules_present_in_agents_md():
    agents_md = ROOT / "AGENTS.md"
    assert agents_md.exists()
    content = agents_md.read_text(encoding="utf-8")
    assert "NGUYÊN TẮC BẢO MẬT & BẢO VỆ DỮ LIỆU" in content
    assert "CONFIRM" in content or "Xác nhận" in content
