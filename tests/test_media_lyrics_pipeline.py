# -*- coding: utf-8 -*-
"""
test_media_lyrics_pipeline.py - Kiểm thử toàn diện module xử lý nhạc và phụ đề Karaoke:
- Kiểm tra chuẩn hoá tiếng Việt Unicode NFC
- Kiểm tra định dạng thời gian LRC, ASS, SRT
- Kiểm tra tính hợp lệ của thẻ đổi màu Karaoke \\k trong file .ass
- Kiểm tra cấu trúc JSON Timeline
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from sync_lyrics_engine import (
    LineSegment,
    WordSegment,
    export_enhanced_lrc,
    export_json_timeline,
    export_karaoke_ass,
    export_srt,
    export_standard_lrc,
    format_timestamp_ass,
    format_timestamp_lrc,
    format_timestamp_srt,
    normalize_vietnamese_text
)


def test_timestamp_formatting():
    secs = 75.34  # 1 phút 15 giây 34 centiseconds

    lrc_ts = format_timestamp_lrc(secs)
    assert lrc_ts == "[01:15.34]", f"LRC ts mong đợi [01:15.34], nhận: {lrc_ts}"

    ass_ts = format_timestamp_ass(secs)
    assert ass_ts == "0:01:15.34", f"ASS ts mong đợi 0:01:15.34, nhận: {ass_ts}"

    srt_ts = format_timestamp_srt(secs)
    assert srt_ts == "00:01:15,340", f"SRT ts mong đợi 00:01:15,340, nhận: {srt_ts}"


def test_vietnamese_unicode_normalization():
    raw_str = "Nơi  này  có   anh,  bầu  trời  êm   ả  "
    clean_str = normalize_vietnamese_text(raw_str)
    assert clean_str == "Nơi này có anh, bầu trời êm ả"


def test_karaoke_ass_generation():
    line = LineSegment(
        text="Nơi này có anh",
        start=10.0,
        end=13.0,
        words=[
            WordSegment(word="Nơi", start=10.0, end=10.5),
            WordSegment(word="này", start=10.5, end=11.2),
            WordSegment(word="có", start=11.2, end=11.8),
            WordSegment(word="anh", start=11.8, end=13.0),
        ]
    )

    ass_content = export_karaoke_ass([line], title="Test Song", resolution="1920x1080")
    assert "[Script Info]" in ass_content
    assert "PlayResX: 1920" in ass_content
    assert "PlayResY: 1080" in ass_content
    assert "Style: Karaoke,Montserrat" in ass_content
    # Kiểm tra có thẻ \k đổi màu chữ
    assert r"{\k50}Nơi" in ass_content
    assert r"{\k70}này" in ass_content
    assert r"{\k60}có" in ass_content
    assert r"{\k120}anh" in ass_content


def test_standard_and_enhanced_lrc():
    line = LineSegment(
        text="Em là ai từ đâu bước đến",
        start=15.2,
        end=19.5,
        words=[
            WordSegment(word="Em", start=15.2, end=15.6),
            WordSegment(word="là", start=15.6, end=16.0),
            WordSegment(word="ai", start=16.0, end=16.5)
        ]
    )

    std_lrc = export_standard_lrc([line], title="Em Của Ngày Hôm Qua", artist="Sơn Tùng M-TP")
    assert "[ti:Em Của Ngày Hôm Qua]" in std_lrc
    assert "[00:15.20]Em là ai từ đâu bước đến" in std_lrc

    enh_lrc = export_enhanced_lrc([line], title="Em Của Ngày Hôm Qua", artist="Sơn Tùng M-TP")
    assert "[00:15.20] <00:15.20> Em <00:15.60> là <00:16.00> ai" in enh_lrc


def test_json_timeline():
    line = LineSegment(
        text="Dòng sông xanh biếc",
        start=5.0,
        end=8.0,
        words=[
            WordSegment(word="Dòng", start=5.0, end=5.8),
            WordSegment(word="sông", start=5.8, end=6.5)
        ]
    )
    json_str = export_json_timeline([line])
    parsed = json.loads(json_str)
    assert len(parsed) == 1
    assert parsed[0]["text"] == "Dòng sông xanh biếc"
    assert len(parsed[0]["words"]) == 2
    assert parsed[0]["words"][0]["word"] == "Dòng"
