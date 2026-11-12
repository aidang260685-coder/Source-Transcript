import sys
from pathlib import Path
import json
import re

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "tools"))

from faster_whisper import WhisperModel
from tools.sync_lyrics_engine import normalize_vietnamese_text

def transcribe_and_align():
    wav_path = BASE_DIR / "output/music/Sai_của_sai_KHÔNG_là_đúng_-_cover_by_HY_-_HY_Music/mp3/Sai_của_sai_KHÔNG_là_đúng_-_cover_by_HY_-_HY_Music_16k.wav"
    lyrics_txt = BASE_DIR / "input/lyrics/Sai_của_sai_KHÔNG_là_đúng_-_cover_by_HY_-_HY_Music.txt"
    
    with open(lyrics_txt, "r", encoding="utf-8") as f:
        clean_lines = [line.strip() for line in f if line.strip()]
        
    print(f"🎵 Đang chạy Whisper trích xuất mốc thời gian toàn bộ bài hát...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(wav_path), language="vi", word_timestamps=True)
    
    all_words = []
    for s in segments:
        for w in s.words:
            all_words.append({
                "word": w.word.strip(),
                "start": w.start,
                "end": w.end
            })
            
    print(f"✓ Trích xuất được {len(all_words)} từ thực tế từ âm thanh ca sĩ hát.")
    
    # Save raw words for inspection
    raw_path = BASE_DIR / "output/whisper_words.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_words, f, ensure_ascii=False, indent=2)
    print(f"✓ Đã lưu mốc thời gian thực vào {raw_path}")

if __name__ == "__main__":
    transcribe_and_align()
