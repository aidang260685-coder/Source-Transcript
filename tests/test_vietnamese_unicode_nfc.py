# -*- coding: utf-8 -*-
"""
Test Vietnamese & Unicode NFC Normalization:
Đảm bảo 100% các file mã nguồn, markdown, cấu hình dùng chuẩn UTF-8 và Unicode NFC (Form C).
"""
import os
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def test_all_text_files_are_nfc():
    skip_dirs = {".git", ".venv", "__pycache__", "runs", ".pytest_cache"}
    exts = {".py", ".md", ".html", ".txt", ".json", ".toml"}
    
    nfd_violations = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if any(f.endswith(ext) for ext in exts):
                p = Path(root) / f
                try:
                    content = p.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    nfd_violations.append(f"{p.relative_to(ROOT)}: Lỗi không phải UTF-8 hợp lệ")
                    continue
                
                # Kiểm tra xem có chứa ký tự tổ hợp (NFD) hay không
                if not unicodedata.is_normalized("NFC", content):
                    nfd_violations.append(f"{p.relative_to(ROOT)}: Chứa ký tự Unicode tổ hợp (NFD)")
    
    assert len(nfd_violations) == 0, f"Phát hiện file vi phạm chuẩn Unicode NFC: {nfd_violations}"
