"""
算命学システムの簡易動作テスト

定数の確認と基本的な関数のテストを行います。
"""

import sys
import io

# Windows環境でのUTF-8出力対応
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# プロジェクトのパスを追加
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

from const import sanmei_const as sc
import math


def print_section(title: str):
    """セクションヘッダ出力"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_constants():
    """定数のテスト"""
    print_section("【テスト1】定数の確認")
    
    print(f"\n六十干支の数: {len(sc.SIXTY_GANZHI)}")
    print(f"最初の10干支: {', '.join(sc.SIXTY_GANZHI[:10])}")
    
    print(f"\n天干: {', '.join(sc.STEMS)}")
    print(f"地支: {', '.join(sc.BRANCHES)}")
    
    print(f"\n五行: {sc.WuXing.WOOD}, {sc.WuXing.FIRE}, {sc.WuXing.EARTH}, {sc.WuXing.METAL}, {sc.WuXing.WATER}")


def test_ganzhi_angles():
    """干支の角度テストget"""
    print_section("【テスト2】宇宙盤の角度計算")
    
    test_ganzhi = ["甲子", "甲午", "甲寅", "癸亥"]
    
    print("\n干支 -> 角度")
    for gz in test_ganzhi:
        angle = sc.get_ganzhi_angle(gz)
        print(f"  {gz}: {angle:>6.1f}度")


def test_zanggan():
    """蔵干のテスト"""
    print_section("【テスト3】算命学の蔵干（二十八元）")
    
    print("\n地支 -> 本元, 中元, 初元")
    for branch in sc.BRANCHES:
        zanggan = sc.SANMEI_ZANGGAN[branch]
        hongen = zanggan["本元"]
        chugen = zanggan["中元"] if zanggan["中元"] else "-"
        shoben = zanggan["初元"] if zanggan["初元"] else "-"
        print(f"  {branch}: 本元={hongen}, 中元={chugen}, 初元={shoben}")


def test_main_stars():
    """十大主星のテスト"""
    print_section("【テスト4】十大主星の計算テーブル")
    
    print("\n主星の種類:")
    print(f"  {sc.TenMainStars.KANSAKU} (比和・陽)")
    print(f"  {sc.TenMainStars.SEKIMON} (比和・陰)")
    print(f"  {sc.TenMainStars.HOUKAKU} (洩気・陽)")
    print(f"  {sc.TenMainStars.CHOUSHO} (洩気・陰)")
    print(f"  {sc.TenMainStars.ROKUSON} (受生・陽)")
    print(f"  {sc.TenMainStars.SHIROKU} (受生・陰)")
    print(f"  {sc.TenMainStars.SHAKI} (剋出・陽)")
    print(f"  {sc.TenMainStars.KENGYUU} (剋出・陰)")
    print(f"  {sc.TenMainStars.RYUKOU} (生出・陽)")
    print(f"  {sc.TenMainStars.GYOKUDOU} (生出・陰)")
    
    print(f"\n主星テーブルのエントリー数: {len(sc.MAIN_STAR_TABLE)}")


def test_sub_stars():
    """十二大従星のテスト"""
    print_section("【テスト5】十二大従星")
    
    print("\n従星とエネルギー点数:")
    for star, score in sc.SUBSTAR_SCORES.items():
        print(f"  {star}: {score:>2d}点")


def test_tenchusatsu():
    """天中殺のテスト"""
    print_section("【テスト6】天中殺の種類")
    
    print("\n天中殺 -> 対応する地支:")
    for t_type, branches in sc.TENCHUSATSU_TYPES.items():
        print(f"  {t_type}: {', '.join(branches)}")


def test_uchuban_visualization():
    """宇宙盤の可視化テスト"""
    print_section("【テスト7】宇宙盤の座標計算と可視化")
    
    # テストデータ
    year_ganzhi = "壬申"
    month_ganzhi = "壬寅"
    day_ganzhi = "癸亥"
    
    print(f"\nテストデータ:")
    print(f"  年柱: {year_ganzhi}")
    print(f"  月柱: {month_ganzhi}")
    print(f"  日柱: {day_ganzhi}")
    
    # 各干支の角度と座標を計算
    print("\n各干支の座標:")
    ganzhi_list = [(year_ganzhi, "Year"), (month_ganzhi, "Month"), (day_ganzhi, "Day")]
    
    coords = []
    for gz, label in ganzhi_list:
        angle = sc.get_ganzhi_angle(gz)
        angle_rad = math.radians(angle)
        x = math.cos(angle_rad)
        y = math.sin(angle_rad)
        coords.append((x, y))
        print(f"  {label} ({gz}): 角度={angle:>6.1f}°, X={x:>8.4f}, Y={y:>8.4f}")
    
    # 三角形の面積を計算
    x1, y1 = coords[0]
    x2, y2 = coords[1]
    x3, y3 = coords[2]
    
    area = abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)
    print(f"\n三角形の面積: {area:.4f}")
    
    # 簡易的なASCIIアート表示
    print("\n簡易宇宙盤（ASCII）:")
    print("      北(90°)")
    print("        |")
    print("西(180°)--+--東(0°)")
    print("        |")
    print("      南(270°)")


def main():
    """メインテストルーチン"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 25 + "算命学定数テスト" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        test_constants()
        test_ganzhi_angles()
        test_zanggan()
        test_main_stars()
        test_sub_stars()
        test_tenchusatsu()
        test_uchuban_visualization()
        
        print_section("✓ 全テスト完了")
        print("\n全ての定数テストが正常に完了しました！\n")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
