"""
算命学専用定数定義 (Sanmeigaku Constants)

このモジュールは算命学（Sanmeigaku）の計算に必要な全ての定数を定義します。
- 六十干支の角度マッピング（宇宙盤用）
- 算命学独自の蔵干表（二十八元）
- 十大主星の定義と計算テーブル
- 十二大従星の定義と計算テーブル
- 天中殺の種類と判定テーブル
- 異常干支の定義
"""
from typing import Dict, List, Tuple

# ============================================
# 基本的な干支定義
# ============================================

# 十干（天干）
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 十二支（地支）
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 六十干支（甲子から癸亥まで）
SIXTY_GANZHI = [
    f"{STEMS[i % 10]}{BRANCHES[i % 12]}" 
    for i in range(60)
]

# ============================================
# 五行の定義
# ============================================

class WuXing:
    """五行"""
    WOOD = "木"
    FIRE = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"

# 天干の五行と陰陽
STEM_WUXING: Dict[str, Tuple[str, str]] = {
    # (五行, 陰陽)
    "甲": (WuXing.WOOD, "陽"),
    "乙": (WuXing.WOOD, "陰"),
    "丙": (WuXing.FIRE, "陽"),
    "丁": (WuXing.FIRE, "陰"),
    "戊": (WuXing.EARTH, "陽"),
    "己": (WuXing.EARTH, "陰"),
    "庚": (WuXing.METAL, "陽"),
    "辛": (WuXing.METAL, "陰"),
    "壬": (WuXing.WATER, "陽"),
    "癸": (WuXing.WATER, "陰"),
}

# 地支の五行と陰陽
BRANCH_WUXING: Dict[str, Tuple[str, str]] = {
    # (五行, 陰陽)
    "子": (WuXing.WATER, "陽"),
    "丑": (WuXing.EARTH, "陰"),
    "寅": (WuXing.WOOD, "陽"),
    "卯": (WuXing.WOOD, "陰"),
    "辰": (WuXing.EARTH, "陽"),
    "巳": (WuXing.FIRE, "陰"),
    "午": (WuXing.FIRE, "陽"),
    "未": (WuXing.EARTH, "陰"),
    "申": (WuXing.METAL, "陽"),
    "酉": (WuXing.METAL, "陰"),
    "戌": (WuXing.EARTH, "陽"),
    "亥": (WuXing.WATER, "陰"),
}

# ============================================
# 宇宙盤用：六十干支の角度マッピング
# ============================================

# 子（ね）を真北（90度）に配置し、時計回りに配置
# 数学的座標系では、0度=東（3時方向）、90度=北（12時方向）
# 1干支 = 6度

def get_ganzhi_angle(ganzhi: str) -> float:
    """
    干支の宇宙盤上の角度を取得
    
    Args:
        ganzhi: 干支（例: "甲子"）
    
    Returns:
        角度（度）0-360、北を90度とし時計回りに増加
    """
    if ganzhi not in SIXTY_GANZHI:
        raise ValueError(f"無効な干支: {ganzhi}")
    
    index = SIXTY_GANZHI.index(ganzhi)
    # 甲子（index=0）を90度（北）から開始
    # 時計回りなので角度は減少する
    angle = (90 - index * 6) % 360
    return angle

# 全干支の角度マッピングテーブル
GANZHI_ANGLES: Dict[str, float] = {
    ganzhi: get_ganzhi_angle(ganzhi) 
    for ganzhi in SIXTY_GANZHI
}

# ============================================
# 算命学独自の蔵干表（二十八元）
# ============================================

# 各地支に含まれる蔵干（本元・中元・初元）
# 四柱推命とは異なる算命学独自の定義
SANMEI_ZANGGAN: Dict[str, Dict[str, str]] = {
    "子": {"本元": "癸", "中元": None, "初元": None},
    "丑": {"本元": "己", "中元": "癸", "初元": "辛"},
    "寅": {"本元": "甲", "中元": "丙", "初元": "戊"},
    "卯": {"本元": "乙", "中元": None, "初元": None},
    "辰": {"本元": "戊", "中元": "乙", "初元": "癸"},
    "巳": {"本元": "丙", "中元": "庚", "初元": "戊"},
    "午": {"本元": "丁", "中元": None, "初元": None},
    "未": {"本元": "己", "中元": "丁", "初元": "乙"},
    "申": {"本元": "庚", "中元": "壬", "初元": "戊"},
    "酉": {"本元": "辛", "中元": None, "初元": None},
    "戌": {"本元": "戊", "中元": "辛", "初元": "丁"},
    "亥": {"本元": "壬", "中元": "甲", "初元": None},
}

