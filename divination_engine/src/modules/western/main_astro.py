import json
from datetime import datetime
import argparse
from typing import Dict, Any

# Import modules
# 注意: 実行環境によってパスが変わるため、相対インポートではなく絶対インポートを想定
# ここではスタンドアロン実行用にsys.path調整が必要かもしれないが、
# アプリケーション内での使用を前提とする。

try:
    from ...const.astro_const import HouseSystem
    from .astro_core import AstroCore
    from .horoscope_logic import ChartBuilder
    from .aspect_logic import AspectEngine
except ImportError:
    # スタンドアロンテスト用ハック
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
    from divination_engine.src.const.astro_const import HouseSystem
    from divination_engine.src.modules.western.astro_core import AstroCore
    from divination_engine.src.modules.western.horoscope_logic import ChartBuilder
    from divination_engine.src.modules.western.aspect_logic import AspectEngine

class WesternAstrologyEngine:
    def __init__(self):
        self.core = AstroCore()
        self.builder = ChartBuilder(self.core)
        self.aspect_engine = AspectEngine()
        
    def generate_chart_data(
        self,
        dt: datetime,
        lat: float,
        lon: float,
        alt: float = 0.0,
        house_system: str = 'P',
        topocentric: bool = True,
        mnode: bool = False # True = Mean Node, False = True Node
    ) -> Dict[str, Any]:
        """
        チャートデータ生成のエントリーポイント
        """
        # 1. ユリウス日計算
        jd = self.core.get_julian_day(dt)
        
        # 2. ハウスシステム解決
        try:
            h_sys_enum = HouseSystem(house_system)
        except ValueError:
            h_sys_enum = HouseSystem.PLACIDUS
            
        # 3. チャート構築
        chart_data = self.builder.build_chart(
            julian_day=jd,
            lat=lat,
            lon=lon,
            alt=alt,
            house_system=h_sys_enum,
            topocentric=topocentric,
            true_node=not mnode, # 引数はIsMeanなので反転
            five_deg_rule=False # デフォルトOFF
        )
        
        # 4. アスペクト計算
        aspects = self.aspect_engine.calculate_aspects(chart_data['bodies'])
        
        # 5. レスポンス整形
        response = {
            "meta": {
                "datetime": dt.isoformat(),
                "julian_day": jd,
                "location": { "lat": lat, "lon": lon, "alt": alt },
                "house_system": chart_data['options']['house_system'],
                "coordinates": "Topocentric" if topocentric else "Geocentric"
            },
            "points": chart_data['bodies'],
            "houses": chart_data['houses'], # cusps, angles
            "aspects": aspects
        }
        
        return response

# CLI実行用
if __name__ == "__main__":
    import sys
    
    # 簡易引数処理
    # python main_astro.py 2024-01-01T12:00:00 35.68 139.76
    if len(sys.argv) < 4:
        print("Usage: python main_astro.py <ISO-Date> <Lat> <Long> [Alt] [HouseSys]")
        sys.exit(1)
        
    date_str = sys.argv[1]
    lat = float(sys.argv[2])
    lon = float(sys.argv[3])
    alt = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    hsys = sys.argv[5] if len(sys.argv) > 5 else 'P'
    
    dt = datetime.fromisoformat(date_str)
    
    engine = WesternAstrologyEngine()
    result = engine.generate_chart_data(dt, lat, lon, alt, hsys)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
