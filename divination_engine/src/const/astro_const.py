"""
西洋占星術 定数定義モジュール
Western Astrology Constants Module

天体ID、サイン、ハウスシステム、アスペクト、オーブ設定
"""

from typing import Dict, List, Tuple
from enum import Enum, IntEnum
from dataclasses import dataclass


# ============================================
# 天体ID（Swiss Ephemeris準拠）
# ============================================

class CelestialBody(IntEnum):
    """天体ID（pyswisseph互換）"""
    SUN = 0
    MOON = 1
    MERCURY = 2
    VENUS = 3
    MARS = 4
    JUPITER = 5
    SATURN = 6
    URANUS = 7
    NEPTUNE = 8
    PLUTO = 9
    MEAN_NODE = 10      # 平均ノード（ドラゴンヘッド）
    TRUE_NODE = 11      # 真ノード
    MEAN_APOGEE = 12    # 平均リリス（ブラックムーン）
    OSCU_APOGEE = 13    # 真リリス
    CHIRON = 15         # キロン
    PHOLUS = 16
    CERES = 17          # セレス
    PALLAS = 18         # パラス
    JUNO = 19           # ジュノー
    VESTA = 20          # ベスタ


# 天体の日本語名
BODY_NAMES_JA = {
    CelestialBody.SUN: "太陽",
    CelestialBody.MOON: "月",
    CelestialBody.MERCURY: "水星",
    CelestialBody.VENUS: "金星",
    CelestialBody.MARS: "火星",
    CelestialBody.JUPITER: "木星",
    CelestialBody.SATURN: "土星",
    CelestialBody.URANUS: "天王星",
    CelestialBody.NEPTUNE: "海王星",
    CelestialBody.PLUTO: "冥王星",
    CelestialBody.MEAN_NODE: "ドラゴンヘッド（平均）",
    CelestialBody.TRUE_NODE: "ドラゴンヘッド（真）",
    CelestialBody.MEAN_APOGEE: "リリス（平均）",
    CelestialBody.OSCU_APOGEE: "リリス（真）",
    CelestialBody.CHIRON: "キロン",
    CelestialBody.CERES: "セレス",
    CelestialBody.PALLAS: "パラス",
    CelestialBody.JUNO: "ジュノー",
    CelestialBody.VESTA: "ベスタ",
}

# 天体の英語名
BODY_NAMES_EN = {
    CelestialBody.SUN: "Sun",
    CelestialBody.MOON: "Moon",
    CelestialBody.MERCURY: "Mercury",
    CelestialBody.VENUS: "Venus",
    CelestialBody.MARS: "Mars",
    CelestialBody.JUPITER: "Jupiter",
    CelestialBody.SATURN: "Saturn",
    CelestialBody.URANUS: "Uranus",
    CelestialBody.NEPTUNE: "Neptune",
    CelestialBody.PLUTO: "Pluto",
    CelestialBody.MEAN_NODE: "North Node (Mean)",
    CelestialBody.TRUE_NODE: "North Node (True)",
    CelestialBody.MEAN_APOGEE: "Lilith (Mean)",
    CelestialBody.OSCU_APOGEE: "Lilith (True)",
    CelestialBody.CHIRON: "Chiron",
    CelestialBody.CERES: "Ceres",
    CelestialBody.PALLAS: "Pallas",
    CelestialBody.JUNO: "Juno",
    CelestialBody.VESTA: "Vesta",
}

# 天体のシンボル
BODY_SYMBOLS = {
    CelestialBody.SUN: "☉",
    CelestialBody.MOON: "☽",
    CelestialBody.MERCURY: "☿",
    CelestialBody.VENUS: "♀",
    CelestialBody.MARS: "♂",
    CelestialBody.JUPITER: "♃",
    CelestialBody.SATURN: "♄",
    CelestialBody.URANUS: "♅",
    CelestialBody.NEPTUNE: "♆",
    CelestialBody.PLUTO: "♇",
    CelestialBody.MEAN_NODE: "☊",
    CelestialBody.TRUE_NODE: "☊",
    CelestialBody.CHIRON: "⚷",
}


# ============================================
# 十二サイン（黄道十二宮）
# ============================================

