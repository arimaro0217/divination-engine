"""
西洋占星術 天体計算コアモジュール
Western Astrology Core Calculation Module

pyswissephによる精密天体計算、トポセントリック座標、逆行判定
"""

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

try:
    import swisseph as swe
except ImportError:
    raise ImportError("pyswissephがインストールされていません: pip install pyswisseph")

try:
    from ..const import astro_const as ac
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.const import astro_const as ac


# ============================================
# データ構造
# ============================================

@dataclass
class CelestialPosition:
    """天体の位置情報"""
    body_id: int
    body_name: str
    longitude: float          # 黄経（0-360）
    latitude: float           # 黄緯
    distance: float           # 地球からの距離（AU）
    speed: float              # 黄経方向の速度（度/日）
    declination: float        # 赤緯
    right_ascension: float    # 赤経
    is_retrograde: bool       # 逆行中かどうか
    sign_index: int           # サインインデックス（0-11）
    sign_name: str            # サイン名
    sign_degree: float        # サイン内の度数（0-30）
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": ac.BODY_NAMES_EN.get(self.body_id, f"Body_{self.body_id}"),
            "name_ja": ac.BODY_NAMES_JA.get(self.body_id, ""),
            "longitude": round(self.longitude, 4),
            "latitude": round(self.latitude, 4),
            "distance": round(self.distance, 6),
            "speed": round(self.speed, 4),
            "is_retrograde": self.is_retrograde,
            "sign": self.sign_name,
            "sign_id": self.sign_index,
            "relative_degree": round(self.sign_degree, 2),
            "formatted": ac.format_degree(self.longitude)
        }


@dataclass
class HouseCusps:
    """ハウスカスプ情報"""
    cusps: List[float]        # 12ハウスのカスプ（1-12、インデックス1から）
    asc: float                # アセンダント
    mc: float                 # MC
    armc: float               # ARMC（恒星時）
    vertex: float             # バーテックス
    equasc: float             # イコリアルアセンダント
    house_system: str         # 使用したハウスシステム
    
    @property
    def dsc(self) -> float:
        """ディセンダント"""
        return (self.asc + 180) % 360
    
    @property
    def ic(self) -> float:
        """IC"""
        return (self.mc + 180) % 360
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cusps": [round(c, 4) for c in self.cusps[1:]],  # 1-12
            "asc": round(self.asc, 4),
            "mc": round(self.mc, 4),
            "dsc": round(self.dsc, 4),
            "ic": round(self.ic, 4),
            "vertex": round(self.vertex, 4),
            "house_system": self.house_system
        }


# ============================================
# AstroCore: 天体計算エンジン
# ============================================

