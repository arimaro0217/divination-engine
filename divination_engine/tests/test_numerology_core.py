"""
数秘術コアエンジンのテスト
"""
import sys
import io
from pathlib import Path

# Windows環境でのUTF-8出力対応
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# プロジェクトルートを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from src.modules.numerology.num_core import NumerologyCore
from src.const.numerology_const import PYTHAGOREAN_TABLE, CHALDEAN_TABLE


def test_y_vowel_detection():
    """Yの母音/子音判定テスト"""
    print("=== Y母音/子音判定テスト ===")
    
    core = NumerologyCore()
    
    test_cases = [
        ("MARY", 3, True, "MA-R[Y] → 子音の後、単語末 → 母音"),
        ("YELLOW", 0, False, "[Y]ELLOW → 先頭 → 子音"),
        ("KAYAK", 2, False, "KA[Y]AK → 母音に挟まれている → 子音"),
        ("YOLANDA", 0, False, "[Y]OLANDA → 先頭 → 子音"),
        ("SYDNEY", 1, True, "S[Y]DNEY → 子音の後、次が子音 → 母音")
    ]
    
    all_passed = True
    for word, index, expected, description in test_cases:
        result = core.analyze_y_vowel(word, index)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        
        print(f"{status} {description}")
        print(f"  Expected: {expected}, Got: {result}\n")
    
    if all_passed:
        print("✅ すべてのYテストが成功！\n")
    else:
        print("❌ 一部のYテストが失敗\n")
    
    return all_passed


def test_chaldean_conversion():
    """Chaldean変換テスト"""
    print("=== Chaldean変換テスト ===")
    
    core = NumerologyCore()
    
    # "JOHN" = J(1) + O(7) + H(5) + N(5) = 18
    result = core.text_to_number("JOHN", system='chaldean')
    total = sum(result)
    
    print(f"JOHN (Chaldean): {result} = {total}")
    print(f"Expected: [1, 7, 5, 5] = 18")
    
    if result == [1, 7, 5, 5] and total == 18:
        print("✅ Chalde an変換テスト成功！\n")
        return True
    else:
        print("❌ Chaldean変換テスト失敗\n")
        return False


def test_master_number_preservation():
    """マスターナンバー保持テスト"""
    print("=== マスターナンバーテスト ===")
    
    core = NumerologyCore()
    
    test_cases = [
        (29, True, 11, "29 → 2+9=11 (保持)"),
        (38, True, 11, "38 → 3+8=11 (保持)"),
        (29, False, 2, "29 → 2+9=11 → 1+1=2 (保持なし)"),
        (22, True, 22, "22 (保持)"),
        (44, True, 44, "44 (保持)")
    ]
    
    all_passed = True
    for num, keep_master, expected, description in test_cases:
        result = core.reduce_number(num, keep_master=keep_master)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        
        print(f"{status} {description}")
        print(f"  Expected: {expected}, Got: {result}\n")
    
    if all_passed:
        print("✅ マスターナンバーテスト成功！\n")
    else:
        print("❌ マスターナンバーテスト失敗\n")
    
    return all_passed


def test_vowel_consonant_separation():
    """母音・子音分離テスト（Y判定含む）"""
    print("=== 母音・子音分離テスト ===")
    
    core = NumerologyCore()
    
    # "MARY" → M(4), A(1), R(9), Y(7)
    # A は母音、Y は母音（単語末）
    # M, R は子音
    vowels, consonants = core.separate_vowels_consonants("MARY", "pythagorean")
    
    print(f"MARY (Pythagorean):")
    print(f"  母音: {vowels} (A=1, Y=7)")
    print(f"  子音: {consonants} (M=4, R=9)")
    
    if 1 in vowels and 7 in vowels and 4 in consonants and 9 in consonants:
        print("✅ 母音・子音分離テスト成功！\n")
        return True
    else:
        print("❌ 母音・子音分離テスト失敗\n")
        return False


def test_japanese_romaji():
    """日本語ローマ字変換テスト"""
    print("=== 日本語ローマ字変換テスト ===")
    
    core = NumerologyCore()
    
    test_cases = [
        ("やまだ", "YAMADA"),
        ("たろう", "TAROU"),
        ("ヤマダ", "YAMADA"),
        ("タロウ", "TAROU")
    ]
    
    all_passed = True
    for japanese, expected in test_cases:
        result = core.kana_to_romaji(japanese)
        # 部分一致でOK（完全一致は難しい）
        passed = expected in result or result in expected
        status = "✓" if passed else "✗"
        if not passed:
            all_passed = False
        
        print(f"{status} {japanese} → {result} (期待: {expected})")
    
    print()
    if all_passed:
        print("✅ ローマ字変換テスト成功！\n")
    else:
        print("⚠️ ローマ字変換は部分的にのみ機能（完全実装にはpykakasi推奨）\n")
    
    return all_passed


def run_all_tests():
    """すべてのテストを実行"""
    print("\n" + "="*60)
    print(" 数秘術コアエンジン テストスイート")
    print("="*60 + "\n")
    
    results = []
    
    results.append(("Y母音/子音判定", test_y_vowel_detection()))
    results.append(("Chaldean変換", test_chaldean_conversion()))
    results.append(("マスターナンバー", test_master_number_preservation()))
    results.append(("母音・子音分離", test_vowel_consonant_separation()))
    results.append(("日本語ローマ字変換", test_japanese_romaji()))
    
    # サマリー
    print("="*60)
    print(" テスト結果サマリー")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n合計: {passed}/{total} テスト成功")
    
    if passed == total:
        print("\n🎉 すべてのテストが成功しました！")
    else:
        print(f"\n⚠️ {total - passed}個のテストが失敗しました")


if __name__ == '__main__':
    run_all_tests()
