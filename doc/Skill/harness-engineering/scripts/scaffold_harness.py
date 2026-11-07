#!/usr/bin/env python3
"""Dựng dự án Harness mới từ lõi tham chiếu (assets/harness_core).

Dùng:  python scaffold_harness.py <thư_mục_đích> [--force]
Không ghi đè thư mục đã có nội dung nếu thiếu --force.
"""
import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "harness_core")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    dst = args[0]
    if os.path.exists(dst) and os.listdir(dst) and "--force" not in sys.argv:
        sys.exit(f"'{dst}' đã có nội dung. Dùng --force nếu thực sự muốn ghi đè.")
    shutil.copytree(SRC, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "runs"))
    print(f"Đã tạo Harness tại {dst}\n  cd {dst} && python examples/demo.py && python -m unittest discover -s tests")


if __name__ == "__main__":
    main()
