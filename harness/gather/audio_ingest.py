# -*- coding: utf-8 -*-
"""
Audio & File Ingestor: Thu thập và kiểm tra tính toàn vẹn của tệp ghi âm / bản phiên âm thô.
"""
from pathlib import Path
from typing import Dict, List, Any
import os

class AudioIngestor:
    AUDIO_EXTENSIONS = {".m4a", ".mp3", ".wav", ".wma", ".aac", ".ogg"}

    def __init__(self, target_path: Path):
        self.target_path = Path(target_path)

    def scan(self) -> List[Dict[str, Any]]:
        """Quét và gom toàn bộ tệp đầu vào cần xử lý"""
        items = []

        if self.target_path.is_file():
            items.append(self._analyze_file(self.target_path))
        elif self.target_path.is_dir():
            for file in self.target_path.iterdir():
                if file.suffix.lower() in self.AUDIO_EXTENSIONS or file.suffix.lower() == ".txt":
                    # Bỏ qua các file phụ trợ
                    if file.name.endswith("_flagged.txt") or file.name.startswith("ALL_"):
                        continue
                    items.append(self._analyze_file(file))

        return items

    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        stat = file_path.stat()
        file_type = "audio" if file_path.suffix.lower() in self.AUDIO_EXTENSIONS else "transcript"

        # Tìm file flagged tương ứng nếu là transcript
        flagged_file = file_path.with_name(f"{file_path.stem}_flagged.txt")

        return {
            "path": str(file_path),
            "filename": file_path.name,
            "stem": file_path.stem,
            "type": file_type,
            "size_bytes": stat.st_size,
            "has_flagged": flagged_file.exists(),
            "flagged_path": str(flagged_file) if flagged_file.exists() else None
        }
