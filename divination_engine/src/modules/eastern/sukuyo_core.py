"""
宿曜占星術 旧暦コア・本命宿算出モジュール
Sukuyo Calendar Core Module

pyswissephによる旧暦変換と旧暦法による本命宿計算
"""

from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from ...core.lunar_core import LunisolarEngine, LunarDate, LeapMonthMode
    from ...const import sukuyou_const as sk
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from src.core.lunar_core import LunisolarEngine, LunarDate, LeapMonthMode
    from src.const import sukuyou_const as sk


# ============================================
# データ構造
# ============================================

class LeapMonthHandling(Enum):
    """閏月の処理方法"""
    PREVIOUS_MONTH = "previous"   # 全期間を前月扱い（密教の一般的解釈）
    SPLIT_BY_15 = "split"         # 15日で分割


@dataclass
class SukuyoProfile:
    """宿曜プロファイル"""
    birth_datetime: datetime
    lunar_date: LunarDate
    honmei_shuku: str           # 本命宿名
    honmei_index: int           # 本命宿インデックス（0-26）
    birth_weekday: str          # 生まれた曜日
    seven_luminary: str         # 七曜属性
    personality_group: str      # 性格グループ


# ============================================
# SukuyoCalendar: 暦と宿の導出
# ============================================

class SukuyoCalendar:
    """
    宿曜暦計算エンジン
    
    pyswissephを使用した旧暦変換と、
    宿曜経の宿割テーブルに基づく本命宿算出
    """
    
    def __init__(self, leap_handling: LeapMonthHandling = LeapMonthHandling.PREVIOUS_MONTH):
        """
        初期化
        
        Args:
            leap_handling: 閏月の処理方法
        """
        self.lunar_engine = LunisolarEngine(use_jst=True)
        self.leap_handling = leap_handling
    
    def calculate_lunar_date(
        self, 
        birth_dt: datetime,
        leap_mode: str = "B"  # 宿曜では閏月を前月扱いが一般的
    ) -> LunarDate:
        """
        グレゴリオ暦を旧暦に変換
        
        Args:
            birth_dt: 生年月日時
            leap_mode: 閏月処理モード
            
        Returns:
            LunarDate: 旧暦日付
        """
        mode = LeapMonthMode(leap_mode)
        return self.lunar_engine.convert_to_lunar(birth_dt, mode)
    
    def get_honmei_shuku(
        self, 
        lunar_month: int, 
        lunar_day: int,
        is_leap_month: bool = False
    ) -> Tuple[int, str]:
        """
        旧暦法による本命宿を算出
        
        宿曜経の「宿割」テーブルに基づく計算。
        各月の1日には起算宿が設定されており、
        そこから日数分だけ宿が進む。
        
        Args:
            lunar_month: 旧暦月（1-12）
            lunar_day: 旧暦日（1-30）
            is_leap_month: 閏月かどうか
            
        Returns:
            (宿インデックス0-26, 宿名)
        """
        # 閏月の処理
        effective_month = lunar_month
        if is_leap_month:
            if self.leap_handling == LeapMonthHandling.PREVIOUS_MONTH:
                pass  # そのまま前月として扱う
            elif self.leap_handling == LeapMonthHandling.SPLIT_BY_15:
                if lunar_day > 15:
                    effective_month = (lunar_month % 12) + 1
        
        # その月の起算宿を取得
        start_mansion = sk.MONTH_START_MANSION.get(effective_month, 22)
        
        # 日数分だけ宿を進める（1日は起算宿）
        mansion_index = (start_mansion + lunar_day - 1) % 27
        
        return mansion_index, sk.MANSIONS[mansion_index]
    
    def get_birth_weekday(self, birth_dt: datetime) -> str:
        """
        生まれた曜日を取得
        
        Args:
            birth_dt: 生年月日時
            
        Returns:
            曜日名（日月火水木金土）
        """
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        return weekdays[birth_dt.weekday()]
    
    def calculate_profile(self, birth_dt: datetime) -> SukuyoProfile:
        """
        完全な宿曜プロファイルを計算
        
        Args:
            birth_dt: 生年月日時
            
        Returns:
            SukuyoProfile: 完全なプロファイル
        """
        # 旧暦変換
        lunar_date = self.calculate_lunar_date(birth_dt)
        
        # 本命宿算出
        mansion_index, mansion_name = self.get_honmei_shuku(
            lunar_date.month,
            lunar_date.day,
            lunar_date.is_leap_month
        )
        
        # 生まれた曜日
        birth_weekday = self.get_birth_weekday(birth_dt)
        
        # 七曜属性
        seven_luminary = sk.MANSION_WEEKDAY[mansion_index]
        
        # 性格グループ
        group = sk.MANSION_PERSONALITY_GROUP.get(
            mansion_index,
            sk.PersonalityGroup.WAZOU
        )
        
        return SukuyoProfile(
            birth_datetime=birth_dt,
            lunar_date=lunar_date,
            honmei_shuku=mansion_name,
            honmei_index=mansion_index,
            birth_weekday=birth_weekday,
            seven_luminary=seven_luminary,
            personality_group=group.value
        )


