# -*- coding: utf-8 -*-
"""
Noise Filter: Loại bỏ ảo giác Whisper, từ đệm vô nghĩa và vòng lặp văn bản.
"""
import re
import unicodedata
from typing import List, Tuple

class NoiseFilter:
    # Các mẫu câu ảo giác đặc thù của Whisper tiếng Việt
    HALLUCINATION_PATTERNS = [
        re.compile(r"^hãy\s+subscribe\s+cho\s+kênh", re.IGNORECASE),
        re.compile(r"để\s+không\s+bỏ\s+lỡ\s+những\s+video\s+hấp\s+dẫn", re.IGNORECASE),
        re.compile(r"^cảm\s+ơn\s+(các\s+bạn|quý\s+vị)\s+đã\s+(xem|theo\s+dõi|lắng\s+nghe)", re.IGNORECASE),
        re.compile(r"^hẹn\s+gặp\s+lại\s+(các\s+bạn|quý\s+vị)", re.IGNORECASE),
        re.compile(r"^subtitles?\s+by", re.IGNORECASE),
        re.compile(r"^amara\.org", re.IGNORECASE),
        re.compile(r"^ghi\s*ền\s+mì\s+gõ", re.IGNORECASE),
        re.compile(r"^la\s+la\s+school", re.IGNORECASE),
    ]

    # Các từ đệm hội thoại làm rác cửa sổ ngữ cảnh (CPU Cache)
    FILLER_WORDS = [
        (re.compile(r"\b(ờ|à|ừm|ờm)\b", re.IGNORECASE), " "),
        (re.compile(r"\b(kiểu\s+như\s+là|kiểu\s+như|cái\s+kiểu|thì\s+là)\b", re.IGNORECASE), " "),
        (re.compile(r"\b(nói\s+chung\s+là)\b", re.IGNORECASE), "nói chung "),
    ]

    def is_hallucination(self, text: str) -> bool:
        norm = text.strip()
        for pat in self.HALLUCINATION_PATTERNS:
            if pat.search(norm):
                return True
        return False

    def clean_filler(self, text: str) -> str:
        """Lọc sạch từ đệm mà không làm sai lệch ý câu"""
        text = unicodedata.normalize("NFC", text)
        for pat, repl in self.FILLER_WORDS:
            text = pat.sub(repl, text)
        # Thu gọn khoảng trắng thừa
        text = re.sub(r"[ \t]+", " ", text).strip()
        return text

    def sanitize_lines(self, lines: List[str]) -> List[str]:
        cleaned = []
        last_line = ""
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            if self.is_hallucination(line_str):
                continue
            # Bỏ lặp câu vô tận (repetition loop)
            if line_str == last_line:
                continue

            cleaned_line = self.clean_filler(line_str)
            if cleaned_line:
                cleaned.append(cleaned_line)
                last_line = line_str

        return cleaned
