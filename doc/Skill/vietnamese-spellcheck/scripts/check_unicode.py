#!/usr/bin/env python3
"""
Kiểm tra mức Unicode cho các từ tiếng Việt nghi vấn trong file .docx.

Dùng khi người dùng báo "chữ này sai" nhưng cần xác minh xem lỗi nằm
trong dữ liệu file hay chỉ là lỗi hiển thị (font rendering) của trình xem.

Usage:
    python check_unicode.py <file.docx> "cụm từ nghi vấn"
    python check_unicode.py <file.docx> --scan   # quét toàn bộ các chữ có dấu chồng
"""
import sys
import re
import zipfile
import unicodedata

# Các nguyên âm có dấu chồng (2 dấu trên 1 chữ) — nhóm dễ bị trình xem render sai nhất.
DOUBLE_DIACRITIC_CHARS = set(
    "ệẫỡữặộẹẩẳẵỏởỗíìỉĩị"
    "ỆẪỠỮẶỘẸẨẲẴỎỞỖÍÌỈĨỊ"
)


def extract_text(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        data = z.read("word/document.xml").decode("utf-8")
    texts = re.findall(r"<w:t[^>]*>(.*?)</w:t>", data)
    return "".join(texts)


def show_codepoints(snippet):
    for ch in snippet:
        name = unicodedata.name(ch, "?")
        print(f"  {ch!r:6} U+{ord(ch):04X}  {name}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    docx_path = sys.argv[1]
    full = extract_text(docx_path)

    if len(sys.argv) >= 3 and sys.argv[2] != "--scan":
        query = sys.argv[2]
        idx = full.find(query)
        if idx == -1:
            print(f"Không tìm thấy cụm '{query}' trong file.")
            sys.exit(1)
        print(f"Tìm thấy tại vị trí {idx}:")
        show_codepoints(full[idx : idx + len(query) + 5])
    else:
        print("Quét các từ chứa nguyên âm có dấu chồng (dễ bị render sai nhất):\n")
        words = re.findall(r"\S+", full)
        flagged = [w for w in words if any(c in DOUBLE_DIACRITIC_CHARS for c in w)]
        seen = set()
        for w in flagged:
            if w in seen:
                continue
            seen.add(w)
            print(f"'{w}':")
            show_codepoints(w)
            print()


if __name__ == "__main__":
    main()
