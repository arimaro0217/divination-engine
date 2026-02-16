"""
ジョーティシュ（インド占星術）計算エンジン
Jyotish Vedic Astrology Engine

pyswissephによる恒星黄道帯計算、アヤナムサ、ナクシャトラ、分割図
"""

import math
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

try:
    import swisseph as swe
except ImportError:
    raise ImportError("pyswissephがインストールされていません: pip install pyswisseph")

try:
    from ..const import jyotish_const as jc
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.const import jyotish_const as jc


# ============================================
# データ構造
# ============================================

@dataclass
class GrahaPosition:
    """グラハ（惑星）の位置情報"""
    graha: jc.Graha
    longitude: float           # 恒星黄経（サイデリアル）
    latitude: float            # 黄緯
    speed: float               # 速度（度/日）
    is_retrograde: bool        # 逆行
    rashi: int                 # ラシインデックス（0-11）
    rashi_name: str            # ラシ名
    degree_in_rashi: float     # ラシ内の度数（0-30）
    nakshatra: int             # ナクシャトラインデックス（0-26）
    nakshatra_name: str        # ナクシャトラ名
    pada: int                  # パダ（1-4）
    navamsha_rashi: int        # ナヴァムシャのラシ（0-11）
    dignity: str               # 品位（高揚/減衰/ムーラトリコーナ/自室/中立）
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": jc.GRAHA_NAMES_EN[self.graha],
            "name_ja": jc.GRAHA_NAMES_JA[self.graha],
            "name_sanskrit": jc.GRAHA_NAMES_SANSKRIT[self.graha],
            "longitude": round(self.longitude, 4),
            "sign": jc.RASHI_NAMES_EN[self.rashi],
            "sign_sanskrit": jc.RASHI_NAMES_SANSKRIT[self.rashi],
            "degree": round(self.degree_in_rashi, 2),
            "nakshatra": self.nakshatra_name,
            "nakshatra_index": self.nakshatra,
            "pada": self.pada,
            "house_d1": self.rashi + 1,
            "sign_d9": jc.RASHI_NAMES_EN[self.navamsha_rashi],
            "sign_d9_sanskrit": jc.RASHI_NAMES_SANSKRIT[self.navamsha_rashi],
            "is_retrograde": self.is_retrograde,
            "dignity": self.dignity,
            "speed": round(self.speed, 4)
        }


@dataclass
class JyotishChart:
    """ジョーティシュチャート"""
    birth_datetime: datetime
    latitude: float
    longitude: float
    timezone_offset: float
    ayanamsa_mode: str
    ayanamsa_value: float
    
    lagna: float               # アセンダント（恒星黄経）
    lagna_rashi: int           # ラグナのラシ
    
    grahas: List[GrahaPosition] = field(default_factory=list)
    
    # 分割図
    d1_chart: Dict[int, List[str]] = field(default_factory=dict)  # ラシ→グラハリスト
    d9_chart: Dict[int, List[str]] = field(default_factory=dict)  # ナヴァムシャ
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "meta": {
                "datetime": self.birth_datetime.isoformat(),
                "latitude": self.latitude,
                "longitude": self.longitude,
                "timezone_offset": self.timezone_offset,
                "ayanamsa": self.ayanamsa_mode,
                "ayanamsa_val": round(self.ayanamsa_value, 4),
                "ascendant": {
                    "sign": jc.RASHI_NAMES_EN[self.lagna_rashi],
                    "sign_sanskrit": jc.RASHI_NAMES_SANSKRIT[self.lagna_rashi],
                    "degree": round(self.lagna % 30, 2)
                }
            },
            "planets": [g.to_dict() for g in self.grahas],
            "charts": {
                "D1": self.d1_chart,
                "D9": self.d9_chart
            }
        }


# ============================================
# VedicAstroCore: 天体計算エンジン
# ============================================

