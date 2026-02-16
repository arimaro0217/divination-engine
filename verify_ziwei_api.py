
import sys
import os
import json
from datetime import datetime

# パス設定
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'divination_engine'))

try:
    from src.modules.eastern.ziwei_api import ZiweiAPI
except ImportError:
    print("Error: Could not import ZiweiAPI. Check paths.")
    sys.exit(1)

def test_api_structure():
    print("Testing ZiweiAPI response structure...")
    api = ZiweiAPI()
    
    # テストデータ: 1992年2月17日 17:18 東京 男性
    result = api.generate_chart(
        birth_year=1992,
        birth_month=2,
        birth_day=17,
        birth_hour=17,
        birth_minute=18,
        longitude=139.76,
        latitude=35.68,
        gender="male"
    )
    
    # 必須キーの確認
    required_keys = ['basic_info', 'palaces', 'grid_layout']
    missing_keys = [k for k in required_keys if k not in result]
    
    if missing_keys:
        print(f"FAILED: Missing top-level keys: {missing_keys}")
        return

    # basic_info内の確認
    basic_info = result.get('basic_info', {})
    required_basic = ['life_master', 'body_master', 'bureau_name', 'ziwei_position', 'lunar_date']
    missing_basic = [k for k in required_basic if k not in basic_info]
    
    if missing_basic:
        print(f"FAILED: Missing basic_info keys: {missing_basic}")
    else:
        print("SUCCESS: usage of basic_info keys confirmed.")
        print(f"Life Master: {basic_info.get('life_master')}")
        print(f"Body Master: {basic_info.get('body_master')}")
        print(f"Bureau: {basic_info.get('bureau_name')}")

    # JSON出力の一部を表示
    print("\n--- JSON Output Sample (Basic Info) ---")
    print(json.dumps(basic_info, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_api_structure()
