"""
統合占いアプリ - フロントエンド統合テストスクリプト

Pythonバックエンドの高度数秘術APIを使用して
JSON出力を生成し、フロントエンドで表示できるか確認
"""
import sys
import io
import json
from pathlib import Path
from datetime import datetime

# Windows UTF- 8 output
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from src.modules.numerology.num_api import NumerologyAPI


def generate_frontend_test_data():
    """フロントエンド用のテストデータ生成"""
    print("="*60)
    print("高度数秘術API - フロントエンド統合テスト")
    print("="*60)
    
    api = NumerologyAPI()
    
    # サンプルデータ
    test_cases = [
        {
            "name": "Mary Johnson",
            "birth": datetime(1992, 2, 17, 12, 0),
            "system": "pythagorean",
            "output": "test_numerology_mary.json"
        },
        {
            "name": "やまだ たろう",
            "birth": datetime(1990, 5, 5, 14, 30),
            "system": "pythagorean",
            "output": "test_numerology_yamada.json"
        },
        {
            "name": "John Smith",
            "birth": datetime(1985, 12, 25, 8, 0),
            "system": "chaldean",
            "output": "test_numerology_john_chaldean.json"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}/3] {test['name']} ({test['system']})")
        
        try:
            result = api.generate_full_report(
                name_input=test["name"],
                birth_date=test["birth"],
                system=test["system"]
            )
            
            # Console output (summary)
            print(f"  Life Path: {result['core_numbers']['life_path']['number']}")
            print(f"  Destiny: {result['core_numbers']['destiny']['number']}")
            print(f"  Soul Urge: {result['core_numbers']['soul_urge']['number']}")
            print(f"  Personal Year: {result['forecasting']['personal_year']['number']}")
            
            if result['core_numbers']['life_path']['planet_status']:
                planet_status = result['core_numbers']['life_path']['planet_status']
                print(f"  Planet: {result['core_numbers']['life_path']['ruler_planet']}")
                print(f"  Sign: {planet_status['sign']}, Dignity: {planet_status['dignity']}")
            
            # Save to file
            output_path = Path(__file__).parent.parent / 'webapp' / 'test_data' / test['output']
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Saved to: {output_path}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("Test data generation complete!")
    print("="*60)


if __name__ == '__main__':
    generate_frontend_test_data()
