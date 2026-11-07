# -*- coding: utf-8 -*-
"""
Entity Resolver: Nhận diện, đối chiếu và chuẩn hóa thực thể nhân sự, chức vụ, bộ phận KTT.
Chống nhầm lẫn giới tính (Anti-Misgendering) và chuẩn hóa danh xưng công sở.
"""
import re
import unicodedata
from typing import Dict, List, Tuple, Optional
from ..gather.knowledge_registry import KnowledgeRegistry

class EntityResolver:
    def __init__(self, registry: KnowledgeRegistry):
        self.registry = registry

        # Danh sách đại từ khẩu ngữ cần chuyển hóa sang văn phong biên bản
        self.SLANG_PRONOUNS = [
            (re.compile(r"\b(mày\s+tao|mày|tao)\b", re.IGNORECASE), "nhân sự"),
            (re.compile(r"\b(ông\s+đó|ông\s+kia)\b", re.IGNORECASE), "nhân sự phụ trách"),
            (re.compile(r"\b(bà\s+đó|bà\s+kia)\b", re.IGNORECASE), "nhân sự phụ trách"),
            (re.compile(r"\b(nó)\b", re.IGNORECASE), "nhân sự"),
        ]

    def resolve_text_entities(self, text: str) -> Tuple[str, List[str]]:
        """
        Chuẩn hóa tên người trong đoạn văn sang định dạng: <Anh/Chị> <Tên> (<Tag>)
        Trả về: (văn bản đã chuẩn hóa, danh sách cảnh báo danh xưng chưa rõ)
        """
        text = unicodedata.normalize("NFC", text)
        warnings = []

        # 1. Chuyển hóa đại từ khẩu ngữ
        for pat, repl in self.SLANG_PRONOUNS:
            text = pat.sub(repl, text)

        # 2. Quét tên nhân sự đã biết trong Registry để ép định dạng chuẩn
        for name_key, person in self.registry.personnel.items():
            name = person["name"]
            gender = person["gender"]
            dept = person["department"]
            full_tag = person["full"]  # VD: Anh Tân (Kho)

            # Trường hợp transcript nhận sai giới tính (ví dụ "Chị Tân" trong khi Tân là Nam)
            opposite_gender = "Chị" if gender == "Anh" else "Anh"
            wrong_pattern = rf"(?<![0-9A-Za-zÀ-ỹ_]){opposite_gender}\s+{re.escape(name)}(?![0-9A-Za-zÀ-ỹ_])"
            text = re.sub(wrong_pattern, full_tag, text, flags=re.IGNORECASE)

            # Trường hợp chỉ gọi mỗi tên trần trụi hoặc "anh Tân" chưa có tag phòng ban
            base_pattern = rf"(?<![0-9A-Za-zÀ-ỹ_])(?:{gender}\s+)?{re.escape(name)}(?!\s*\([^)]+\))(?![0-9A-Za-zÀ-ỹ_])"
            text = re.sub(base_pattern, full_tag, text, flags=re.IGNORECASE)

        # 3. Áp dụng toàn bộ quy tắc glossary sửa lỗi chính tả/thuật ngữ
        text = self.registry.apply_glossary_to_text(text)

        return text, warnings
