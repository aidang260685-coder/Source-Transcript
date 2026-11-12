#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KTT Large File Guard (Pre-commit & CI Gate)
Kiểm tra kích thước của toàn bộ các file được chuẩn bị commit/push lên Git.
Quy định: File có dung lượng lớn (> 45 MB) TUYỆT ĐỐI KHÔNG đẩy lên Git, chỉ lưu tại local.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
MAX_SIZE_BYTES = 45 * 1024 * 1024  # 45 MB (Ngưỡng an toàn trước giới hạn 50MB warning / 100MB block của GitHub)


def get_git_binary() -> str:
    system_git = shutil.which("git")
    if system_git:
        return system_git
    prog_files = os.environ.get("ProgramFiles")
    if prog_files and (Path(prog_files) / "Git" / "cmd" / "git.exe").is_file():
        return str(Path(prog_files) / "Git" / "cmd" / "git.exe")
    return "git"


def check_staged_or_tracked_files() -> bool:
    print("=" * 70)
    print("🛡️ KTT LARGE FILE GUARD — KIỂM TRA DUNG LƯỢNG FILE GIT")
    print("=" * 70)

    git_bin = get_git_binary()

    # 1. Lấy danh sách các file đang được staged (nếu có)
    try:
        res = subprocess.run(
            [git_bin, "-C", str(ROOT_DIR), "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=True
        )
        staged_files = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        staged_files = []

    # Nếu không có file nào đang staged, kiểm tra toàn bộ file đang được track bởi Git
    if not staged_files:
        try:
            res = subprocess.run(
                [git_bin, "-C", str(ROOT_DIR), "ls-files"],
                capture_output=True, text=True, check=True
            )
            files_to_check = [line.strip() for line in res.stdout.splitlines() if line.strip()]
            mode_desc = "toàn bộ file đang được Git theo dõi (tracked files)"
        except Exception as e:
            print(f"Lỗi khi đọc git: {e}")
            return True
    else:
        files_to_check = staged_files
        mode_desc = "các file đang chuẩn bị commit (staged files)"

    print(f"📁 Đang kiểm tra dung lượng cho {len(files_to_check)} {mode_desc}...")

    oversized = []
    for rel_path in files_to_check:
        full_path = ROOT_DIR / rel_path
        if full_path.exists() and full_path.is_file():
            size = full_path.stat().st_size
            if size > MAX_SIZE_BYTES:
                size_mb = size / (1024 * 1024)
                oversized.append((rel_path, size_mb))

    if oversized:
        print("\n❌ [BLOCKED] PHÁT HIỆN FILE DUNG LƯỢNG LỚN VƯỢT QUY ĐỊNH (> 45 MB):")
        for path, mb in oversized:
            print(f"   - {path}: {mb:.2f} MB")
        print("\n⚠️ HƯỚNG DẪN XỬ LÝ:")
        print("   Theo quy định của dự án, các file có dung lượng lớn CHỈ ĐƯỢC LƯU LOCAL, KHÔNG ĐẨY LÊN GIT.")
        print("   1. Hủy stage file:  git reset HEAD <tên_file>")
        print("   2. Đưa vào .gitignore: thêm đường dẫn file vào file .gitignore")
        print("   File gốc vẫn được giữ nguyên an toàn trên máy của bạn.")
        return False

    print("\n✅ TẤT CẢ CÁC FILE ĐỀU ĐẠT CHUẨN DUNG LƯỢNG AN TOÀN (< 45 MB)!")
    return True


if __name__ == "__main__":
    passed = check_staged_or_tracked_files()
    sys.exit(0 if passed else 1)
