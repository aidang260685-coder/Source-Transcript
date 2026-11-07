# -*- coding: utf-8 -*-
"""
Knowledge Registry: Nạp và chỉ mục hóa toàn bộ tri thức thực thể của Kiên Thành Tín (KTT).
"""
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from ..config import GLOSSARY_PATH

class KnowledgeRegistry:
    def __init__(self, glossary_file: Optional[Path] = None):
        self.glossary_file = glossary_file or GLOSSARY_PATH
        self.replacements: List[Tuple[re.Pattern, str]] = []
        self.personnel: Dict[str, Dict[str, str]] = {}
        self.valid_terms: Set[str] = set()
        self.departments: Set[str] = {
            "BOD", "KT", "Kế toán", "Kho", "MKT", "Marketing",
            "Sale", "HR", "QC", "IT", "PP", "DA"
        }
        self._load()

    def _load(self):
        if not self.glossary_file.exists():
            return

        with open(self.glossary_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        raw_replacements: List[Tuple[str, str]] = []

        # Regex tìm danh xưng nhân sự: "Anh Tân (Kho)", "Chị Thanh (BOD)"
        person_pattern = re.compile(r"^(Anh|Chị)\s+([^(]+)\s*\(([^)]+)\)$", re.IGNORECASE)

        for line in lines:
            line = unicodedata.normalize("NFC", line.strip())
            if not line or line.startswith("#"):
                continue

            if "=>" in line:
                parts = line.split("=>")
                if len(parts) == 2:
                    src, dst = parts[0].strip(), parts[1].strip()
                    if src and dst:
                        raw_replacements.append((src, dst))
                continue

            # Kiểm tra dòng nhân sự
            match = person_pattern.match(line)
            if match:
                gender, name, dept = match.group(1).title(), match.group(2).strip(), match.group(3).strip()
                self.personnel[name.lower()] = {
                    "name": name,
                    "gender": gender,
                    "department": dept,
                    "full": f"{gender} {name} ({dept})"
                }
                # Lưu tên đầy đủ vào danh sách thuật ngữ hợp lệ
                self.valid_terms.add(f"{gender} {name} ({dept})")
            else:
                self.valid_terms.add(line)

        # Sắp xếp các quy tắc thay thế: dài nhất lên trước để tránh xung đột regex
        raw_replacements.sort(key=lambda x: len(x[0]), reverse=True)
        for src, dst in raw_replacements:
            # Ranh giới từ hỗ trợ đầy đủ ký tự tiếng Việt có dấu
            pattern_str = rf"(?<![0-9A-Za-zÀ-ỹ_]){re.escape(src)}(?![0-9A-Za-zÀ-ỹ_])"
            self.replacements.append((re.compile(pattern_str, re.IGNORECASE), dst))

    def resolve_person(self, raw_name: str) -> Optional[Dict[str, str]]:
        """Tra cứu nhân sự theo tên ngắn hoặc tên đầy đủ"""
        clean_name = raw_name.strip().lower()
        # Bỏ danh xưng "anh", "chị" nếu có ở đầu để tìm kiếm linh hoạt
        clean_name = re.sub(r"^(anh|chị)\s+", "", clean_name).strip()
        # Bỏ tag (Kho), (KT) nếu có
        clean_name = re.sub(r"\s*\([^)]*\)", "", clean_name).strip()
        return self.personnel.get(clean_name)

    def apply_glossary_to_text(self, text: str) -> str:
        """Áp dụng quy tắc glossary thay thế chuẩn xác"""
        text = unicodedata.normalize("NFC", text)
        for pattern, dst in self.replacements:
            text = pattern.sub(dst, text)
        return text
