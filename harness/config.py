# -*- coding: utf-8 -*-
"""
Cấu hình tập trung cho Hệ thống Harness (KTT Harness Config 2026).
"""
import os
from pathlib import Path

# Thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parent.parent

# Đường dẫn tài nguyên tri thức nền
GLOSSARY_PATH = BASE_DIR / "doc" / "glossary.txt"
TEMPLATES_DIR = BASE_DIR / "doc" / "Skill" / "meeting-note" / "assets"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
GHI_AM_DIR = BASE_DIR / "ghi_am"
OUTPUT_DIR = BASE_DIR / "output"

# Đảm bảo các thư mục tồn tại
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cấu hình Token Budgeting (Context CPU Cache Hierarchy)
CONTEXT_CACHE_CONFIG = {
    "max_l1_tokens": 16000,        # Cửa sổ L1 Buffer lý tưởng để duy trì 100% attention focus
    "max_chunk_tokens": 8000,      # Kích thước chunk logic theo từng phòng ban
    "chunk_overlap_tokens": 500,   # Vùng đệm gối đầu chống rách ngữ cảnh giữa các lượt nói
    "compression_target_ratio": 0.65  # Tỉ lệ nén mục tiêu sau khi lọc từ đệm và nhiễu hội thoại
}

# Cấu hình Vòng lặp Kiểm chứng & Tự sửa (Guardrail & Self-Healing Loop)
VERIFICATION_CONFIG = {
    "max_retries": 3,              # Giới hạn số lần retry trước khi escalate
    "temperature_initial": 0.2,    # Nhiệt độ ban đầu để trích xuất cấu trúc mượt mà
    "temperature_retry": 0.0,      # Nhiệt độ 0.0 cho các lượt patch lỗi (tối đa tính tất định)
    "strict_fact_checking": True,  # Bắt buộc 100% số liệu phải có đối chiếu với transcript gốc
    "strict_gender_check": True,   # Bắt buộc danh xưng Anh/Chị phải khớp danh bạ
    "unicode_form": "NFC"          # Chuẩn Unicode dựng sẵn
}
