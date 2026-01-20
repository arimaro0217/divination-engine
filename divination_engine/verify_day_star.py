"""
1992年2月17日の日命星を正確に計算する検証スクリプト
"""
# 日命星の簡易計算（陽遁・隠遁を考慮）
# 
# 1992年2月17日は：
# - 1991年12月の冬至（12月22日頃）から最寄りの甲子日を起点に陽遁
# - 陽遁期間は冬至最寄りの甲子日から夏至最寄りの甲子日まで
# 
# 既知の基準日アプローチ：
# 1991年12月22日（冬至）に近い甲子日を探す

from datetime import datetime, timedelta

# 六十干支
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def get_ganzhi_from_jd(jd_int):
    """ユリウス日から干支を計算"""
    # 甲子日の基準: 1984年2月2日 = JD 2445731.5 が甲子日
    base_jd = 2445731  # 甲子日
    idx = int(jd_int - base_jd) % 60
    stem = STEMS[idx % 10]
    branch = BRANCHES[idx % 12]
    return f"{stem}{branch}", idx

def datetime_to_jd(dt):
    """日時をユリウス日に変換"""
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    jd = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jd

# 1991年冬至（12月22日）前後で甲子日を探す
print("=== 1991年冬至付近の甲子日を探す ===")
winter_solstice_1991 = datetime(1991, 12, 22)

for days_offset in range(-30, 35):
    check_date = winter_solstice_1991 + timedelta(days=days_offset)
    jd = datetime_to_jd(check_date)
    ganzhi, idx = get_ganzhi_from_jd(jd)
    if ganzhi == "甲子":
        print(f"甲子日発見: {check_date.strftime('%Y-%m-%d')} (JD: {jd}, 冬至から{days_offset}日)")

# 1992年2月17日の日命星を計算
print("\n=== 1992年2月17日の日命星計算 ===")
target_date = datetime(1992, 2, 17)
target_jd = datetime_to_jd(target_date)
print(f"対象日: {target_date.strftime('%Y-%m-%d')}, JD: {target_jd}")

# 冬至に最も近い甲子日を基準とする
# 1991年12月22日（冬至）の前後で最も近い甲子日
# 上記のループで確認すると...

# 既知の甲子日から計算
# 1984年2月4日 = 甲子年立春（JD 2445733）とされることが多い
# しかし実際は1984年2月2日が甲子日

base_date_1984 = datetime(1984, 2, 2)  # 甲子日の一つ
base_jd_1984 = datetime_to_jd(base_date_1984)
print(f"基準甲子日: {base_date_1984.strftime('%Y-%m-%d')}, JD: {base_jd_1984}")

# 1984年甲子日から1992年2月17日までの日数
days_diff = target_jd - base_jd_1984
print(f"基準日から{days_diff}日経過")

# 60日周期で甲子日を特定
cycles = days_diff // 60
remaining = days_diff % 60
print(f"60日周期: {cycles}回 + {remaining}日")

# 各甲子日の日命星開始値を確定するには、陽遁・隠遁を判定する必要がある
# 簡易的には：
# - 冬至最寄り甲子から夏至最寄り甲子まで：陽遁（1→9）
# - 夏至最寄り甲子から冬至最寄り甲子まで：隠遁（9→1）

# 1992年2月17日は冬至（1991/12/22）→夏至（1992/6/21）の期間なので陽遁
print("\n1992年2月は陽遁期間")

# 陽遁の場合の日命星計算
# 直近の甲子日を探す

print("\n=== 対象日付近の甲子日 ===")
for days_offset in range(-9, 10):
    check_date = target_date + timedelta(days=days_offset)
    jd = datetime_to_jd(check_date)
    ganzhi, idx = get_ganzhi_from_jd(jd)
    if ganzhi == "甲子":
        print(f"甲子日: {check_date.strftime('%Y-%m-%d')} (対象から{days_offset}日)")

# 対象日の干支を確認
target_ganzhi, ganzhi_idx = get_ganzhi_from_jd(target_jd)
print(f"\n1992年2月17日の干支: {target_ganzhi} (60干支インデックス: {ganzhi_idx})")

# 日命星の計算
# 陽遁の場合、甲子日から1→2→3...→9→1と進む
# 60日周期で甲子日が来る
# 9日周期で九星が循環

# 直前の甲子日からの経過日数
days_in_cycle = ganzhi_idx  # 甲子=0からの日数
print(f"直前の甲子日から{days_in_cycle}日経過")

# 陽遁の場合、甲子日を1（一白水星）として
# 毎日+1ずつ進む
# 9日で一周
star_in_9cycle = (days_in_cycle % 9) + 1
print(f"陽遁の場合: 九星 = {star_in_9cycle}")

# 確認：
# きちんと計算するには、この日が陽遁で開始値が何かを確認する必要
# 実際には「陽遁の甲子日は一白水星（1）から開始」が基本

# もし結果が4（四緑木星）でなく6（六白金星）が正しいなら
# 開始値が異なるか、隠遁として計算すべき可能性がある

# 隠遁の場合
# 甲子日を9（九紫火星）として、毎日-1ずつ進む
star_in_9cycle_inton = 9 - (days_in_cycle % 9)
if star_in_9cycle_inton <= 0:
    star_in_9cycle_inton += 9
print(f"隠遁の場合: 九星 = {star_in_9cycle_inton}")

print("\n=== 検証結果 ===")
print(f"陽遁として計算: {star_in_9cycle}（{['一白水星','二黒土星','三碧木星','四緑木星','五黄土星','六白金星','七赤金星','八白土星','九紫火星'][star_in_9cycle-1]}）")
print(f"隠遁として計算: {star_in_9cycle_inton}（{['一白水星','二黒土星','三碧木星','四緑木星','五黄土星','六白金星','七赤金星','八白土星','九紫火星'][star_in_9cycle_inton-1]}）")

# ユーザーの期待値は「六白金星（6）」なので、
# 隠遁として計算するか、または陽遁でも開始値が異なる流派がある可能性

print("\n=== 別の計算方法：陽遁の甲子日開始値を「五黄土星」とする場合 ===")
# 一部の流派では甲子日を五黄土星（中宮）として計算する
star_from_5 = (5 + days_in_cycle) % 9
if star_from_5 == 0:
    star_from_5 = 9
print(f"甲子=五黄として陽遁: {star_from_5}（{['一白水星','二黒土星','三碧木星','四緑木星','五黄土星','六白金星','七赤金星','八白土星','九紫火星'][star_from_5-1]}）")

star_from_5_inton = (5 - days_in_cycle) % 9
if star_from_5_inton <= 0:
    star_from_5_inton += 9
print(f"甲子=五黄として隠遁: {star_from_5_inton}（{['一白水星','二黒土星','三碧木星','四緑木星','五黄土星','六白金星','七赤金星','八白土星','九紫火星'][star_from_5_inton-1]}）")
