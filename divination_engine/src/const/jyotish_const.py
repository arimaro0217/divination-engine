"""
ジョーティシュ（インド占星術）定数定義
Jyotish (Vedic Astrology) Constants

12ラシ、9グラハ、27ナクシャトラ、ダシャー期間、ヨーガ定義
"""

from typing import Dict, List, Tuple
from enum import Enum, IntEnum
from dataclasses import dataclass


# ============================================
# グラハ（惑星）
# ============================================

class Graha(IntEnum):
    """9つのグラハ（惑星）"""
    SURYA = 0       # 太陽 (Sun)
    CHANDRA = 1     # 月 (Moon)
    MANGALA = 2     # 火星 (Mars)
    BUDHA = 3       # 水星 (Mercury)
    GURU = 4        # 木星 (Jupiter)
    SHUKRA = 5      # 金星 (Venus)
    SHANI = 6       # 土星 (Saturn)
    RAHU = 7        # ラーフ (North Node)
    KETU = 8        # ケートゥ (South Node)


# グラハ名（サンスクリット語）
GRAHA_NAMES_SANSKRIT = {
    Graha.SURYA: "Surya",
    Graha.CHANDRA: "Chandra",
    Graha.MANGALA: "Mangala",
    Graha.BUDHA: "Budha",
    Graha.GURU: "Guru",
    Graha.SHUKRA: "Shukra",
    Graha.SHANI: "Shani",
    Graha.RAHU: "Rahu",
    Graha.KETU: "Ketu",
}

# グラハ名（英語）
GRAHA_NAMES_EN = {
    Graha.SURYA: "Sun",
    Graha.CHANDRA: "Moon",
    Graha.MANGALA: "Mars",
    Graha.BUDHA: "Mercury",
    Graha.GURU: "Jupiter",
    Graha.SHUKRA: "Venus",
    Graha.SHANI: "Saturn",
    Graha.RAHU: "Rahu",
    Graha.KETU: "Ketu",
}

# グラハ名（日本語）
GRAHA_NAMES_JA = {
    Graha.SURYA: "太陽",
    Graha.CHANDRA: "月",
    Graha.MANGALA: "火星",
    Graha.BUDHA: "水星",
    Graha.GURU: "木星",
    Graha.SHUKRA: "金星",
    Graha.SHANI: "土星",
    Graha.RAHU: "ラーフ",
    Graha.KETU: "ケートゥ",
}

# Swiss Ephemeris天体ID
GRAHA_SWE_ID = {
    Graha.SURYA: 0,    # SE_SUN
    Graha.CHANDRA: 1,  # SE_MOON
    Graha.MANGALA: 4,  # SE_MARS
    Graha.BUDHA: 2,    # SE_MERCURY
    Graha.GURU: 5,     # SE_JUPITER
    Graha.SHUKRA: 3,   # SE_VENUS
    Graha.SHANI: 6,    # SE_SATURN
    Graha.RAHU: 10,    # SE_MEAN_NODE (True: 11)
    Graha.KETU: -1,    # Calculated from Rahu + 180
}


# ============================================
# ラシ（サイン）
# ============================================

class Rashi(IntEnum):
    """12のラシ（サイン）"""
    MESHA = 0       # 牡羊座 (Aries)
    VRISHABHA = 1   # 牡牛座 (Taurus)
    MITHUNA = 2     # 双子座 (Gemini)
    KARKA = 3       # 蟹座 (Cancer)
    SIMHA = 4       # 獅子座 (Leo)
    KANYA = 5       # 乙女座 (Virgo)
    TULA = 6        # 天秤座 (Libra)
    VRISHCHIKA = 7  # 蠍座 (Scorpio)
    DHANU = 8       # 射手座 (Sagittarius)
    MAKARA = 9      # 山羊座 (Capricorn)
    KUMBHA = 10     # 水瓶座 (Aquarius)
    MEENA = 11      # 魚座 (Pisces)


# ラシ名（サンスクリット語）
RASHI_NAMES_SANSKRIT = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
]

# ラシ名（英語）
RASHI_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# ラシ名（日本語）
RASHI_NAMES_JA = [
    "牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
    "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"
]

# ラシの支配星（Lord）
RASHI_LORDS = {
    Rashi.MESHA: Graha.MANGALA,
    Rashi.VRISHABHA: Graha.SHUKRA,
    Rashi.MITHUNA: Graha.BUDHA,
    Rashi.KARKA: Graha.CHANDRA,
    Rashi.SIMHA: Graha.SURYA,
    Rashi.KANYA: Graha.BUDHA,
    Rashi.TULA: Graha.SHUKRA,
    Rashi.VRISHCHIKA: Graha.MANGALA,
    Rashi.DHANU: Graha.GURU,
    Rashi.MAKARA: Graha.SHANI,
    Rashi.KUMBHA: Graha.SHANI,
    Rashi.MEENA: Graha.GURU,
}

