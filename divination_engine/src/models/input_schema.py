"""
入力データスキーマ定義
Pydanticによる型バリデーション
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class Gender(str, Enum):
    """性別"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class DivinationType(str, Enum):
    """占術タイプ"""
    WESTERN = "western"           # 西洋占星術
    VEDIC = "vedic"               # インド占星術
    BAZI = "bazi"                 # 四柱推命
    SANMEI = "sanmei"             # 算命学
    KYUSEI = "kyusei"             # 九星気学
    SEXAGENARY = "sexagenary"     # 干支
    ZIWEI = "ziwei"               # 紫微斗数
    SUKUYOU = "sukuyou"           # 宿曜占星術
    MAYAN = "mayan"               # マヤ暦
    SEIMEI = "seimei"             # 姓名判断
    NUMEROLOGY = "numerology"     # 数秘術
    KABBALAH = "kabbalah"         # カバラ


class UserProfile(BaseModel):
    """ユーザープロフィール"""
    name_kanji: str = Field(..., description="氏名（漢字）")
    name_kana: str = Field(..., description="氏名（カナ）")
    birth_datetime: datetime = Field(..., description="生年月日時（タイムゾーン付き）")
    birth_place: Optional[str] = Field(None, description="出生地（市区町村名）")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="出生地緯度")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="出生地経度")
    gender: Gender = Field(..., description="性別")

    @field_validator('name_kanji', 'name_kana')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('名前は空にできません')
        return v.strip()


class DivinationRequest(BaseModel):
    """占い計算リクエスト"""
    user: UserProfile
    divination_types: List[DivinationType] = Field(
        default_factory=lambda: list(DivinationType),
        description="計算する占術タイプのリスト（未指定時は全占術）"
    )
    include_interpretations: bool = Field(
        default=False,
        description="解釈テキストを含めるか"
    )


class BirthChartRequest(BaseModel):
    """簡易リクエスト（占星術用）"""
    birth_datetime: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = Field(default="Asia/Tokyo")
