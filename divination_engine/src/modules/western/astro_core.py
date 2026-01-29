import swisseph as swe
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import os

from ...const.astro_const import PlanetId

class AstroCore:
    """
    Swiss Ephemeris Wrapper for High-Precision Astrology
    
    NASA JPL Horizons相当の精度を目指し、
    トポセントリック座標、真位置/平均位置の切り替え、
    精密な速度計算などを提供するコアエンジン。
    """
    
    def __init__(self, ephe_path: Optional[str] = None):
        """
        Args:
            ephe_path: エフェメリスファイルのパス (Noneの場合は環境変数またはデフォルト)
        """
        # エフェメリスパスの設定
        if ephe_path:
            swe.set_ephe_path(ephe_path)
        else:
            # 一般的なパスを試行
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, 'data', 'ephe')
            if os.path.exists(data_dir):
                swe.set_ephe_path(data_dir)
            # なければシステムのデフォルトまたは環境変数に依存
            
    def get_julian_day(self, dt: datetime) -> float:
        """
        datetimeオブジェクトをユリウス日(UTC)に変換
        """
        # UTCに変換
        if dt.tzinfo:
            dt_utc = dt.astimezone(timezone.utc)
        else:
            dt_utc = dt.replace(tzinfo=timezone.utc)
            
        return swe.julday(
            dt_utc.year, dt_utc.month, dt_utc.day,
            dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
        )
        
    def calculate_body(
        self, 
        julian_day: float, 
        body_id: int, 
        lat: float = 0.0, 
        lon: float = 0.0, 
        alt: float = 0.0,
        topocentric: bool = False
    ) -> Dict[str, float]:
        """
        天体位置を計算
        
        Args:
            julian_day: ユリウス日
            body_id: 天体ID (PlanetId参照)
            lat: 緯度 (度)
            lon: 経度 (度)
            alt: 標高 (メートル)
            topocentric: Trueならトポセントリック(地表)座標、Falseならジオセントリック(地心)座標
            
        Returns:
            {
                "longitude": 黄経 (0-360),
                "latitude": 黄緯,
                "distance": 地球からの距離 (AU),
                "speed_long": 黄経方向の速度 (度/日),
                "declination": 赤緯,
                "right_ascension": 赤経,
                "is_retrograde": 逆行フラグ
            }
        """
        # フラグ設定
        # SEFLG_SPEED: 速度計算を含める
        # SEFLG_SWIEPH: Swiss Ephemeris計算を使用
        flags = swe.FLG_SPEED | swe.FLG_SWIEPH
        
        if topocentric:
            # トポセントリック計算
            swe.set_topo(lon, lat, alt)
            flags |= swe.FLG_TOPOCTR
        else:
            # ジオセントリック（デフォルト）
            pass
            
        # 計算実行 (黄道座標)
        try:
            # longitude, latitude, distance, speed_long, speed_lat, speed_dist
            res = swe.calc_ut(julian_day, body_id, flags)
            xx = res[0]
            
            # 赤道座標も計算
            flags_eq = flags | swe.FLG_EQUATORIAL
            try:
                res_eq = swe.calc_ut(julian_day, body_id, flags_eq)
                xx_eq = res_eq[0]
            except swe.Error:
                # 赤道座標だけ失敗することは稀だが、フォールバックとして0を入れるか
                xx_eq = [0.0, 0.0]

            return {
                "longitude": xx[0],
                "latitude": xx[1],
                "distance": xx[2],
                "speed_long": xx[3],
                "declination": xx_eq[1],     
                "right_ascension": xx_eq[0], 
                "is_retrograde": xx[3] < 0
            }
            
        except swe.Error as e:
            # エラー処理: ファイルがない場合など
            err_msg = str(e)
            if "SwissEph file" in err_msg and "not found" in err_msg:
                # Moshier Ephemerisで再試行 (FLG_SWIEPHを外す)
                if body_id < swe.CHIRON: # 主要惑星のみ
                    flags &= ~swe.FLG_SWIEPH
                    try:
                        res = swe.calc_ut(julian_day, body_id, flags)
                        xx = res[0]
                        return {
                            "longitude": xx[0],
                            "latitude": xx[1],
                            "distance": xx[2],
                            "speed_long": xx[3],
                            "declination": 0.0, # 簡易
                            "right_ascension": 0.0,
                            "is_retrograde": xx[3] < 0
                        }
                    except swe.Error:
                        pass
            
            # それでもダメなら(小惑星など)、ダミーデータを返すか例外
            # ここでは処理継続のためダミーデータを返し、警告を出す
            print(f"Warning: Calculation failed for body {body_id}. {e}")
            return {
                "longitude": 0.0, "latitude": 0.0, "distance": 0.0, 
                "speed_long": 0.0, "declination": 0.0, "right_ascension": 0.0,
                "is_retrograde": False,
                "error": str(e)
            }

    def get_node_position(self, julian_day: float, mean_mode: bool = True) -> Dict[str, float]:
        """
        ノード（ドラゴンヘッド）の位置計算
        
        Args:
            mlat: True/Meanの切り替え
        """
        node_id = PlanetId.MEAN_NODE if mean_mode else PlanetId.TRUE_NODE
        return self.calculate_body(julian_day, node_id)

    def get_lilith_position(self, julian_day: float, mean_mode: bool = True) -> Dict[str, float]:
        """
        リリス（月の遠地点）の位置計算
        """
        lilith_id = PlanetId.MEAN_APOGEE if mean_mode else PlanetId.OSCU_APOGEE
        return self.calculate_body(julian_day, lilith_id)


