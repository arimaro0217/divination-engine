"""
西洋占星術テストスクリプト
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone, timedelta
import json

print("=== 西洋占星術テスト ===\n")

# 定数テスト
print("--- 定数テスト ---")
from src.const import astro_const as ac
print(f"天体数: {len(ac.BODY_NAMES_EN)}")
print(f"サイン数: {len(ac.SIGN_NAMES_EN)}")
print(f"ハウスシステム: {len(ac.HouseSystem)}")
print(f"アスペクト: {len(ac.MAJOR_ASPECTS)}メジャー + {len(ac.MINOR_ASPECTS)}マイナー")
print()

# コア計算テスト
print("--- コア計算テスト ---")
try:
    from src.modules.western.astro_core import AstroCore, AspectEngine
    
    core = AstroCore()
    
    # 1992年2月17日 12:00 UTC
    test_dt = datetime(1992, 2, 17, 3, 0, tzinfo=timezone.utc)  # JST 12:00
    jd = core.datetime_to_jd(test_dt)
    print(f"日時: {test_dt}")
    print(f"ユリウス日: {jd}")
    
    # 太陽の位置
    sun = core.calculate_body(jd, ac.CelestialBody.SUN)
    print(f"\n太陽:")
    print(f"  黄経: {sun.longitude:.4f}° ({sun.sign_name} {sun.sign_degree:.2f}°)")
    print(f"  速度: {sun.speed:.4f}°/日")
    print(f"  逆行: {sun.is_retrograde}")
    
    # 月の位置
    moon = core.calculate_body(jd, ac.CelestialBody.MOON, 35.68, 139.76, 0, topocentric=True)
    print(f"\n月（トポセントリック補正あり）:")
    print(f"  黄経: {moon.longitude:.4f}° ({moon.sign_name} {moon.sign_degree:.2f}°)")
    print(f"  速度: {moon.speed:.4f}°/日")
    
    # ハウス計算
    houses = core.calculate_houses(jd, 35.68, 139.76, ac.HouseSystem.PLACIDUS)
    print(f"\nハウス（プラシーダス、東京）:")
    print(f"  ASC: {houses.asc:.2f}° ({ac.format_degree(houses.asc)})")
    print(f"  MC: {houses.mc:.2f}° ({ac.format_degree(houses.mc)})")
    print(f"  1H: {houses.cusps[1]:.2f}°")
    print(f"  10H: {houses.cusps[10]:.2f}°")
    
except Exception as e:
    print(f"コア計算テストエラー: {e}")
    import traceback
    traceback.print_exc()

# アスペクトテスト
print("\n--- アスペクトテスト ---")
try:
    aspect_engine = AspectEngine()
    
    # 全天体位置
    positions = core.calculate_all_bodies(jd, 35.68, 139.76)
    print(f"天体数: {len(positions)}")
    
    # アスペクト検出
    aspects = aspect_engine.find_all_aspects(positions)
    print(f"検出アスペクト数: {len(aspects)}")
    
    if aspects:
        print("\n最初の3アスペクト:")
        for asp in aspects[:3]:
            print(f"  {asp['body_a']} {asp['type_ja']} {asp['body_b']}: {asp['orb']:.2f}° ({asp['state']})")
    
except Exception as e:
    print(f"アスペクトテストエラー: {e}")
    import traceback
    traceback.print_exc()

# ホロスコープ構築テスト
print("\n--- ホロスコープ構築テスト ---")
try:
    from src.modules.western.horoscope_logic import ChartBuilder, generate_natal_chart
    
    chart_data = generate_natal_chart(
        birth_year=1992,
        birth_month=2,
        birth_day=17,
        birth_hour=12,
        birth_minute=0,
        lat=35.68,
        lon=139.76,
        tz_offset=9.0,
        house_system="PLACIDUS"
    )
    
    print(f"ハウスシステム: {chart_data['meta']['house_system']}")
    print(f"天体数: {len(chart_data['points'])}")
    print(f"アスペクト数: {len(chart_data['aspects'])}")
    
    # 太陽と月の位置
    sun_point = next(p for p in chart_data['points'] if p['id'] == 'Sun')
    moon_point = next(p for p in chart_data['points'] if p['id'] == 'Moon')
    
    print(f"\n太陽: {sun_point['sign']} {sun_point['relative_degree']:.1f}° (第{sun_point['house']}ハウス)")
    print(f"月: {moon_point['sign']} {moon_point['relative_degree']:.1f}° (第{moon_point['house']}ハウス)")
    print(f"ASC: {ac.format_degree(chart_data['angles']['asc'])}")
    print(f"MC: {ac.format_degree(chart_data['angles']['mc'])}")
    
except Exception as e:
    print(f"ホロスコープテストエラー: {e}")
    import traceback
    traceback.print_exc()

print("\n=== テスト完了 ===")
