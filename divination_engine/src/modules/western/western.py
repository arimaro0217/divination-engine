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
    Swiss Ephemerisベースの現代西洋占星術エンジンを使用
    """
    
    def __init__(self):
        # 新しいエンジンを初期化
        from .main_astro import WesternAstrologyEngine
        self.engine = WesternAstrologyEngine()
    
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
        # エンジンで計算 (標準設定: プラシーダス、Topocentric)
        # ※必要に応じてAPIからオプションを受け取れるように拡張可能
        chart_data = self.engine.generate_chart_data(
            dt=birth_dt,
            lat=latitude,
            lon=longitude,
            alt=0.0, # 標高はとりあえず0
            house_system='P', # プラシーダス
            topocentric=True, # トポセントリック
            mnode=False # True Node
        )
        
        # 結果をスキーマに合わせて変換
        
        # 1. 惑星
        planets = []
        for body in chart_data['points']:
            # エラーがある場合（Chironなど）はスキップするか、デフォルト値を入れる
            # ここではエラーが含まれる場合はスキップ
            if "error" in body:
                continue
                
            planets.append(PlanetPosition(
                planet=body['name'], # 日本語名は別途マッピングが必要だが、スキーマはstrなので英語でも一旦OK
                longitude=body['longitude'],
                sign=body['sign_jp'], # sign_infoでjpを持たせている
                degree_in_sign=body['relative_degree'],
                house=body['house'],
                retrograde=body['is_retrograde']
            ))
            
        # 2. ハウス (list -> dict)
        # chart_data['houses']['cusps'] はリスト
        house_cusps = {i+1: cusp for i, cusp in enumerate(chart_data['houses']['cusps'])}
        
        # 3. アングル
        asc = chart_data['houses']['angles']['asc']
        mc = chart_data['houses']['angles']['mc']
        
        # 4. アスペクト
        aspects = []
        for asp in chart_data['aspects']:
            aspects.append(Aspect(
                planet1=asp['body_a'],
                planet2=asp['body_b'],
                aspect_type=asp['type'], # 英語名
                orb=asp['orb'],
                applying=(asp['state'] == "Applying")
            ))
            
        return WesternResult(
            planets=planets,
            houses=house_cusps,
            ascendant=asc,
            midheaven=mc,
            aspects=aspects
        )

    def get_sign_ruler(self, sign: str) -> str:
        """サインの支配星を取得"""
        rulers = {
            "牡羊座": "火星", "牡牛座": "金星", "双子座": "水星",
            "蟹座": "月", "獅子座": "太陽", "乙女座": "水星",
            "天秤座": "金星", "蠍座": "冥王星", "射手座": "木星",
            "山羊座": "土星", "水瓶座": "天王星", "魚座": "海王星"
        }
        return rulers.get(sign, "不明")
