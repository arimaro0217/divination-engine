"""
紫微斗数 APIモジュール
Zi Wei Dou Shu API Module

Webフロントエンド向けJSON出力を生成
"""

from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from ...const import ziwei_const as zc
    from ...core.lunar_core import (
        LunisolarEngine, LunarDate, ChineseHour, LeapMonthMode
    )
except ImportError:
    # 直接実行時のフォールバック
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from src.const import ziwei_const as zc
    from src.core.lunar_core import LunisolarEngine, LunarDate, ChineseHour, LeapMonthMode
from .ziwei_logic import ZiweiBuilder, ZiweiChart, DecadeLuckCalculator, Star


# ============================================
# ZiweiAPI: メインAPIクラス
# ============================================

class ZiweiAPI:
    """
    紫微斗数 APIクラス
    
    生年月日時と出生地から完全な命盤JSONを生成
    """
    
    def __init__(self):
        """初期化"""
        self.lunar_engine = LunisolarEngine(use_jst=True)
        self.builder = ZiweiBuilder()
        self.decade_calc = DecadeLuckCalculator()
    
    def generate_chart(
        self,
        birth_year: int,
        birth_month: int,
        birth_day: int,
        birth_hour: int,
        birth_minute: int = 0,
        longitude: float = 139.76,  # 東京
        latitude: float = 35.68,
        gender: str = "male",
        leap_mode: str = "A"
    ) -> Dict[str, Any]:
        """
        紫微斗数命盤を生成
        
        Args:
            birth_year: 生年（西暦）
            birth_month: 生月（1-12）
            birth_day: 生日（1-31）
            birth_hour: 生時（0-23）
            birth_minute: 生分（0-59）
            longitude: 経度（東経が正）
            latitude: 緯度
            gender: 性別（"male" or "female"）
            leap_mode: 閏月処理モード（"A", "B", "C"）
            
        Returns:
            完全な命盤JSON構造
        """
        # 生年月日時のdatetime
        birth_dt = datetime(birth_year, birth_month, birth_day, birth_hour, birth_minute)
        
        # 真太陽時を計算
        true_solar_time = self.lunar_engine.get_true_solar_time(birth_dt, longitude)
        
        # 時辰を取得
        hour_branch = self.lunar_engine.get_chinese_hour(true_solar_time)
        
        # 旧暦変換
        lunar_date = self.lunar_engine.convert_to_lunar(
            birth_dt, 
            LeapMonthMode(leap_mode)
        )
        
        # 年干支を計算
        year_stem, year_branch = self._calculate_year_ganzhi(birth_year, birth_month, birth_day)
        
        # 命盤を構築
        chart = self.builder.build_chart(
            birth_datetime=birth_dt,
            lunar_date=lunar_date,
            hour_branch=hour_branch,
            year_stem=year_stem,
            year_branch=year_branch,
            gender=gender
        )
        
        # 大限を計算
        decade_luck = self.decade_calc.calculate_decade_luck(
            chart.bureau,
            gender,
            year_stem,
            chart.life_palace_index
        )
        
        # JSON構造に変換
        return self._chart_to_json(chart, decade_luck)
    
    def _calculate_year_ganzhi(
        self, 
        year: int, 
        month: int, 
        day: int
    ) -> tuple:
        """
        年干支を計算（立春基準）
        
        Args:
            year: 西暦年
            month: 月
            day: 日
            
        Returns:
            (年干, 年支) のタプル
        """
        # 立春前は前年として扱う
        # 簡易版：2月4日を節目とする
        if month < 2 or (month == 2 and day < 4):
            year -= 1
        
        # 干支計算
        # 1984年は甲子年
        stem_idx = (year - 4) % 10
        branch_idx = (year - 4) % 12
        
        return zc.STEMS[stem_idx], zc.BRANCHES[branch_idx]
    
    def _chart_to_json(
        self, 
        chart: ZiweiChart,
        decade_luck: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        ZiweiChartをJSON構造に変換
        
        Args:
            chart: 命盤
            decade_luck: 大限情報
            
        Returns:
            JSON構造
        """
        # 命主・身主を特定
        life_palace = next(
            (p for p in chart.palaces if p.palace_type == "命宮"), 
            None
        )
        body_palace = next(
            (p for p in chart.palaces if p.index == chart.body_palace_index),
            None
        )
        
        life_master = ""
        body_master = ""
        
        if life_palace and life_palace.major_stars:
            life_master = life_palace.major_stars[0].name
        if body_palace and body_palace.major_stars:
            body_master = body_palace.major_stars[0].name
        
        # 基本情報
        basic_info = {
            "birth_datetime": chart.birth_datetime.isoformat(),
            "lunar_date": str(chart.lunar_date),
            "lunar_year": chart.lunar_date.year,
            "lunar_month": chart.lunar_date.month,
            "lunar_day": chart.lunar_date.day,
            "is_leap_month": chart.lunar_date.is_leap_month,
            "hour_branch": chart.hour_branch.branch_name,
            "hour_branch_index": chart.hour_branch.branch_index,
            "gender": chart.gender,
            "bureau": chart.bureau,
            "bureau_name": chart.bureau_name,
            "year_ganzhi": f"{chart.year_stem}{chart.year_branch}",
            "life_palace_branch": zc.BRANCHES[chart.life_palace_index],
            "body_palace_branch": zc.BRANCHES[chart.body_palace_index],
            "life_master": life_master,
            "body_master": body_master,
            "ziwei_position": zc.BRANCHES[chart.ziwei_position],
            "tianfu_position": zc.BRANCHES[chart.tianfu_position]
        }
        
        # 十二宮
        palaces = []
        for palace in chart.palaces:
            palace_data = {
                "position": f"{palace.branch} ({zc.BRANCHES.index(palace.branch)})",
                "branch": palace.branch,
                "branch_index": palace.index,
                "stem": palace.stem,
                "name": palace.palace_type,
                "ganzhi": f"{palace.stem}{palace.branch}",
                "major_stars": [
                    self._star_to_dict(s) for s in palace.major_stars
                ],
                "minor_stars": [s.name for s in palace.minor_stars],
                "bad_stars": [s.name for s in palace.bad_stars],
                "twelve_phase": palace.twelve_phase,
                "coordinates": {
                    "row": palace.grid_coords[0],
                    "col": palace.grid_coords[1]
                }
            }
            
            # 大限情報を追加
            luck = next(
                (d for d in decade_luck if d["palace_index"] == palace.index),
                None
            )
            if luck:
                palace_data["decade_luck"] = luck["period"]
            
            # 身宮かどうか
            palace_data["is_body_palace"] = (palace.index == chart.body_palace_index)
            
            palaces.append(palace_data)
        
        # 三合宮（命宮・財帛宮・官禄宮）
        life_idx = chart.life_palace_index
        triangular = {
            "life_triad": [
                zc.BRANCHES[life_idx],
                zc.BRANCHES[(life_idx + 4) % 12],  # 財帛宮
                zc.BRANCHES[(life_idx + 8) % 12]   # 官禄宮
            ]
        }
        
        # 四化情報
        sihua_info = []
        for palace in chart.palaces:
            for star in palace.major_stars:
                if star.sihua:
                    sihua_info.append({
                        "star": star.name,
                        "transform": star.sihua,
                        "palace": palace.palace_type,
                        "branch": palace.branch
                    })
        
        return {
            "basic_info": basic_info,
            "palaces": palaces,
            "decade_luck": decade_luck,
            "triangular_relationship": triangular,
            "sihua": sihua_info,
            "grid_layout": self._generate_grid_layout(chart)
        }
    
    def _star_to_dict(self, star: Star) -> Dict[str, Any]:
        """StarオブジェクトをJSON形式に変換"""
        brightness_name = None
        if star.brightness is not None:
            brightness_name = zc.BRIGHTNESS_NAMES.get(star.brightness, "")
        
        return {
            "name": star.name,
            "brightness": brightness_name,
            "brightness_value": star.brightness,
            "transform": star.sihua
        }
    
    def _generate_grid_layout(self, chart: ZiweiChart) -> List[List[Dict]]:
        """
        Webフロント用の4x4グリッドレイアウトを生成
        
        Returns:
            4x4のグリッド構造（中央2x2は空）
        """
        grid = [[None for _ in range(4)] for _ in range(4)]
        
        for palace in chart.palaces:
            row, col = palace.grid_coords
            if row is not None and col is not None:
                grid[row][col] = {
                    "branch": palace.branch,
                    "name": palace.palace_type,
                    "major_stars": [s.name for s in palace.major_stars],
                    "is_life_palace": palace.palace_type == "命宮",
                    "is_body_palace": palace.index == chart.body_palace_index
                }
        
        return grid


# ============================================
# 簡易関数
# ============================================

def generate_ziwei_chart(
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    birth_minute: int = 0,
    longitude: float = 139.76,
    latitude: float = 35.68,
    gender: str = "male",
    leap_mode: str = "A"
) -> Dict[str, Any]:
    """
    紫微斗数命盤を生成する簡易関数
    
    Args:
        birth_year: 生年（西暦）
        birth_month: 生月（1-12）
        birth_day: 生日（1-31）
        birth_hour: 生時（0-23）
        birth_minute: 生分（0-59）
        longitude: 経度
        latitude: 緯度
        gender: 性別
        leap_mode: 閏月処理モード
        
    Returns:
        命盤JSON
    """
    api = ZiweiAPI()
    return api.generate_chart(
        birth_year, birth_month, birth_day,
        birth_hour, birth_minute,
        longitude, latitude,
        gender, leap_mode
    )


# ============================================
# メイン（テスト用）
# ============================================

if __name__ == "__main__":
    import json
    
    # テスト: 1992年2月17日 12:00 東京 男性
    chart = generate_ziwei_chart(
        birth_year=1992,
        birth_month=2,
        birth_day=17,
        birth_hour=12,
        birth_minute=0,
        longitude=139.76,
        latitude=35.68,
        gender="male"
    )
    
    print(json.dumps(chart, ensure_ascii=False, indent=2))
