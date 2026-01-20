"""
西洋占星術モジュール
ホロスコープ（惑星位置、ハウス、アスペクト）の計算
"""
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from ...core.ephemeris import AstroEngine, Planet, ZODIAC_SIGNS
from ...core.time_manager import TimeManager
from ...models.output_schema import (
    WesternResult, PlanetPosition, Aspect
)


class WesternAstrologyCalculator:
    """
    西洋占星術計算クラス
    トロピカル方式によるホロスコープ作成
    """
    
    # アスペクトの定義
    ASPECTS = {
        0: ("合", "Conjunction", 10),      # コンジャンクション
        60: ("六分", "Sextile", 6),         # セクスタイル
        90: ("矩", "Square", 8),            # スクエア
        120: ("三分", "Trine", 8),          # トライン
        180: ("衝", "Opposition", 10),      # オポジション
        30: ("半六分", "Semi-sextile", 2),  # セミセクスタイル
        150: ("五六分", "Quincunx", 3),     # クインカンクス
        45: ("半矩", "Semi-square", 2),     # セミスクエア
        135: ("一矩半", "Sesquiquadrate", 2), # セスキコードレート
    }
    
    # 主要惑星
    MAJOR_PLANETS = [
        Planet.SUN, Planet.MOON, Planet.MERCURY, Planet.VENUS, Planet.MARS,
        Planet.JUPITER, Planet.SATURN, Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO
    ]
    
    def __init__(self):
        self.astro = AstroEngine()
    
    def calculate(self, birth_dt: datetime, latitude: float, longitude: float) -> WesternResult:
        """
        西洋占星術ホロスコープを計算
        
        Args:
            birth_dt: 生年月日時
            latitude: 出生地緯度
            longitude: 出生地経度
            
        Returns:
            WesternResult
        """
        jd = TimeManager.to_julian_day(birth_dt)
        
        # 惑星位置を取得
        planets = self._get_planet_positions(jd)
        
        # ハウスを計算
        houses = self.astro.get_houses(jd, latitude, longitude)
        
        # 惑星にハウスを割り当て
        planets_with_houses = self._assign_houses(planets, houses.cusps)
        
        # アスペクトを計算
        aspects = self._calc_aspects(planets)
        
        # ハウスカスプを辞書に変換
        house_cusps = {i+1: cusp for i, cusp in enumerate(houses.cusps)}
        
        return WesternResult(
            planets=planets_with_houses,
            houses=house_cusps,
            ascendant=houses.ascendant,
            midheaven=houses.midheaven,
            aspects=aspects
        )
    
    def _get_planet_positions(self, jd: float) -> List[PlanetPosition]:
        """惑星位置を取得"""
        positions = []
        
        for planet_id in self.MAJOR_PLANETS:
            data = self.astro.get_planet_position(jd, planet_id, sidereal=False)
            
            positions.append(PlanetPosition(
                planet=data.name,
                longitude=round(data.longitude, 4),
                sign=data.sign,
                degree_in_sign=round(data.degree_in_sign, 2),
                house=None,  # 後で割り当て
                retrograde=data.is_retrograde
            ))
        
        # ノード（ラーフ）も追加
        node_data = self.astro.get_planet_position(jd, Planet.TRUE_NODE, sidereal=False)
        positions.append(PlanetPosition(
            planet="ノード",
            longitude=round(node_data.longitude, 4),
            sign=node_data.sign,
            degree_in_sign=round(node_data.degree_in_sign, 2),
            house=None,
            retrograde=node_data.is_retrograde
        ))
        
        return positions
    
    def _assign_houses(self, planets: List[PlanetPosition], cusps: List[float]) -> List[PlanetPosition]:
        """惑星にハウスを割り当て"""
        result = []
        
        for planet in planets:
            house = self._find_house(planet.longitude, cusps)
            result.append(PlanetPosition(
                planet=planet.planet,
                longitude=planet.longitude,
                sign=planet.sign,
                degree_in_sign=planet.degree_in_sign,
                house=house,
                retrograde=planet.retrograde
            ))
        
        return result
    
    def _find_house(self, longitude: float, cusps: List[float]) -> int:
        """惑星がどのハウスにあるかを判定"""
        for i in range(12):
            next_i = (i + 1) % 12
            cusp_start = cusps[i]
            cusp_end = cusps[next_i]
            
            # 通常のケース
            if cusp_start < cusp_end:
                if cusp_start <= longitude < cusp_end:
                    return i + 1
            else:
                # 魚座→牡羊座をまたぐケース
                if longitude >= cusp_start or longitude < cusp_end:
                    return i + 1
        
        return 1  # デフォルト
    
    def _calc_aspects(self, planets: List[PlanetPosition]) -> List[Aspect]:
        """アスペクトを計算"""
        aspects = []
        
        for i, p1 in enumerate(planets):
            for p2 in planets[i+1:]:
                aspect = self._check_aspect(p1.longitude, p2.longitude)
                if aspect:
                    aspects.append(Aspect(
                        planet1=p1.planet,
                        planet2=p2.planet,
                        aspect_type=aspect[0],
                        orb=round(aspect[1], 2),
                        applying=aspect[2]
                    ))
        
        return aspects
    
    def _check_aspect(self, lon1: float, lon2: float) -> Optional[tuple]:
        """
        アスペクトを判定
        
        Returns:
            (アスペクト名, オーブ, 接近中か) または None
        """
        diff = abs(lon1 - lon2)
        if diff > 180:
            diff = 360 - diff
        
        for angle, (name_jp, name_en, max_orb) in self.ASPECTS.items():
            orb = abs(diff - angle)
            if orb <= max_orb:
                # 接近中（applying）か離反中（separating）かは速度で判断
                # ここでは簡略化
                applying = True
                return (name_jp, orb, applying)
        
        return None
    
    def get_sign_ruler(self, sign: str) -> str:
        """サインの支配星を取得"""
        rulers = {
            "牡羊座": "火星", "牡牛座": "金星", "双子座": "水星",
            "蟹座": "月", "獅子座": "太陽", "乙女座": "水星",
            "天秤座": "金星", "蠍座": "冥王星", "射手座": "木星",
            "山羊座": "土星", "水瓶座": "天王星", "魚座": "海王星"
        }
        return rulers.get(sign, "不明")
