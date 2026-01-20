"""
60干支の正しい計算方法を検証
"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 60干支の完全なリストを正しく生成
print("60干支の正しいリスト:")
ganzhi_60 = []
for i in range(60):
    # 正しい計算方法
    stem_idx = i % 10
    branch_idx = i % 12
    ganzhi = f"{STEMS[stem_idx]}{BRANCHES[branch_idx]}"
    ganzhi_60.append(ganzhi)
    if i < 15 or i >= 55:
        print(f"{i:2d}: {ganzhi}")
    elif i == 15:
        print("...")

# 期待される主要な干支を確認
print("\n主要な干支の確認:")
test_ganzhi = [
    ("甲子", 0),
    ("癸亥", 59),
    ("甲辰", 40),
    ("癸巳", 29),
]

for gz, expected_idx in test_ganzhi:
    actual_idx = ganzhi_60.index(gz) if gz in ganzhi_60 else -1
    match = "✓" if actual_idx == expected_idx else "✗"
    print(f"{gz}: 期待インデックス={expected_idx}, 実際={actual_idx} {match}")

# 問題: なぜ各日付から逆算した基準日が異なるのか？
# → 正しい「甲子日」を基準にすれば、すべての日付で一貫した計算ができるはず

import swisseph as swe

# 確実な甲子日を見つける
# 1984年2月2日 = 甲子日（広く知られている）
known_jiazi_date = (1984, 2, 2)
jiazi_jd = swe.julday(*known_jiazi_date, 0.0)
jiazi_jd_0ut = int(jiazi_jd - 0.5) + 0.5

print(f"\n\n既知の甲子日: {known_jiazi_date[0]}年{known_jiazi_date[1]}月{known_jiazi_date[2]}日")
print(f"JD: {jiazi_jd_0ut}")

# この基準日で既知のデータを検証
known_dates = [
    (1992, 2, 17, "癸亥"),
    (2000, 1, 1, "甲辰"),
    (2024, 1, 1, "癸巳"),
    (1984, 2, 2, "甲子"),  # 基準日自身
]

print(f"\n検証（基準日: 1984年2月2日）:")
for year, month, day, expected in known_dates:
    test_jd = swe.julday(year, month, day, 0.0)
    test_jd_0ut = int(test_jd - 0.5) + 0.5
    
    days = int(test_jd_0ut - jiazi_jd_0ut)
    idx = days % 60
    result = ganzhi_60[idx]
    
    match = "✓" if result == expected else "✗"
    print(f"{year}/{month:02d}/{day:02d}: 経過{days:5d}日, idx={idx:2d}, 期待={expected}, 計算={result} {match}")
