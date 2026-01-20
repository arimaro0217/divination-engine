"""
インド占星術（Vedic/Jyotish）モジュール
サイデリアル方式、ナクシャトラ、ダシャー計算
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ...core.ephemeris import AstroEngine, Planet
from ...core.time_manager import TimeManager
from ...models.output_schema import VedicResult, PlanetPosition


class VedicAstrologyCalculator:
    """
    インド占星術計算クラス
    ラヒリ・アヤナムサによるサイデリアル計算
    """
    
    # ナクシャトラ（27宿）
    NAKSHATRAS = [
        "アシュヴィニー", "バラニー", "クリッティカー", "ローヒニー",
        "ムリガシラー", "アールドラー", "プナルヴァス", "プシュヤ",
        "アーシュレーシャー", "マガー", "プールヴァ・パールグニー",
        "ウッタラ・パールグニー", "ハスタ", "チトラー", "スヴァーティー",
        "ヴィシャーカー", "アヌラーダー", "ジェーシュター", "ムーラ",
        "プールヴァ・アシャーダー", "ウッタラ・アシャーダー", "シュラヴァナ",
        "ダニシュター", "シャタビシャー", "プールヴァ・バードラパダー",
        "ウッタラ・バードラパダー", "レーヴァティー"
    ]
    
    # ナクシャトラの支配星
    NAKSHATRA_LORDS = [
        "ケートゥ", "金星", "太陽", "月", "火星", "ラーフ", "木星",
        "土星", "水星", "ケートゥ", "金星", "太陽", "月", "火星",
        "ラーフ", "木星", "土星", "水星", "ケートゥ", "金星", "太陽",
        "月", "火星", "ラーフ", "木星", "土星", "水星"
    ]
    
    # ヴィムショッタリ・ダシャーの年数
    DASHA_YEARS = {
        "ケートゥ": 7, "金星": 20, "太陽": 6, "月": 10, "火星": 7,
        "ラーフ": 18, "木星": 16, "土星": 19, "水星": 17
    }
    
    # ダシャーの順序
    DASHA_ORDER = ["ケートゥ", "金星", "太陽", "月", "火星", "ラーフ", "木星", "土星", "水星"]
    
    # サイン
    SIGNS = [
        "牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
        "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"
    ]
    
    def __init__(self):
        self.astro = AstroEngine()
    
    def calculate(self, birth_dt: datetime, latitude: float, longitude: float) -> VedicResult:
        """
        インド占星術を計算
        
        Args:
            birth_dt: 生年月日時
            latitude: 出生地緯度
            longitude: 出生地経度
            
        Returns:
            VedicResult
        """
        jd = TimeManager.to_julian_day(birth_dt)
        
        # アヤナムサ値を取得
        ayanamsa = self.astro.get_ayanamsa(jd)
        
        # 惑星位置（サイデリアル）
        planets = self._get_planet_positions(jd)
        
        # 月のナクシャトラ
        nakshatra_num, nakshatra_name, nakshatra_degree = self.astro.get_moon_nakshatra(jd)
        nakshatra_lord = self.NAKSHATRA_LORDS[nakshatra_num - 1]
        
        # ダシャーを計算
        dasha = self._calc_vimshottari_dasha(birth_dt, nakshatra_num, nakshatra_degree)
        
        # ナバムシャ（D9）を計算
        d9_positions = self._calc_navamsa(planets)
        
        return VedicResult(
            ayanamsa=round(ayanamsa, 4),
            planets=planets,
            nakshatra=nakshatra_name,
            nakshatra_lord=nakshatra_lord,
            dasha=dasha,
            d9_positions=d9_positions
        )
    
    def _get_planet_positions(self, jd: float) -> List[PlanetPosition]:
        """惑星位置（サイデリアル）を取得"""
        positions = []
        
        planet_ids = [
            Planet.SUN, Planet.MOON, Planet.MERCURY, Planet.VENUS, Planet.MARS,
            Planet.JUPITER, Planet.SATURN, Planet.TRUE_NODE
        ]
        
        for planet_id in planet_ids:
            data = self.astro.get_planet_position(jd, planet_id, sidereal=True)
            
            positions.append(PlanetPosition(
                planet=data.name,
                longitude=round(data.longitude, 4),
                sign=self.SIGNS[data.sign_index],
                degree_in_sign=round(data.degree_in_sign, 2),
                house=None,
                retrograde=data.is_retrograde
            ))
        
        # ケートゥ（ラーフの対極）を追加
        rahu = self.astro.get_planet_position(jd, Planet.TRUE_NODE, sidereal=True)
        ketu_longitude = (rahu.longitude + 180) % 360
        ketu_sign_index = int(ketu_longitude // 30)
        ketu_degree = ketu_longitude % 30
        
        positions.append(PlanetPosition(
            planet="ケートゥ",
            longitude=round(ketu_longitude, 4),
            sign=self.SIGNS[ketu_sign_index],
            degree_in_sign=round(ketu_degree, 2),
            house=None,
            retrograde=True
        ))
        
        return positions
    
    def _calc_vimshottari_dasha(self, birth_dt: datetime, 
                                 nakshatra_num: int, 
                                 degree_in_nakshatra: float) -> Dict:
        """
        ヴィムショッタリ・ダシャーを計算
        """
        # ナクシャトラの支配星がダシャーの開始
        first_lord = self.NAKSHATRA_LORDS[nakshatra_num - 1]
        
        # ナクシャトラ内での経過度数から、初期ダシャーの残り期間を計算
        nakshatra_span = 360 / 27  # 13.333...度
        progress = degree_in_nakshatra / nakshatra_span
        
        first_dasha_years = self.DASHA_YEARS[first_lord]
        remaining_years = first_dasha_years * (1 - progress)
        
        # ダシャーの順序を決定
        lord_index = self.DASHA_ORDER.index(first_lord)
        
        # 現在日時との比較でダシャー期間を計算
        dasha_periods = {}
        current_date = birth_dt
        
        # 最初のダシャー（残り期間）
        end_date = current_date + timedelta(days=remaining_years * 365.25)
        dasha_periods[first_lord] = {
            "start": current_date.isoformat(),
            "end": end_date.isoformat(),
            "years": round(remaining_years, 2)
        }
        current_date = end_date
        
        # 続くダシャー（フルサイクル）
        for i in range(1, 9):
            lord = self.DASHA_ORDER[(lord_index + i) % 9]
            years = self.DASHA_YEARS[lord]
            end_date = current_date + timedelta(days=years * 365.25)
            dasha_periods[lord] = {
                "start": current_date.isoformat(),
                "end": end_date.isoformat(),
                "years": years
            }
            current_date = end_date
        
        return dasha_periods
    
    def _calc_navamsa(self, planets: List[PlanetPosition]) -> List[PlanetPosition]:
        """
        ナバムシャ（D9分割図）を計算
        """
        d9_positions = []
        
        for planet in planets:
            # D9はサイン内度数を9分割
            navamsa_index = int(planet.degree_in_sign / (30 / 9))
            
            # 火のサインから始まる場合
            sign_index = self.SIGNS.index(planet.sign)
            
            # ナバムシャのサインを決定
            if sign_index % 3 == 0:  # 火のサイン（牡羊、獅子、射手）
                d9_sign_index = navamsa_index
            elif sign_index % 3 == 1:  # 土のサイン（牡牛、乙女、山羊）
                d9_sign_index = (navamsa_index + 9) % 12
            else:  # 風のサイン（双子、天秤、水瓶）
                d9_sign_index = (navamsa_index + 6) % 12
            
            d9_positions.append(PlanetPosition(
                planet=planet.planet,
                longitude=0,  # D9では黄経は意味がない
                sign=self.SIGNS[d9_sign_index],
                degree_in_sign=0,
                house=None,
                retrograde=planet.retrograde
            ))
        
        return d9_positions
