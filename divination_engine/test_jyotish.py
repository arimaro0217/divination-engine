"""
ジョーティシュ（インド占星術）テストスクリプト
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import json

print("=== Jyotish Test ===\n")

# 定数テスト
print("--- Constants ---")
from src.const import jyotish_const as jc
print(f"Grahas: {len(jc.Graha)}")
print(f"Rashis: {len(jc.RASHI_NAMES_EN)}")
print(f"Nakshatras: {len(jc.NAKSHATRAS)}")
print(f"Dasha Order: {[jc.GRAHA_NAMES_EN[g] for g in jc.DASHA_ORDER]}")
print()

# コア計算テスト
print("--- Core Calculation ---")
try:
    from src.modules.indian.jyotish_engine import VedicAstroCore, DashaSystem, JyotishAPI
    
    core = VedicAstroCore()
    
    # 1992年2月17日 12:00 JST
    from datetime import timezone, timedelta
    test_dt = datetime(1992, 2, 17, 3, 0, tzinfo=timezone.utc)  # JST 12:00
    jd = core.datetime_to_jd(test_dt)
    
    # アヤナムサ値
    ayanamsa_val = core.get_ayanamsa_value(jd)
    print(f"Date: 1992-02-17 12:00 JST")
    print(f"Julian Day: {jd}")
    print(f"Ayanamsa (Lahiri): {ayanamsa_val:.4f} deg")
    
    # グラハ位置
    grahas = core.calculate_sidereal_planets(jd, 35.68, 139.76)
    
    print("\nGraha Positions (Sidereal):")
    for g in grahas[:5]:  # 最初の5つ
        print(f"  {g.graha.name}: {g.rashi_name} {g.degree_in_rashi:.2f} deg")
        print(f"    Nakshatra: {g.nakshatra_name} Pada {g.pada}")
        print(f"    D9 (Navamsha): {jc.RASHI_NAMES_EN[g.navamsha_rashi]}")
        print(f"    Dignity: {g.dignity}")
    
    # ラグナ
    lagna = core.calculate_lagna(jd, 35.68, 139.76)
    lagna_rashi = jc.get_rashi_from_longitude(lagna)
    print(f"\nLagna (Ascendant): {jc.RASHI_NAMES_EN[lagna_rashi]} {lagna % 30:.2f} deg")
    
except Exception as e:
    print(f"Core Test Error: {e}")
    import traceback
    traceback.print_exc()

# ダシャーテスト
print("\n--- Vimshottari Dasha ---")
try:
    dasha = DashaSystem()
    
    # 月の位置から計算
    moon = next(g for g in grahas if g.graha == jc.Graha.CHANDRA)
    birth = datetime(1992, 2, 17, 12, 0)
    
    dashas = dasha.calculate_vimshottari(moon.longitude, birth)
    
    print(f"Moon Nakshatra: {moon.nakshatra_name}")
    print(f"Nakshatra Lord: {jc.GRAHA_NAMES_EN[jc.NAKSHATRA_LORDS[moon.nakshatra]]}")
    
    print("\nFirst 5 Mahadashas:")
    for d in dashas[:5]:
        print(f"  {d['lord']}: {d['start_date']} to {d['end_date']} ({d['years']:.1f} years)")
    
    # 現在のダシャー
    current = dasha.get_current_dasha(dashas, datetime.now())
    if current:
        print(f"\nCurrent Dasha: {current['mahadasha']}/{current['antardasha']}")
    
except Exception as e:
    print(f"Dasha Test Error: {e}")
    import traceback
    traceback.print_exc()

# 完全チャート生成テスト
print("\n--- Full Chart Generation ---")
try:
    api = JyotishAPI()
    chart = api.generate_chart(
        1992, 2, 17, 12, 0,
        35.68, 139.76,
        tz_offset=9.0,
        ayanamsa="LAHIRI"
    )
    
    print(f"Ayanamsa: {chart['meta']['ayanamsa']} ({chart['meta']['ayanamsa_val']:.2f} deg)")
    print(f"Lagna: {chart['meta']['ascendant']['sign']} {chart['meta']['ascendant']['degree']:.1f} deg")
    print(f"Planets: {len(chart['planets'])}")
    print(f"D1 Chart populated: {sum(1 for v in chart['charts']['D1'].values() if v)}")
    print(f"D9 Chart populated: {sum(1 for v in chart['charts']['D9'].values() if v)}")
    
    if chart.get('current_dasha'):
        print(f"Current Period: {chart['current_dasha']}")
    
except Exception as e:
    print(f"API Test Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
