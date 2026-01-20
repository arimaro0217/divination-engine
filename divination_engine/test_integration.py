"""
統合占いエンジン 総合テスト
"""
from datetime import datetime

print('=== 統合テスト ===')

# 1. Ziwei (紫微斗数)
try:
    from src.modules.eastern.ziwei_api import generate_ziwei_chart
    chart = generate_ziwei_chart(1992, 2, 17, 12, 0)
    print(f"1. 紫微斗数: {chart['basic_info']['bureau_name']} / 命宮: {chart['basic_info']['life_palace_branch']}宮")
except Exception as e:
    print(f"1. 紫微斗数: ERROR - {e}")

# 2. Jyotish (インド占星術)
try:
    from src.modules.indian.jyotish_engine import JyotishAPI
    api = JyotishAPI()
    chart = api.generate_chart(1992, 2, 17, 12, 0, 35.68, 139.76)
    print(f"2. Jyotish: Lagna {chart['meta']['ascendant']['sign']}")
except Exception as e:
    print(f"2. Jyotish: ERROR - {e}")

# 3. Sanmei (算命学)
try:
    from src.modules.eastern.sanmei import SanmeiCalculator
    calc = SanmeiCalculator(datetime(1992, 2, 17, 12, 0), 35.68, 139.76)
    result = calc.get_full_analysis()
    print(f"3. 算命学: {result['tenchusatsu']['type']}")
except Exception as e:
    print(f"3. 算命学: ERROR - {e}")

# 4. Kigaku (九星気学)
try:
    from src.modules.eastern.kigaku_core import KigakuCalendar
    kigaku = KigakuCalendar()
    year_star = kigaku.get_year_star(datetime(1992, 2, 17))
    print(f"4. 九星気学: 本命星 {year_star}")
except Exception as e:
    print(f"4. 九星気学: ERROR - {e}")

# 5. Sukuyo (宿曜占星術)
try:
    from src.modules.eastern.sukuyo_core import SukuyouEngine
    sukuyo = SukuyouEngine()
    result = sukuyo.calculate(1992, 2, 17, 35.68, 139.76)
    print(f"5. 宿曜占星術: {result['nakshatra']['name_ja']}")
except Exception as e:
    print(f"5. 宿曜占星術: ERROR - {e}")

print('\n=== テスト完了 ===')
