"""
紫微斗数 テストスクリプト
"""
import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import json

# 定数をインポート
from src.const import ziwei_const as zc

# 旧暦エンジンをテスト
print("=== 旧暦変換テスト ===")
try:
    from src.core.lunar_core import LunisolarEngine, LeapMonthMode
    
    engine = LunisolarEngine()
    test_date = datetime(1992, 2, 17, 12, 0)
    
    # 旧暦変換
    lunar = engine.convert_to_lunar(test_date)
    print(f"生年月日: {test_date}")
    print(f"旧暦: {lunar}")
    
    # 時辰
    true_solar = engine.get_true_solar_time(test_date, 139.76)
    hour_branch = engine.get_chinese_hour(true_solar)
    print(f"真太陽時: {true_solar}")
    print(f"時辰: {hour_branch.branch_name}の刻")
    
except Exception as e:
    print(f"旧暦テストエラー: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 命盤構築テスト ===")
try:
    from src.modules.eastern.ziwei_logic import ZiweiBuilder, DecadeLuckCalculator
    from src.core.lunar_core import ChineseHour
    
    builder = ZiweiBuilder()
    
    # 仮の旧暦データ
    class MockLunarDate:
        year = 1992
        month = 1
        day = 14
        is_leap_month = False
        def __str__(self):
            return f"旧暦{self.year}年{self.month}月{self.day}日"
    
    class MockHourBranch:
        branch_index = 6  # 午の刻
        branch_name = "午"
        is_early_rat = False
    
    lunar_date = MockLunarDate()
    hour_branch = MockHourBranch()
    
    # 命宮を計算
    life_palace = builder.determine_life_palace(lunar_date.month, hour_branch.branch_index)
    body_palace = builder.determine_body_palace(lunar_date.month, hour_branch.branch_index)
    
    print(f"命宮: {zc.BRANCHES[life_palace]}")
    print(f"身宮: {zc.BRANCHES[body_palace]}")
    
    # 五行局を計算
    year_stem_idx = (1992 - 4) % 10  # 壬
    palace_stem = builder.calculate_palace_stem(life_palace, year_stem_idx)
    bureau = builder.calculate_bureau(palace_stem, life_palace)
    print(f"命宮天干: {palace_stem}")
    print(f"五行局: {zc.JU_NAMES[bureau]}")
    
    # 紫微星の位置
    ziwei_pos = builder.calculate_ziwei_position(lunar_date.day, bureau)
    tianfu_pos = builder.calculate_tianfu_position(ziwei_pos)
    print(f"紫微星: {zc.BRANCHES[ziwei_pos]}")
    print(f"天府星: {zc.BRANCHES[tianfu_pos]}")
    
    # 四化
    year_stem = zc.STEMS[year_stem_idx]
    sihua = builder.apply_sihua(year_stem)
    print(f"年干: {year_stem}")
    print(f"四化: {sihua}")
    
    # 大限
    decade_calc = DecadeLuckCalculator()
    decade_luck = decade_calc.calculate_decade_luck(bureau, "male", year_stem, life_palace)
    print(f"\n大限:")
    for luck in decade_luck[:3]:
        print(f"  {luck['branch']}: {luck['period']}")
    
    print("\n=== 紫微斗数 実装テスト完了 ===")
    
except Exception as e:
    print(f"命盤構築テストエラー: {e}")
    import traceback
    traceback.print_exc()