# エレメント（タットヴァ）
RASHI_ELEMENTS = ["火", "地", "風", "水"] * 3

# モダリティ（グナ）
RASHI_MODALITIES = ["チャラ(活動)", "スティラ(固定)", "ドヴィスヴァバ(柔軟)"] * 4


# ============================================
# ナクシャトラ（27星宿）
# ============================================

# ナクシャトラリスト（27宿）
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", 
    "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", 
    "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", 
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# ナクシャトラ名（日本語）
NAKSHATRAS_JA = [
    "アシュヴィニー", "バラニー", "クリッティカー", "ローヒニー", "ムリガシラー",
    "アールドラー", "プナルヴァス", "プシャー", "アシュレーシャー",
    "マガー", "プールヴァ・パールグニー", "ウッタラ・パールグニー", "ハスタ", "チトラー",
    "スヴァーティー", "ヴィシャーカー", "アヌラーダー", "ジェーシュター",
    "ムーラ", "プールヴァ・アシャーダー", "ウッタラ・アシャーダー", "シュラヴァナ", "ダニシュター",
    "シャタビシャー", "プールヴァ・バードラパダー", "ウッタラ・バードラパダー", "レーヴァティー"
]

# ナクシャトラの支配星（ダシャー順）
NAKSHATRA_LORDS = [
    Graha.KETU, Graha.SHUKRA, Graha.SURYA,     # Ashwini, Bharani, Krittika
    Graha.CHANDRA, Graha.MANGALA, Graha.RAHU,  # Rohini, Mrigashira, Ardra
    Graha.GURU, Graha.SHANI, Graha.BUDHA,      # Punarvasu, Pushya, Ashlesha
    Graha.KETU, Graha.SHUKRA, Graha.SURYA,     # Magha, P.Phalguni, U.Phalguni
    Graha.CHANDRA, Graha.MANGALA, Graha.RAHU,  # Hasta, Chitra, Swati
    Graha.GURU, Graha.SHANI, Graha.BUDHA,      # Vishakha, Anuradha, Jyeshtha
    Graha.KETU, Graha.SHUKRA, Graha.SURYA,     # Mula, P.Ashadha, U.Ashadha
    Graha.CHANDRA, Graha.MANGALA, Graha.RAHU,  # Shravana, Dhanishtha, Shatabhisha
    Graha.GURU, Graha.SHANI, Graha.BUDHA,      # P.Bhadrapada, U.Bhadrapada, Revati
]

# 各ナクシャトラの幅（度）
NAKSHATRA_SPAN = 360.0 / 27.0  # 13°20' = 13.333...°

# 各パダの幅（度）
PADA_SPAN = NAKSHATRA_SPAN / 4.0  # 3°20' = 3.333...°


# ============================================
# ヴィムショッタリ・ダシャー
# ============================================

# ダシャー期間（年）
DASHA_YEARS = {
    Graha.KETU: 7,
    Graha.SHUKRA: 20,
    Graha.SURYA: 6,
    Graha.CHANDRA: 10,
    Graha.MANGALA: 7,
    Graha.RAHU: 18,
    Graha.GURU: 16,
    Graha.SHANI: 19,
    Graha.BUDHA: 17,
}

# ダシャーの順序（ケートゥから始まる120年周期）
DASHA_ORDER = [
    Graha.KETU,      # 7年
    Graha.SHUKRA,    # 20年
    Graha.SURYA,     # 6年
    Graha.CHANDRA,   # 10年
    Graha.MANGALA,   # 7年
    Graha.RAHU,      # 18年
    Graha.GURU,      # 16年
    Graha.SHANI,     # 19年
    Graha.BUDHA,     # 17年
]

# 総周期（年）
TOTAL_DASHA_YEARS = 120


# ============================================
# アヤナムサ（歳差補正）
# ============================================

class AyanamsaMode(Enum):
    """アヤナムサの種類"""
    LAHIRI = 1              # Lahiri (Chitra Paksha) - 標準
    RAMAN = 3               # B.V. Raman
    KRISHNAMURTI = 5        # KP System
    FAGAN_BRADLEY = 0       # Fagan-Bradley (Western Sidereal)
    TRUE_CHITRA = 27        # True Chitra
    YUKTESHWAR = 7          # Sri Yukteshwar


# デフォルトはラヒリ
DEFAULT_AYANAMSA = AyanamsaMode.LAHIRI


# ============================================
# 惑星の品位（Dignity）
# ============================================

# 高揚（Exaltation）の位置
EXALTATION_SIGNS = {
    Graha.SURYA: Rashi.MESHA,       # 牡羊座10度
    Graha.CHANDRA: Rashi.VRISHABHA, # 牡牛座3度
    Graha.MANGALA: Rashi.MAKARA,    # 山羊座28度
    Graha.BUDHA: Rashi.KANYA,       # 乙女座15度
    Graha.GURU: Rashi.KARKA,        # 蟹座5度
    Graha.SHUKRA: Rashi.MEENA,      # 魚座27度
    Graha.SHANI: Rashi.TULA,        # 天秤座20度
}

