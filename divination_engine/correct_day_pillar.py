"""
日の境界を23時JSTとして正しく計算
"""
import sys
import io
import swisseph as swe
from datetime import datetime, timedelta

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ganzhi_60 = [f"{STEMS[i%10]}{BRANCHES[i%12]}" for i in range(60)]

def get_day_ganzhi_jd(year, month, day):
    """
    指定された日（JST）の日干支を計算するためのJDを取得
    
    日の境界は前日23時JST
    """
    # その日の23時JSTのJDを計算（これが翌日の始まり）
    # JST 23:00 = UT 14:00
    jd_23jst = swe.julday(year, month, day, 23.0 - 9.0)  # 14:00 UT
    return jd_23jst

# 基準日: 1900年1月1日 = 辛丑
# 辛丑から甲子まで遡る
xinchou_idx = ganzhi_60.index("辛丑")  # 37
base_date_jd = get_day_ganzhi_jd(1900, 1, 1) - xinchou_idx

base_y, base_m, base_d, base_h = swe.revjul(base_date_jd)
print(f"基準日（甲子日の23時JST相当）:")
print(f"  JD: {base_date_jd}")
print(f"  UT: {int(base_y)}/{int(base_m)}/{int(base_d)} {base_h:.2f}時")

# 検証データ
verified_dates = [
    (2024, 1, 1, "癸巳"),
    (2000, 1, 1, "甲辰"),
    (1992, 2, 17, "癸亥"),
    (1900, 1, 1, "辛丑"),
]

print(f"\n検証（日の境界=前日23時JST）:\n")
for year, month, day, expected in verified_dates:
    test_jd = get_day_ganzhi_jd(year, month, day)
    days = int(test_jd - base_date_jd)
    idx = days % 60
    result = ganzhi_60[idx]
    match = "✓" if result == expected else "✗"
    print(f"{year}/{month:02d}/{day:02d}: 経過{days:5d}日, idx={idx:2d}, 計算={result}, 期待={expected} {match}")

# 1992年2月17日の詳細検証
print(f"\n\n1992年2月17日の詳細検証:")
target_year, target_month, target_day = 1992, 2, 17

# 異なる時刻での計算
test_times = [
    (0, 0, "前日23時以降の干支"),
    (12, 0, "同じ日の干支"),
    (17, 18, "ユーザー指定時刻"),
    (22, 59, "まだ同じ日"),
    (23, 0, "翌日の干支に切り替わる"),
]

for hour, minute, desc in test_times:
    # 実際の日時
    actual_dt = datetime(target_year, target_month, target_day, hour, minute)
    
    # この時刻が属する「干支の日」を判定
    # 23時以降なら翌日の干支
    if hour >= 23:
        ganzhi_date = actual_dt + timedelta(days=1)
    else:
        ganzhi_date = actual_dt
    
    test_jd = get_day_ganzhi_jd(ganzhi_date.year, ganzhi_date.month, ganzhi_date.day)
    days = int(test_jd - base_date_jd)
    idx = days % 60
    result = ganzhi_60[idx]
    
    print(f"{target_year}/{target_month:02d}/{target_day:02d} {hour:02d}:{minute:02d} → {result} ({desc})")
