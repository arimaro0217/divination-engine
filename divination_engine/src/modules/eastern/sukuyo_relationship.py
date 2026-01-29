"""
宿曜占星術 相性判定・円盤データ生成モジュール
Sukuyo Relationship & Mandala Module

相性マトリクス計算、日運判定、円盤描画データ生成
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from ...const import sukuyou_const as sk
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from src.const import sukuyou_const as sk


# ============================================
# データ構造
# ============================================

@dataclass
class RelationshipResult:
    """相性判定結果"""
    target_mansion: str           # 相手の宿
    target_index: int             # 相手の宿インデックス
    relation_type: str            # 相性タイプ（栄・親・安・壊など）
    distance: int                 # 距離（0-26）
    distance_type: str            # 距離タイプ（近距離・中距離・遠距離）
    is_active: bool               # 自分が主導権を持つか
    fortune_level: int            # 吉凶レベル（0-5）
    description: str              # 説明文
    angle: float                  # 円盤上の角度


@dataclass
class DailyFortuneResult:
    """日運結果"""
    target_date: datetime
    day_mansion: str              # その日の宿
    day_mansion_index: int
    luck_type: str                # 運勢タイプ
    fortune: str                  # 吉凶
    description: str              # 説明


# ============================================
# RelationshipEngine: 相性計算エンジン
# ============================================

class RelationshipEngine:
    """
    宿曜 相性計算エンジン
    
    11種類の相性（命・業・胎・栄・親・友・衰・安・壊・危・成）と
    距離（近距離・中距離・遠距離）を判定
    """
    
    def __init__(self):
        self.mansions = sk.MANSIONS
    
    def calculate_compatibility(
        self, 
        mansion_a: int, 
        mansion_b: int
    ) -> RelationshipResult:
        """
        2つの宿の相性を計算
        
        Args:
            mansion_a: 自分の宿インデックス（0-26）
            mansion_b: 相手の宿インデックス（0-26）
            
        Returns:
            RelationshipResult: 詳細な相性結果
        """
        # 距離を計算（円環上）
        distance = (mansion_b - mansion_a) % 27
        
        # 相性マトリクスから取得
        relation_type, is_active = sk.COMPATIBILITY_MATRIX.get(
            distance, 
            (sk.RelationType.YU, True)
        )
        
        # 距離タイプを判定
        if distance <= 6 or distance >= 21:
            distance_type = sk.DistanceType.NEAR.value
        elif distance <= 10 or distance >= 17:
            distance_type = sk.DistanceType.MIDDLE.value
        else:
            distance_type = sk.DistanceType.FAR.value
        
        # 吉凶レベル
        fortune_level = sk.RELATION_FORTUNE_LEVEL.get(relation_type, 2)
        
        # 説明文
        description = sk.RELATION_DESCRIPTIONS.get(
            relation_type, 
            {"ja": ""}
        )["ja"]
        
        # 角度（円盤描画用）
        angle = sk.get_mandala_angle(mansion_b)
        
        return RelationshipResult(
            target_mansion=self.mansions[mansion_b],
            target_index=mansion_b,
            relation_type=relation_type.value,
            distance=distance,
            distance_type=distance_type,
            is_active=is_active,
            fortune_level=fortune_level,
            description=description,
            angle=angle
        )
    
    def generate_mandala(self, user_mansion: int) -> List[Dict[str, Any]]:
        """
        円盤（マンダラ）データを生成
        
        Args:
            user_mansion: ユーザーの本命宿インデックス
            
        Returns:
            27宿すべてとの相性データリスト
        """
        mandala = []
        
        for i in range(27):
            result = self.calculate_compatibility(user_mansion, i)
            
            mandala.append({
                "shuku": result.target_mansion,
                "index": result.target_index,
                "distance": result.distance,
                "distance_type": result.distance_type,
                "relation_type": result.relation_type,
                "is_active": result.is_active,
                "fortune_level": result.fortune_level,
                "is_user": (i == user_mansion),
                "angle": result.angle,
                "description": result.description
            })
        
        return mandala
    
    def get_an_kai_direction(
        self, 
        mansion_a: int, 
        mansion_b: int
    ) -> Dict[str, Any]:
        """
        安壊関係の方向性を判定
        
        安壊は宿曜で最も強烈な因縁関係。
        どちらが「安」でどちらが「壊」かを明確にする。
        
        Args:
            mansion_a: 自分の宿
            mansion_b: 相手の宿
            
        Returns:
            方向性の詳細
        """
        distance_ab = (mansion_b - mansion_a) % 27
        distance_ba = (mansion_a - mansion_b) % 27
        
        # 安壊の距離は7または20（近安・遠安）、10または17（近壊・遠壊）
        is_an_kai = distance_ab in [7, 10, 17, 20]
        
        if not is_an_kai:
            return {
                "is_an_kai": False,
                "message": "安壊の関係ではありません"
            }
        
        # 距離7/20は「安」、距離10/17は「壊」
        if distance_ab in [7, 20]:
            return {
                "is_an_kai": True,
                "user_role": "安",
                "partner_role": "壊",
                "message": "あなたは相手を安定させ、コントロールできる立場です。"
            }
        else:  # distance_ab in [10, 17]
            return {
                "is_an_kai": True,
                "user_role": "壊",
                "partner_role": "安",
                "message": "相手によってあなたが壊される危険性があります。注意が必要です。"
            }


# ============================================
# DestinyMatrix: 運勢・性格判定
# ============================================

class DestinyMatrix:
    """
    宿曜 運勢・性格判定エンジン
    """
    
    def __init__(self):
        self.mansions = sk.MANSIONS
    
    def get_personality(self, mansion_index: int) -> Dict[str, Any]:
        """
        宿の性格情報を取得
        
        Args:
            mansion_index: 宿インデックス（0-26）
            
        Returns:
            性格情報
        """
        # 性格グループ
        group = sk.MANSION_PERSONALITY_GROUP.get(
            mansion_index, 
            sk.PersonalityGroup.WAZOU
        )
        
        # 七曜
        weekday = sk.MANSION_WEEKDAY[mansion_index]
        
        # 詳細情報
        details = sk.MANSION_DETAILS.get(mansion_index, {})
        
        return {
            "mansion": self.mansions[mansion_index],
            "index": mansion_index,
            "reading": sk.MANSION_READINGS[mansion_index],
            "personality_group": group.value,
            "weekday": weekday,
            "weekday_english": sk.WEEKDAY_ENGLISH.get(weekday, ""),
            "nature": details.get("nature", ""),
            "keywords": details.get("keywords", []),
            "strengths": details.get("strengths", []),
            "weaknesses": details.get("weaknesses", [])
        }
    
    def get_daily_fortune(
        self, 
        user_mansion: int, 
        target_date: datetime
    ) -> DailyFortuneResult:
        """
        指定日の日運を判定
        
        Args:
            user_mansion: ユーザーの本命宿
            target_date: 対象日
            
        Returns:
            日運結果
        """
        # その日の宿を計算
        # 簡易版: 1日ごとに宿が1つ進む
        # 基準日: 2000年1月1日 = 角宿(11)と仮定
        base_date = datetime(2000, 1, 1)
        days_diff = (target_date - base_date).days
        day_mansion = (11 + days_diff) % 27
        
        # 本命宿との距離
        distance = (day_mansion - user_mansion) % 27
        
        # 運勢サイクルから取得
        fortune_info = sk.DAILY_FORTUNE_CYCLE.get(distance, {
            "type": "普通",
            "fortune": "平",
            "description": "特に際立った運勢の日ではありません。"
        })
        
        return DailyFortuneResult(
            target_date=target_date,
            day_mansion=self.mansions[day_mansion],
            day_mansion_index=day_mansion,
            luck_type=fortune_info["type"],
            fortune=fortune_info["fortune"],
            description=fortune_info["description"]
        )
    
    def get_six_harmful_days(
        self, 
        user_mansion: int,
        start_date: datetime,
        days: int = 30
    ) -> List[datetime]:
        """
        六害宿（凶日）を取得
        
        自分の本命宿と同じ日（命の日）、
        壊の日などを警告日として返す。
        
        Args:
            user_mansion: ユーザーの本命宿
            start_date: 開始日
            days: 日数
            
        Returns:
            凶日のリスト
        """
        harmful_days = []
        
        for i in range(days):
            check_date = start_date + timedelta(days=i)
            fortune = self.get_daily_fortune(user_mansion, check_date)
            
            # 壊・危・命の日を警告
            if fortune.luck_type in ["壊", "危", "命"]:
                harmful_days.append(check_date)
        
        return harmful_days


# ============================================
# 凌犯期間（七曜陵逼）判定
# ============================================

class RyohanEngine:
    """
    凌犯期間（七曜陵逼・りょうはんきかん）判定エンジン
    
    旧暦1月1日の曜日によって、その年の運勢が逆転する特殊期間（吉→凶）
    を判定する。宿曜占星術における最重要の警告機能。
    
    原理:
    - 旧暦1月1日が何曜日かによって「陵逼」の期間が決まる
    - 陵逼期間中は、通常の吉が凶に、凶が吉に逆転する
    - 特に重要な決断は避けるべき
    """
    
    def __init__(self):
        try:
            from ...core.lunar_core import LunisolarEngine, LeapMonthMode
        except ImportError:
            from src.core.lunar_core import LunisolarEngine, LeapMonthMode
        
        self.lunar_engine = LunisolarEngine(use_jst=True)
    
    # 七曜陵逼テーブル
    # 旧暦1月1日の曜日 -> (陵逼開始月, 陵逼終了月)
    # ※月は旧暦月
    RYOHAN_TABLE = {
        "日": (1, 7),    # 日曜始まり: 1月〜7月が陵逼期間
        "月": (2, 8),    # 月曜始まり: 2月〜8月が陵逼期間
        "火": (3, 9),    # 火曜始まり: 3月〜9月が陵逼期間
        "水": (4, 10),   # 水曜始まり: 4月〜10月が陵逼期間
        "木": (5, 11),   # 木曜始まり: 5月〜11月が陵逼期間
        "金": (6, 12),   # 金曜始まり: 6月〜12月が陵逼期間
        "土": (7, 1),    # 土曜始まり: 7月〜翌1月が陵逼期間（年跨ぎ）
    }
    
    def get_lunar_new_year_weekday(self, year: int) -> str:
        """
        指定年の旧暦1月1日の曜日を取得
        
        Args:
            year: 年（西暦）
            
        Returns:
            曜日（日月火水木金土）
        """
        # 旧暦1月1日を計算
        # 注意: yearは西暦年なので、その年の旧暦1月1日を探す
        lunar_new_year = self.lunar_engine.find_lunar_new_year(year)
        
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        return weekdays[lunar_new_year.weekday()]
    
    def get_ryohan_period(self, year: int) -> Dict[str, Any]:
        """
        指定年の凌犯期間を取得
        
        Args:
            year: 年（西暦）
            
        Returns:
            凌犯期間の情報
        """
        try:
            weekday = self.get_lunar_new_year_weekday(year)
            period = self.RYOHAN_TABLE.get(weekday, (1, 7))
            
            is_year_crossing = period[0] > period[1]  # 年跨ぎ
            
            return {
                "year": year,
                "lunar_new_year_weekday": weekday,
                "ryohan_start_month": period[0],
                "ryohan_end_month": period[1],
                "is_year_crossing": is_year_crossing,
                "description": f"{weekday}曜始まりの年。旧暦{period[0]}月〜{period[1]}月が凌犯期間。",
                "warning": "凌犯期間中は吉凶が逆転。重要な決断は避けること。"
            }
        except Exception as e:
            return {
                "year": year,
                "error": str(e),
                "description": "凌犯期間の計算に失敗しました。"
            }
    
    def is_ryohan_period(self, target_date: datetime) -> Dict[str, Any]:
        """
        指定日が凌犯期間かどうかを判定
        
        Args:
            target_date: 判定対象日
            
        Returns:
            判定結果
        """
        try:
            from ...core.lunar_core import LeapMonthMode
        except ImportError:
            from src.core.lunar_core import LeapMonthMode
        
        try:
            # 西暦年から旧暦年を特定
            lunar_date = self.lunar_engine.convert_to_lunar(
                target_date, 
                LeapMonthMode.B  # 前月扱い
            )
            
            ryohan_info = self.get_ryohan_period(target_date.year)
            
            if "error" in ryohan_info:
                return {
                    "is_ryohan": False,
                    "error": ryohan_info["error"]
                }
            
            start_month = ryohan_info["ryohan_start_month"]
            end_month = ryohan_info["ryohan_end_month"]
            is_year_crossing = ryohan_info["is_year_crossing"]
            
            lunar_month = lunar_date.month
            
            # 凌犯期間かどうかを判定
            if is_year_crossing:
                # 年跨ぎの場合（例: 7月〜翌1月）
                is_ryohan = lunar_month >= start_month or lunar_month <= end_month
            else:
                # 通常の場合
                is_ryohan = start_month <= lunar_month <= end_month
            
            return {
                "target_date": target_date.strftime("%Y-%m-%d"),
                "lunar_date": f"旧暦{lunar_date.year}年{lunar_date.month}月{lunar_date.day}日",
                "is_ryohan": is_ryohan,
                "ryohan_info": ryohan_info,
                "warning": "吉凶逆転期間中！通常の吉日が凶日に変わります。" if is_ryohan else None
            }
        except Exception as e:
            return {
                "is_ryohan": False,
                "error": str(e)
            }



# ============================================
# JSON出力用ユーティリティ
# ============================================

def generate_sukuyo_json(
    user_mansion_index: int,
    birth_date: datetime,
    lunar_month: int,
    lunar_day: int,
    target_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Webフロントエンド向け完全なJSONを生成
    
    Args:
        user_mansion_index: 本命宿インデックス
        birth_date: 生年月日
        lunar_month: 旧暦月
        lunar_day: 旧暦日
        target_date: 日運対象日（省略時は今日）
        
    Returns:
        完全なJSON構造
    """
    if target_date is None:
        target_date = datetime.now()
    
    relationship_engine = RelationshipEngine()
    destiny_matrix = DestinyMatrix()
    
    # ユーザープロファイル
    personality = destiny_matrix.get_personality(user_mansion_index)
    user_profile = {
        "birth_date": birth_date.strftime("%Y-%m-%d"),
        "lunar_date": f"旧暦{lunar_month}月{lunar_day}日",
        "honmei_shuku": sk.MANSIONS[user_mansion_index],
        "group": personality["personality_group"],
        "seven_luminary": f"{personality['weekday']}曜日 ({personality['weekday_english']})",
        "personality": personality
    }
    
    # 日運
    daily_fortune = destiny_matrix.get_daily_fortune(user_mansion_index, target_date)
    daily_fortune_json = {
        "target_date": target_date.strftime("%Y-%m-%d"),
        "day_shuku": daily_fortune.day_mansion,
        "luck_type": daily_fortune.luck_type,
        "fortune": daily_fortune.fortune,
        "description": daily_fortune.description
    }
    
    # 円盤データ
    mandala = relationship_engine.generate_mandala(user_mansion_index)
    
    return {
        "user_profile": user_profile,
        "daily_fortune": daily_fortune_json,
        "relationship_mandala": mandala
    }