# ============================================
# メインAPI
# ============================================

class SukuyoAPI:
    """
    宿曜占星術 統合API
    """
    
    def __init__(self):
        from .sukuyo_relationship import RelationshipEngine, DestinyMatrix
        
        self.calendar = SukuyoCalendar()
        self.relationship = RelationshipEngine()
        self.destiny = DestinyMatrix()
    
    def generate_chart(
        self,
        birth_year: int,
        birth_month: int,
        birth_day: int,
        target_date: Optional[datetime] = None
    ) -> Dict:
        """
        完全な宿曜チャートを生成
        
        Args:
            birth_year: 生年
            birth_month: 生月
            birth_day: 生日
            target_date: 日運対象日
            
        Returns:
            完全なJSON構造
        """
        if target_date is None:
            target_date = datetime.now()
        
        birth_dt = datetime(birth_year, birth_month, birth_day)
        
        # プロファイル計算
        profile = self.calendar.calculate_profile(birth_dt)
        
        # 性格情報
        personality = self.destiny.get_personality(profile.honmei_index)
        
        # 日運
        daily_fortune = self.destiny.get_daily_fortune(
            profile.honmei_index,
            target_date
        )
        
        # 円盤データ
        mandala = self.relationship.generate_mandala(profile.honmei_index)
        
        return {
            "user_profile": {
                "birth_date": birth_dt.strftime("%Y-%m-%d"),
                "lunar_date": str(profile.lunar_date),
                "honmei_shuku": profile.honmei_shuku,
                "honmei_index": profile.honmei_index,
                "group": profile.personality_group,
                "seven_luminary": f"{profile.seven_luminary}曜日",
                "birth_weekday": f"{profile.birth_weekday}曜日",
                "personality": personality
            },
            "daily_fortune": {
                "target_date": target_date.strftime("%Y-%m-%d"),
                "day_shuku": daily_fortune.day_mansion,
                "luck_type": daily_fortune.luck_type,
                "fortune": daily_fortune.fortune,
                "description": daily_fortune.description
            },
            "relationship_mandala": mandala
        }
    
    def get_compatibility(
        self,
        user_birth_date: datetime,
        partner_birth_date: datetime
    ) -> Dict:
        """
        二人の相性を計算
        
        Args:
            user_birth_date: 自分の生年月日
            partner_birth_date: 相手の生年月日
            
        Returns:
            詳細な相性結果
        """
        user_profile = self.calendar.calculate_profile(user_birth_date)
        partner_profile = self.calendar.calculate_profile(partner_birth_date)
        
        compatibility = self.relationship.calculate_compatibility(
            user_profile.honmei_index,
            partner_profile.honmei_index
        )
        
        an_kai = self.relationship.get_an_kai_direction(
            user_profile.honmei_index,
            partner_profile.honmei_index
        )
        
        return {
            "user": {
                "shuku": user_profile.honmei_shuku,
                "index": user_profile.honmei_index,
                "group": user_profile.personality_group
            },
            "partner": {
                "shuku": partner_profile.honmei_shuku,
                "index": partner_profile.honmei_index,
                "group": partner_profile.personality_group
            },
            "compatibility": {
                "relation_type": compatibility.relation_type,
                "distance": compatibility.distance,
                "distance_type": compatibility.distance_type,
                "is_active": compatibility.is_active,
                "fortune_level": compatibility.fortune_level,
                "description": compatibility.description
            },
            "an_kai_analysis": an_kai
        }


# ============================================
# 簡易関数
# ============================================

def get_honmei_shuku(
    birth_year: int,
    birth_month: int,
    birth_day: int
) -> Tuple[int, str]:
    """
    本命宿を取得する簡易関数
    
    Args:
        birth_year: 生年
        birth_month: 生月
        birth_day: 生日
        
    Returns:
        (宿インデックス, 宿名)
    """
    calendar = SukuyoCalendar()
    birth_dt = datetime(birth_year, birth_month, birth_day)
    profile = calendar.calculate_profile(birth_dt)
    return profile.honmei_index, profile.honmei_shuku


# ============================================
# テスト用
# ============================================

if __name__ == "__main__":
    import json
    
    # テスト
    print("=== 宿曜占星術テスト ===")
    
    calendar = SukuyoCalendar()
    birth_dt = datetime(1992, 2, 17)
    
    profile = calendar.calculate_profile(birth_dt)
    print(f"生年月日: {birth_dt}")
    print(f"旧暦: {profile.lunar_date}")
    print(f"本命宿: {profile.honmei_shuku}")
    print(f"七曜: {profile.seven_luminary}曜")
    print(f"性格グループ: {profile.personality_group}")
