"""
正しい日干支計算 - JSTの日付ベース
calendar_cn.pyの修正版
"""
import sys
import io
import swisseph as swe
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ganzhi_60 = [f"{STEMS[i%10]}{BRANCHES[i%12]}" for i in range(60)]

def calc_day_pillar_correct(dt_jst, use_23h_boundary=True):
    """
    正しい日柱計算
    
    Args:
        dt_jst: datetime (JST timezone aware)
        use_23h_boundary: True なら 23時以降は翌日の干支
    
    Returns:
        (干支文字列, インデックス)
    """
    # 23時以降は翌日として扱う
    if use_23h_boundary and dt_jst.hour >= 23:
        dt_jst = dt_jst + timedelta(days=1)
    
    # 基準日: 1992年2月17日 JST午前0時 = 癸亥
    # (ユーザー確認済み、この日の17時18分も癸亥)
    base_dt = datetime(1992, 2, 17, 0, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
    
    # 日数差を計算
    days_diff = (dt_jst.date() - base_dt.date()).days
    
    # 癸亥のインデックス: 59
    kuikai_idx = 59
    
    # 計算
    ganzhi_idx = (kuikai_idx + days_diff) % 60
    
    return ganzhi_60[ganzhi_idx], ganzhi_idx

# テスト
print("日柱計算テスト（正しい方法）\n")

test_cases = [
    (1992, 2, 17, 0, 0, "癸亥"),    # 基準日
    (1992, 2, 17, 17, 18, "癸亥"),  # ユーザー指摘
    (1992, 2, 17, 22, 59, "癸亥"),  # まだ同じ日
    (1992, 2, 17, 23, 0, "甲子"),   # 翌日
    (1992, 2, 18, 0, 0, "甲子"),    # 翌日
    (2000, 1, 1, 12, 0, "甲辰"),
    (2024, 1, 1, 12, 0, "癸巳"),
]

for year, month, day, hour, minute, expected in test_cases:
    dt = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo("Asia/Tokyo"))
    result, idx = calc_day_pillar_correct(dt)
    match = "✓" if result == expected else "✗"
    print(f"{year}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}: 計算={result} ({idx:2d}), 期待={expected} {match}")

# 1900年1月1日を確認
dt_1900 = datetime(1900, 1, 1, 12, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
result_1900, idx_1900 = calc_day_pillar_correct(dt_1900)
print(f"\n1900/01/01: {result_1900} ({idx_1900})")