class VedicAstroCore:
    """
    ジョーティシュ天体計算エンジン
    
    恒星黄道帯（Sidereal Zodiac）でのグラハ位置計算
    """
    
    def __init__(self, ayanamsa: jc.AyanamsaMode = jc.DEFAULT_AYANAMSA):
        """
        初期化
        
        Args:
            ayanamsa: アヤナムサモード
        """
        self.ayanamsa = ayanamsa
        swe.set_ephe_path(None)
    
    def datetime_to_jd(self, dt: datetime) -> float:
        """datetimeをユリウス日に変換"""
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc)
        hour_decimal = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        return swe.julday(dt.year, dt.month, dt.day, hour_decimal)
    
    def set_ayanamsa(self, mode: jc.AyanamsaMode):
        """アヤナムサを設定"""
        self.ayanamsa = mode
        swe.set_sid_mode(mode.value)
    
    def get_ayanamsa_value(self, jd: float) -> float:
        """
        現在のアヤナムサ値を取得
        
        Args:
            jd: ユリウス日
            
        Returns:
            アヤナムサ値（度）
        """
        swe.set_sid_mode(self.ayanamsa.value)
        return swe.get_ayanamsa_ut(jd)
    
    def calculate_sidereal_planets(
        self,
        jd: float,
        lat: float = 0.0,
        lon: float = 0.0,
        use_true_node: bool = False
    ) -> List[GrahaPosition]:
        """
        恒星黄道帯でのグラハ位置を計算
        
        Args:
            jd: ユリウス日
            lat: 緯度
            lon: 経度
            use_true_node: 真ノードを使用（Falseで平均ノード）
            
        Returns:
            GrahaPositionのリスト
        """
        # アヤナムサ設定
        swe.set_sid_mode(self.ayanamsa.value)
        ayanamsa_val = swe.get_ayanamsa_ut(jd)
        
        positions = []
        
        for graha in jc.Graha:
            if graha == jc.Graha.KETU:
                # ケートゥはラーフの対向
                continue
            
            # ノードの種類を選択
            if graha == jc.Graha.RAHU:
                swe_id = 11 if use_true_node else 10
            else:
                swe_id = jc.GRAHA_SWE_ID[graha]
            
            # 恒星黄道帯フラグ
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
            
            result, _ = swe.calc_ut(jd, swe_id, flags)
            
            longitude = result[0]
            latitude = result[1]
            speed = result[3]
            
            pos = self._create_graha_position(graha, longitude, latitude, speed)
            positions.append(pos)
        
        # ケートゥを追加（ラーフの対向）
        rahu = next(p for p in positions if p.graha == jc.Graha.RAHU)
        ketu_lon = (rahu.longitude + 180) % 360
        ketu_pos = self._create_graha_position(
            jc.Graha.KETU, ketu_lon, -rahu.latitude, -rahu.speed
        )
        positions.append(ketu_pos)
        
        return positions
    
    def _create_graha_position(
        self,
        graha: jc.Graha,
        longitude: float,
        latitude: float,
        speed: float
    ) -> GrahaPosition:
        """GrahaPositionオブジェクトを作成"""
        # ラシ
        rashi = jc.get_rashi_from_longitude(longitude)
        degree_in_rashi = jc.get_degree_in_rashi(longitude)
        
        # ナクシャトラ
        nakshatra, pada = jc.get_nakshatra_from_longitude(longitude)
        
        # ナヴァムシャ
        navamsha_rashi = self.calculate_navamsha(longitude)
        
        # 品位判定
        dignity = self._determine_dignity(graha, rashi, degree_in_rashi)
        
        return GrahaPosition(
            graha=graha,
            longitude=longitude,
            latitude=latitude,
            speed=speed,
            is_retrograde=speed < 0,
            rashi=rashi,
            rashi_name=jc.RASHI_NAMES_EN[rashi],
            degree_in_rashi=degree_in_rashi,
            nakshatra=nakshatra,
            nakshatra_name=jc.NAKSHATRAS[nakshatra],
            pada=pada,
            navamsha_rashi=navamsha_rashi,
            dignity=dignity
        )
    
    def _determine_dignity(
        self,
        graha: jc.Graha,
        rashi: int,
        degree: float
    ) -> str:
        """グラハの品位を判定"""
        # ラーフ・ケートゥは品位なし
        if graha in [jc.Graha.RAHU, jc.Graha.KETU]:
            return "中立"
        
        # 高揚
        if graha in jc.EXALTATION_SIGNS and jc.EXALTATION_SIGNS[graha] == rashi:
            return "高揚"
        
        # 減衰
        if graha in jc.DEBILITATION_SIGNS and jc.DEBILITATION_SIGNS[graha] == rashi:
            return "減衰"
        
        # ムーラトリコーナ
        if graha in jc.MOOLATRIKONA:
            mt_rashi, mt_start, mt_end = jc.MOOLATRIKONA[graha]
            if rashi == mt_rashi and mt_start <= degree < mt_end:
                return "ムーラトリコーナ"
        
        # 自室（Own Sign）
        if graha in jc.RASHI_LORDS.values():
            for r, lord in jc.RASHI_LORDS.items():
                if lord == graha and r == rashi:
                    return "自室"
        
        return "中立"
    
    def calculate_lagna(self, jd: float, lat: float, lon: float) -> float:
        """
        ラグナ（アセンダント）を計算
        
        Args:
            jd: ユリウス日
            lat: 緯度
            lon: 経度
            
        Returns:
            ラグナの恒星黄経
        """
        swe.set_sid_mode(self.ayanamsa.value)
        
        # ハウス計算（ホールサイン）
        cusps, ascmc = swe.houses(jd, lat, lon, b'W')
        
        # トロピカルASCをサイデリアルに変換
        ayanamsa_val = swe.get_ayanamsa_ut(jd)
        sidereal_asc = (ascmc[0] - ayanamsa_val) % 360
        
        return sidereal_asc
    
    def calculate_navamsha(self, longitude: float) -> int:
        """
        ナヴァムシャ（D9）を計算
        
        各サインを9分割し、対応するナヴァムシャ・サインを返す
        
        Args:
            longitude: 恒星黄経
            
        Returns:
            ナヴァムシャのラシインデックス（0-11）
        """
        rashi = jc.get_rashi_from_longitude(longitude)
        degree_in_rashi = jc.get_degree_in_rashi(longitude)
        
        # サイン内を9分割（各3°20' = 3.333...°）
        navamsha_division = int(degree_in_rashi / (30.0 / 9.0))
        
        # エレメントに応じた開始サインを取得
        start_rashi = jc.NAVAMSHA_START[jc.Rashi(rashi)]
        
        # ナヴァムシャ・サインを計算
        navamsha_rashi = (start_rashi + navamsha_division) % 12
        
        return navamsha_rashi
    
    def get_nakshatra_info(self, longitude: float) -> Dict[str, Any]:
        """
        ナクシャトラ情報を取得
        
        Args:
            longitude: 恒星黄経
            
        Returns:
            ナクシャトラ詳細情報
        """
        nakshatra_idx, pada = jc.get_nakshatra_from_longitude(longitude)
        progress = jc.get_nakshatra_progress(longitude)
        lord = jc.NAKSHATRA_LORDS[nakshatra_idx]
        
        return {
            "index": nakshatra_idx,
            "name": jc.NAKSHATRAS[nakshatra_idx],
            "name_ja": jc.NAKSHATRAS_JA[nakshatra_idx],
            "pada": pada,
            "lord": jc.GRAHA_NAMES_EN[lord],
            "lord_ja": jc.GRAHA_NAMES_JA[lord],
            "progress_percent": round(progress * 100, 2),
            "degree_in_nakshatra": round(longitude % jc.NAKSHATRA_SPAN, 4)
        }