class ZodiacSign(IntEnum):
    """十二サイン"""
    ARIES = 0       # 牡羊座
    TAURUS = 1      # 牡牛座
    GEMINI = 2      # 双子座
    CANCER = 3      # 蟹座
    LEO = 4         # 獅子座
    VIRGO = 5       # 乙女座
    LIBRA = 6       # 天秤座
    SCORPIO = 7     # 蠍座
    SAGITTARIUS = 8 # 射手座
    CAPRICORN = 9   # 山羊座
    AQUARIUS = 10   # 水瓶座
    PISCES = 11     # 魚座


SIGN_NAMES_JA = [
    "牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
    "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"
]

SIGN_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# 各サインの性質
SIGN_ELEMENTS = ["火", "地", "風", "水"] * 3  # 火地風水
SIGN_MODALITIES = ["活動", "固定", "柔軟"] * 4  # 活動固定柔軟


# ============================================
# ハウスシステム
# ============================================

class HouseSystem(Enum):
    """ハウス分割方式"""
    PLACIDUS = 'P'          # プラシーダス（標準）
    KOCH = 'K'              # コッホ
    REGIOMONTANUS = 'R'     # レギオモンタヌス
    CAMPANUS = 'C'          # カンパヌス
    EQUAL = 'E'             # イコール（ASCから30度刻み）
    WHOLE_SIGN = 'W'        # ホールサイン
    PORPHYRY = 'O'          # ポルフィリー
    ALCABITIUS = 'B'        # アルカビティウス
    MORINUS = 'M'           # モリヌス
    MERIDIAN = 'X'          # メリディアン


HOUSE_SYSTEM_NAMES = {
    HouseSystem.PLACIDUS: "プラシーダス",
    HouseSystem.KOCH: "コッホ",
    HouseSystem.REGIOMONTANUS: "レギオモンタヌス",
    HouseSystem.CAMPANUS: "カンパヌス",
    HouseSystem.EQUAL: "イコール",
    HouseSystem.WHOLE_SIGN: "ホールサイン",
    HouseSystem.PORPHYRY: "ポルフィリー",
    HouseSystem.ALCABITIUS: "アルカビティウス",
}


# ============================================
# アスペクト
# ============================================

class AspectType(Enum):
    """アスペクトの種類"""
    CONJUNCTION = 0      # コンジャンクション（合）
    SEXTILE = 60         # セクスタイル（六分）
    SQUARE = 90          # スクエア（四角）
    TRINE = 120          # トライン（三角）
    OPPOSITION = 180     # オポジション（衝）
    # マイナーアスペクト
    SEMI_SEXTILE = 30    # セミセクスタイル
    SEMI_SQUARE = 45     # セミスクエア
    QUINTILE = 72        # クインタイル
    SESQUIQUADRATE = 135 # セスキコードレイト
    QUINCUNX = 150       # クインカンクス（インコンジャクト）


ASPECT_NAMES = {
    AspectType.CONJUNCTION: {"ja": "合", "en": "Conjunction", "symbol": "☌"},
    AspectType.SEXTILE: {"ja": "六分", "en": "Sextile", "symbol": "⚹"},
    AspectType.SQUARE: {"ja": "四角", "en": "Square", "symbol": "□"},
    AspectType.TRINE: {"ja": "三角", "en": "Trine", "symbol": "△"},
    AspectType.OPPOSITION: {"ja": "衝", "en": "Opposition", "symbol": "☍"},
    AspectType.SEMI_SEXTILE: {"ja": "セミセクスタイル", "en": "Semi-sextile", "symbol": "⚺"},
    AspectType.SEMI_SQUARE: {"ja": "セミスクエア", "en": "Semi-square", "symbol": "∠"},
    AspectType.QUINTILE: {"ja": "クインタイル", "en": "Quintile", "symbol": "Q"},
    AspectType.SESQUIQUADRATE: {"ja": "セスキコードレイト", "en": "Sesquiquadrate", "symbol": "⚼"},
    AspectType.QUINCUNX: {"ja": "クインカンクス", "en": "Quincunx", "symbol": "⚻"},
}

# メジャーアスペクト
MAJOR_ASPECTS = [
    AspectType.CONJUNCTION,
    AspectType.SEXTILE,
    AspectType.SQUARE,
    AspectType.TRINE,
    AspectType.OPPOSITION
]

