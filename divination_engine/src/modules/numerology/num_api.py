"""
数秘術APIエントリーポイント
Numerology API Entry Point

完全な数秘術レポートをJSON形式で生成
"""
from typing import Dict, Optional
from datetime import datetime
import json
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

from .num_logic import ChartBuilder, AstroWeighting
from .num_core import NumerologyCore
from ...const.numerology_const import (
    NUMBER_MEANINGS,
    KARMIC_MEANINGS,
    PERSONAL_YEAR_MEANINGS
)


class NumerologyAPI:
    """
    数秘術API
    
    フロントエンド統合用のJSON出力を提供
    """
    
    def __init__(self):
        pass
    
    def generate_full_report(
        self,
        name_input: str,
        birth_date: datetime,
        system: str = 'pythagorean',
        target_year: Optional[int] = None,
        latitude: float = 35.68,
        longitude: float = 139.76
    ) -> Dict:
        """
        完全な数秘術レポートを生成
        
        Args:
            name_input: フルネーム（英字 or 日本語）
            birth_date: 生年月日時
            system: 'pythagorean' or 'chaldean'
            target_year: 予測対象年（Noneなら現在年）
            latitude: 出生地緯度（天体計算用、未使用でもよい）
            longitude: 出生地経度（天体計算用、未使用でもよい）
            
        Returns:
            完全なJSON形式レポート
        """
        builder = ChartBuilder(system)
        astro = AstroWeighting()
        core = NumerologyCore()
        
        # 日本語判定とローマ字変換
        if core.is_japanese(name_input):
            name_roman = core.kana_to_romaji(name_input)
        else:
            name_roman = name_input.upper()
        
        # ============================================
        # Core Numbers計算
        # ============================================
        
        life_path_data = builder.calc_life_path(birth_date)
        destiny_data = builder.calc_destiny(name_roman)
        soul_urge_data = builder.calc_soul_urge(name_roman)
        personality_data = builder.calc_personality(name_roman)
        maturity = builder.calc_maturity(
            life_path_data['number'],
            destiny_data['number']
        )
        birthday_number = builder.calc_birthday_number(birth_date.day)
        
        # ============================================
        # 天体連携
        # ============================================
        
        # ユリウス日計算
        if HAS_SWISSEPH:
            jd = swe.julday(
                birth_date.year,
                birth_date.month,
                birth_date.day,
                birth_date.hour + birth_date.minute / 60.0
            )
        else:
            jd = 0.0
        
        # ライフパス数の支配星
        life_path_planet = astro.get_ruler_planet(life_path_data['number'])
        planet_status = astro.evaluate_planet_strength(jd, life_path_planet)
        
        # ============================================
        # Personal Year
        # ============================================
        
        if target_year is None:
            target_year = datetime.now().year
        
        personal_year = builder.calc_personal_year(birth_date, target_year)
        personal_year_meaning = PERSONAL_YEAR_MEANINGS.get(personal_year, {})
        
        # ============================================
        # Pinnacles & Challenges
        # ============================================
        
        pinnacles = builder.calc_pinnacles(birth_date)
        challenges = builder.calc_challenges(birth_date)
        
        # 現在のピナクル判定
        current_age = target_year - birth_date.year
        current_pinnacle = None
        for p in pinnacles:
            if p['end_age'] is None or current_age <= p['end_age']:
                current_pinnacle = p
                break
        
        # ============================================
        # Grid Matrix
        # ============================================
        
        grid = builder.calc_grid_matrix(birth_date, name_roman)
        
        # ============================================
        # Karmic Detection
        # ============================================
        
        all_name_numbers = core.text_to_number(name_roman, system)
        karmic_numbers = core.detect_karmic(birth_date, all_name_numbers)
        
        # ============================================
        # JSON構築
        # ============================================
        
        return {
            'profile': {
                'name_input': name_input,
                'name_roman': name_roman,
                'birth_date': birth_date.isoformat(),
                'system': system.capitalize(),
                'target_year': target_year
            },
            'core_numbers': {
                'life_path': {
                    'number': life_path_data['number'],
                    'is_master': life_path_data['is_master'],
                    'calculation': life_path_data['calculation'],
                    'ruler_planet': life_path_planet,
                    'planet_status': planet_status,
                    'meaning': NUMBER_MEANINGS.get(life_path_data['number'], {})
                },
                'destiny': {
                    'number': destiny_data['number'],
                    'is_master': destiny_data['is_master'],
                    'meaning': NUMBER_MEANINGS.get(destiny_data['number'], {}).get('keywords', [])
                },
                'soul_urge': {
                    'number': soul_urge_data['number'],
                    'is_master': soul_urge_data['is_master'],
                    'meaning': NUMBER_MEANINGS.get(soul_urge_data['number'], {}).get('keywords', [])
                },
                'personality': {
                    'number': personality_data['number'],
                    'is_master': personality_data['is_master'],
                    'meaning': NUMBER_MEANINGS.get(personality_data['number'], {}).get('keywords', [])
                },
                'maturity': {
                    'number': maturity,
                    'meaning': NUMBER_MEANINGS.get(maturity, {}).get('keywords', [])
                },
                'birthday': {
                    'number': birthday_number,
                    'meaning': NUMBER_MEANINGS.get(birthday_number, {}).get('keywords', [])
                },
                'karmic_lessons': [
                    {
                        'number': k,
                        **KARMIC_MEANINGS.get(k, {})
                    } for k in karmic_numbers
                ]
            },
            'forecasting': {
                'personal_year': {
                    'number': personal_year,
                    'theme': personal_year_meaning.get('theme', ''),
                    'description': personal_year_meaning.get('description', '')
                },
                'current_pinnacle': current_pinnacle,
                'all_pinnacles': pinnacles,
                'challenges': challenges
            },
            'grid_matrix': grid
        }
    
    def generate_simple_report(
        self,
        name_input: str,
        birth_date: datetime,
        system: str = 'pythagorean'
    ) -> Dict:
        """
        簡易レポート生成（Core Numbersのみ）
        
        Args:
            name_input: フルネーム
            birth_date: 生年月日
            system: 'pythagorean' or 'chaldean'
            
        Returns:
            簡易JSON形式レポート
        """
        builder = ChartBuilder(system)
        core = NumerologyCore()
        
        # 日本語判定
        if core.is_japanese(name_input):
            name_roman = core.kana_to_romaji(name_input)
        else:
            name_roman = name_input.upper()
        
        # Core Numbers only
        life_path_data = builder.calc_life_path(birth_date)
        destiny_data = builder.calc_destiny(name_roman)
        soul_urge_data = builder.calc_soul_urge(name_roman)
        personality_data = builder.calc_personality(name_roman)
        
        return {
            'name': name_roman,
            'birth_date': birth_date.isoformat(),
            'system': system,
            'life_path': life_path_data['number'],
            'destiny': destiny_data['number'],
            'soul_urge': soul_urge_data['number'],
            'personality': personality_data['number']
        }


# ============================================
# コマンドライン実行用
# ============================================

def main():
    """
    コマンドライン実行テスト
    
    Usage:
        python -m src.modules.numerology.num_api
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Numerology Calculator')
    parser.add_argument('--name', type=str, required=True, help='Full name')
    parser.add_argument('--date', type=str, required=True, help='Birth date (YYYY-MM-DD)')
    parser.add_argument('--system', type=str, default='pythagorean', choices=['pythagorean', 'chaldean'])
    
    args = parser.parse_args()
    
    # 日付パース
    birth_date = datetime.strptime(args.date, '%Y-%m-%d')
    
    # API実行
    api = NumerologyAPI()
    result = api.generate_full_report(
        name_input=args.name,
        birth_date=birth_date,
        system=args.system
    )
    
    # JSON出力
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
