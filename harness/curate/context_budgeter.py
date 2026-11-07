# -*- coding: utf-8 -*-
"""
Context Budgeter: Quản lý Cửa sổ Ngữ cảnh như Bộ đệm CPU (Context Cache Hierarchy).
Đảm bảo nén vừa khít L1 Buffer (8k - 16k tokens) để duy trì tối đa Attention Focus.
"""
from typing import List, Dict, Any
from ..config import CONTEXT_CACHE_CONFIG

class ContextBudgeter:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or CONTEXT_CACHE_CONFIG
        self.max_l1_tokens = self.config.get("max_l1_tokens", 16000)
        self.max_chunk_tokens = self.config.get("max_chunk_tokens", 8000)
        self.overlap_tokens = self.config.get("chunk_overlap_tokens", 500)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Ước lượng số token cho văn bản tiếng Việt có dấu:
        Trung bình ~1 từ tiếng Việt = 1.3 token, hoặc ~2.2 ký tự = 1 token.
        """
        words = text.split()
        return max(1, int(len(words) * 1.3))

    def budget_lines(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Phân mảnh các dòng transcript thành các Context Block có kiểm soát ngân sách token
        """
        chunks = []
        current_lines = []
        current_token_count = 0
        chunk_idx = 1

        for line in lines:
            line_tokens = self.estimate_tokens(line)

            if current_token_count + line_tokens > self.max_chunk_tokens and current_lines:
                # Đóng gói chunk hiện tại
                chunk_text = "\n".join(current_lines)
                chunks.append({
                    "chunk_id": f"CHUNK_{chunk_idx:02d}",
                    "text": chunk_text,
                    "estimated_tokens": current_token_count,
                    "line_count": len(current_lines)
                })
                chunk_idx += 1

                # Giữ lại một số dòng cuối làm vùng đệm gối đầu (overlap) để chống rách ngữ cảnh
                overlap_lines = []
                overlap_tokens = 0
                for rev_line in reversed(current_lines):
                    tok = self.estimate_tokens(rev_line)
                    if overlap_tokens + tok > self.overlap_tokens:
                        break
                    overlap_lines.insert(0, rev_line)
                    overlap_tokens += tok

                current_lines = overlap_lines + [line]
                current_token_count = overlap_tokens + line_tokens
            else:
                current_lines.append(line)
                current_token_count += line_tokens

        # Gom chunk cuối cùng
        if current_lines:
            chunk_text = "\n".join(current_lines)
            chunks.append({
                "chunk_id": f"CHUNK_{chunk_idx:02d}",
                "text": chunk_text,
                "estimated_tokens": current_token_count,
                "line_count": len(current_lines)
            })

        return chunks
