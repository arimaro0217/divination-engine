"""
算命学システムの動作検証と可視化テスト

このスクリプトは以下を実行します：
1. 算命学計算エンジンの動作テスト
2. 人体星図データの検証
3. 宇宙盤の座標計算検証
4. Matplotlibによる宇宙盤の可視化と画像保存
"""

import sys
import io
from datetime import datetime
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Windows環境でのUTF-8出力対応
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# プロジェクトのパスを追加
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

from modules.eastern.sanmei import SanmeiCalculator
from const import sanmei_const as sc


def print_section(title: str):
    """セクションヘッダーを出力"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_basic_calculation():
    """基本的な算命学計算のテスト"""
    print_section("【テスト1】基本的な算命学計算")
    
    # テストデータ: 1992年2月17日 17:18 東京
    birth_dt = datetime(1992, 2, 17, 17, 18)
    latitude = 35.68
    longitude = 139.76
    
    print(f"\n生年月日時: {birth_dt.strftime('%Y年%m月%d日 %H:%M')}")
    print(f"出生地: 北緯{latitude}度, 東経{longitude}度（東京）\n")
    
    # 算命学計算
    calc = SanmeiCalculator(birth_dt, latitude, longitude)
    result = calc.get_full_analysis()
    
    # 基本情報の表示
    print("[基本情報]")
    print(f"  年柱: {result['basic']['year_ganzhi']}")
    print(f"  月柱: {result['basic']['month_ganzhi']}")
    print(f"  日柱: {result['basic']['day_ganzhi']}")
    if result['basic']['hour_ganzhi']:
        print(f"  時柱: {result['basic']['hour_ganzhi']}")
    
    return result


def test_jintai_seizu(result: dict):
    """人体星図のテスト"""
    print_section("【テスト2】人体星図（陽占）")
    
    print("\n[8つのスロット配置]")
    print(f"{'位置':<15} {'星タイプ':<12} {'星名':<15} {'スコア':<6} 意味")
    print("-" * 80)
    
    for slot in result['jintai_seizu']:
        position_label = {
            'north': '頭（北）',
            'left_shoulder': '左肩',
            'right_hand': '右手',
            'center': '胸（中央）',
            'left_hand': '左手',
            'south': '腹（南）',
            'right_foot': '右足',
            'left_foot': '左足'
        }.get(slot['position'], slot['position'])
        
        star_type_label = '主星' if slot['star_type'] == 'main_star' else '従星'
        score_str = f"{slot['score']:>2d}点" if slot['score'] is not None else "  -  "
        
        print(f"{position_label:<15} {star_type_label:<12} {slot['star_name']:<15} "
              f"{score_str:<6} {slot['meaning']}")
    
    # 従星の合計点数を計算
    total_score = sum(slot['score'] for slot in result['jintai_seizu'] 
                     if slot['score'] is not None)
    print(f"\n従星合計スコア: {total_score}点")


def test_uchuban(result: dict):
    """宇宙盤のテスト"""
    print_section("【テスト3】宇宙盤（行動領域）")
    
    print("\n[三点の座標]")
    print(f"{'位置':<8} {'干支':<8} {'角度':<10} {'X座標':<12} {'Y座標':<12}")
    print("-" * 60)
    
    for point in result['uchuban']['points']:
        print(f"{point['label']:<8} {point['ganzhi']:<8} {point['angle']:>6.1f}度  "
              f"{point['x']:>10.6f}  {point['y']:>10.6f}")
    
    print(f"\n三角形の面積: {result['uchuban']['area_size']:.4f}")
    print(f"行動パターン: {result['uchuban']['pattern_type']}")


def test_energy_score(result: dict):
    """エネルギースコアのテスト"""
    print_section("【テスト4】五行エネルギースコア（数理法）")
    
    print("\n[五行別エネルギー点数]")
    energy = result['energy_score']
    
    total = sum(energy.values())
    
    print(f"  木: {energy['木']:>3d}点 ({energy['木']/total*100:>5.1f}%)")
    print(f"  火: {energy['火']:>3d}点 ({energy['火']/total*100:>5.1f}%)")
    print(f"  土: {energy['土']:>3d}点 ({energy['土']/total*100:>5.1f}%)")
    print(f"  金: {energy['金']:>3d}点 ({energy['金']/total*100:>5.1f}%)")
    print(f"  水: {energy['水']:>3d}点 ({energy['水']/total*100:>5.1f}%)")
    print(f"  ───────────────")
    print(f"合計: {total:>3d}点")


def test_tenchusatsu(result: dict):
    """天中殺のテスト"""
    print_section("【テスト5】天中殺情報")
    
    tenchusatsu = result['tenchusatsu']
    
    print(f"\n天中殺のタイプ: {tenchusatsu['type']}")
    print(f"天中殺の支: {', '.join(tenchusatsu['branches'])}")
    
    if tenchusatsu['shukumei']:
        print(f"\n⚠ 宿命天中殺: {', '.join(tenchusatsu['shukumei'])}")
    else:
        print("\n宿命天中殺: なし")


def test_special_notes(result: dict):
    """異常干支のテスト"""
    print_section("【テスト6】特記事項（異常干支）")
    
    if result['special_notes']:
        print("\n異常干支が検出されました:")
        for note in result['special_notes']:
            print(f"  ⚠ {note}")
    else:
        print("\n異常干支: なし")


def visualize_uchuban(result: dict, filename: str = "uchuban_visualization.png"):
    """
    宇宙盤を可視化してPNG画像として保存
    
    Args:
        result: 算命学の計算結果
        filename: 保存するファイル名
    """
    print_section("【テスト7】宇宙盤の可視化")
    
    # 日本語フォントの設定（環境に応じて変更）
    plt.rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_aspect('equal')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_title(f"宇宙盤 - {result['basic']['year_ganzhi']}年生まれ", 
                 fontsize=16, fontweight='bold', pad=20)
    
    # 背景を白に
    ax.set_facecolor('#f8f8f8')
    
    # 円を描画
    circle = patches.Circle((0, 0), 1.0, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    
    # 60干支を円周上に配置
    for i, ganzhi in enumerate(sc.SIXTY_GANZHI):
        angle = sc.get_ganzhi_angle(ganzhi)
        angle_rad = np.radians(angle)
        
        # テキスト位置（円の外側）
        x_text = 1.15 * np.cos(angle_rad)
        y_text = 1.15 * np.sin(angle_rad)
        
        # 10干支ごとに強調
        if i % 10 == 0:
            ax.text(x_text, y_text, ganzhi, ha='center', va='center',
                   fontsize=9, fontweight='bold', color='red')
        else:
            ax.text(x_text, y_text, ganzhi, ha='center', va='center',
                   fontsize=7, color='gray', alpha=0.6)
    
    # 年・月・日の座標を取得
    points = result['uchuban']['points']
    year_point = next(p for p in points if p['label'] == 'Year')
    month_point = next(p for p in points if p['label'] == 'Month')
    day_point = next(p for p in points if p['label'] == 'Day')
    
    # 三角形を描画
    triangle = patches.Polygon([
        (year_point['x'], year_point['y']),
        (month_point['x'], month_point['y']),
        (day_point['x'], day_point['y'])
    ], fill=True, facecolor='lightblue', edgecolor='blue', 
       linewidth=3, alpha=0.4)
    ax.add_patch(triangle)
    
    # 各点にマーカーと ラベルを追加
    colors = {'Year': 'red', 'Month': 'green', 'Day': 'orange'}
    labels_jp = {'Year': '年', 'Month': '月', 'Day': '日'}
    
    for point in points:
        x, y = point['x'], point['y']
        color = colors[point['label']]
        label_jp = labels_jp[point['label']]
        
        # マーカー
        ax.plot(x, y, 'o', markersize=15, color=color, 
               markeredgecolor='black', markeredgewidth=2, zorder=5)
        
        # ラベル（干支 + 年/月/日）
        ax.text(x, y - 0.15, f"{point['ganzhi']}\n({label_jp})", 
               ha='center', va='top', fontsize=11, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=color, 
                        alpha=0.7, edgecolor='black'))
    
    # 中心に原点マーク
    ax.plot(0, 0, '+', markersize=15, color='black', markeredgewidth=2)
    
    # 情報テキストを追加
    info_text = (
        f"面積: {result['uchuban']['area_size']:.4f}\n"
        f"パターン: {result['uchuban']['pattern_type']}"
    )
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # グリッド
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(y=0, color='k', linewidth=0.5, alpha=0.3)
    ax.axvline(x=0, color='k', linewidth=0.5, alpha=0.3)
    
    # 保存
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\n✓ 宇宙盤の画像を保存しました: {filename}")
    plt.close()


def export_json(result: dict, filename: str = "sanmei_result.json"):
    """結果をJSON形式で保存"""
    print_section("【テスト8】JSON出力")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 算命学の計算結果をJSON形式で保存しました: {filename}")


def main():
    """メインテストルーチン"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "算命学システム - 動作検証と可視化テスト" + " " * 20 + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        # テスト実行
        result = test_basic_calculation()
        test_jintai_seizu(result)
        test_uchuban(result)
        test_energy_score(result)
        test_tenchusatsu(result)
        test_special_notes(result)
        
        # 可視化
        visualize_uchuban(result)
        
        # JSON出力
        export_json(result)
        
        # 完了
        print_section("✓ 全テスト完了")
        print("\n全てのテストが正常に完了しました！\n")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
