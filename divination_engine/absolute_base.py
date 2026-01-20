"""
1992年2月17日=癸亥を絶対的な基準として逆算
"""
import sys
import io
import swisseph as swe

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ganzhi_60 = [f"{STEMS[i%10]}{BRANCHES[i%12]}" for i in range(60)]

# 絶対的な基準: 1992年2月17日 = 癸亥（ユーザー確認済み）
# この日の昼12時JSTを基準点とする
ref_year, ref_month, ref_day = 1992, 2, 17
ref_jd = swe.julday(ref_year, ref_month, ref_day, 12.0 - 9.0)  # 12時JST = 3時UT

# 癸亥のインデックス
kuikai_idx = ganzhi_60.index("癸亥")  # 59

# この日から甲子日まで遡る
base_jd = ref_jd - kuikai_idx

base_y, base_m, base_d, base_h = swe.revjul(base_jd)
print(f"1992/2/17 = 癸亥 から逆算した甲子日:")
print(f"  日付: {int(base_y)}/{int(base_m)}/{int(base_d)} {base_h:.2f}時UT")
print(f"  JD: {base_jd}\n")

# 検証
verified_dates = [
    (1992, 2, 17, "癸亥"),  # 基準
    (2000, 1, 1, "甲辰"),   
    (2024, 1, 1, "癸巳"),
    (1900, 1, 1, "?"),      # これを確認
]

print("検証:")
for year, month, day, expected in verified_dates:
    test_jd = swe.julday(year, month, day, 12.0 - 9.0)
    days = int(test_jd - base_jd)
    idx = days % 60
    result = ganzhi_60[idx]
    
    if expected != "?":
        match = "✓" if result == expected else "✗"
        print(f"{year}/{month:02d}/{day:02d}: 経過{days:5d}日, idx={idx:2d}, 計算={result}, 期待={expected} {match}")
    else:
        print(f"{year}/{month:02d}/{day:02d}: 経過{days:5d}日, idx={idx:2d}, 計算={result}")
