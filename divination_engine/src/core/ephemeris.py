"""
天体計算エンジン（Swiss Ephemeris Wrapper）
Moshier ephemeris使用（外部ファイル不要）
"""
import swisseph as swe
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import IntEnum
import math


class Planet(IntEnum):
    """惑星ID（Swiss Ephemeris定義）"""
    SUN = swe.SUN
    MOON = swe.MOON
    MERCURY = swe.MERCURY
    VENUS = swe.VENUS
    MARS = swe.MARS
    JUPITER = swe.JUPITER
    SATURN = swe.SATURN
    URANUS = swe.URANUS
    NEPTUNE = swe.NEPTUNE
    PLUTO = swe.PLUTO
    MEAN_NODE = swe.MEAN_NODE      # 平均ノード（ラーフ）
    TRUE_NODE = swe.TRUE_NODE      # 真ノード
    CHIRON = swe.CHIRON


PLANET_NAMES = {
    Planet.SUN: "太陽",
    Planet.MOON: "月",
    Planet.MERCURY: "水星",
    Planet.VENUS: "金星",
    Planet.MARS: "火星",
    Planet.JUPITER: "木星",
    Planet.SATURN: "土星",
    Planet.URANUS: "天王星",
    Planet.NEPTUNE: "海王星",
    Planet.PLUTO: "冥王星",
    Planet.MEAN_NODE: "ラーフ",
    Planet.TRUE_NODE: "真ラーフ",
    Planet.CHIRON: "キロン",
}

ZODIAC_SIGNS = [
    "牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
    "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"
]

ZODIAC_SIGNS_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


@dataclass
class PlanetData:
    """惑星データ"""
    planet_id: int
    name: str
    longitude: float          # 黄経（度）
    latitude: float           # 黄緯（度）
    distance: float           # 距離（AU）
    speed: float              # 日速度（度/日）
    sign_index: int           # サインインデックス（0-11）
    sign: str                 # サイン名
    degree_in_sign: float     # サイン内度数
    is_retrograde: bool       # 逆行中フラグ


@dataclass  
class HouseData:
    """ハウスデータ"""
    cusps: List[float]        # 12ハウスのカスプ度数
    ascendant: float          # ASC
    midheaven: float          # MC
    armc: float               # ARMC（赤経中天）
    vertex: float             # バーテックス
    equatorial_ascendant: float  # 赤道上昇点


