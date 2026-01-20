"""
四柱推命の日柱計算の検証
1992年2月17日の日柱が「癸亥」であることを確認
"""
import sys
import io
import swisseph as swe
from datetime import datetime

# UTF-8出力
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 天干・地支
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# テスト日: 1992年2月17日
year, month, day = 1992, 2, 17

# ユリウス日を計算（正午UT）
jd = swe.julday(year, month, day, 12.0)

print(f"検証: {year}年{month}月{day}日")
print(f"ユリウス日: {jd}")

# 現在のロジック: 1900年1月31日 = 甲子日を基準
base_jd = 2415035.5  # 1900年1月31日 0時UT

# 0時UTのJDを計算
jd_0ut = int(jd - 0.5) + 0.5

# 基準日からの日数
days = int(jd_0ut - base_jd)

# 60干支のインデックス
index = days % 60

stem_index = index % 10
branch_index = index % 12

print(f"\n【現在のロジック】")
print(f"0時UTのJD: {jd_0ut}")
print(f"基準日からの日数: {days}日")
print(f"60干支インデックス: {index}")
print(f"天干インデックス: {stem_index} ({STEMS[stem_index]})")
print(f"地支インデックス: {branch_index} ({BRANCHES[branch_index]})")
print(f"→ 結果: {STEMS[stem_index]}{BRANCHES[branch_index]}")

# 正しい結果は「癸亥」
# 癸 = インデックス 9
# 亥 = インデックス 11

print(f"\n【期待される結果】")
print(f"天干: 癸 (インデックス 9)")
print(f"地支: 亥 (インデックス 11)")
print(f"→ 癸亥")

# 癸亥のインデックスを計算
# 60干支の配列: 甲子(0), 乙丑(1), ... 癸亥(59)
# 癸亥 = 59番目（0始まり）
correct_index = 59  # 癸亥

print(f"\n【検証】")
print(f"癸亥の60干支インデックス: {correct_index}")
print(f"現在の計算結果: {index}")
print(f"差分: {index - correct_index}")

# 正しい基準日を逆算
if index != correct_index:
    # 正しい基準日を計算
    correct_days = days - (index - correct_index)
    correct_base_jd = jd_0ut - correct_days
    
    # 基準日の日付を取得
    base_year, base_month, base_day, base_hour = swe.revjul(correct_base_jd)
    
    print(f"\n【修正提案】")
    print(f"正しい基準日のJD: {correct_base_jd}")
    print(f"正しい基準日: {int(base_year)}年{int(base_month)}月{int(base_day)}日")
    print(f"現在の基準日: 1900年1月31日")

# 別の基準日での検証（1984年2月2日 = 甲子日）
# これはよく使われる現代の基準日
modern_base_year, modern_base_month, modern_base_day = 1984, 2, 2
modern_base_jd = swe.julday(modern_base_year, modern_base_month, modern_base_day, 0.0)
modern_base_jd_0ut = int(modern_base_jd - 0.5) + 0.5

moden_days = int(jd_0ut - modern_base_jd_0ut)
modern_index = moden_days % 60
modern_stem = modern_index % 10
modern_branch = modern_index % 12

print(f"\n【別の基準日で検証】")
print(f"基準日: 1984年2月2日 = 甲子日")
print(f"基準日JD: {modern_base_jd_0ut}")
print(f"経過日数: {moden_days}日")
print(f"60干支インデックス: {modern_index}")
print(f"結果: {STEMS[modern_stem]}{BRANCHES[modern_branch]}")
