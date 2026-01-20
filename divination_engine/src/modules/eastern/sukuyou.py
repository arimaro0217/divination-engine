"""
宿曜占星術モジュール
二十七宿の計算と相性判定
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ...core.ephemeris import AstroEngine, Planet
from ...core.time_manager import TimeManager
from ...models.output_schema import SukuyouResult
from ...const import sukuyou_const as sk


class SukuyouEngine:
    """
    宿曜占星術計算エンジン
    月の実位置（経度法）に基づいて27宿を判定
    
    主な機能：
    - 月の黄経から本命宿を算出（経度法）
    - 七曜属性の判定
    - 人間関係（相性）判定の枠組み
    """
    
    def __init__(self):
        """初期化"""
        self.astro = AstroEngine()
    
    def calculate(self, birth_dt: datetime) -> SukuyouResult:
        """
        宿曜を計算
        
        高精度を目指すため、旧暦の日付ではなく、
        月の実位置（黄経）から27宿を割り出す「経度法」を採用。
        
        Args:
            birth_dt: 生年月日時（タイムゾーン付き）
            
        Returns:
            SukuyouResult: 宿曜計算結果
            
        Raises:
            ValueError: 計算に失敗した場合
        """
        try:
            jd = TimeManager.to_julian_day(birth_dt)
            
            # 月の位置から宿を計算（経度法）
            mansion_num, mansion_name = self._calc_mansion_from_moon(jd)
            
            # 宿の属性を取得
            element = sk.MANSION_BASE_TYPE[mansion_num % 7]
            
            # 七曜を取得
            weekday = sk.MANSION_WEEKDAY[mansion_num]
            
            return SukuyouResult(
                natal_mansion=mansion_name,
                mansion_number=mansion_num + 1,  # 1-indexed
                element=element
            )
        except Exception as e:
            # エラー時は失敗結果を返す
            return SukuyouResult(
                divination_type="sukuyou",
                success=False,
                error_message=f"宿曜計算エラー: {str(e)}",
                natal_mansion="",
                mansion_number=0,
                element=""
            )
    
    def _calc_mansion_from_moon(self, jd: float) -> Tuple[int, str]:
        """
        月の黄経から二十七宿を計算（経度法）
        
        インド占星術のナクシャトラと同様に、
        黄道を27分割し、月の位置から宿を決定する。
        
        各宿の幅: 360° / 27 = 13° 20' = 13.333...°
        起点: 昴宿の開始位置（プレアデス星団、牡羊座26度付近）
        
        Args:
            jd: ユリウス日
            
        Returns:
            (宿のインデックス0-26, 宿名)
        """
        # 月の位置を取得（トロピカル方式）
        moon = self.astro.get_planet_position(jd, Planet.MOON, sidereal=False)
        moon_longitude = moon.longitude
        
        # 昴宿の起点を考慮して調整
        # 宿曜では牡羊座26度付近から昴宿が始まる
        adjusted_longitude = (moon_longitude - sk.MANSION_START_OFFSET + 360) % 360
        
        # 27宿に分割して宿インデックスを計算
        mansion_index = int(adjusted_longitude / sk.MANSION_SPAN)
        
        # 範囲チェック（0-26）
        if mansion_index < 0 or mansion_index >= 27:
            mansion_index = mansion_index % 27
        
        return mansion_index, sk.MANSIONS[mansion_index]
    
    def calc_compatibility(self, mansion1: int, mansion2: int) -> str:
        """
        二つの宿の相性を計算
        
        宿曜における相性は、2つの宿の距離（0-26）によって決まる。
        同じ宿なら「命」、距離1なら「業」など。
        
        Args:
            mansion1: 本命宿の番号（0-26）
            mansion2: 相手の宿の番号（0-26）
            
        Returns:
            相性の種類（例: "命（同じ宿）", "業（近業）"）
        """
        # 距離を計算（0-26の範囲）
        distance = (mansion2 - mansion1) % 27
        
        # 相性マトリクスから取得
        return sk.COMPATIBILITY.get(distance, "不明")
    
    def get_mansion_details(self, mansion_index: int) -> Dict:
        """
        宿の詳細情報を取得
        
        Args:
            mansion_index: 宿のインデックス（0-26）
            
        Returns:
            宿の詳細情報（名前、読み、七曜、属性など）
        """
        if 0 <= mansion_index < 27:
            return {
                "name": sk.MANSIONS[mansion_index],
                "reading": sk.MANSION_READINGS[mansion_index],
                "weekday": sk.MANSION_WEEKDAY[mansion_index],
                "type": sk.MANSION_BASE_TYPE[mansion_index % 7],
                "number": mansion_index + 1
            }
        return {}
    
    def calc_relationship_type(self, own_mansion: int, other_mansion: int) -> Dict[str, str]:
        """
        人間関係の分類を計算
        
        宿曜では、自分の宿から見た相手の宿との関係を、
        「命・業・胎・栄・親・友・安・危・成・壊・衰」などに分類する。
        
        Args:
            own_mansion: 自分の宿インデックス（0-26）
            other_mansion: 相手の宿インデックス（0-26）
            
        Returns:
            関係の詳細情報
        """
        compatibility = self.calc_compatibility(own_mansion, other_mansion)
        distance = (other_mansion - own_mansion) % 27
        
        # 近距離・中距離・遠距離の判定
        if distance <= 13:
            range_type = "近"
        else:
            range_type = "遠"
        
        return {
            "compatibility": compatibility,
            "distance": distance,
            "range": range_type
        }
    
    def get_seven_luminaries(self, jd: float) -> Dict[str, float]:
        """
        九曜（七曜 + 羅睺・計都）の位置を取得
        
        宿曜占星術では、太陽・月・火星・水星・木星・金星・土星の
        七曜に加えて、羅睺（ラーフ、月の昇交点）と計都（ケートゥ、降交点）
        の九曜を使用する。
        
        Args:
            jd: ユリウス日
            
        Returns:
            各曜の黄経（度）
        """
        positions = {}
        
        # 七曜の位置を取得
        sun = self.astro.get_planet_position(jd, Planet.SUN)
        moon = self.astro.get_planet_position(jd, Planet.MOON)
        mars = self.astro.get_planet_position(jd, Planet.MARS)
        mercury = self.astro.get_planet_position(jd, Planet.MERCURY)
        jupiter = self.astro.get_planet_position(jd, Planet.JUPITER)
        venus = self.astro.get_planet_position(jd, Planet.VENUS)
        saturn = self.astro.get_planet_position(jd, Planet.SATURN)
        
        # 羅睺（ラーフ）= 月の平均昇交点
        rahu = self.astro.get_planet_position(jd, Planet.MEAN_NODE)
        
        # 計都（ケートゥ）= 羅睺の対向（180度反対側）
        ketu_longitude = (rahu.longitude + 180) % 360
        
        positions = {
            "日": sun.longitude,
            "月": moon.longitude,
            "火": mars.longitude,
            "水": mercury.longitude,
            "木": jupiter.longitude,
            "金": venus.longitude,
            "土": saturn.longitude,
            "羅睺": rahu.longitude,
            "計都": ketu_longitude
        }
        
        return positions
