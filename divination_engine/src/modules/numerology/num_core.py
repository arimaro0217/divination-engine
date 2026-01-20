"""
数秘術コア計算エンジン
Numerology Core Engine

基本的な計算関数を提供：
- 数値還元（マスターナンバー保持）
- テキスト→数値変換
- Y

の母音/子音判定（最重要）
- 日本語ローマ字変換
- カルマナンバー検出
"""
from typing import List, Tuple, Optional, Set
from datetime import datetime
import sys
import io

# Windows環境でのUTF-8出力対応（安全版）
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from ...const.numerology_const import (
    PYTHAGOREAN_TABLE,
    CHALDEAN_TABLE,
    VOWELS,
    MASTER_NUMBERS,
    KARMIC_NUMBERS
)


class NumerologyCore:
    """
    数秘術コア計算クラス
    
    基本的な計算ロジックを提供
    """
    
    def __init__(self):
        pass
    
    def reduce_number(self, n: int, keep_master: bool = True) -> int:
        """
        数値を1桁に還元
        
        Args:
            n: 還元する数値
            keep_master: マスターナンバー（11,22,33,44）を保持するか
            
        Returns:
            還元された数値
            
        Examples:
            >>> reduce_number(29)  # 2+9=11 (Master)
            11
            >>> reduce_number(38)  # 3+8=11 (Master)
            11
            >>> reduce_number(29, keep_master=False)  # 2+9=11, 1+1=2
            2
        """
        while n > 9:
            if keep_master and n in MASTER_NUMBERS:
                return n
            n = sum(int(d) for d in str(n))
        return n
    
    def text_to_number(
        self, 
        text: str, 
        system: str = 'pythagorean'
    ) -> List[int]:
        """
        テキストを数値配列に変換
        
        Args:
            text: 変換するテキスト（アルファベット）
            system: 'pythagorean' or 'chaldean'
            
        Returns:
            数値のリスト
            
        Examples:
            >>> text_to_number("JOHN", "pythagorean")
            [1, 6, 8, 5]
            >>> text_to_number("JOHN", "chaldean")
            [1, 7, 5, 5]
        """
        table = CHALDEAN_TABLE if system == 'chaldean' else PYTHAGOREAN_TABLE
        text = text.upper().replace(' ', '').replace('-', '')
        
        return [table.get(c, 0) for c in text if c.isalpha()]
    
    def analyze_y_vowel(self, word: str, index: int) -> bool:
        """
        Yが母音として振る舞うか判定（数秘術の最難関ポイント）
        
        ルール：
        1. 単語の先頭 → 子音
        2. 母音に挟まれている → 子音
        3. 子音の後で、次が子音または単語末 → 母音
        4. 子音の後で、次が母音 → 場合による（通常は子音）
        
        Args:
            word: 単語（大文字）
            index: Yの位置
            
        Returns:
            True: 母音として扱う
            False: 子音として扱う
            
        Examples:
            >>> analyze_y_vowel("MARY", 3)  # MA-R[Y]
            True  # 子音の後、単語末 → 母音
            
            >>> analyze_y_vowel("YELLOW", 0)  # [Y]ELLOW
            False  # 先頭 → 子音
            
            >>> analyze_y_vowel("KAYAK", 2)  # KA[Y]AK
            False  # 母音に挟まれている → 子音
            
            >>> analyze_y_vowel("YOLANDA", 0)  # [Y]OLANDA
            False  # 先頭 → 子音
            
            >>> analyze_y_vowel("SYDNEY", 1)  # S[Y]DNEY
            True  # SY-DNEY, 子音の後で次が子音 → 母音
        """
        word = word.upper()
        
        # ルール1: 先頭のYは常に子音
        if index == 0:
            return False
        
        # 前後の文字を取得
        prev_char = word[index - 1] if index > 0 else ''
        next_char = word[index + 1] if index < len(word) - 1 else ''
        
        # 前の文字が母音かチェック
        prev_is_vowel = prev_char in VOWELS
        next_is_vowel = next_char in VOWELS if next_char else False
        
        # ルール2: 母音に挟まれている → 子音
        if prev_is_vowel and next_is_vowel:
            return False
        
        # ルール3: 子音の後で、かつ（単語末 or 次が子音） → 母音
        if not prev_is_vowel:
            # 単語末
            if next_char == '':
                return True
            # 次が子音
            if not next_is_vowel:
                return True
        
        # デフォルト: 子音として扱う
        # （前が母音で、次が子音または末尾の場合も子音扱いが一般的）
        return False
    
    def separate_vowels_consonants(
        self, 
        text: str, 
        system: str = 'pythagorean'
    ) -> Tuple[List[int], List[int]]:
        """
        名前を母音と子音に分離し、それぞれの数値を返す
        
        Args:
            text: 名前（アルファベット）
            system: 'pythagorean' or 'chaldean'
            
        Returns:
            (母音の数値リスト, 子音の数値リスト)
            
        Examples:
            >>> separate_vowels_consonants("MARY")
            ([1, 7], [4, 9])  # A,Y (vowels) | M,R (consonants)
        """
        table = CHALDEAN_TABLE if system == 'chaldean' else PYTHAGOREAN_TABLE
        text = text.upper().replace(' ', '').replace('-', '')
        
        vowels = []
        consonants = []
        
        for i, c in enumerate(text):
            if not c.isalpha():
                continue
                
            value = table.get(c, 0)
            if value == 0:
                continue
            
            # Yの特殊処理
            if c == 'Y':
                if self.analyze_y_vowel(text, i):
                    vowels.append(value)
                else:
                    consonants.append(value)
            # 通常の母音
            elif c in VOWELS:
                vowels.append(value)
            # 子音
            else:
                consonants.append(value)
        
        return vowels, consonants
    
    def detect_karmic(
        self, 
        birth_date: datetime, 
        name_numbers: List[int]
    ) -> List[int]:
        """
        カルマナンバー（13,14,16,19）を検出
        
        生年月日と名前から出現する数値パターンを分析
        
        Args:
            birth_date: 生年月日
            name_numbers: 名前から算出された数値リスト
            
        Returns:
            カルマナンバーのリスト
        """
        karmic_found = []
        
        # 生年月日の数字をすべて結合
        date_str = birth_date.strftime('%Y%m%d')
        all_numbers = [int(d) for d in date_str] + name_numbers
        
        # 連続する2桁の組み合わせをチェック
        for i in range(len(date_str) - 1):
            two_digit = int(date_str[i:i+2])
            if two_digit in KARMIC_NUMBERS and two_digit not in karmic_found:
                karmic_found.append(two_digit)
        
        return sorted(karmic_found)
    
    def kana_to_romaji(self, text: str) -> str:
        """
        かな（ひらがな/カタカナ）をヘボン式ローマ字に変換
        
        簡易辞書による変換（完全実装にはpykakasiライブラリ推奨）
        
        Args:
            text: 日本語テキスト
            
        Returns:
            ローマ字（大文字）
        """
        # 簡易変換テーブル（ひらがな）
        HIRAGANA_TO_ROMAJI = {
            'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
            'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
            'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
            'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
            'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
            'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
            'だ': 'da', 'ぢ': 'ji', 'づ': 'zu', 'で': 'de', 'ど': 'do',
            'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
            'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
            'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
            'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
            'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
            'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
            'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
            'わ': 'wa', 'を': 'wo', 'ん': 'n',
            'ゃ': 'ya', 'ゅ': 'yu', 'ょ': 'yo',
            'っ': '',  # 促音は次の子音を重ねる（簡略化）
            'ー': '',  # 長音記号
            ' ': ' ', '　': ' '
        }
        
        # カタカナも同じマッピング（ひらがなに変換してから処理）
        KATAKANA_TO_HIRAGANA = str.maketrans(
            'アイウエオカキクケコガギグゲゴサシスセソザジズゼゾタチツテトダヂヅデドナニヌネノハヒフヘホバビブベボパピプペポマミムメモヤユヨラリルレロワヲンャュョッー',
            'あいうえおかきくけこがぎぐげごさしすせそざじずぜぞたちつてとだぢづでどなにぬねのはひふへほばびぶべぼぱぴぷぺぽまみむめもやゆよらりるれろわをんゃゅょっー'
        )
        
        # カタカナをひらがなに変換
        text = text.translate(KATAKANA_TO_HIRAGANA)
        
        # ローマ字変換
        romaji = ''
        i = 0
        while i < len(text):
            # 2文字先読み（拗音：きゃ、しゅ等）
            if i < len(text) - 1:
                two_char = text[i:i+2]
                # 拗音の特殊処理
                if two_char in ['きゃ', 'きゅ', 'きょ']:
                    romaji += two_char.replace('き', 'k').replace('ゃ', 'ya').replace('ゅ', 'yu').replace('ょ', 'yo')
                    i += 2
                    continue
                elif two_char in ['しゃ', 'しゅ', 'しょ']:
                    romaji += two_char.replace('し', 'sh').replace('ゃ', 'a').replace('ゅ', 'u').replace('ょ', 'o')
                    i += 2
                    continue
                elif two_char in ['ちゃ', 'ちゅ', 'ちょ']:
                    romaji += two_char.replace('ち', 'ch').replace('ゃ', 'a').replace('ゅ', 'u').replace('ょ', 'o')
                    i += 2
                    continue
            
            # 1文字ずつ変換
            char = text[i]
            romaji += HIRAGANA_TO_ROMAJI.get(char, char)
            i += 1
        
        return romaji.upper()
    
    def is_japanese(self, text: str) -> bool:
        """
        テキストが日本語（ひらがな/カタカナ/漢字）を含むか判定
        
        Args:
            text: テキスト
            
        Returns:
            True: 日本語を含む
        """
        for char in text:
            # ひらがな: U+3040-309F
            # カタカナ: U+30A0-30FF
            # 漢字:     U+4E00-9FFF
            code = ord(char)
            if (0x3040 <= code <= 0x309F) or \
               (0x30A0 <= code <= 0x30FF) or \
               (0x4E00 <= code <= 0x9FFF):
                return True
        return False
