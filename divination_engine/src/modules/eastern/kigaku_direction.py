"""
九星気学 - GIS連携ユーティリティ

地図上での方位盤表示に必要な機能：
- 方位の角度計算（30/60度分割）
- 磁気偏角の計算
- 地図オーバーレイ用データ生成
"""

import sys
import io
from datetime import datetime
from typing import Dict, List, Tuple
import math

from ...const import kigaku_const as kc

# Windows環境でのUTF-8出力対応（安全版）
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ============================================
# DirectionSplitter: 方位角度計算
# ============================================

class DirectionSplitter:
    """
    方位の角度範囲を計算するクラス
    """
    
    @staticmethod
    def get_direction_range(direction: str, mode: str = "standard") -> Dict[str, float]:
        """
        方位の開始角度・終了角度を取得
        
        Args:
            direction: 方位（"N", "NE", etc.）
            mode: "standard"（30/60度）または "equal"（45度）
        
        Returns:
            {"start": 開始角度, "end": 終了角度, "width": 幅}
        """
        if mode == "standard":
            return kc.DIRECTION_ANGLES_STANDARD.get(direction, {"start": 0, "end": 0, "width": 0})
        else:
            return kc.DIRECTION_ANGLES_EQUAL.get(direction, {"start": 0, "end": 0, "width": 0})
    
    @staticmethod
    def angle_to_direction(angle: float, mode: str = "standard") -> str:
        """
        角度から方位を判定
        
        Args:
            angle: 角度（0-360度、北=0度）
            mode: 分割モード
        
        Returns:
            方位（"N", "NE", etc.）
        """
        # 角度を0-360に正規化
        angle = angle % 360
        
        angles = kc.DIRECTION_ANGLES_STANDARD if mode == "standard" else kc.DIRECTION_ANGLES_EQUAL
        
        for direction, range_data in angles.items():
            start = range_data["start"]
            end = range_data["end"]
            
            # 北方向のみ、0度をまたぐので特別処理
            if start > end:
                if angle >= start or angle < end:
                    return direction
            else:
                if start <= angle < end:
                    return direction
        
        return "N"  # デフォルト


# ============================================
# MagneticDeclination: 偏角計算
# ============================================

class MagneticDeclination:
    """
    地磁気偏角の計算クラス（日本国内簡易版）
    """
    
    @staticmethod
    def calc_declination_japan(lat: float, lon: float, date: datetime = None) -> float:
        """
        日本国内の磁気偏角を簡易計算
        
        基準点：東京（北緯35度、東経140度）で約-7度（西偏）
        
        Args:
            lat: 緯度
            lon: 経度
            date: 日時（将来の時間変化対応用、現在は未使用）
        
        Returns:
            偏角（度）負の値は西偏
        """
        # 簡易計算式
        # declination ≈ base + (lat - base_lat) * lat_coef + (lon - base_lon) * lon_coef
        
        declination = (
            kc.MAGNETIC_DECLINATION_BASE +
            (lat - kc.MAGNETIC_BASE_LAT) * kc.MAGNETIC_LAT_COEFFICIENT +
            (lon - kc.MAGNETIC_BASE_LON) * kc.MAGNETIC_LON_COEFFICIENT
        )
        
        return declination
    
    @staticmethod
    def apply_declination(true_north_angle: float, declination: float) -> float:
        """
        真北の角度に偏角を適用して磁北の角度を取得
        
        Args:
            true_north_angle: 真北基準の角度
            declination: 偏角（西偏は負）
        
        Returns:
            磁北基準の角度
        """
        # 西偏（負の偏角）の場合、角度を減算
        magnetic_north_angle = (true_north_angle - declination) % 360
        return magnetic_north_angle


# ============================================
# MapOverlay: 地図オーバーレイデータ生成
# ============================================

class MapOverlay:
    """
    地図上に方位盤を表示するためのデータを生成
    """
    
    def __init__(self):
        """初期化"""
        self.splitter = DirectionSplitter()
        self.declination_calc = MagneticDeclination()
    
    def create_overlay_data(
        self,
        center_lat: float,
        center_lon: float,
        directions_info: Dict[str, any],
        mode: str = "standard",
        use_magnetic: bool = False
    ) -> Dict:
        """
        地図オーバーレイ用のJSON データを生成
        
        Args:
            center_lat: 中心点の緯度
            center_lon: 中心点の経度
            directions_info: 各方位の情報（DirectionInfoのdict）
            mode: 分割モード
            use_magnetic: 磁北を使用するか
        
        Returns:
            オーバーレイデータ
        """
        # 偏角を計算
        declination = 0.0
        if use_magnetic:
            declination = self.declination_calc.calc_declination_japan(center_lat, center_lon)
        
        sectors = []
        
        for direction in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
            # 角度範囲を取得
            range_data = self.splitter.get_direction_range(direction, mode)
            start_angle = range_data["start"]
            end_angle = range_data["end"]
            
            # 偏角補正
            if use_magnetic:
                start_angle = self.declination_calc.apply_declination(start_angle, declination)
                end_angle = self.declination_calc.apply_declination(end_angle, declination)
            
            # 方位情報
            dir_info = directions_info.get(direction, {})
            
            sector = {
                "label": direction,
                "name_jp": kc.DIRECTION_NAMES_JP[direction],
                "start_angle": round(start_angle, 1),
                "end_angle": round(end_angle, 1),
                "star": dir_info.get("star", 5),
                "star_name": dir_info.get("star_name", ""),
                "status": dir_info.get("status", "neutral"),
                "notes": dir_info.get("notes", [])
            }
            
            sectors.append(sector)
        
        return {
            "center_lat": center_lat,
            "center_lon": center_lon,
            "magnetic_declination": round(declination, 2) if use_magnetic else 0.0,
            "division_mode": mode,
            "use_magnetic_north": use_magnetic,
            "sectors": sectors
        }