class AstroCore:
    """
    西洋占星術 天体計算エンジン
    
    pyswissephを使用した高精度天体計算
    """
    
    def __init__(self):
        """初期化"""
        swe.set_ephe_path(None)  # デフォルトエフェメリス
    
    def datetime_to_jd(self, dt: datetime) -> float:
        """
        datetimeをユリウス日に変換
        
        Args:
            dt: datetime（UTCであること）
            
        Returns:
            ユリウス日
        """
        # UTCに変換
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc)
        
        hour_decimal = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        return swe.julday(dt.year, dt.month, dt.day, hour_decimal)
    
    def jd_to_datetime(self, jd: float) -> datetime:
        """
        ユリウス日をdatetimeに変換
        """
        year, month, day, hour_frac = swe.revjul(jd)
        hour = int(hour_frac)
        minute = int((hour_frac - hour) * 60)
        second = int(((hour_frac - hour) * 60 - minute) * 60)
        return datetime(int(year), int(month), int(day), hour, minute, second, tzinfo=timezone.utc)
    
    def calculate_body(
        self,
        jd: float,
        body_id: int,
        lat: float = 0.0,
        lon: float = 0.0,
        alt: float = 0.0,
        topocentric: bool = False
    ) -> CelestialPosition:
        """
        天体の位置を計算
        
        Args:
            jd: ユリウス日
            body_id: 天体ID（CelestialBody enum）
            lat: 観測地の緯度
            lon: 観測地の経度
            alt: 観測地の標高（メートル）
            topocentric: トポセントリック座標を使用するか
            
        Returns:
            CelestialPosition: 天体位置情報
        """
        # 計算フラグ
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        
        if topocentric:
            # トポセントリック座標（視差補正）
            flags |= swe.FLG_TOPOCTR
            swe.set_topo(lon, lat, alt)
        
        # 天体位置計算
        result, ret_flags = swe.calc_ut(jd, body_id, flags)
        
        longitude = result[0]
        latitude = result[1]
        distance = result[2]
        speed = result[3]
        
        # 赤道座標も計算
        flags_eq = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
        result_eq, _ = swe.calc_ut(jd, body_id, flags_eq)
        right_ascension = result_eq[0]
        declination = result_eq[1]
        
        # サイン計算
        sign_idx, sign_degree = ac.degree_to_sign(longitude)
        
        # 逆行判定
        is_retrograde = speed < 0
        
        return CelestialPosition(
            body_id=body_id,
            body_name=ac.BODY_NAMES_EN.get(body_id, f"Body_{body_id}"),
            longitude=longitude,
            latitude=latitude,
            distance=distance,
            speed=speed,
            declination=declination,
            right_ascension=right_ascension,
            is_retrograde=is_retrograde,
            sign_index=sign_idx,
            sign_name=ac.SIGN_NAMES_EN[sign_idx],
            sign_degree=sign_degree
        )
    
    def calculate_all_bodies(
        self,
        jd: float,
        lat: float = 0.0,
        lon: float = 0.0,
        alt: float = 0.0,
        topocentric: bool = False,
        use_true_node: bool = True,
        use_true_lilith: bool = False,
        include_asteroids: bool = True
    ) -> List[CelestialPosition]:
        """
        全天体の位置を計算
        
        Args:
            jd: ユリウス日
            lat, lon, alt: 観測地
            topocentric: トポセントリック補正
            use_true_node: 真ノードを使用（Falseで平均ノード）
            use_true_lilith: 真リリスを使用（Falseで平均リリス）
            include_asteroids: 小惑星を含める
            
        Returns:
            全天体の位置リスト
        """
        positions = []
        
        # 10大天体
        main_bodies = [
            ac.CelestialBody.SUN,
            ac.CelestialBody.MOON,
            ac.CelestialBody.MERCURY,
            ac.CelestialBody.VENUS,
            ac.CelestialBody.MARS,
            ac.CelestialBody.JUPITER,
            ac.CelestialBody.SATURN,
            ac.CelestialBody.URANUS,
            ac.CelestialBody.NEPTUNE,
            ac.CelestialBody.PLUTO,
        ]
        
        for body in main_bodies:
            # 月はトポセントリック補正が有効
            use_topo = topocentric and (body == ac.CelestialBody.MOON)
            pos = self.calculate_body(jd, body, lat, lon, alt, use_topo)
            positions.append(pos)
        
        # ノード
        node_id = ac.CelestialBody.TRUE_NODE if use_true_node else ac.CelestialBody.MEAN_NODE
        positions.append(self.calculate_body(jd, node_id, lat, lon, alt))
        
        # リリス
        lilith_id = ac.CelestialBody.OSCU_APOGEE if use_true_lilith else ac.CelestialBody.MEAN_APOGEE
        positions.append(self.calculate_body(jd, lilith_id, lat, lon, alt))
        
        # キロン
        try:
            positions.append(self.calculate_body(jd, ac.CelestialBody.CHIRON, lat, lon, alt))
        except:
            pass  # エフェメリスがない場合はスキップ
        
        # 小惑星
        if include_asteroids:
            asteroids = [
                ac.CelestialBody.CERES,
                ac.CelestialBody.PALLAS,
                ac.CelestialBody.JUNO,
                ac.CelestialBody.VESTA,
            ]
            for ast in asteroids:
                try:
                    positions.append(self.calculate_body(jd, ast, lat, lon, alt))
                except:
                    pass  # エフェメリスがない場合はスキップ
        
        return positions
    
    def calculate_houses(
        self,
        jd: float,
        lat: float,
        lon: float,
        house_system: ac.HouseSystem = ac.HouseSystem.PLACIDUS
    ) -> HouseCusps:
        """
        ハウスカスプを計算
        
        Args:
            jd: ユリウス日
            lat: 緯度
            lon: 経度
            house_system: ハウスシステム
            
        Returns:
            HouseCusps: ハウスカスプ情報
        """
        try:
            # ハウス計算
            cusps, ascmc = swe.houses(jd, lat, lon, house_system.value.encode())
            
            # cuspsは13要素（0番目は未使用、1-12がハウス）
            # ascmcは10要素
            # ascmc[0] = ASC, ascmc[1] = MC, ascmc[2] = ARMC, ascmc[3] = Vertex...
            
            return HouseCusps(
                cusps=list(cusps),
                asc=ascmc[0],
                mc=ascmc[1],
                armc=ascmc[2],
                vertex=ascmc[3],
                equasc=ascmc[4],
                house_system=house_system.name
            )
            
        except Exception as e:
            # 高緯度でプラシーダスが失敗した場合、ポルフィリーにフォールバック
            if house_system == ac.HouseSystem.PLACIDUS:
                return self.calculate_houses(jd, lat, lon, ac.HouseSystem.PORPHYRY)
            raise e
    
    def calculate_part_of_fortune(
        self,
        sun_lon: float,
        moon_lon: float,
        asc: float,
        is_night: bool = False
    ) -> float:
        """
        パート・オブ・フォーチュン（幸運点）を計算
        
        昼生まれ: ASC + Moon - Sun
        夜生まれ: ASC + Sun - Moon
        
        Args:
            sun_lon: 太陽黄経
            moon_lon: 月黄経
            asc: アセンダント
            is_night: 夜生まれかどうか
            
        Returns:
            幸運点の黄経
        """
        if is_night:
            fortune = asc + sun_lon - moon_lon
        else:
            fortune = asc + moon_lon - sun_lon
        
        return fortune % 360
    
    def is_night_chart(self, sun_lon: float, asc: float) -> bool:
        """
        夜生まれかどうかを判定
        
        太陽がASC-DSCラインより下（7-12ハウス側）にあれば夜
        """
        dsc = (asc + 180) % 360
        
        # 太陽がDSC側にあるかチェック
        if asc < dsc:
            return asc < sun_lon < dsc
        else:
            return sun_lon > asc or sun_lon < dsc


