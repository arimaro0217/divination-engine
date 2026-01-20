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

# シングルトンインスタンス（必要に応じて）
default_core = AstroCore()