# マイナーアスペクト
MINOR_ASPECTS = [
    AspectType.SEMI_SEXTILE,
    AspectType.SEMI_SQUARE,
    AspectType.QUINTILE,
    AspectType.SESQUIQUADRATE,
    AspectType.QUINCUNX
]


# ============================================
# オーブ設定
# ============================================

@dataclass
class OrbSettings:
    """オーブ（許容度）設定"""
    conjunction: float = 10.0
    sextile: float = 6.0
    square: float = 8.0
    trine: float = 8.0
    opposition: float = 10.0
    semi_sextile: float = 2.0
    semi_square: float = 2.0
    quintile: float = 2.0
    sesquiquadrate: float = 2.0
    quincunx: float = 3.0


# デフォルトオーブ
DEFAULT_ORBS = OrbSettings()

# 天体ごとのオーブ補正係数
# 太陽・月は広め、外惑星は狭め
ORB_MODIFIERS = {
    CelestialBody.SUN: 1.0,
    CelestialBody.MOON: 1.0,
    CelestialBody.MERCURY: 0.8,
    CelestialBody.VENUS: 0.8,
    CelestialBody.MARS: 0.8,
    CelestialBody.JUPITER: 0.7,
    CelestialBody.SATURN: 0.7,
    CelestialBody.URANUS: 0.6,
    CelestialBody.NEPTUNE: 0.6,
    CelestialBody.PLUTO: 0.6,
    CelestialBody.CHIRON: 0.5,
    CelestialBody.MEAN_NODE: 0.5,
    CelestialBody.TRUE_NODE: 0.5,
}


# ============================================
# アスペクトの状態
# ============================================

class AspectState(Enum):
    """アスペクトの状態"""
    APPLYING = "Applying"       # 接近中（これからタイトになる）
    SEPARATING = "Separating"   # 分離中（タイトからルーズへ）
    EXACT = "Exact"             # 正確（オーブが非常に小さい）


# ============================================
# アングル（感受点）
# ============================================

class ChartAngle(Enum):
    """ホロスコープのアングル"""
    ASC = "Ascendant"           # アセンダント（上昇点）
    MC = "Midheaven"            # MC（天頂）
    DSC = "Descendant"          # ディセンダント（下降点）
    IC = "Imum Coeli"           # IC（天底）
    VERTEX = "Vertex"           # バーテックス


# ============================================
# 計算設定
# ============================================

@dataclass
class CalculationSettings:
    """計算設定"""
    # ノードの種類
    use_true_node: bool = True
    use_true_lilith: bool = False
    
    # トポセントリック補正
    use_topocentric: bool = False
    
    # 5度前ルール
    use_five_degree_rule: bool = False
    five_degree_threshold: float = 5.0
    
    # アスペクト設定
    include_minor_aspects: bool = False
    orbs: OrbSettings = None
    
    def __post_init__(self):
        if self.orbs is None:
            self.orbs = OrbSettings()


# ============================================
# ユーティリティ関数
# ============================================

def degree_to_sign(absolute_degree: float) -> Tuple[int, float]:
    """
    絶対度数からサインと相対度数を取得
    
    Args:
        absolute_degree: 0-360の絶対度数
        
    Returns:
        (サインインデックス0-11, サイン内の度数0-30)
    """
    normalized = absolute_degree % 360
    sign_idx = int(normalized / 30)
    relative_degree = normalized % 30
    return sign_idx, relative_degree


def format_degree(absolute_degree: float) -> str:
    """
    度数を読みやすい形式にフォーマット
    
    Args:
        absolute_degree: 0-360の絶対度数
        
    Returns:
        例: "♌ 15°23'"
    """
    sign_idx, relative = degree_to_sign(absolute_degree)
    degrees = int(relative)
    minutes = int((relative - degrees) * 60)
    return f"{SIGN_SYMBOLS[sign_idx]} {degrees}°{minutes:02d}'"


def normalize_angle(angle: float) -> float:
    """角度を0-360に正規化"""
    return angle % 360


def angle_difference(angle1: float, angle2: float) -> float:
    """2つの角度の最短距離を計算"""
    diff = abs(angle1 - angle2) % 360
    return min(diff, 360 - diff)
