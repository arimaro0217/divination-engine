"""
出力データスキーマ定義
各占術の計算結果を格納するモデル
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


# === 共通基底クラス ===
class BaseDivinationResult(BaseModel):
    """占術結果の基底クラス"""
    divination_type: str
    calculated_at: datetime = Field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None


# === 干支関連 ===
class Pillar(BaseModel):
    """干支の柱"""
    heavenly_stem: str = Field(..., description="天干（甲乙丙丁戊己庚辛壬癸）")
    earthly_branch: str = Field(..., description="地支（子丑寅卯辰巳午未申酉戌亥）")
    
    @property
    def full(self) -> str:
        return f"{self.heavenly_stem}{self.earthly_branch}"


class FourPillars(BaseModel):
    """四柱"""
    year: Pillar = Field(..., description="年柱")
    month: Pillar = Field(..., description="月柱")
    day: Pillar = Field(..., description="日柱")
    hour: Pillar = Field(..., description="時柱")


class BaZiResult(BaseDivinationResult):
    """四柱推命結果"""
    divination_type: str = "bazi"
    four_pillars: FourPillars
    void_branches: List[str] = Field(..., description="空亡（天中殺）")
    day_master: str = Field(..., description="日主（日干）")
    ten_gods: Dict[str, str] = Field(default_factory=dict, description="通変星")
    twelve_stages: Dict[str, str] = Field(default_factory=dict, description="十二運")
    hidden_stems: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="蔵干詳細")
    month_info: Optional[Dict[str, Any]] = Field(None, description="節入り情報")


class SanmeiResult(BaseDivinationResult):
    """算命学結果"""
    divination_type: str = "sanmei"
    four_pillars: Optional[FourPillars] = None
    void_branches: List[str] = Field(default_factory=list, description="天中殺")
    void_group_name: Optional[str] = Field(None, description="天中殺グループ名")
    void_period: Dict[str, str] = Field(default_factory=dict, description="天中殺期間")
    main_stars: Dict[str, str] = Field(default_factory=dict, description="十大主星")
    sub_stars: Dict[str, str] = Field(default_factory=dict, description="十二大従星")
    body_chart: Dict[str, str] = Field(default_factory=dict, description="人体星図")
    energy_values: Dict[str, int] = Field(default_factory=dict, description="数理法：エネルギー数値")
    phases: Dict[str, List[str]] = Field(default_factory=dict, description="位相法：合法と散法")


class KyuseiResult(BaseDivinationResult):
    """九星気学結果"""
    divination_type: str = "kyusei"
    year_star: str = Field(..., description="本命星")
    month_star: str = Field(..., description="月命星")
    day_star: str = Field(..., description="日命星")
    inclination: str = Field(..., description="傾斜宮")


class SexagenaryResult(BaseDivinationResult):
    """干支結果"""
    divination_type: str = "sexagenary"
    four_pillars: FourPillars
    sexagenary_year: int = Field(..., description="干支番号（1-60）")


# === 紫微斗数 ===
class ZiWeiResult(BaseDivinationResult):
    """紫微斗数結果"""
    divination_type: str = "ziwei"
    lunar_date: str = Field(..., description="旧暦生年月日")
    ming_palace: str = Field(..., description="命宮位置")
    body_palace: str = Field(..., description="身宮位置")
    main_stars: Dict[str, List[str]] = Field(default_factory=dict, description="各宮の主星")
    four_transformations: Dict[str, str] = Field(default_factory=dict, description="四化星")


# === 宿曜 ===
class SukuyouResult(BaseDivinationResult):
    """宿曜占星術結果"""
    divination_type: str = "sukuyou"
    natal_mansion: str = Field(..., description="本命宿")
    mansion_number: int = Field(..., description="宿番号（1-27）")
    element: str = Field(..., description="属性（栄・親・友・安・危・業・胎）")


# === 西洋占星術 ===
class PlanetPosition(BaseModel):
    """惑星位置"""
    planet: str
    longitude: float = Field(..., description="黄経（度）")
    sign: str = Field(..., description="サイン")
    degree_in_sign: float = Field(..., description="サイン内度数")
    house: Optional[int] = Field(None, description="ハウス番号")
    retrograde: bool = Field(default=False, description="逆行中")


class Aspect(BaseModel):
    """アスペクト"""
    planet1: str
    planet2: str
    aspect_type: str = Field(..., description="アスペクト種類")
    orb: float = Field(..., description="オーブ（度）")
    applying: bool = Field(..., description="接近中か離反中か")


class WesternResult(BaseDivinationResult):
    """西洋占星術結果"""
    divination_type: str = "western"
    planets: List[PlanetPosition] = Field(default_factory=list)
    houses: Dict[int, float] = Field(default_factory=dict, description="ハウスカスプ")
    ascendant: float = Field(..., description="ASC度数")
    midheaven: float = Field(..., description="MC度数")
    aspects: List[Aspect] = Field(default_factory=list)


# === インド占星術 ===
class VedicResult(BaseDivinationResult):
    """インド占星術結果"""
    divination_type: str = "vedic"
    ayanamsa: float = Field(..., description="アヤナムサ値")
    planets: List[PlanetPosition] = Field(default_factory=list)
    nakshatra: str = Field(..., description="月のナクシャトラ")
    nakshatra_lord: str = Field(..., description="ナクシャトラ支配星")
    dasha: Dict[str, Any] = Field(default_factory=dict, description="ダシャー期間")
    d9_positions: List[PlanetPosition] = Field(default_factory=list, description="ナバムシャ")


# === マヤ暦 ===
class MayanResult(BaseDivinationResult):
    """マヤ暦結果"""
    divination_type: str = "mayan"
    kin_number: int = Field(..., ge=1, le=260, description="KIN番号")
    solar_seal: str = Field(..., description="太陽の紋章")
    wavespell: str = Field(..., description="ウェイブスペル")
    galactic_tone: int = Field(..., ge=1, le=13, description="銀河の音")
    guide: str = Field(..., description="ガイドキン")


# === 姓名判断 ===
class SeimeiResult(BaseDivinationResult):
    """姓名判断結果"""
    divination_type: str = "seimei"
    strokes: Dict[str, int] = Field(..., description="各文字の画数")
    tenkaku: int = Field(..., description="天格")
    jinkaku: int = Field(..., description="人格")
    chikaku: int = Field(..., description="地格")
    gaikaku: int = Field(..., description="外格")
    soukaku: int = Field(..., description="総格")


# === 数秘術 ===
class NumerologyResult(BaseDivinationResult):
    """数秘術結果"""
    divination_type: str = "numerology"
    life_path: int = Field(..., ge=1, le=33, description="ライフパス数")
    birthday_number: int = Field(..., ge=1, le=31, description="バースデー数")
    expression_number: int = Field(..., description="運命数")
    soul_urge: int = Field(..., description="ソウルナンバー")
    personality_number: int = Field(..., description="人格数")


# === カバラ ===
class KabbalahResult(BaseDivinationResult):
    """カバラ結果"""
    divination_type: str = "kabbalah"
    soul_number: int = Field(..., description="魂数")
    personality_number: int = Field(..., description="人格数")
    destiny_number: int = Field(..., description="運命数")
    path_positions: List[str] = Field(default_factory=list, description="生命の樹パス位置")


# === 統合結果 ===
class DivinationResult(BaseModel):
    """全占術の統合結果"""
    user_name: str
    birth_datetime: datetime
    calculated_at: datetime = Field(default_factory=datetime.now)
    
    western: Optional[WesternResult] = None
    vedic: Optional[VedicResult] = None
    bazi: Optional[BaZiResult] = None
    sanmei: Optional[SanmeiResult] = None
    kyusei: Optional[KyuseiResult] = None
    sexagenary: Optional[SexagenaryResult] = None
    ziwei: Optional[ZiWeiResult] = None
    sukuyou: Optional[SukuyouResult] = None
    mayan: Optional[MayanResult] = None
    seimei: Optional[SeimeiResult] = None
    numerology: Optional[NumerologyResult] = None
    kabbalah: Optional[KabbalahResult] = None
