"""
西洋占星術 ホロスコープ構築・シナストリーモジュール
Western Astrology Horoscope & Synastry Module

ネイタルチャート生成、トランジット、シナストリー（相性図）
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import math

try:
    from .astro_core import AstroCore, AspectEngine, CelestialPosition, HouseCusps
    from ..const import astro_const as ac
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.modules.western.astro_core import AstroCore, AspectEngine, CelestialPosition, HouseCusps
    from src.const import astro_const as ac


# ============================================
# データ構造
# ============================================

@dataclass
class ChartPoint:
    """チャート上の点（天体または感受点）"""
    id: str
    name_ja: str
    longitude: float
    sign_index: int
    sign_name: str
    sign_degree: float
    house: int
    is_retrograde: bool = False
    speed: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name_ja": self.name_ja,
            "absolute_degree": round(self.longitude, 4),
            "sign": self.sign_name,
            "sign_id": self.sign_index,
            "relative_degree": round(self.sign_degree, 2),
            "house": self.house,
            "is_retrograde": self.is_retrograde,
            "speed": round(self.speed, 4),
            "formatted": ac.format_degree(self.longitude)
        }


@dataclass
class NatalChart:
    """ネイタルチャート（出生図）"""
    birth_datetime: datetime
    latitude: float
    longitude: float
    altitude: float
    timezone_offset: float
    house_system: str
    
    points: List[ChartPoint] = field(default_factory=list)
    cusps: List[float] = field(default_factory=list)
    angles: Dict[str, float] = field(default_factory=dict)
    aspects: List[Dict] = field(default_factory=list)
    
    part_of_fortune: Optional[ChartPoint] = None
    vertex: Optional[ChartPoint] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "meta": {
                "datetime": self.birth_datetime.isoformat(),
                "latitude": self.latitude,
                "longitude": self.longitude,
                "altitude": self.altitude,
                "timezone_offset": self.timezone_offset,
                "house_system": self.house_system
            },
            "points": [p.to_dict() for p in self.points],
            "cusps": [round(c, 4) for c in self.cusps],
            "angles": {k: round(v, 4) for k, v in self.angles.items()},
            "aspects": self.aspects
        }


# ============================================
# ChartBuilder: ホロスコープ構築
# ============================================

class ChartBuilder:
    """
    ホロスコープ構築クラス
    
    ネイタル、トランジット、シナストリーチャートを生成
    """
    
    def __init__(self, settings: ac.CalculationSettings = None):
        """初期化"""
        self.core = AstroCore()
        self.aspect_engine = AspectEngine(settings.orbs if settings else None)
        self.settings = settings or ac.CalculationSettings()
    
    def build_natal_chart(
        self,
        birth_dt: datetime,
        lat: float,
        lon: float,
        alt: float = 0.0,
        tz_offset: float = 0.0,
        house_system: ac.HouseSystem = ac.HouseSystem.PLACIDUS
    ) -> NatalChart:
        """
        ネイタルチャートを構築
        
        Args:
            birth_dt: 出生日時（UTC）
            lat: 緯度
            lon: 経度
            alt: 標高（メートル）
            tz_offset: タイムゾーンオフセット（時間）
            house_system: ハウスシステム
            
        Returns:
            NatalChart: 完全なネイタルチャート
        """
        # ユリウス日に変換
        jd = self.core.datetime_to_jd(birth_dt)
        
        # ハウス計算
        houses = self.core.calculate_houses(jd, lat, lon, house_system)
        
        # 全天体位置計算
        positions = self.core.calculate_all_bodies(
            jd, lat, lon, alt,
            topocentric=self.settings.use_topocentric,
            use_true_node=self.settings.use_true_node,
            use_true_lilith=self.settings.use_true_lilith
        )
        
        # 天体をチャートポイントに変換
        points = []
        for pos in positions:
            house = self._determine_house(pos.longitude, houses)
            
            point = ChartPoint(
                id=ac.BODY_NAMES_EN.get(pos.body_id, f"Body_{pos.body_id}"),
                name_ja=ac.BODY_NAMES_JA.get(pos.body_id, ""),
                longitude=pos.longitude,
                sign_index=pos.sign_index,
                sign_name=pos.sign_name,
                sign_degree=pos.sign_degree,
                house=house,
                is_retrograde=pos.is_retrograde,
                speed=pos.speed
            )
            points.append(point)
        
        # パート・オブ・フォーチュン
        sun = next(p for p in positions if p.body_id == ac.CelestialBody.SUN)
        moon = next(p for p in positions if p.body_id == ac.CelestialBody.MOON)
        is_night = self.core.is_night_chart(sun.longitude, houses.asc)
        
        fortune_lon = self.core.calculate_part_of_fortune(
            sun.longitude, moon.longitude, houses.asc, is_night
        )
        fortune_sign, fortune_degree = ac.degree_to_sign(fortune_lon)
        fortune_house = self._determine_house(fortune_lon, houses)
        
        part_of_fortune = ChartPoint(
            id="Part_of_Fortune",
            name_ja="幸運点",
            longitude=fortune_lon,
            sign_index=fortune_sign,
            sign_name=ac.SIGN_NAMES_EN[fortune_sign],
            sign_degree=fortune_degree,
            house=fortune_house
        )
        points.append(part_of_fortune)
        
        # バーテックス
        vertex_sign, vertex_degree = ac.degree_to_sign(houses.vertex)
        vertex_house = self._determine_house(houses.vertex, houses)
        
        vertex = ChartPoint(
            id="Vertex",
            name_ja="バーテックス",
            longitude=houses.vertex,
            sign_index=vertex_sign,
            sign_name=ac.SIGN_NAMES_EN[vertex_sign],
            sign_degree=vertex_degree,
            house=vertex_house
        )
        points.append(vertex)
        
        # アスペクト計算
        aspects = self.aspect_engine.find_all_aspects(
            positions,
            include_minor=self.settings.include_minor_aspects
        )
        
        # アングル
        angles = {
            "asc": houses.asc,
            "mc": houses.mc,
            "dsc": houses.dsc,
            "ic": houses.ic,
            "vertex": houses.vertex
        }
        
        return NatalChart(
            birth_datetime=birth_dt,
            latitude=lat,
            longitude=lon,
            altitude=alt,
            timezone_offset=tz_offset,
            house_system=house_system.name,
            points=points,
            cusps=houses.cusps[1:13],  # 1-12ハウス
            angles=angles,
            aspects=aspects,
            part_of_fortune=part_of_fortune,
            vertex=vertex
        )
    
    def _determine_house(
        self,
        longitude: float,
        houses: HouseCusps
    ) -> int:
        """
        黄経からハウス番号を決定
        
        Args:
            longitude: 黄経
            houses: ハウスカスプ情報
            
        Returns:
            ハウス番号（1-12）
        """
        cusps = houses.cusps
        
        for i in range(1, 13):
            next_i = i % 12 + 1
            cusp_start = cusps[i]
            cusp_end = cusps[next_i]
            
            # 5度前ルール
            if self.settings.use_five_degree_rule:
                cusp_start = (cusp_start - self.settings.five_degree_threshold) % 360
            
            # カスプをまたぐ場合の処理
            if cusp_start <= cusp_end:
                if cusp_start <= longitude < cusp_end:
                    return i
            else:  # 0度をまたぐ場合
                if longitude >= cusp_start or longitude < cusp_end:
                    return i
        
        return 1  # フォールバック
    
    def build_transit_chart(
        self,
        natal_chart: NatalChart,
        transit_dt: datetime
    ) -> Tuple[NatalChart, List[Dict]]:
        """
        トランジットチャートを構築
        
        Args:
            natal_chart: ネイタルチャート
            transit_dt: トランジット日時
            
        Returns:
            (トランジットチャート, ネイタルとのアスペクトリスト)
        """
        # トランジット時点のチャートを構築
        transit_chart = self.build_natal_chart(
            transit_dt,
            natal_chart.latitude,
            natal_chart.longitude,
            natal_chart.altitude,
            natal_chart.timezone_offset,
            ac.HouseSystem[natal_chart.house_system]
        )
        
        # トランジット天体 vs ネイタル天体のアスペクト
        transit_aspects = []
        
        for t_point in transit_chart.points:
            for n_point in natal_chart.points:
                # 仮のCelestialPositionを作成
                t_pos = CelestialPosition(
                    body_id=0, body_name=t_point.id,
                    longitude=t_point.longitude, latitude=0, distance=0,
                    speed=t_point.speed, declination=0, right_ascension=0,
                    is_retrograde=t_point.is_retrograde,
                    sign_index=t_point.sign_index,
                    sign_name=t_point.sign_name,
                    sign_degree=t_point.sign_degree
                )
                n_pos = CelestialPosition(
                    body_id=0, body_name=n_point.id,
                    longitude=n_point.longitude, latitude=0, distance=0,
                    speed=n_point.speed, declination=0, right_ascension=0,
                    is_retrograde=n_point.is_retrograde,
                    sign_index=n_point.sign_index,
                    sign_name=n_point.sign_name,
                    sign_degree=n_point.sign_degree
                )
                
                aspect = self.aspect_engine.find_aspect(t_pos, n_pos)
                if aspect:
                    aspect["transit_body"] = t_point.id
                    aspect["natal_body"] = n_point.id
                    transit_aspects.append(aspect)
        
        return transit_chart, transit_aspects


# ============================================
# SynastryEngine: 相性・二重円
# ============================================

class SynastryEngine:
    """
    シナストリー（相性図）エンジン
    
    2つのチャート間のアスペクトとハウスオーバーレイを計算
    """
    
    def __init__(self, settings: ac.CalculationSettings = None):
        """初期化"""
        self.aspect_engine = AspectEngine(settings.orbs if settings else None)
    
    def calculate_synastry(
        self,
        chart_a: NatalChart,
        chart_b: NatalChart
    ) -> Dict[str, Any]:
        """
        シナストリー（相性）を計算
        
        Args:
            chart_a: Person Aのチャート
            chart_b: Person Bのチャート
            
        Returns:
            シナストリー結果
        """
        # アスペクト計算
        aspects = self._find_cross_aspects(chart_a, chart_b)
        
        # ハウスオーバーレイ
        overlay_a_to_b = self._calculate_house_overlay(chart_a, chart_b)
        overlay_b_to_a = self._calculate_house_overlay(chart_b, chart_a)
        
        # 相性スコア計算
        score = self._calculate_compatibility_score(aspects)
        
        return {
            "person_a": {
                "datetime": chart_a.birth_datetime.isoformat(),
            },
            "person_b": {
                "datetime": chart_b.birth_datetime.isoformat(),
            },
            "aspects": aspects,
            "house_overlay": {
                "a_in_b_houses": overlay_a_to_b,
                "b_in_a_houses": overlay_b_to_a
            },
            "compatibility_score": score
        }
    
    def _find_cross_aspects(
        self,
        chart_a: NatalChart,
        chart_b: NatalChart
    ) -> List[Dict[str, Any]]:
        """2つのチャート間のアスペクトを検出"""
        aspects = []
        
        for point_a in chart_a.points:
            for point_b in chart_b.points:
                # 仮のCelestialPositionを作成
                pos_a = CelestialPosition(
                    body_id=0, body_name=point_a.id,
                    longitude=point_a.longitude, latitude=0, distance=0,
                    speed=point_a.speed, declination=0, right_ascension=0,
                    is_retrograde=point_a.is_retrograde,
                    sign_index=point_a.sign_index,
                    sign_name=point_a.sign_name,
                    sign_degree=point_a.sign_degree
                )
                pos_b = CelestialPosition(
                    body_id=0, body_name=point_b.id,
                    longitude=point_b.longitude, latitude=0, distance=0,
                    speed=point_b.speed, declination=0, right_ascension=0,
                    is_retrograde=point_b.is_retrograde,
                    sign_index=point_b.sign_index,
                    sign_name=point_b.sign_name,
                    sign_degree=point_b.sign_degree
                )
                
                aspect = self.aspect_engine.find_aspect(pos_a, pos_b)
                if aspect:
                    aspect["person_a_body"] = point_a.id
                    aspect["person_b_body"] = point_b.id
                    aspects.append(aspect)
        
        return aspects
    
    def _calculate_house_overlay(
        self,
        chart_from: NatalChart,
        chart_to: NatalChart
    ) -> List[Dict[str, Any]]:
        """
        ハウスオーバーレイを計算
        
        chart_fromの天体がchart_toの何ハウスに入るか
        """
        overlay = []
        
        # chart_toのハウスカスプを取得
        cusps = [0] + chart_to.cusps  # 1-indexedにする
        
        for point in chart_from.points:
            house = self._find_house_for_longitude(point.longitude, cusps)
            overlay.append({
                "body": point.id,
                "body_ja": point.name_ja,
                "in_house": house
            })
        
        return overlay
    
    def _find_house_for_longitude(
        self,
        longitude: float,
        cusps: List[float]
    ) -> int:
        """黄経からハウス番号を取得"""
        for i in range(1, 13):
            next_i = i % 12 + 1
            if cusps[i] <= longitude < cusps[next_i]:
                return i
            # 0度をまたぐ場合
            if cusps[i] > cusps[next_i]:
                if longitude >= cusps[i] or longitude < cusps[next_i]:
                    return i
        return 1
    
    def _calculate_compatibility_score(
        self,
        aspects: List[Dict]
    ) -> Dict[str, Any]:
        """
        相性スコアを計算
        
        ハーモニアス（吉）とチャレンジング（凶）の重み付け
        """
        harmonious = 0
        challenging = 0
        
        harmonious_types = ["CONJUNCTION", "SEXTILE", "TRINE"]
        challenging_types = ["SQUARE", "OPPOSITION", "QUINCUNX"]
        
        for aspect in aspects:
            if aspect["type"] in harmonious_types:
                harmonious += 10 - aspect["orb"]
            elif aspect["type"] in challenging_types:
                challenging += 10 - aspect["orb"]
        
        total = harmonious + challenging
        harmony_ratio = harmonious / total if total > 0 else 0.5
        
        return {
            "harmonious_points": round(harmonious, 1),
            "challenging_points": round(challenging, 1),
            "harmony_ratio": round(harmony_ratio, 2),
            "overall": "良好" if harmony_ratio > 0.6 else "普通" if harmony_ratio > 0.4 else "困難"
        }


# ============================================
# API関数
# ============================================

def generate_natal_chart(
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    birth_minute: int,
    lat: float,
    lon: float,
    alt: float = 0.0,
    tz_offset: float = 9.0,  # JST
    house_system: str = "PLACIDUS"
) -> Dict[str, Any]:
    """
    ネイタルチャートを生成するAPI関数
    """
    # UTCに変換
    from datetime import timedelta
    local_dt = datetime(birth_year, birth_month, birth_day, birth_hour, birth_minute)
    utc_dt = local_dt - timedelta(hours=tz_offset)
    utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    
    # チャート構築
    builder = ChartBuilder()
    hs = ac.HouseSystem[house_system]
    chart = builder.build_natal_chart(utc_dt, lat, lon, alt, tz_offset, hs)
    
    return chart.to_dict()


def generate_synastry(
    person_a_birth: Tuple[int, int, int, int, int],  # (y, m, d, h, min)
    person_a_location: Tuple[float, float],           # (lat, lon)
    person_b_birth: Tuple[int, int, int, int, int],
    person_b_location: Tuple[float, float],
    tz_offset: float = 9.0
) -> Dict[str, Any]:
    """
    シナストリー（相性図）を生成するAPI関数
    """
    from datetime import timedelta
    
    # Person A
    a_local = datetime(*person_a_birth)
    a_utc = (a_local - timedelta(hours=tz_offset)).replace(tzinfo=timezone.utc)
    
    # Person B
    b_local = datetime(*person_b_birth)
    b_utc = (b_local - timedelta(hours=tz_offset)).replace(tzinfo=timezone.utc)
    
    # チャート構築
    builder = ChartBuilder()
    chart_a = builder.build_natal_chart(a_utc, *person_a_location)
    chart_b = builder.build_natal_chart(b_utc, *person_b_location)
    
    # シナストリー計算
    synastry = SynastryEngine()
    return synastry.calculate_synastry(chart_a, chart_b)
