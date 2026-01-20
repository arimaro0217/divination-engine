"""
複数の既知データから正しい基準日を特定
"""
import sys
import io
import swisseph as swe

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 60干支リスト生成
ganzhi_list = []
for i in range(60):
    s_idx = i % 10
    b_idx = i % 12
    ganzhi_list.append(f"{STEMS[s_idx]}{BRANCHES[b_idx]}")

print("60干支リスト（最初の10個）:")
for i in range(10):
    print(f"{i}: {ganzhi_list[i]}")
print()

# 既知のデータ
known_dates = [
    (1992, 2, 17, "癸亥"),
    (2000, 1, 1, "甲辰"),
    (2024, 1, 1, "癸巳"),  # 検証用
]

print("既知のデータから基準日を計算:\n")

for year, month, day, expected_ganzhi in known_dates:
    jd = swe.julday(year, month, day, 0.0)
    jd_0ut = int(jd - 0.5) + 0.5
    
    # 期待される干支のインデックス
    ganzhi_idx = ganzhi_list.index(expected_ganzhi)
    
    # 基準日（甲子日）を逆算
    base_jd = jd_0ut - ganzhi_idx
    base_y, base_m, base_d, _ = swe.revjul(base_jd)
    
    print(f"{year}年{month}月{day}日 = {expected_ganzhi} (インデックス{ganzhi_idx})")
    print(f"  → 基準日: {int(base_y)}年{int(base_m)}月{int(base_d)}日 (JD: {base_jd})")
    
    # この基準日で60日周期を確認
    # 60日後は同じ干支になるはず
    verify_jd = base_jd + 60
    verify_days = int(verify_jd - base_jd)
    verify_idx = verify_days % 60
    print(f"  60日後の干支インデックス: {verify_idx} (0になるべき)")
    print()

# 1900年1月1日からの甲子日を探す
print("\n1900年周辺の甲子日を探索:")
start_jd = swe.julday(1899, 12, 25, 0.0)

for i in range(70):  # 70日分チェック
    test_jd = start_jd + i
    test_jd_0ut = int(test_jd - 0.5) + 0.5
    test_y, test_m, test_d, _ = swe.revjul(test_jd_0ut)
    
    # 2000年1月1日=甲辰から逆算した基準日で計算
    # 2000/1/1 = 甲辰 (インデックス40)
    ref_jd = swe.julday(2000, 1, 1, 0.0)
    ref_jd_0ut = int(ref_jd - 0.5) + 0.5
    ref_base_jd = ref_jd_0ut - 40  # 甲辰のインデックス
    
    days_from_ref_base = int(test_jd_0ut - ref_base_jd)
    idx_from_ref = days_from_ref_base % 60
    
    if idx_from_ref == 0:  # 甲子
        print(f"甲子日: {int(test_y)}年{int(test_m)}月{int(test_d)}日 (JD: {test_jd_0ut})")

print("\n\n正しい基準日を確定:")
# 2000年1月1日 = 甲辰 (インデックス40) から逆算
ref_jd_2000 = swe.julday(2000, 1, 1, 0.0)
ref_jd_2000_0ut = int(ref_jd_2000 - 0.5) + 0.5
correct_base_jd = ref_jd_2000_0ut - 40

base_y, base_m, base_d, _ = swe.revjul(correct_base_jd)
print(f"基準日（甲子日）: {int(base_y)}年{int(base_m)}月{int(base_d)}日")
print(f"JD: {correct_base_jd}")

# 検証
print("\n検証:")
for year, month, day, expected in known_dates:
    test_jd = swe.julday(year, month, day, 0.0)
    test_jd_0ut = int(test_jd - 0.5) + 0.5
    days = int(test_jd_0ut - correct_base_jd)
    idx = days % 60
    result_ganzhi = ganzhi_list[idx]
    match = "✓" if result_ganzhi == expected else "✗"
    print(f"{year}/{month}/{day}: 期待={expected}, 計算={result_ganzhi} {match}")
