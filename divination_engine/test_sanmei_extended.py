"""
算命学モジュールのテスト
拡張された機能（天中殺期間、数理法、位相法）の動作確認
"""
import sys
import io
from datetime import datetime
from zoneinfo import ZoneInfo

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.modules.eastern.sanmei import SanmeiCalculator

# 算命学計算
calculator = SanmeiCalculator()

# テストデータ: 1992年2月17日 17:18
birth_dt = datetime(1992, 2, 17, 17, 18, tzinfo=ZoneInfo("Asia/Tokyo"))

print("="*70)
print("算命学 統合テスト")
print("="*70)
print(f"\n生年月日時: 1992年2月17日 17:18 JST")
print(f"氏名: 安瀬 諒（テスト）\n")

# 計算実行
result = calculator.calculate(birth_dt)

# 結果表示
print("【陰占：四柱干支】")
print(f"年柱: {result.four_pillars.year.heavenly_stem}{result.four_pillars.year.earthly_branch}")
print(f"月柱: {result.four_pillars.month.heavenly_stem}{result.four_pillars.month.earthly_branch}")
print(f"日柱: {result.four_pillars.day.heavenly_stem}{result.four_pillars.day.earthly_branch}")
print(f"時柱: {result.four_pillars.hour.heavenly_stem}{result.four_pillars.hour.earthly_branch}")

print(f"\n【陽占：人体星図】")
print("十大主星:")
for position, star in result.main_stars.items():
    print(f"  {position}: {star}")

print("\n十二大従星:")
for position, star in result.sub_stars.items():
    print(f"  {position}: {star}")

print("\n人体星図:")
for part, star in result.body_chart.items():
    print(f"  {part}: {star}")

print(f"\n【天中殺】")
print(f"種類: {result.void_group_name}")
print(f"地支: {', '.join(result.void_branches)}")
print("期間:")
for period_type, period_value in result.void_period.items():
    print(f"  {period_type}: {period_value}")

print(f"\n【数理法：エネルギー数値】")
for key, value in result.energy_values.items():
    print(f"  {key}: {value}")

print(f"\n【位相法】")
print("合法（良い組み合わせ）:")
for phase in result.phases.get("合法", []):
    print(f"  • {phase}")

print("\n散法（悪い組み合わせ）:")
for phase in result.phases.get("散法", []):
    print(f"  • {phase}")

print("\n" + "="*70)
print("テスト完了")
print("="*70)
