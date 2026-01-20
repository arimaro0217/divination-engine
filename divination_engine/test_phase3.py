"""
フェーズ3モジュールの簡易テスト
紫微斗数と宿曜占星術の動作確認
"""
import sys
import io
from datetime import datetime
from zoneinfo import ZoneInfo

# Windows環境でのUTF-8出力対応
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# モジュールのインポート
from src.modules.eastern.ziwei import ZiWeiEngine
from src.modules.eastern.sukuyou import SukuyouEngine


def test_ziwei():
    """紫微斗数のテスト"""
    print("=" * 60)
    print("紫微斗数テスト")
    print("=" * 60)
    
    # テストデータ: 1992年2月17日 17:18 JST
    birth_dt = datetime(1992, 2, 17, 17, 18, tzinfo=ZoneInfo("Asia/Tokyo"))
    
    engine = ZiWeiEngine()
    result = engine.calculate(birth_dt)
    
    if result.success:
        print(f"[OK] 計算成功")
        print(f"  旧暦: {result.lunar_date}")
        print(f"  命宮: {result.ming_palace}")
        print(f"  身宮: {result.body_palace}")
        print(f"  四化星: {result.four_transformations}")
        print(f"\n  主星配置:")
        for branch, stars in result.main_stars.items():
            if stars:
                print(f"    {branch}宮: {', '.join(stars)}")
    else:
        print(f"[NG] 計算失敗: {result.error_message}")
    
    print()


def test_sukuyou():
    """宿曜占星術のテスト"""
    print("=" * 60)
    print("宿曜占星術テスト")
    print("=" * 60)
    
    # テストデータ: 1992年2月17日 17:18 JST
    birth_dt = datetime(1992, 2, 17, 17, 18, tzinfo=ZoneInfo("Asia/Tokyo"))
    
    engine = SukuyouEngine()
    result = engine.calculate(birth_dt)
    
    if result.success:
        print(f"[OK] 計算成功")
        print(f"  本命宿: {result.natal_mansion}（第{result.mansion_number}宿）")
        print(f"  属性: {result.element}")
        
        # 詳細情報を取得
        details = engine.get_mansion_details(result.mansion_number - 1)
        if details:
            print(f"  読み: {details.get('reading', 'N/A')}")
            print(f"  七曜: {details.get('weekday', 'N/A')}")
    else:
        print(f"[NG] 計算失敗: {result.error_message}")
    
    print()


def test_compatibility():
    """宿曜の相性判定テスト"""
    print("=" * 60)
    print("宿曜の相性判定テスト")
    print("=" * 60)
    
    engine = SukuyouEngine()
    
    # テスト: 昴宿（0）と畢宿（1）の相性
    mansion1 = 0  # 昴宿
    mansion2 = 1  # 畢宿
    
    compatibility = engine.calc_compatibility(mansion1, mansion2)
    relationship = engine.calc_relationship_type(mansion1, mansion2)
    
    print(f"  昴宿（第1宿）と 畢宿（第2宿）の相性:")
    print(f"    相性: {compatibility}")
    print(f"    距離: {relationship['distance']}")
    print(f"    範囲: {relationship['range']}")
    
    print()


if __name__ == "__main__":
    print("\n### フェーズ3モジュール動作確認 ###\n")
    
    try:
        test_ziwei()
    except Exception as e:
        print(f"紫微斗数テストでエラー: {e}\n")
    
    try:
        test_sukuyou()
    except Exception as e:
        print(f"宿曜占星術テストでエラー: {e}\n")
    
    try:
        test_compatibility()
    except Exception as e:
        print(f"相性判定テストでエラー: {e}\n")
    
    print("=" * 60)
    print("テスト完了")
    print("=" * 60)
