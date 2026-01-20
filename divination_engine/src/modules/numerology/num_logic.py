"""
数秘術ビジネスロジック
Numerology Business Logic

チャート構築、天体連携、ピナクル・チャレンジ計算
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys
import io

# Windows環境でのUTF-8出力対応（安全版）
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import swisseph as swe
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False
    print("Warning: pyswisseph not installed. Astro weighting will be disabled.")

from .num_core import NumerologyCore
from ...const.numerology_const import (
    MASTER_NUMBERS,
    PLANET_RULERS,
    PLANET_IDS,
    ZODIAC_SIGNS,
    DOMICILE,
    EXALTATION,
    DETRIMENT,
    FALL,
    NUMBER_MEANINGS,
    PERSONAL_YEAR_MEANINGS
)


class ChartBuilder:
    """
    数秘術チャート構築クラス
    
    Core Numbers, Cycles, Pinnacles を計算
    """
    
    def __init__(self, system: str = 'pythagorean'):
        """
        Args:
            system: 'pythagorean' or 'chaldean'
        """
        self.core = NumerologyCore()
        self.system = system
    
    # ============================================
    # Core Numbers
    # ============================================
    
    def calc_life_path(self, birth_date: datetime) -> Dict:
        """
        ライフパス数を計算
        
        方法: 生年月日の各要素を還元してから合算
        
        Args:
            birth_date: 生年月日
            
        Returns:
            {
                'number': int,
                'is_master': bool,
                'calculation': str  # 計算過程
            }
        """
        year = birth_date.year
        month = birth_date.month
        day = birth_date.day
        
        # 各要素を還元
        year_reduced = self.core.reduce_number(year)
        month_reduced = self.core.reduce_number(month)
        day_reduced = self.core.reduce_number(day)
        
        # 合算
        total = year_reduced + month_reduced + day_reduced
        final = self.core.reduce_number(total)
        
        calc_str = f"{year}→{year_reduced} + {month}→{month_reduced} + {day}→{day_reduced} = {total} → {final}"
        
        return {
            'number': final,
            'is_master': final in MASTER_NUMBERS,
            'calculation': calc_str
        }
    
    def calc_destiny(self, full_name: str) -> Dict:
        """
        Destiny (Expression) Number
        
        名前全体の数値合計
        
        Args:
            full_name: フルネーム
            
        Returns:
            {'number': int, 'is_master': bool}
        """
        numbers = self.core.text_to_number(full_name, self.system)
        total = sum(numbers)
        final = self.core.reduce_number(total)
        
        return {
            'number': final,
            'is_master': final in MASTER_NUMBERS
        }
    
    def calc_soul_urge(self, full_name: str) -> Dict:
        """
        Soul Urge (Heart's Desire)
        
        名前の母音のみの合計（Y判定を適用）
        
        Args:
            full_name: フルネーム
            
        Returns:
            {'number': int, 'is_master': bool,  'vowels': list}
        """
        vowels, _ = self.core.separate_vowels_consonants(full_name, self.system)
        total = sum(vowels)
        final = self.core.reduce_number(total) if total > 0 else 1
        
        return {
            'number': final,
            'is_master': final in MASTER_NUMBERS,
            'vowels': vowels
        }
    
    def calc_personality(self, full_name: str) -> Dict:
        """
        Personality Number
        
        名前の子音のみの合計
        
        Args:
            full_name: フルネーム
            
        Returns:
            {'number': int, 'is_master': bool, 'consonants': list}
        """
        _, consonants = self.core.separate_vowels_consonants(full_name, self.system)
        total = sum(consonants)
        final = self.core.reduce_number(total) if total > 0 else 1
        
        return {
            'number': final,
            'is_master': final in MASTER_NUMBERS,
            'consonants': consonants
        }
    
    def calc_maturity(self, life_path: int, destiny: int) -> int:
        """
        Maturity Number
        
        Life Path + Destiny
        
        Args:
            life_path: ライフパス数
            destiny: デスティニー数
            
        Returns:
            Maturity Number
        """
        total = life_path + destiny
        return self.core.reduce_number(total)
    
    def calc_birthday_number(self, day: int) -> int:
        """
        Birthday Number
        
        生まれた日（1-31）の特性
        
        Args:
            day: 日（1-31）
            
        Returns:
            Birthday Number (1-9 or Master)
        """
        return self.core.reduce_number(day)
    
    # ============================================
    # Cycles & Forecasting
    # ============================================
    
    def calc_personal_year(self, birth_date: datetime, target_year: int) -> int:
        """
        Personal Year Number
        
        (Birth Month + Birth Day + Target Year) を還元
        
        Args:
            birth_date: 生年月日
            target_year: 対象年
            
        Returns:
            Personal Year (1-9)
        """
        month = birth_date.month
        day = birth_date.day
        
        # 各要素を還元してから合算
        month_reduced = self.core.reduce_number(month, keep_master=False)
        day_reduced = self.core.reduce_number(day, keep_master=False)
        year_reduced = self.core.reduce_number(target_year, keep_master=False)
        
        total = month_reduced + day_reduced + year_reduced
        return self.core.reduce_number(total, keep_master=False)
    
    def calc_pinnacles(self, birth_date: datetime) -> List[Dict]:
        """
        4つのピナクル（Pinnacles）を計算
        
        人生の4つの頂点期のテーマ
        
        計算:
        - 1st: (birth_month + birth_day)
        - 2nd: (birth_day + birth_year)
        - 3rd: 1st + 2nd
        - 4th: (birth_month + birth_year)
        
        期間:
        - 1st: 0 ~ (36 - Life Path)歳
        - 2nd: 次の9年
        - 3rd: 次の9年
        - 4th: 以降
        
        Args:
            birth_date: 生年月日
            
        Returns:
            List of {
                'period': str,
                'number': int,
                'start_age': int,
                'end_age': int
            }
        """
        month = birth_date.month
        day = birth_date.day
        year = birth_date.year
        
        # ライフパス数を取得（期間計算用）
        life_path_data = self.calc_life_path(birth_date)
        life_path = life_path_data['number']
        if life_path in MASTER_NUMBERS:
            # マスターナンバーは基数に還元
            life_path = self.core.reduce_number(life_path, keep_master=False)
        
        # ピナクル計算
        month_r = self.core.reduce_number(month, keep_master=False)
        day_r = self.core.reduce_number(day, keep_master=False)
        year_r = self.core.reduce_number(year, keep_master=False)
        
        pinnacle_1 = self.core.reduce_number(month_r + day_r, keep_master=False)
        pinnacle_2 = self.core.reduce_number(day_r + year_r, keep_master=False)
        pinnacle_3 = self.core.reduce_number(pinnacle_1 + pinnacle_2, keep_master=False)
        pinnacle_4 = self.core.reduce_number(month_r + year_r, keep_master=False)
        
        # 期間計算
        first_end = 36 - life_path
        second_end = first_end + 9
        third_end = second_end + 9
        
        return [
            {
                'period': 'First Pinnacle',
                'number': pinnacle_1,
                'start_age': 0,
                'end_age': first_end
            },
            {
                'period': 'Second Pinnacle',
                'number': pinnacle_2,
                'start_age': first_end + 1,
                'end_age': second_end
            },
            {
                'period': 'Third Pinnacle',
                'number': pinnacle_3,
                'start_age': second_end + 1,
                'end_age': third_end
            },
            {
                'period': 'Fourth Pinnacle',
                'number': pinnacle_4,
                'start_age': third_end + 1,
                'end_age': None  # 以降
            }
        ]
    
    def calc_challenges(self, birth_date: datetime) -> List[Dict]:
        """
        4つのチャレンジ（Challenges）を計算
        
        人生の試練・課題
        
        計算:
        - 1st: |birth_month - birth_day|
        - 2nd: |birth_day - birth_year|
        - 3rd: |1st - 2nd|
        - 4th: |birth_month - birth_year|
        
        Args:
            birth_date: 生年月日
            
        Returns:
            List of {'period': str, 'number': int}
        """
        month = birth_date.month
        day = birth_date.day
        year = birth_date.year
        
        month_r = self.core.reduce_number(month, keep_master=False)
        day_r = self.core.reduce_number(day, keep_master=False)
        year_r = self.core.reduce_number(year, keep_master=False)
        
        challenge_1 = abs(month_r - day_r)
        challenge_2 = abs(day_r - year_r)
        challenge_3 = abs(challenge_1 - challenge_2)
        challenge_4 = abs(month_r - year_r)
        
        return [
            {'period': 'First Challenge', 'number': challenge_1},
            {'period': 'Second Challenge', 'number': challenge_2},
            {'period': 'Third Challenge', 'number': challenge_3},
            {'period': 'Fourth Challenge', 'number': challenge_4}
        ]
    
    # ============================================
    # Grid Matrix
    # ============================================
    
    def calc_grid_matrix(
        self, 
        birth_date: datetime, 
        full_name: str
    ) -> Dict[int, int]:
        """
        1-9の出現頻度マトリックス
        
        生年月日と名前から1-9各数字の出現回数を計算
        
        Args:
            birth_date: 生年月日
            full_name: フルネーム
            
        Returns:
            {1: count, 2: count, ..., 9: count}
        """
        # 初期化
        grid = {i: 0 for i in range(1, 10)}
        
        # 生年月日から
        date_str = birth_date.strftime('%Y%m%d')
        for digit in date_str:
            num = int(digit)
            if 1 <= num <= 9:
                grid[num] += 1
        
        # 名前から
        name_numbers = self.core.text_to_number(full_name, self.system)
        for num in name_numbers:
            if 1 <= num <= 9:
                grid[num] += 1
        
        return grid


class AstroWeighting:
    """
    天体連携による重み付けクラス
    
    pyswissephを使用して惑星の状態を評価
    """
    
    def __init__(self):
        if not HAS_SWISSEPH:
            print("Warning: pyswisseph not available. Astro features disabled.")
    
    def get_ruler_planet(self, number: int) -> str:
        """
        数字の支配星を取得
        
        Args:
            number: 数字（1-9 or 11,22,33）
            
        Returns:
            惑星名（例: 'Sun', 'Moon'）
        """
        return PLANET_RULERS.get(number, 'Sun')
    
    def evaluate_planet_strength(
        self, 
        julian_day: float, 
        planet_name: str
    ) -> Dict:
        """
        惑星の状態を評価
        
        pyswissephを使用して、指定ユリウス日における惑星の状態を計算
        
        Args:
            julian_day: ユリウス日
            planet_name: 惑星名（例: 'Sun', 'Moon'）
            
        Returns:
            {
                'sign': str,           # 星座名
                'sign_ja': str,        # 星座名（日本語）
                'degree': float,       # 度数
                'is_retrograde': bool, # 逆行中か
                'dignity': str,        # 品位 (Domicile/Exaltation/Detriment/Fall/None)
                'strength_score': float  # 強さスコア 0.0-1.2
            }
        """
        if not HAS_SWISSEPH:
            return self._dummy_planet_status()
        
        try:
            planet_id = PLANET_IDS.get(planet_name, 0)
            
            # 惑星位置計算
            result = swe.calc_ut(julian_day, planet_id)
            longitude = result[0][0]  # 黄経
            speed = result[0][3]      # 速度
            
            # サイン判定（30度ごと）
            sign_index = int(longitude / 30)
            sign_name = ZODIAC_SIGNS[sign_index]
            degree = longitude % 30
            
            # 逆行判定（速度が負）
            is_retrograde = speed < 0
            
            # 品位評価
            dignity = self._assess_dignity(planet_name, sign_name)
            
            # スコア計算
            strength = 1.0
            if dignity == 'Domicile':
                strength = 1.2
            elif dignity == 'Exaltation':
                strength = 1.1
            elif dignity == 'Detriment':
                strength = 0.8
            elif dignity == 'Fall':
                strength = 0.7
            
            if is_retrograde:
                strength *= 0.9
            
            return {
                'sign': sign_name,
                'sign_ja': ZODIAC_SIGNS[sign_index] if sign_index < len(ZODIAC_SIGNS) else sign_name,
                'degree': round(degree, 2),
                'is_retrograde': is_retrograde,
                'dignity': dignity,
                'strength_score': round(min(strength, 1.2), 2)
            }
            
        except Exception as e:
            print(f"Error evaluating planet {planet_name}: {e}")
            return self._dummy_planet_status()
    
    def _assess_dignity(self, planet_name: str, sign_name: str) -> str:
        """
        惑星の品位を評価
        
        Args:
            planet_name: 惑星名
            sign_name: 星座名
            
        Returns:
            'Domicile' / 'Exaltation' / 'Detriment' / 'Fall' / None
        """
        # Domicile（本来の座）
        if sign_name in DOMICILE.get(planet_name, []):
            return 'Domicile'
        
        # Exaltation（高揚）
        if sign_name == EXALTATION.get(planet_name):
            return 'Exaltation'
        
        # Detriment（障害）
        if sign_name in DETRIMENT.get(planet_name, []):
            return 'Detriment'
        
        # Fall（下降）
        if sign_name == FALL.get(planet_name):
            return 'Fall'
        
        return None
    
    def _dummy_planet_status(self) -> Dict:
        """
        pyswissephが利用できない場合のダミーステータス
        """
        return {
            'sign': 'Unknown',
            'sign_ja': '不明',
            'degree': 0.0,
            'is_retrograde': False,
            'dignity': None,
            'strength_score': 1.0
        }