def get_zanggan_hongen(branch: str) -> str:
    """
    地支の本元（主蔵干）を取得
    
    Args:
        branch: 地支（例: "子"）
    
    Returns:
        本元の天干（例: "癸"）
    """
    if branch not in SANMEI_ZANGGAN:
        raise ValueError(f"無効な地支: {branch}")
    return SANMEI_ZANGGAN[branch]["本元"]

# ============================================
# 十大主星（Ten Great Stars）
# ============================================

# 日干と他の天干の五行関係から算出される星
# 比和、生、剋、洩、受の関係性で決定

class TenMainStars:
    """十大主星"""
    KANSAKU = "貫索星"      # 比和・陽 (自立心)
    SEKIMON = "石門星"      # 比和・陰 (協調性)
    HOUKAKU = "鳳閣星"      # 洩気・陽 (伝達本能)
    CHOUSHO = "調舒星"      # 洩気・陰 (繊細さ)
    ROKUSON = "禄存星"      # 受生・陽 (奉仕)
    SHIROKU = "司禄星"      # 受生・陰 (蓄財)
    SHAKI = "車騎星"        # 剋出・陽 (行動力)
    KENGYUU = "牽牛星"      # 剋出・陰 (名誉欲)
    RYUKOU = "龍高星"       # 生出・陽 (改革)
    GYOKUDOU = "玉堂星"     # 生出・陰 (学習)

# 五行関係による主星の決定テーブル
# (日干の五行, 相手の五行, 日干陰陽, 相手陰陽) -> 主星
MAIN_STAR_TABLE: Dict[Tuple[str, str, str, str], str] = {}

# 比和（同じ五行）
for element in [WuXing.WOOD, WuXing.FIRE, WuXing.EARTH, WuXing.METAL, WuXing.WATER]:
    MAIN_STAR_TABLE[(element, element, "陽", "陽")] = TenMainStars.KANSAKU
    MAIN_STAR_TABLE[(element, element, "陽", "陰")] = TenMainStars.SEKIMON
    MAIN_STAR_TABLE[(element, element, "陰", "陽")] = TenMainStars.SEKIMON
    MAIN_STAR_TABLE[(element, element, "陰", "陰")] = TenMainStars.KANSAKU

# 相生・相剋の関係定義
SHENG_RELATIONS = {
    WuXing.WOOD: WuXing.FIRE,
    WuXing.FIRE: WuXing.EARTH,
    WuXing.EARTH: WuXing.METAL,
    WuXing.METAL: WuXing.WATER,
    WuXing.WATER: WuXing.WOOD,
}

KE_RELATIONS = {
    WuXing.WOOD: WuXing.EARTH,
    WuXing.EARTH: WuXing.WATER,
    WuXing.WATER: WuXing.FIRE,
    WuXing.FIRE: WuXing.METAL,
    WuXing.METAL: WuXing.WOOD,
}

# 洩気（日干が生む相手）
for day_element, target_element in SHENG_RELATIONS.items():
    MAIN_STAR_TABLE[(day_element, target_element, "陽", "陽")] = TenMainStars.HOUKAKU
    MAIN_STAR_TABLE[(day_element, target_element, "陽", "陰")] = TenMainStars.CHOUSHO
    MAIN_STAR_TABLE[(day_element, target_element, "陰", "陽")] = TenMainStars.CHOUSHO
    MAIN_STAR_TABLE[(day_element, target_element, "陰", "陰")] = TenMainStars.HOUKAKU