# ============================================
# DashaSystem: ダシャー計算
# ============================================

class DashaSystem:
    """
    ヴィムショッタリ・ダシャー計算システム
    """
    
    def __init__(self):
        self.total_years = jc.TOTAL_DASHA_YEARS
    
    def calculate_vimshottari(
        self,
        moon_longitude: float,
        birth_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        ヴィムショッタリ・ダシャーを計算
        
        Args:
            moon_longitude: 月の恒星黄経
            birth_date: 生年月日
            
        Returns:
            マハダシャーリスト（アンタルダシャー含む）
        """
        # 月のナクシャトラ
        nakshatra_idx, pada = jc.get_nakshatra_from_longitude(moon_longitude)
        nakshatra_lord = jc.NAKSHATRA_LORDS[nakshatra_idx]
        
        # ナクシャトラ内の進行度
        progress = jc.get_nakshatra_progress(moon_longitude)
        
        # 最初のダシャーの残り期間（Balance of Dasha）
        first_dasha_years = jc.DASHA_YEARS[nakshatra_lord]
        balance = first_dasha_years * (1 - progress)
        
        # ダシャーの開始インデックスを特定
        start_idx = jc.DASHA_ORDER.index(nakshatra_lord)
        
        dashas = []
        current_date = birth_date
        
        # 120年分のダシャーを生成
        for cycle in range(2):  # 2サイクル分（240年）
            for i in range(9):
                idx = (start_idx + i) % 9
                lord = jc.DASHA_ORDER[idx]
                
                # 期間を計算
                if cycle == 0 and i == 0:
                    years = balance
                else:
                    years = jc.DASHA_YEARS[lord]
                
                end_date = current_date + timedelta(days=years * 365.25)
                
                # アンタルダシャーを計算
                sub_periods = self._calculate_antardasha(lord, current_date, end_date)
                
                dashas.append({
                    "lord": jc.GRAHA_NAMES_EN[lord],
                    "lord_ja": jc.GRAHA_NAMES_JA[lord],
                    "start_date": current_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "years": round(years, 2),
                    "level": 1,
                    "sub_periods": sub_periods
                })
                
                current_date = end_date
                
                # 200年を超えたら終了
                if (current_date - birth_date).days > 200 * 365.25:
                    return dashas
        
        return dashas
    
    def _calculate_antardasha(
        self,
        maha_lord: jc.Graha,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        アンタルダシャー（中運）を計算
        
        Args:
            maha_lord: マハダシャーの支配星
            start_date: 開始日
            end_date: 終了日
            
        Returns:
            アンタルダシャーリスト
        """
        maha_years = jc.DASHA_YEARS[maha_lord]
        total_days = (end_date - start_date).days
        
        sub_periods = []
        current_date = start_date
        
        # マハダシャー支配星から開始
        start_idx = jc.DASHA_ORDER.index(maha_lord)
        
        for i in range(9):
            idx = (start_idx + i) % 9
            antar_lord = jc.DASHA_ORDER[idx]
            
            # 按分計算
            antar_years = jc.DASHA_YEARS[antar_lord]
            fraction = (maha_years * antar_years) / self.total_years
            antar_days = total_days * (fraction / maha_years)
            
            antar_end = current_date + timedelta(days=antar_days)
            
            sub_periods.append({
                "lord": jc.GRAHA_NAMES_EN[antar_lord],
                "lord_ja": jc.GRAHA_NAMES_JA[antar_lord],
                "start_date": current_date.strftime("%Y-%m-%d"),
                "end_date": antar_end.strftime("%Y-%m-%d"),
                "level": 2
            })
            
            current_date = antar_end
        
        return sub_periods
    
    def get_current_dasha(
        self,
        dashas: List[Dict],
        target_date: datetime
    ) -> Dict[str, Any]:
        """
        指定日時の現在ダシャーを取得
        
        Args:
            dashas: ダシャーリスト
            target_date: 対象日
            
        Returns:
            現在のマハダシャーとアンタルダシャー
        """
        target_str = target_date.strftime("%Y-%m-%d")
        
        for maha in dashas:
            if maha["start_date"] <= target_str <= maha["end_date"]:
                # アンタルダシャーを探索
                for antar in maha["sub_periods"]:
                    if antar["start_date"] <= target_str <= antar["end_date"]:
                        return {
                            "mahadasha": maha["lord"],
                            "mahadasha_ja": maha["lord_ja"],
                            "antardasha": antar["lord"],
                            "antardasha_ja": antar["lord_ja"],
                            "maha_end": maha["end_date"],
                            "antar_end": antar["end_date"]
                        }
        
        return {}


# ============================================
# JyotishAPI: 統合API
# ============================================

class JyotishAPI:
    """
    ジョーティシュ統合API
    """
    
    def __init__(self, ayanamsa: jc.AyanamsaMode = jc.DEFAULT_AYANAMSA):
        self.core = VedicAstroCore(ayanamsa)
        self.dasha = DashaSystem()
    
    def generate_chart(
        self,
        birth_year: int,
        birth_month: int,
        birth_day: int,
        birth_hour: int,
        birth_minute: int,
        lat: float,
        lon: float,
        tz_offset: float = 5.5,  # インド標準時
        ayanamsa: str = "LAHIRI",
        use_true_node: bool = False
    ) -> Dict[str, Any]:
        """
        完全なジョーティシュチャートを生成
        
        Args:
            birth_year: 生年
            birth_month: 生月
            birth_day: 生日
            birth_hour: 生時
            birth_minute: 生分
            lat: 緯度
            lon: 経度
            tz_offset: タイムゾーンオフセット（インドは+5.5）
            ayanamsa: アヤナムサ名
            use_true_node: 真ノードを使用
            
        Returns:
            完全なチャートJSON
        """
        # アヤナムサ設定
        ayanamsa_mode = getattr(jc.AyanamsaMode, ayanamsa, jc.DEFAULT_AYANAMSA)
        self.core.set_ayanamsa(ayanamsa_mode)
        
        # UTCに変換
        local_dt = datetime(birth_year, birth_month, birth_day, birth_hour, birth_minute)
        utc_dt = local_dt - timedelta(hours=tz_offset)
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
        
        jd = self.core.datetime_to_jd(utc_dt)
        ayanamsa_val = self.core.get_ayanamsa_value(jd)
        
        # ラグナ計算
        lagna = self.core.calculate_lagna(jd, lat, lon)
        lagna_rashi = jc.get_rashi_from_longitude(lagna)
        
        # グラハ位置計算
        grahas = self.core.calculate_sidereal_planets(jd, lat, lon, use_true_node)
        
        # D1チャート（ラシチャート）
        d1_chart = self._build_chart_map(grahas)
        
        # D9チャート（ナヴァムシャ）
        d9_chart = self._build_navamsha_map(grahas)
        
        # ダシャー計算
        moon = next(g for g in grahas if g.graha == jc.Graha.CHANDRA)
        dashas = self.dasha.calculate_vimshottari(moon.longitude, local_dt)
        
        # 現在のダシャー
        current_dasha = self.dasha.get_current_dasha(dashas, datetime.now())
        
        # チャート構築
        chart = JyotishChart(
            birth_datetime=local_dt,
            latitude=lat,
            longitude=lon,
            timezone_offset=tz_offset,
            ayanamsa_mode=ayanamsa,
            ayanamsa_value=ayanamsa_val,
            lagna=lagna,
            lagna_rashi=lagna_rashi,
            grahas=grahas,
            d1_chart=d1_chart,
            d9_chart=d9_chart
        )
        
        result = chart.to_dict()
        result["vimshottari_dasha"] = dashas[:12]  # 最初の12期間
        result["current_dasha"] = current_dasha
        
        # ナクシャトラ詳細
        nakshatra_info = self.core.get_nakshatra_info(moon.longitude)
        result["moon_nakshatra"] = nakshatra_info
        
        # トップレベルに追加（スキーマ対応）
        result["nakshatra"] = nakshatra_info["name_ja"]
        result["nakshatra_lord"] = nakshatra_info["lord_ja"]
        
        return result
    
    def _build_chart_map(self, grahas: List[GrahaPosition]) -> Dict[int, List[str]]:
        """D1チャートマップを構築"""
        chart = {i: [] for i in range(12)}
        for g in grahas:
            chart[g.rashi].append(jc.GRAHA_NAMES_EN[g.graha])
        return chart
    
    def _build_navamsha_map(self, grahas: List[GrahaPosition]) -> Dict[int, List[str]]:
        """D9チャートマップを構築"""
        chart = {i: [] for i in range(12)}
        for g in grahas:
            chart[g.navamsha_rashi].append(jc.GRAHA_NAMES_EN[g.graha])
        return chart


# ============================================
# 簡易関数
# ============================================

def generate_jyotish_chart(
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    birth_minute: int,
    lat: float,
    lon: float,
    tz_offset: float = 9.0,  # JST
    ayanamsa: str = "LAHIRI"
) -> Dict[str, Any]:
    """
    ジョーティシュチャートを生成する簡易関数
    """
    api = JyotishAPI()
    return api.generate_chart(
        birth_year, birth_month, birth_day,
        birth_hour, birth_minute,
        lat, lon, tz_offset, ayanamsa
    )
