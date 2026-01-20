import swisseph as swe
from enum import Enum, auto

# ============================================
# 天体ID定義 (Swiss Ephemeris準拠)
# ============================================
class PlanetId(int, Enum):
    SUN = swe.SUN
    MOON = swe.MOON
    MERCURY = swe.MERCURY
    VENUS = swe.VENUS
    MARS = swe.MARS
    JUPITER = swe.JUPITER
    SATURN = swe.SATURN
    URANUS = swe.URANUS
    NEPTUNE = swe.NEPTUNE
    PLUTO = swe.PLUTO
    
    # 小惑星・感受点
    CHIRON = swe.CHIRON
    PHOLUS = swe.PHOLUS
    CERES = swe.CERES
    PALLAS = swe.PALLAS
    JUNO = swe.JUNO
    VESTA = swe.VESTA
    
    # 仮想点 (swe.CALC_... は計算用ID)
    MEAN_NODE = swe.MEAN_NODE  # 平均ノード
    TRUE_NODE = swe.TRUE_NODE  # 真ノード
    MEAN_APOGEE = swe.MEAN_APOG # リリス(平均)
    OSCU_APOGEE = swe.OSCU_APOG # リリス(真)
    
    EARTH = swe.EARTH

# ============================================
# ハウスシステム定義
# ============================================
class HouseSystem(str, Enum):
    PLACIDUS = 'P'
    KOCH = 'K'
    PORPHYRY = 'O'
    REGIOMONTANUS = 'R'
    CAMPANUS = 'C'
    EQUAL = 'E'
    WHOLE_SIGN = 'W'
    ALCABITIUS = 'B'
    MORINUS = 'M'

# ============================================
# サイン定義
# ============================================
SIGNS_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", 
    "Leo", "Virgo", "Libra", "Scorpio", 
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGNS_JP = [
    "牡羊座", "牡牛座", "双子座", "蟹座", 
    "獅子座", "乙女座", "天秤座", "蠍座", 
    "射手座", "山羊座", "水瓶座", "魚座"
]

ELEMENTS = {
    "Fire": ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air": ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"]
}

MODALITIES = {
    "Cardinal": ["Aries", "Cancer", "Libra", "Capricorn"],
    "Fixed": ["Taurus", "Leo", "Scorpio", "Aquarius"],
    "Mutable": ["Gemini", "Virgo", "Sagittarius", "Pisces"]
}

# ============================================
# アスペクト定義
# ============================================
class AspectType(str, Enum):
    CONJUNCTION = "Conjunction" # 0
    OPPOSITION = "Opposition"   # 180
    TRINE = "Trine"             # 120
    SQUARE = "Square"           # 90
    SEXTILE = "Sextile"         # 60
    
    # マイナー
    QUINCUNX = "Quincunx"       # 150
    SEMI_SEXTILE = "Semi-Sextile" # 30
    SEMI_SQUARE = "Semi-Square"   # 45
    SESQUIQUADRATE = "Sesquiquadrate" # 135
    QUINTILE = "Quintile"       # 72
    BI_QUINTILE = "Bi-Quintile" # 144

ASPECT_ANGLES = {
    AspectType.CONJUNCTION: 0,
    AspectType.OPPOSITION: 180,
    AspectType.TRINE: 120,
    AspectType.SQUARE: 90,
    AspectType.SEXTILE: 60,
    AspectType.QUINCUNX: 150,
    AspectType.SEMI_SEXTILE: 30,
    AspectType.SEMI_SQUARE: 45,
    AspectType.SESQUIQUADRATE: 135,
    AspectType.QUINTILE: 72,
    AspectType.BI_QUINTILE: 144
}

# ============================================
# デフォルトオーブ設定 (度)
# ============================================
DEFAULT_ORBS = {
    # (AspectType, IsLuminary_SunMoon?) -> Orb
    (AspectType.CONJUNCTION, True): 8.0,
    (AspectType.CONJUNCTION, False): 6.0,
    
    (AspectType.OPPOSITION, True): 8.0,
    (AspectType.OPPOSITION, False): 6.0,
    
    (AspectType.TRINE, True): 8.0,
    (AspectType.TRINE, False): 6.0,
    
    (AspectType.SQUARE, True): 8.0,
    (AspectType.SQUARE, False): 6.0,
    
    (AspectType.SEXTILE, True): 6.0,
    (AspectType.SEXTILE, False): 4.0,
    
    # マイナーアスペクトは一律狭く
    (AspectType.QUINCUNX, True): 3.0,
    (AspectType.QUINCUNX, False): 2.5,
    
    (AspectType.SEMI_SEXTILE, True): 2.0,
    (AspectType.SEMI_SEXTILE, False): 1.5,
    
    (AspectType.SEMI_SQUARE, True): 2.0,
    (AspectType.SEMI_SQUARE, False): 1.5,
    
    (AspectType.SESQUIQUADRATE, True): 2.0,
    (AspectType.SESQUIQUADRATE, False): 1.5,
    
    (AspectType.QUINTILE, True): 2.0,
    (AspectType.QUINTILE, False): 1.5,
    
    (AspectType.BI_QUINTILE, True): 2.0,
    (AspectType.BI_QUINTILE, False): 1.5
}