# 受生（相手が日干を生む）
for target_element, day_element in SHENG_RELATIONS.items():
    MAIN_STAR_TABLE[(day_element, target_element, "陽", "陽")] = TenMainStars.ROKUSON
    MAIN_STAR_TABLE[(day_element, target_element, "陽", "陰")] = TenMainStars.SHIROKU
    MAIN_STAR_TABLE[(day_element, target_element, "陰", "陽")] = TenMainStars.SHIROKU
    MAIN_STAR_TABLE[(day_element, target_element, "陰", "陰")] = TenMainStars.ROKUSON

# 剋出（日干が剋す相手）
for day_element, target_element in KE_RELATIONS.items():
    MAIN_STAR_TABLE[(day_element, target_element, "陽", "陽")] = TenMainStars.SHAKI
    MAIN_STAR_TABLE[(day_element, target_element, "陽", "陰")] = TenMainStars.KENGYUU
    MAIN_STAR_TABLE[(day_element, target_element, "陰", "陽")] = TenMainStars.KENGYUU
    MAIN_STAR_TABLE[(day_element, target_element, "陰", "陰")] = TenMainStars.SHAKI

# 剋入（相手が日干を剋す） = 生出の逆方向
for target_element, day_element in KE_RELATIONS.items():
    MAIN_STAR_TABLE[(day_element, target_element, "陽", "陽")] = TenMainStars.RYUKOU
    MAIN_STAR_TABLE[(day_element, target_element, "陽", "陰")] = TenMainStars.GYOKUDOU
    MAIN_STAR_TABLE[(day_element, target_element, "陰", "陽")] = TenMainStars.GYOKUDOU
    MAIN_STAR_TABLE[(day_element, target_element, "陰", "陰")] = TenMainStars.RYUKOU

# ============================================
# 十二大従星（Twelve Great Imperial Stars）
# ============================================

class TwelveSubStars:
    """十二大従星"""
    TENHOU = "天報星"      # 0点（赤子）
    TENIN = "天印星"       # 2点（幼児）
    TENKI = "天貴星"       # 4点（少年）
    TENKOU = "天恍星"      # 6点（青年）
    TENNAN = "天南星"      # 8点（壮年）
    TENROKU = "天禄星"     # 10点（実業家）
    TENSHOU = "天将星"     # 12点（帝王）
    TENDOU = "天堂星"      # 10点（老人）
    TENKO = "天胡星"       # 8点（病人）
    TENKYOKU = "天極星"    # 6点（死者）
    TENKO_ALT = "天庫星"   # 4点（入墓）
    TENCHI = "天馳星"      # 2点（胎児）

# 日干と地支の関係による従星の決定
# 十二運星の概念を使用
TWELVE_POSITIONS = ["長生", "沐浴", "冠帯", "建禄", "帝旺", "衰", "病", "死", "墓", "絶", "胎", "養"]

# 各五行の長生位置
CHANGSHEN_POSITIONS = {
    # 陽干
    (WuXing.WOOD, "陽"): "亥",
    (WuXing.FIRE, "陽"): "寅",
    (WuXing.METAL, "陽"): "巳",
    (WuXing.WATER, "陽"): "申",
    (WuXing.EARTH, "陽"): "申",  # 陽土は寄金
    # 陰干
    (WuXing.WOOD, "陰"): "午",
    (WuXing.FIRE, "陰"): "酉",
    (WuXing.METAL, "陰"): "子",
    (WuXing.WATER, "陰"): "卯",
    (WuXing.EARTH, "陰"): "卯",  # 陰土は寄木
}

# 十二運から従星へのマッピング
JUNIUNSEI_TO_SUBSTAR = {
    "長生": TwelveSubStars.TENIN,
    "沐浴": TwelveSubStars.TENCHI,
    "冠帯": TwelveSubStars.TENKI,
    "建禄": TwelveSubStars.TENROKU,
    "帝旺": TwelveSubStars.TENSHOU,
    "衰": TwelveSubStars.TENDOU,
    "病": TwelveSubStars.TENKO,
    "死": TwelveSubStars.TENKYOKU,
    "墓": TwelveSubStars.TENKO_ALT,
    "絶": TwelveSubStars.TENHOU,
    "胎": TwelveSubStars.TENCHI,
    "養": TwelveSubStars.TENKOU,
}

