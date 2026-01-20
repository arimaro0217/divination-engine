"""
宿曜占星術テストスクリプト
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import json

print("=== 宿曜占星術テスト ===\n")

# 定数テスト
print("--- 定数テスト ---")
from src.const import sukuyou_const as sk
print(f"二十七宿: {len(sk.MANSIONS)}宿")
print(f"先頭3宿: {sk.MANSIONS[:3]}")
print(f"相性マトリクス: {len(sk.COMPATIBILITY_MATRIX)}パターン")
print()

# 相性判定テスト
print("--- 相性判定テスト ---")
from src.modules.eastern.sukuyo_relationship import RelationshipEngine, DestinyMatrix

engine = RelationshipEngine()
destiny = DestinyMatrix()

# 角宿(11)と心宿(15)の相性
result = engine.calculate_compatibility(11, 15)
print(f"角宿 → 心宿:")
print(f"  相性タイプ: {result.relation_type}")
print(f"  距離: {result.distance}")
print(f"  距離タイプ: {result.distance_type}")
print(f"  主導権: {'自分' if result.is_active else '相手'}")
print()

# 安壊の方向性テスト
print("--- 安壊方向性テスト ---")
an_kai = engine.get_an_kai_direction(11, 18)  # 角宿と箕宿
print(f"角宿 → 箕宿: {an_kai}")
print()

# 円盤データテスト
print("--- 円盤データテスト ---")
mandala = engine.generate_mandala(0)  # 昴宿
print(f"円盤データ数: {len(mandala)}")
print(f"先頭3宿: {[m['shuku'] for m in mandala[:3]]}")
print()

# 日運テスト
print("--- 日運テスト ---")
fortune = destiny.get_daily_fortune(11, datetime(2026, 1, 12))
print(f"本命宿: 角宿（11）")
print(f"対象日: 2026年1月12日")
print(f"その日の宿: {fortune.day_mansion}")
print(f"運勢タイプ: {fortune.luck_type}")
print(f"吉凶: {fortune.fortune}")
print()

# 旧暦法テスト（lunar_coreが必要）
print("--- 旧暦法テスト ---")
try:
    from src.modules.eastern.sukuyo_core import SukuyoCalendar
    
    calendar = SukuyoCalendar()
    
    # 旧暦法で本命宿を計算
    mansion_idx, mansion_name = calendar.get_honmei_shuku(1, 14, False)
    print(f"旧暦1月14日の本命宿: {mansion_name}({mansion_idx})")
    
    mansion_idx, mansion_name = calendar.get_honmei_shuku(10, 24, False)
    print(f"旧暦10月24日の本命宿: {mansion_name}({mansion_idx})")
    
except Exception as e:
    print(f"旧暦法テストエラー: {e}")
    import traceback
    traceback.print_exc()

print("\n=== テスト完了 ===")