class AstroEngine:
    """
    天体計算エンジン
    Moshier ephemeris使用（外部エフェメリスファイル不要）
    """
    
    # ハウスシステムの定義
    HOUSE_PLACIDUS = b'P'
    HOUSE_KOCH = b'K'
    HOUSE_WHOLE_SIGN = b'W'
    HOUSE_EQUAL = b'E'
    HOUSE_CAMPANUS = b'C'
    HOUSE_REGIOMONTANUS = b'R'
    
    # アヤナムサ（インド占星術用）
    AYANAMSA_LAHIRI = swe.SIDM_LAHIRI
    AYANAMSA_KRISHNAMURTI = swe.SIDM_KRISHNAMURTI
    AYANAMSA_RAMAN = swe.SIDM_RAMAN
    
    def __init__(self):
        """
        初期化
        Moshier ephemerisを使用するため、エフェメリスパスは設定しない
        """
        # Moshier（MOSEPH）を使用する場合、ephe_pathを設定しない
        # pyswissephはデフォルトでMoshier計算を使用
        pass
    
    def calc_julian_day(self, year: int, month: int, day: int, 
                        hour: float = 0.0, ut: bool = True) -> float:
        """ユリウス日を計算"""
        if ut:
            return swe.julday(year, month, day, hour)
        else:
            # ETの場合はΔTを加算
            jd_ut = swe.julday(year, month, day, hour)
            delta_t = swe.deltat(jd_ut)
            return jd_ut + delta_t
    
    def get_planet_position(self, jd_ut: float, planet_id: int, 
                           sidereal: bool = False,
                           ayanamsa: int = None) -> PlanetData:
        """
        惑星位置を計算
        
        Args:
            jd_ut: ユリウス日（UT）
            planet_id: 惑星ID（Planet enum）
            sidereal: サイデリアル方式（インド占星術）
            ayanamsa: アヤナムサタイプ（sidereal=True時）
            
        Returns:
            PlanetData: 惑星位置データ
        """
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        
        if sidereal:
            if ayanamsa is None:
                ayanamsa = self.AYANAMSA_LAHIRI
            swe.set_sid_mode(ayanamsa, 0, 0)
            flags |= swe.FLG_SIDEREAL
        
        result, ret_flag = swe.calc_ut(jd_ut, planet_id, flags)
        
        longitude = result[0]
        latitude = result[1]
        distance = result[2]
        speed = result[3]
        
        # サイン計算
        sign_index = int(longitude // 30)
        degree_in_sign = longitude % 30
        sign = ZODIAC_SIGNS[sign_index]
        
        # 逆行判定（速度が負）
        is_retrograde = speed < 0
        
        # 惑星名取得
        name = PLANET_NAMES.get(planet_id, f"Planet_{planet_id}")
        
        return PlanetData(
            planet_id=planet_id,
            name=name,
            longitude=longitude,
            latitude=latitude,
            distance=distance,
            speed=speed,
            sign_index=sign_index,
            sign=sign,
            degree_in_sign=degree_in_sign,
            is_retrograde=is_retrograde
        )
    
    def get_all_planets(self, jd_ut: float, sidereal: bool = False,
                        ayanamsa: int = None) -> List[PlanetData]:
        """全惑星の位置を取得"""
        planets = [
            Planet.SUN, Planet.MOON, Planet.MERCURY, Planet.VENUS,
            Planet.MARS, Planet.JUPITER, Planet.SATURN,
            Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO,
            Planet.TRUE_NODE, Planet.CHIRON
        ]
        
        return [self.get_planet_position(jd_ut, p, sidereal, ayanamsa) 
                for p in planets]
    
    def get_houses(self, jd_ut: float, latitude: float, longitude: float,
                   house_system: bytes = None) -> HouseData:
        """
        ハウスカスプを計算
        
        Args:
            jd_ut: ユリウス日
            latitude: 出生地緯度
            longitude: 出生地経度
            house_system: ハウスシステム（デフォルト：プラシーダス）
            
        Returns:
            HouseData: ハウスデータ
        """
        if house_system is None:
            house_system = self.HOUSE_PLACIDUS
        
        cusps, ascmc = swe.houses(jd_ut, latitude, longitude, house_system)
        
        # cuspsは1-12のインデックス（0は未使用）
        # ascmcは[ASC, MC, ARMC, Vertex, Equasc, ...]
        
        return HouseData(
            cusps=list(cusps[1:13]),  # 12ハウス分
            ascendant=ascmc[0],
            midheaven=ascmc[1],
            armc=ascmc[2],
            vertex=ascmc[3],
            equatorial_ascendant=ascmc[4]
        )
    
    def get_solar_longitude(self, jd_ut: float) -> float:
        """太陽黄経を取得（二十四節気計算用）"""
        sun = self.get_planet_position(jd_ut, Planet.SUN)
        return sun.longitude
    
    def find_solar_term_time(self, year: int, target_longitude: float,
                             start_jd: float = None) -> float:
        """
        太陽が特定の黄経に達する時刻を検索
        
        Args:
            year: 年
            target_longitude: 目標黄経（度）
            start_jd: 検索開始ユリウス日（省略時は1月1日）
            
        Returns:
            ユリウス日
        """
        if start_jd is None:
            start_jd = self.calc_julian_day(year, 1, 1, 0)
        
        # 初期推定（太陽は約1度/日移動）
        current_lon = self.get_solar_longitude(start_jd)
        
        # 目標との差分を計算（0-360度範囲で正規化）
        diff = (target_longitude - current_lon) % 360
        if diff > 180:
            diff -= 360
        
        # 初期推定日
        jd = start_jd + diff
        
        # ニュートン法で収束
        for _ in range(20):
            lon = self.get_solar_longitude(jd)
            diff = target_longitude - lon
            
            # 角度差を-180〜180に正規化
            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360
            
            # 収束判定（0.0001度 ≈ 0.36秒角）
            if abs(diff) < 0.0001:
                break
            
            # 太陽の移動速度（約1度/日）で補正
            jd += diff / 1.0
        
        return jd
    
    def get_ayanamsa(self, jd_ut: float, ayanamsa_type: int = None) -> float:
        """
        アヤナムサ値を取得
        
        Args:
            jd_ut: ユリウス日
            ayanamsa_type: アヤナムサタイプ（デフォルト：Lahiri）
            
        Returns:
            アヤナムサ値（度）
        """
        if ayanamsa_type is None:
            ayanamsa_type = self.AYANAMSA_LAHIRI
        
        swe.set_sid_mode(ayanamsa_type, 0, 0)
        return swe.get_ayanamsa_ut(jd_ut)
    
    def get_moon_nakshatra(self, jd_ut: float, ayanamsa_type: int = None) -> Tuple[int, str, float]:
        """
        月のナクシャトラ（二十七宿）を取得
        
        Returns:
            (ナクシャトラ番号1-27, ナクシャトラ名, ナクシャトラ内度数)
        """
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
        
        moon = self.get_planet_position(jd_ut, Planet.MOON, sidereal=True, ayanamsa=ayanamsa_type)
        
        # ナクシャトラは13度20分（13.333...度）ごと
        nakshatra_span = 360 / 27
        nakshatra_index = int(moon.longitude / nakshatra_span)
        degree_in_nakshatra = moon.longitude % nakshatra_span
        
        return nakshatra_index + 1, NAKSHATRAS[nakshatra_index], degree_in_nakshatra
    
    @staticmethod
    def calc_aspect(lon1: float, lon2: float) -> Tuple[Optional[str], float]:
        """
        二つの黄経間のアスペクトを判定
        
        Returns:
            (アスペクト名, オーブ) またはアスペクトなしの場合は (None, 0)
        """
        ASPECTS = {
            0: ("合", 10),
            60: ("六分", 6),
            90: ("矩", 8),
            120: ("三分", 8),
            180: ("衝", 10),
        }
        
        diff = abs(lon1 - lon2)
        if diff > 180:
            diff = 360 - diff
        
        for angle, (name, max_orb) in ASPECTS.items():
            orb = abs(diff - angle)
            if orb <= max_orb:
                return name, orb
        
        return None, 0
    
    def get_aspects(self, planets: List[PlanetData]) -> List[Dict]:
        """全惑星間のアスペクトを計算"""
        aspects = []
        
        for i, p1 in enumerate(planets):
            for p2 in planets[i+1:]:
                aspect_name, orb = self.calc_aspect(p1.longitude, p2.longitude)
                if aspect_name:
                    aspects.append({
                        "planet1": p1.name,
                        "planet2": p2.name,
                        "aspect": aspect_name,
                        "orb": round(orb, 2)
                    })
        
        return aspects