# 従星のエネルギー点数
SUBSTAR_SCORES = {
    TwelveSubStars.TENHOU: 0,
    TwelveSubStars.TENIN: 2,
    TwelveSubStars.TENKI: 4,
    TwelveSubStars.TENKOU: 6,
    TwelveSubStars.TENNAN: 8,
    TwelveSubStars.TENROKU: 10,
    TwelveSubStars.TENSHOU: 12,
    TwelveSubStars.TENDOU: 10,
    TwelveSubStars.TENKO: 8,
    TwelveSubStars.TENKYOKU: 6,
    TwelveSubStars.TENKO_ALT: 4,
    TwelveSubStars.TENCHI: 2,
}

# ============================================
# 天中殺（Tenchusatsu）
# ============================================

# 6種類の天中殺
TENCHUSATSU_TYPES = {
    "戌亥天中殺": ["戌", "亥"],
    "申酉天中殺": ["申", "酉"],
    "午未天中殺": ["午", "未"],
    "辰巳天中殺": ["辰", "巳"],
    "寅卯天中殺": ["寅", "卯"],
    "子丑天中殺": ["子", "丑"],
}

def get_tenchusatsu_type(branch: str) -> str:
    """
    地支から天中殺のタイプを取得
    
    Args:
        branch: 地支
    
    Returns:
        天中殺のタイプ（例: "戌亥天中殺"）
    """
    for t_type, branches in TENCHUSATSU_TYPES.items():
        if branch in branches:
            return t_type
    raise ValueError(f"無効な地支: {branch}")

# ============================================
# 異常干支（Abnormal Ganzhi）
# ============================================

# 通常異常
NORMAL_ABNORMAL_GANZHI = [
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯",
    "庚辰", "辛巳", "壬午", "癸未"
]

# 暗合異常（対冲する干支）
ANGOUI_ABNORMAL_PAIRS = [
    ("甲子", "庚午"), ("乙丑", "辛未"), ("丙寅", "壬申"),
    ("丁卯", "癸酉"), ("戊辰", "甲戌"), ("己巳", "乙亥"),
]

def is_normal_abnormal(ganzhi: str) -> bool:
    """通常異常干支かどうか判定"""
    return ganzhi in NORMAL_ABNORMAL_GANZHI

def is_angoui_abnormal(ganzhi1: str, ganzhi2: str) -> bool:
    """暗合異常（2つの干支が対応しているか）判定"""
    for pair in ANGOUI_ABNORMAL_PAIRS:
        if (ganzhi1 in pair and ganzhi2 in pair):
            return True
    return False

# ============================================
# 人体星図の位置定義
# ============================================

class JintaiPosition:
    """人体星図の8つの位置"""
    NORTH = "north"              # 頭（親・目上）
    LEFT_SHOULDER = "left_shoulder"   # 左肩
    RIGHT_HAND = "right_hand"         # 右手
    CENTER = "center"                 # 胸（自分・本質）
    LEFT_HAND = "left_hand"           # 左手
    SOUTH = "south"                   # 腹（子供・目下）
    RIGHT_FOOT = "right_foot"         # 右足
    LEFT_FOOT = "left_foot"           # 左足

# 位置ごとの意味
JINTAI_POSITION_MEANINGS = {
    JintaiPosition.NORTH: "親・目上との関係",
    JintaiPosition.LEFT_SHOULDER: "家系の初年期",
    JintaiPosition.RIGHT_HAND: "配偶者との関係",
    JintaiPosition.CENTER: "自分自身の本質",
    JintaiPosition.LEFT_HAND: "子供との関係",
    JintaiPosition.SOUTH: "子孫・目下との関係",
    JintaiPosition.RIGHT_FOOT: "晩年期の運勢",
    JintaiPosition.LEFT_FOOT: "中年期の運勢",
}

# ============================================
# 数理法用：エネルギー点数
# ============================================

# 天干のエネルギー点数
STEM_ENERGY_SCORE = 1

# 地支のエネルギー点数（本元・中元・初元）
BRANCH_ENERGY_SCORES = {
    "本元": 3,
    "中元": 2,
    "初元": 1,
}
