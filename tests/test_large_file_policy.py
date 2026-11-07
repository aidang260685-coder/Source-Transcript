# -*- coding: utf-8 -*-
"""
Test Large File Policy:
Đảm bảo không có bất kỳ file nào vượt quá 45 MB được commit/theo dõi trong kho Git.
File dung lượng lớn chỉ được phép lưu ở local.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from check_large_files import check_staged_or_tracked_files

def test_no_large_files_in_git():
    ok = check_staged_or_tracked_files()
    assert ok is True, "Phát hiện file dung lượng lớn (> 45 MB) trong Git! File lớn chỉ lưu ở local."
