"""
日柱計算の修正版 - 23時切り替え（晩子時）を考慮
"""
import sys
import io
import swisseph as swe
from datetime import datetime, timedelta

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 60干支リスト
ganzhi_60 = []
for i in range(60):
    ganzhi_60.append(f"{STEMS[i % 10]}{BRANCHES[i % 12]}")

# 既知の甲子日: 1984年2月2日（JST）
JIAZI_YEAR, JIAZI_MONTH, JIAZI_DAY = 1984, 2, 2

def calc_day_pillar_classic(year, month, day, hour, minute):
    """
    日柱を計算（23時切り替え方式）
    
    23:00-23:59は翌日の干支を使用
    """
    # JSTのdatetimeを作成
    dt_jst = datetime(year, month, day, hour, minute)
    
    # 23時以降は翌日として扱う
    if hour >= 23:
        dt_jst = dt_jst + timedelta(days=1)
    
    # UTに変換（JST = UTC+9）
    dt_ut = dt_jst - timedelta(hours=9)
    
    # ユリウス日を計算
    jd_ut = swe.julday(dt_ut.year, dt_ut.month, dt_ut.day, 
                       dt_ut.hour + dt_ut.minute / 60.0)
    
    # 日の境界（23時JST = 14時UT）を基準にした日付
    # JSTの日付境界は14:00 UTなので、14時UTより前なら前日
    jd_day_start = int(jd_ut - 14/24) + 14/24
    
    # 基準日（甲子日）のJD
    jiazi_jd = swe.julday(JIAZI_YEAR, JIAZI_MONTH, JIAZI_DAY, 0.0)
    jiazi_day_start = int(jiazi_jd - 14/24) + 14/24
    
    # 経過日数
    days_elapsed = int(jd_day_start - jiazi_day_start)
    
    # 60干支インデックス
    ganzhi_idx = days_elapsed % 60
    
    return ganzhi_60[ganzhi_idx], ganzhi_idx, days_elapsed

# テスト
test_cases = [
    # (年, 月, 日, 時, 分, 期待される干支)
    (1992, 2, 17, 17, 18, "癸亥"),  # ユーザー指摘
    (1992, 2, 17, 22, 59, "癸亥"),  # 22:59はまだ同じ日
    (1992, 2, 17, 23, 0, "甲子"),   # 23:00は翌日
    (1992, 2, 18, 0, 0, "甲子"),    # 翌日0時
    (2000, 1, 1, 12, 0, "甲辰"),
    (1984, 2, 2, 12, 0, "甲子"),    # 基準日
]

print("日柱計算テスト（23時切り替え方式）\n")
print("基準日: 1984年2月2日 = 甲子日\n")

for year, month, day, hour, minute, expected in test_cases:
    result, idx, days = calc_day_pillar_classic(year, month, day, hour, minute)
    match = "✓" if result == expected else "✗"
    
    print(f"{year}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}")
    print(f"  経過日数: {days}日, インデックス: {idx}")
    print(f"  計算結果: {result}, 期待: {expected} {match}")
    print()
