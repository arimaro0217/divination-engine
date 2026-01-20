"""
修正後の日柱計算をテスト
"""
import sys
import io
from datetime import datetime
from zoneinfo import ZoneInfo

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.core.calendar_cn import ChineseCalendar
from src.core.time_manager import TimeManager

calendar = ChineseCalendar()

# テストケース
test_cases = [
    (1992, 2, 17, 17, 18, "癸亥"),  # ユーザー指定
    (1992, 2, 17, 22, 59, "癸亥"),  # 23時前
    (1992, 2, 17, 23, 0, "甲子"),   # 23時以降は翌日
    (1992, 2, 18, 0, 0, "甲子"),    # 翌日
]

print("日柱計算テスト（修正後）\n")

for year, month, day, hour, minute, expected in test_cases:
    dt = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo("Asia/Tokyo"))
    jd = TimeManager.to_julian_day(dt)
    
    # 日柱を計算
    day_pillar = calendar.calc_day_pillar(jd)
    result = f"{day_pillar.stem}{day_pillar.branch}"
    
    match = "✓" if result == expected else "✗"
    print(f"{year}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}: 計算={result}, 期待={expected} {match}")
