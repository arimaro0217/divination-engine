"""
日柱の正しい基準日を特定
"""
import sys
import io
import swisseph as swe

# UTF-8出力
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 既知の日柱データで検証
test_dates = [
    (1992, 2, 17, "癸", "亥"),  # ユーザー指摘
    (2000, 1, 1, "甲", "辰"),   # 2000年1月1日 = 甲辰日（確認済み）
]

print("日柱の基準日を特定中...\n")

# 1992年2月17日 = 癸亥日を基準に計算
target_year, target_month, target_day = 1992, 2, 17
target_jd = swe.julday(target_year, target_month, target_day, 0.0)
target_jd_0ut = int(target_jd - 0.5) + 0.5

# 癸亥 = 60干支の59番目（0始まり）
target_stem = "癸"  # インデックス 9
target_branch = "亥"  # インデックス 11

target_stem_idx = STEMS.index(target_stem)
target_branch_idx = BRANCHES.index(target_branch)

# 六十干支のインデックスを計算
# 甲子=0, 乙丑=1, ... 癸亥=59
# (stem_idx * 6 + (stem_idx + branch_idx) % 5) の式は複雑すぎる
# 単純な方法: すべての組み合わせを列挙

# 60干支の完全なリストを生成
sixty_ganzhi = []
for i in range(60):
    stem_idx = i % 10
    branch_idx = i % 12
    sixty_ganzhi.append((STEMS[stem_idx], BRANCHES[branch_idx]))

# 癸亥のインデックスを検索
for idx, (s, b) in enumerate(sixty_ganzhi):
    if s == target_stem and b == target_branch:
        target_ganzhi_idx = idx
        break

print(f"ターゲット: {target_year}年{target_month}月{target_day}日 = {target_stem}{target_branch}")
print(f"60干支インデックス: {target_ganzhi_idx}")
print(f"ターゲットJD: {target_jd_0ut}\n")

# 基準日を逆算（甲子日を見つける）
# target_jd_0ut から target_ganzhi_idx 日戻れば甲子日
base_jd = target_jd_0ut - target_ganzhi_idx
base_year, base_month, base_day, base_hour = swe.revjul(base_jd)

print(f"【計算された基準日（甲子日）】")
print(f"JD: {base_jd}")
print(f"日付: {int(base_year)}年{int(base_month)}月{int(base_day)}日")

# 検証: この基準日から1992年2月17日までの日数
days_from_base = int(target_jd_0ut - base_jd)
calc_idx = days_from_base % 60
calc_stem_idx = calc_idx % 10
calc_branch_idx = calc_idx % 12

print(f"\n【検証】")
print(f"基準日からの日数: {days_from_base}日")
print(f"60干支インデックス: {calc_idx}")
print(f"計算結果: {STEMS[calc_stem_idx]}{BRANCHES[calc_branch_idx]}")
print(f"期待結果: {target_stem}{target_branch}")
print(f"一致: {'✓' if calc_idx == target_ganzhi_idx else '✗'}")

# 2000年1月1日でも検証
print(f"\n\n【2000年1月1日で検証】")
verify_year, verify_month, verify_day = 2000, 1, 1
verify_expected_stem, verify_expected_branch = "甲", "辰"

verify_jd = swe.julday(verify_year, verify_month, verify_day, 0.0)
verify_jd_0ut = int(verify_jd - 0.5) + 0.5

verify_days = int(verify_jd_0ut - base_jd)
verify_idx = verify_days % 60
verify_stem_idx = verify_idx % 10
verify_branch_idx = verify_idx % 12

print(f"日付: {verify_year}年{verify_month}月{verify_day}日")
print(f"基準日からの日数: {verify_days}日")
print(f"計算結果: {STEMS[verify_stem_idx]}{BRANCHES[verify_branch_idx]}")
print(f"期待結果: {verify_expected_stem}{verify_expected_branch}")
print(f"一致: {'✓' if STEMS[verify_stem_idx] == verify_expected_stem and BRANCHES[verify_branch_idx] == verify_expected_branch else '✗'}")