# 減衰（Debilitation）の位置
DEBILITATION_SIGNS = {
    Graha.SURYA: Rashi.TULA,        # 天秤座10度
    Graha.CHANDRA: Rashi.VRISHCHIKA,# 蠍座3度
    Graha.MANGALA: Rashi.KARKA,     # 蟹座28度
    Graha.BUDHA: Rashi.MEENA,       # 魚座15度
    Graha.GURU: Rashi.MAKARA,       # 山羊座5度
    Graha.SHUKRA: Rashi.KANYA,      # 乙女座27度
    Graha.SHANI: Rashi.MESHA,       # 牡羊座20度
}

# ムーラトリコーナ（Moolatrikona）のサインと度数範囲
MOOLATRIKONA = {
    Graha.SURYA: (Rashi.SIMHA, 0, 20),        # 獅子座0-20度
    Graha.CHANDRA: (Rashi.VRISHABHA, 4, 30),  # 牡牛座4-30度
    Graha.MANGALA: (Rashi.MESHA, 0, 12),      # 牡羊座0-12度
    Graha.BUDHA: (Rashi.KANYA, 16, 20),       # 乙女座16-20度
    Graha.GURU: (Rashi.DHANU, 0, 10),         # 射手座0-10度
    Graha.SHUKRA: (Rashi.TULA, 0, 15),        # 天秤座0-15度
    Graha.SHANI: (Rashi.KUMBHA, 0, 20),       # 水瓶座0-20度
}


# ============================================
# バーヴァ（ハウス）
# ============================================

# バーヴァ名（サンスクリット語）
BHAVA_NAMES = [
    "Tanu", "Dhana", "Sahaja", "Sukha", "Putra", "Ripu",
    "Yuvati", "Mrityu", "Dharma", "Karma", "Labha", "Vyaya"
]

# バーヴァの意味
BHAVA_MEANINGS = [
    "自己・身体", "富・家族", "兄弟・勇気", "家庭・母", "子供・知性", "敵・病気",
    "配偶者・パートナー", "寿命・変容", "幸運・宗教", "職業・名誉", "利益・友人", "損失・解脱"
]

# ケンドラ（角のハウス）
KENDRA_HOUSES = [1, 4, 7, 10]

# トリコーナ（三角のハウス）
TRIKONA_HOUSES = [1, 5, 9]

# ドゥシュタナ（凶のハウス）
DUSTHANA_HOUSES = [6, 8, 12]

# ウパチャヤ（成長のハウス）
UPACHAYA_HOUSES = [3, 6, 10, 11]


# ============================================
# ナヴァムシャ（D9）計算用
# ============================================

# D9の開始サイン（各ラシのナヴァムシャ開始位置）
# 火のサイン→火から、地のサイン→地から、風のサイン→風から、水のサイン→水から
NAVAMSHA_START = {
    Rashi.MESHA: Rashi.MESHA,       # 火→火
    Rashi.VRISHABHA: Rashi.MAKARA,  # 地→地
    Rashi.MITHUNA: Rashi.TULA,      # 風→風
    Rashi.KARKA: Rashi.KARKA,       # 水→水
    Rashi.SIMHA: Rashi.MESHA,       # 火→火
    Rashi.KANYA: Rashi.MAKARA,      # 地→地
    Rashi.TULA: Rashi.TULA,         # 風→風
    Rashi.VRISHCHIKA: Rashi.KARKA,  # 水→水
    Rashi.DHANU: Rashi.MESHA,       # 火→火
    Rashi.MAKARA: Rashi.MAKARA,     # 地→地
    Rashi.KUMBHA: Rashi.TULA,       # 風→風
    Rashi.MEENA: Rashi.KARKA,       # 水→水
}


# ============================================
# パンチャーンガ（暦）
# ============================================

# ティティ（月相）
TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
]

# カラナ（半ティティ）
KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna"
]

# ヨーガ（27種）
YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarman", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]


# ============================================
# ユーティリティ関数
# ============================================

def get_rashi_from_longitude(longitude: float) -> int:
    """黄経からラシを取得"""
    return int(longitude / 30) % 12


def get_degree_in_rashi(longitude: float) -> float:
    """ラシ内の度数を取得"""
    return longitude % 30


def get_nakshatra_from_longitude(longitude: float) -> Tuple[int, int]:
    """黄経からナクシャトラとパダを取得"""
    nakshatra_index = int(longitude / NAKSHATRA_SPAN) % 27
    pada = int((longitude % NAKSHATRA_SPAN) / PADA_SPAN) + 1
    return nakshatra_index, min(pada, 4)


def get_nakshatra_progress(longitude: float) -> float:
    """ナクシャトラ内の進行度（％）を取得"""
    nakshatra_degree = longitude % NAKSHATRA_SPAN
    return nakshatra_degree / NAKSHATRA_SPAN