# ============================================
# 月のボイドタイム計算
# ============================================

class VoidOfCourseCalculator:
    """
    月のボイドタイム（Void of Course）計算エンジン
    
    ボイドタイム = 月が現在のサインを離れるまでに、
    他の惑星とメジャーアスペクトを形成しない期間
    
    ビジネス・契約・重要な決断を避けるべき時間帯として
    プロの占星術師に重要視される機能
    """
    
    # メジャーアスペクト角度（ボイド判定に使用）
    MAJOR_ASPECTS = [0, 60, 90, 120, 180]  # conjunction, sextile, square, trine, opposition
    
    # メジャーアスペクトのオーブ（度）
    MAJOR_ASPECT_ORB = 8.0
    
    # チェック対象惑星
    PLANETS_FOR_VOC = [
        PlanetId.SUN, PlanetId.MERCURY, PlanetId.VENUS, PlanetId.MARS,
        PlanetId.JUPITER, PlanetId.SATURN, PlanetId.URANUS, 
        PlanetId.NEPTUNE, PlanetId.PLUTO
    ]
    
    def __init__(self, core: AstroCore = None):
        self.core = core or AstroCore()
    
    def calculate_void_of_course(
        self,
        julian_day: float,
        lat: float = 0.0,
        lon: float = 0.0,
        alt: float = 0.0
    ) -> Dict[str, Any]:
        """
        指定時刻における月のボイドタイム状態を計算
        
        Args:
            julian_day: ユリウス日
            lat: 緯度
            lon: 経度
            alt: 標高
            
        Returns:
            {
                "is_void": ボイドタイム中かどうか,
                "void_start": ボイド開始時刻（JD）,
                "void_end": サイン変更時刻（JD）,
                "current_sign": 現在の月のサイン,
                "next_sign": 次のサイン,
                "last_aspect": 最後に形成したアスペクト情報,
                "description": 説明文
            }
        """
        # 月の現在位置を取得
        moon_data = self.core.calculate_body(julian_day, PlanetId.MOON, lat, lon, alt)
        moon_lon = moon_data['longitude']
        moon_speed = moon_data['speed_long']
        
        # 現在のサインと次のサイン境界
        current_sign_idx = int(moon_lon // 30)
        next_sign_boundary = (current_sign_idx + 1) * 30
        
        # サイン変更までの時間を計算
        degrees_to_next_sign = next_sign_boundary - moon_lon
        if degrees_to_next_sign <= 0:
            degrees_to_next_sign += 360
        
        # 月の平均速度は約13度/日
        days_to_next_sign = degrees_to_next_sign / abs(moon_speed) if moon_speed != 0 else 1.0
        sign_change_jd = julian_day + days_to_next_sign
        
        # 他の惑星の位置を取得
        planets_data = {}
        for planet_id in self.PLANETS_FOR_VOC:
            planets_data[planet_id] = self.core.calculate_body(julian_day, planet_id, lat, lon, alt)
        
        # 現在から次のサイン境界までにアスペクトを形成するか検索
        last_aspect = None
        next_aspect_before_sign_change = None
        
        # 時間ステップ（1時間 = 1/24日）で検索
        step = 1.0 / 24.0
        check_jd = julian_day
        
        while check_jd < sign_change_jd:
            moon_check = self.core.calculate_body(check_jd, PlanetId.MOON, lat, lon, alt)
            moon_check_lon = moon_check['longitude']
            
            # まだ現在のサインにいることを確認
            if int(moon_check_lon // 30) != current_sign_idx:
                break
            
            for planet_id in self.PLANETS_FOR_VOC:
                planet_check = self.core.calculate_body(check_jd, planet_id, lat, lon, alt)
                planet_lon = planet_check['longitude']
                
                # アスペクトチェック
                aspect = self._check_major_aspect(moon_check_lon, planet_lon)
                if aspect:
                    if check_jd <= julian_day:
                        # 過去または現在のアスペクト
                        last_aspect = {
                            "planet": planet_id.name,
                            "aspect_type": aspect,
                            "time_jd": check_jd
                        }
                    else:
                        # 未来のアスペクト（サイン変更前）
                        next_aspect_before_sign_change = {
                            "planet": planet_id.name,
                            "aspect_type": aspect,
                            "time_jd": check_jd
                        }
                        break
            
            if next_aspect_before_sign_change:
                break
                
            check_jd += step
        
        # ボイド判定
        is_void = (next_aspect_before_sign_change is None)
        
        # サイン名
        sign_names = [
            "牡羊座", "牡牛座", "双子座", "蟹座",
            "獅子座", "乙女座", "天秤座", "蠍座",
            "射手座", "山羊座", "水瓶座", "魚座"
        ]
        current_sign = sign_names[current_sign_idx]
        next_sign = sign_names[(current_sign_idx + 1) % 12]
        
        # 説明文
        if is_void:
            desc = f"月は{current_sign}でボイドタイム中です。次の{next_sign}に入るまで重要な決断は避けましょう。"
        else:
            desc = f"月は{current_sign}でアクティブです。"
        
        return {
            "is_void": is_void,
            "void_end_jd": sign_change_jd if is_void else None,
            "current_sign": current_sign,
            "current_sign_index": current_sign_idx,
            "next_sign": next_sign,
            "degrees_to_next_sign": round(degrees_to_next_sign, 2),
            "hours_to_next_sign": round(days_to_next_sign * 24, 1),
            "last_aspect": last_aspect,
            "next_aspect": next_aspect_before_sign_change,
            "description": desc,
            "warning": "契約・重要決断は避けることを推奨" if is_void else None
        }
    
    def _check_major_aspect(self, moon_lon: float, planet_lon: float) -> str:
        """
        2つの黄経間でメジャーアスペクトが形成されているかチェック
        
        Returns:
            アスペクト名（形成されている場合）またはNone
        """
        diff = abs(moon_lon - planet_lon)
        if diff > 180:
            diff = 360 - diff
        
        aspect_names = {
            0: "Conjunction",
            60: "Sextile",
            90: "Square",
            120: "Trine",
            180: "Opposition"
        }
        
        for angle, name in aspect_names.items():
            if abs(diff - angle) <= self.MAJOR_ASPECT_ORB:
                return name
        
        return None


# シングルトンインスタンス（必要に応じて）
default_core = AstroCore()