# ============================================
# AspectEngine: アスペクト解析エンジン
# ============================================

class AspectEngine:
    """
    アスペクト解析エンジン
    
    アスペクト検出、Applying/Separating判定
    """
    
    def __init__(self, orb_settings: ac.OrbSettings = None):
        """初期化"""
        self.orbs = orb_settings or ac.DEFAULT_ORBS
    
    def get_orb(self, aspect: ac.AspectType) -> float:
        """アスペクトのオーブを取得"""
        orb_map = {
            ac.AspectType.CONJUNCTION: self.orbs.conjunction,
            ac.AspectType.SEXTILE: self.orbs.sextile,
            ac.AspectType.SQUARE: self.orbs.square,
            ac.AspectType.TRINE: self.orbs.trine,
            ac.AspectType.OPPOSITION: self.orbs.opposition,
            ac.AspectType.SEMI_SEXTILE: self.orbs.semi_sextile,
            ac.AspectType.SEMI_SQUARE: self.orbs.semi_square,
            ac.AspectType.QUINTILE: self.orbs.quintile,
            ac.AspectType.SESQUIQUADRATE: self.orbs.sesquiquadrate,
            ac.AspectType.QUINCUNX: self.orbs.quincunx,
        }
        return orb_map.get(aspect, 5.0)
    
    def find_aspect(
        self,
        pos_a: CelestialPosition,
        pos_b: CelestialPosition,
        include_minor: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        2天体間のアスペクトを検出
        
        Args:
            pos_a: 天体Aの位置
            pos_b: 天体Bの位置
            include_minor: マイナーアスペクトを含めるか
            
        Returns:
            アスペクト情報（見つからなければNone）
        """
        # 角度差を計算
        diff = ac.angle_difference(pos_a.longitude, pos_b.longitude)
        
        # チェックするアスペクト
        aspects_to_check = ac.MAJOR_ASPECTS.copy()
        if include_minor:
            aspects_to_check.extend(ac.MINOR_ASPECTS)
        
        for aspect in aspects_to_check:
            orb = self.get_orb(aspect)
            
            # 天体ペアのオーブ補正
            mod_a = ac.ORB_MODIFIERS.get(pos_a.body_id, 0.5)
            mod_b = ac.ORB_MODIFIERS.get(pos_b.body_id, 0.5)
            effective_orb = orb * max(mod_a, mod_b)
            
            # アスペクト判定
            deviation = abs(diff - aspect.value)
            if deviation <= effective_orb:
                # Applying/Separating判定
                state = self._determine_aspect_state(pos_a, pos_b, aspect.value)
                
                return {
                    "body_a": pos_a.body_name,
                    "body_b": pos_b.body_name,
                    "type": aspect.name,
                    "type_ja": ac.ASPECT_NAMES[aspect]["ja"],
                    "angle": aspect.value,
                    "orb": round(deviation, 2),
                    "state": state.value,
                    "is_major": aspect in ac.MAJOR_ASPECTS
                }
        
        return None
    
    def _determine_aspect_state(
        self,
        pos_a: CelestialPosition,
        pos_b: CelestialPosition,
        target_angle: float
    ) -> ac.AspectState:
        """
        アスペクトがApplyingかSeparatingかを判定
        
        速い天体が遅い天体に近づいているかで判定
        """
        # 現在の角度差
        current_diff = (pos_b.longitude - pos_a.longitude) % 360
        if current_diff > 180:
            current_diff -= 360
        
        # 1時間後の位置を予測
        future_lon_a = pos_a.longitude + pos_a.speed / 24
        future_lon_b = pos_b.longitude + pos_b.speed / 24
        
        future_diff = (future_lon_b - future_lon_a) % 360
        if future_diff > 180:
            future_diff -= 360
        
        # オーブがタイトになるか
        current_deviation = abs(abs(current_diff) - target_angle)
        future_deviation = abs(abs(future_diff) - target_angle)
        
        if abs(current_deviation) < 0.05:
            return ac.AspectState.EXACT
        elif future_deviation < current_deviation:
            return ac.AspectState.APPLYING
        else:
            return ac.AspectState.SEPARATING
    
    def find_all_aspects(
        self,
        positions: List[CelestialPosition],
        include_minor: bool = False
    ) -> List[Dict[str, Any]]:
        """
        全天体間のアスペクトを検出
        
        Args:
            positions: 天体位置リスト
            include_minor: マイナーアスペクトを含めるか
            
        Returns:
            アスペクトリスト
        """
        aspects = []
        
        for i, pos_a in enumerate(positions):
            for pos_b in positions[i+1:]:
                aspect = self.find_aspect(pos_a, pos_b, include_minor)
                if aspect:
                    aspects.append(aspect)
        
        return aspects


# ============================================
# VoidOfCourse: ボイドタイム計算
# ============================================

class VoidOfCourseCalculator:
    """
    月のボイドタイム計算
    
    月が次のサインに入るまでメジャーアスペクトを作らない期間
    """
    
    def __init__(self):
        self.core = AstroCore()
        self.aspect_engine = AspectEngine()
    
    def calculate_void_of_course(
        self,
        jd: float,
        lat: float = 0.0,
        lon: float = 0.0
    ) -> Dict[str, Any]:
        """
        現在のボイドタイム状態を計算
        
        Args:
            jd: ユリウス日
            lat, lon: 観測地
            
        Returns:
            ボイドタイム情報
        """
        # 現在の全天体位置
        positions = self.core.calculate_all_bodies(jd, lat, lon)
        
        # 月の位置
        moon = next(p for p in positions if p.body_id == ac.CelestialBody.MOON)
        
        # 月が次のサインに入る時刻を計算
        next_sign_entry = self._find_next_sign_entry(jd, moon)
        
        # 次のサイン入りまでに月がメジャーアスペクトを作るか
        last_aspect, is_void = self._check_void_period(jd, next_sign_entry, positions)
        
        return {
            "is_void": is_void,
            "moon_sign": moon.sign_name,
            "moon_degree": round(moon.sign_degree, 2),
            "next_sign_entry_jd": next_sign_entry,
            "next_sign": ac.SIGN_NAMES_EN[(moon.sign_index + 1) % 12],
            "last_aspect": last_aspect
        }
    
    def _find_next_sign_entry(self, jd: float, moon: CelestialPosition) -> float:
        """月が次のサインに入るJDを計算"""
        degrees_to_next = 30 - moon.sign_degree
        days_to_next = degrees_to_next / abs(moon.speed)
        return jd + days_to_next
    
    def _check_void_period(
        self,
        start_jd: float,
        end_jd: float,
        positions: List[CelestialPosition]
    ) -> Tuple[Optional[Dict], bool]:
        """ボイド期間かどうかをチェック"""
        # 簡易版：現在のアスペクトを確認
        moon = next(p for p in positions if p.body_id == ac.CelestialBody.MOON)
        
        last_aspect = None
        for pos in positions:
            if pos.body_id == ac.CelestialBody.MOON:
                continue
            
            aspect = self.aspect_engine.find_aspect(moon, pos, include_minor=False)
            if aspect and aspect["state"] == ac.AspectState.SEPARATING.value:
                last_aspect = aspect
        
        # 月がApplyingなアスペクトを持っていなければボイド
        has_applying = any(
            a for pos in positions if pos.body_id != ac.CelestialBody.MOON
            for a in [self.aspect_engine.find_aspect(moon, pos)]
            if a and a["state"] == ac.AspectState.APPLYING.value
        )
        
        return last_aspect, not has_applying
