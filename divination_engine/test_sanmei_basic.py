"""
算命学モジュールの簡易テスト
"""
import sys
import io
from datetime import datetime
from zoneinfo import ZoneInfo

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.modules.eastern.sanmei import SanmeiCalculator

calculator = SanmeiCalculator()
birth_dt = datetime(1992, 2, 17, 17, 18, tzinfo=ZoneInfo("Asia/Tokyo"))

print("算命学 基本テスト")
print("="*50)

try:
    result = calculator.calculate(birth_dt)
    
    print("\n【陰占】")
    print(f"年柱: {result.four_pillars.year.heavenly_stem}{result.four_pillars.year.earthly_branch}")
    print(f"月柱: {result.four_pillars.month.heavenly_stem}{result.four_pillars.month.earthly_branch}")
    print(f"日柱: {result.four_pillars.day.heavenly_stem}{result.four_pillars.day.earthly_branch}")
    
    print(f"\n天中殺: {', '.join(result.void_branches)}")
    print(f"グループ: {result.void_group_name}")
    
    print("\n✓ 基本機能は動作中")
    
except Exception as e:
    print(f"✗ エラー: {e}")
    import traceback
    traceback.print_exc()
