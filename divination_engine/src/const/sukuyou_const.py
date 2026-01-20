"""
宿曜占星術 定数定義（完全版）
Sukuyo Astrology Constants

二十七宿、旧暦法宿割、性格グループ、相性マトリクス完全定義
"""

from typing import Dict, List, Tuple
from enum import Enum, IntEnum


# ============================================
# 二十七宿の定義
# ============================================

# 二十七宿（牛宿を除外した標準配列）
MANSIONS = [
    "昴宿", "畢宿", "觜宿", "参宿", "井宿", "鬼宿", "柳宿", "星宿", "張宿",
    "翼宿", "軫宿", "角宿", "亢宿", "氐宿", "房宿", "心宿", "尾宿", "箕宿",
    "斗宿", "女宿", "虚宿", "危宿", "室宿", "壁宿", "奎宿", "婁宿", "胃宿"
]

# 宿のインデックスマッピング
MANSION_INDICES = {name: i for i, name in enumerate(MANSIONS)}

# 宿の読み方
MANSION_READINGS = [
    "ぼうしゅく", "ひつしゅく", "ししゅく", "しんしゅく", "せいしゅく",
    "きしゅく", "りゅうしゅく", "せいしゅく", "ちょうしゅく",
    "よくしゅく", "しんしゅく", "かくしゅく", "こうしゅく", "ていしゅく",
    "ぼうしゅく", "しんしゅく", "びしゅく", "きしゅく",
    "としゅく", "じょしゅく", "きょしゅく", "きしゅく", "しつしゅく",
    "へきしゅく", "けいしゅく", "ろうしゅく", "いしゅく"
]

# 宿の英語名
MANSION_ENGLISH = [
    "Mao", "Bi", "Zi", "Shen", "Jing", "Gui", "Liu", "Xing", "Zhang",
    "Yi", "Zhen", "Jiao", "Kang", "Di", "Fang", "Xin", "Wei", "Ji",
    "Dou", "Nv", "Xu", "Wei2", "Shi", "Bi2", "Kui", "Lou", "Wei3"
]


# ============================================
# 七曜（曜日属性）
# ============================================

# 各宿に対応する七曜
MANSION_WEEKDAY = [
    "日", "月", "火", "水", "木", "金", "土",  # 昴〜柳
    "日", "月", "火", "水", "木", "金", "土",  # 星〜房
    "日", "月", "火", "水", "木", "金", "土",  # 心〜室
    "日", "月", "火", "水", "木", "金"         # 壁〜胃
]

# 七曜の英語名
WEEKDAY_ENGLISH = {
    "日": "Sunday (Sun)",
    "月": "Monday (Moon)",
    "火": "Tuesday (Mars)",
    "水": "Wednesday (Mercury)",
    "木": "Thursday (Jupiter)",
    "金": "Friday (Venus)",
    "土": "Saturday (Saturn)"
}


# ============================================
# 性格グループ（七種）
# ============================================

class PersonalityGroup(Enum):
    """宿曜の性格グループ"""
    MOUAKU = "猛悪宿"      # 激しい性格
    KYUSOKU = "急速宿"     # スピード重視
    KOSHO = "剛柔宿"       # バランス型
    WAZOU = "和善宿"       # 穏やか
    ANCHOKU = "安重宿"     # 安定志向
    KEISOKU = "軽躁宿"     # 軽やか
    GOMAN = "傲慢宿"       # プライド高い


# 各宿の性格グループ
MANSION_PERSONALITY_GROUP = {
    0: PersonalityGroup.KEISOKU,   # 昴宿
    1: PersonalityGroup.MOUAKU,    # 畢宿
    2: PersonalityGroup.WAZOU,     # 觜宿
    3: PersonalityGroup.MOUAKU,    # 参宿
    4: PersonalityGroup.KYUSOKU,   # 井宿
    5: PersonalityGroup.WAZOU,     # 鬼宿
    6: PersonalityGroup.KYUSOKU,   # 柳宿
    7: PersonalityGroup.GOMAN,     # 星宿
    8: PersonalityGroup.ANCHOKU,   # 張宿
    9: PersonalityGroup.ANCHOKU,   # 翼宿
    10: PersonalityGroup.ANCHOKU,  # 軫宿
    11: PersonalityGroup.WAZOU,    # 角宿
    12: PersonalityGroup.KYUSOKU,  # 亢宿
    13: PersonalityGroup.ANCHOKU,  # 氐宿
    14: PersonalityGroup.WAZOU,    # 房宿
    15: PersonalityGroup.MOUAKU,   # 心宿
    16: PersonalityGroup.KYUSOKU,  # 尾宿
    17: PersonalityGroup.KYUSOKU,  # 箕宿
    18: PersonalityGroup.ANCHOKU,  # 斗宿
    19: PersonalityGroup.WAZOU,    # 女宿
    20: PersonalityGroup.ANCHOKU,  # 虚宿
    21: PersonalityGroup.MOUAKU,   # 危宿
    22: PersonalityGroup.MOUAKU,   # 室宿
    23: PersonalityGroup.ANCHOKU,  # 壁宿
    24: PersonalityGroup.GOMAN,    # 奎宿
    25: PersonalityGroup.WAZOU,    # 婁宿
    26: PersonalityGroup.KYUSOKU,  # 胃宿
}


# ============================================
# 旧暦法による宿割（起算宿テーブル）
# ============================================

# 各月の1日の起算宿（旧暦1月1日=室宿が基準）
# 月ごとに起算宿がスライドする
MONTH_START_MANSION = {
    1: 22,   # 正月1日 = 室宿(22)
    2: 24,   # 2月1日 = 奎宿(24)
    3: 26,   # 3月1日 = 胃宿(26)
    4: 1,    # 4月1日 = 畢宿(1)
    5: 3,    # 5月1日 = 参宿(3)
    6: 5,    # 6月1日 = 鬼宿(5)
    7: 7,    # 7月1日 = 星宿(7)
    8: 10,   # 8月1日 = 軫宿(10)
    9: 12,   # 9月1日 = 亢宿(12)
    10: 14,  # 10月1日 = 房宿(14)
    11: 17,  # 11月1日 = 箕宿(17)
    12: 19,  # 12月1日 = 女宿(19)
}


# ============================================
# 相性の種類
# ============================================

class RelationType(Enum):
    """相性の種類"""
    MEI = "命"     # 同じ宿
    GO = "業"      # 業の関係
    TAI = "胎"     # 胎の関係
    EI = "栄"      # 栄える関係
    SHIN = "親"    # 親しい関係
    YU = "友"      # 友人関係
    SUI = "衰"     # 衰える関係
    AN = "安"      # 安定させる関係
    KAI = "壊"     # 壊される関係
    KI = "危"      # 危険な関係
    SEI = "成"     # 成功する関係


class DistanceType(Enum):
    """距離の種類"""
    NEAR = "近距離"
    MIDDLE = "中距離"
    FAR = "遠距離"


# ============================================
# 相性マトリクス（完全版）
# ============================================

# 距離から相性タイプを算出
# (relation_type, is_active) - is_active: 自分が主導権を持つか
COMPATIBILITY_MATRIX = {
    0:  (RelationType.MEI, True),     # 命（同宿）
    1:  (RelationType.GO, True),      # 近業
    2:  (RelationType.TAI, True),     # 近胎
    3:  (RelationType.EI, True),      # 近栄
    4:  (RelationType.SHIN, True),    # 近親
    5:  (RelationType.YU, True),      # 近友
    6:  (RelationType.SUI, True),     # 近衰
    7:  (RelationType.AN, True),      # 近安（自分が安定させる）
    8:  (RelationType.KI, True),      # 近危
    9:  (RelationType.SEI, True),     # 近成
    10: (RelationType.KAI, True),     # 近壊（自分が壊す）
    11: (RelationType.YU, True),      # 中友
    12: (RelationType.SHIN, True),    # 中親
    13: (RelationType.EI, True),      # 中栄
    14: (RelationType.EI, False),     # 中栄
    15: (RelationType.SHIN, False),   # 中親
    16: (RelationType.YU, False),     # 中友
    17: (RelationType.KAI, False),    # 遠壊（自分が壊される）
    18: (RelationType.SEI, False),    # 遠成
    19: (RelationType.KI, False),     # 遠危
    20: (RelationType.AN, False),     # 遠安（相手が安定させる）
    21: (RelationType.SUI, False),    # 遠衰
    22: (RelationType.YU, False),     # 遠友
    23: (RelationType.SHIN, False),   # 遠親
    24: (RelationType.EI, False),     # 遠栄
    25: (RelationType.TAI, False),    # 遠胎
    26: (RelationType.GO, False),     # 遠業
}

# 旧来の相性表示（互換性のため維持）
COMPATIBILITY = {
    0: "命（同じ宿）",
    1: "業（近業）", 26: "業（遠業）",
    2: "胎（近胎）", 25: "胎（遠胎）",
    3: "栄（近栄）", 24: "栄（遠栄）",
    4: "親（近親）", 23: "親（遠親）",
    5: "友（近友）", 22: "友（遠友）",
    6: "衰（近衰）", 21: "衰（遠衰）",
    7: "安（近安）", 20: "安（遠安）",
    8: "危（近危）", 19: "危（遠危）",
    9: "成（近成）", 18: "成（遠成）",
    10: "壊（近壊）", 17: "壊（遠壊）",
    11: "友（中友）", 16: "友（中友）",
    12: "親（中親）", 15: "親（中親）",
    13: "栄（中栄）", 14: "栄（中栄）",
}


# ============================================
# 相性の吉凶レベル
# ============================================

RELATION_FORTUNE_LEVEL = {
    RelationType.MEI: 5,      # 最良（宿命的なつながり）
    RelationType.EI: 5,       # 大吉（繁栄）
    RelationType.SHIN: 4,     # 吉（親愛）
    RelationType.YU: 3,       # 中吉（友人）
    RelationType.AN: 4,       # 吉（安定・相手をコントロール）
    RelationType.SEI: 3,      # 中吉（成功）
    RelationType.TAI: 2,      # 小吉（胎）
    RelationType.GO: 1,       # 凶（業縁）
    RelationType.SUI: 1,      # 凶（衰退）
    RelationType.KI: 0,       # 大凶（危険）
    RelationType.KAI: 0,      # 大凶（破壊）
}


# ============================================
# 相性の説明文
# ============================================

RELATION_DESCRIPTIONS = {
    RelationType.MEI: {
        "ja": "同じ宿同士。宿命的なつながりがあり、良くも悪くも影響し合う運命共同体。",
        "en": "Same mansion. A fateful connection with mutual influence, for better or worse."
    },
    RelationType.GO: {
        "ja": "業の関係。過去世からの因縁があり、学びの多い関係。",
        "en": "Karmic relationship. Deep connection from past lives with much to learn."
    },
    RelationType.TAI: {
        "ja": "胎の関係。新しい始まりを示唆する関係。",
        "en": "Embryonic relationship. Suggests new beginnings."
    },
    RelationType.EI: {
        "ja": "栄の関係。お互いを発展させ、繁栄をもたらす最良の相性。",
        "en": "Prosperity relationship. Mutual growth and success."
    },
    RelationType.SHIN: {
        "ja": "親の関係。親しみやすく、自然と仲良くなれる。",
        "en": "Intimate relationship. Natural affinity and closeness."
    },
    RelationType.YU: {
        "ja": "友の関係。良き友人、恋人になりやすい相性。",
        "en": "Friendship relationship. Good for friends and romantic partners."
    },
    RelationType.SUI: {
        "ja": "衰の関係。エネルギーが減退しやすい。長期的な付き合いは避けた方が良い。",
        "en": "Decline relationship. Energy tends to diminish. Avoid long-term involvement."
    },
    RelationType.AN: {
        "ja": "安の関係。相手を安定させ、コントロールできる有利な立場。",
        "en": "Stability relationship. You can stabilize and control the other party."
    },
    RelationType.KAI: {
        "ja": "壊の関係。相手に壊される危険性がある。注意が必要。",
        "en": "Destruction relationship. Risk of being harmed. Caution required."
    },
    RelationType.KI: {
        "ja": "危の関係。予測不能な危険性があり、波乱が多い。",
        "en": "Danger relationship. Unpredictable hazards and turbulence."
    },
    RelationType.SEI: {
        "ja": "成の関係。異質だが、努力次第で成功できる。",
        "en": "Success relationship. Different but can succeed with effort."
    },
}


# ============================================
# 各宿の詳細情報
# ============================================

MANSION_DETAILS = {
    0: {  # 昴宿
        "name": "昴宿",
        "reading": "ぼうしゅく",
        "weekday": "日",
        "personality_group": "軽躁宿",
        "element": "金",
        "nature": "温厚で社交的。芸術的センスがある。",
        "keywords": ["優しさ", "社交性", "芸術", "協調性"],
        "strengths": ["人付き合いが上手", "美的センス", "調和を重んじる"],
        "weaknesses": ["優柔不断", "流されやすい", "決断力に欠ける"],
    },
    1: {  # 畢宿
        "name": "畢宿",
        "reading": "ひつしゅく",
        "weekday": "月",
        "personality_group": "猛悪宿",
        "element": "金",
        "nature": "強い意志と独立心を持つ。リーダーシップがある。",
        "keywords": ["勇気", "独立心", "リーダーシップ", "決断力"],
        "strengths": ["行動力", "決断力", "統率力"],
        "weaknesses": ["攻撃的", "短気", "独善的"],
    },
    # ... 他の宿も同様（ここでは省略）
}


# ============================================
# 運勢サイクル（日運）
# ============================================

# 本命宿からの距離に応じた日運
DAILY_FORTUNE_CYCLE = {
    0: {"type": "命", "fortune": "特異日", "description": "自分と向き合う日。大きな決断は避ける。"},
    3: {"type": "栄", "fortune": "大吉", "description": "新しいことを始めるのに最適な日。"},
    4: {"type": "親", "fortune": "吉", "description": "人間関係が良好な日。"},
    5: {"type": "友", "fortune": "中吉", "description": "友人との交流に良い日。"},
    6: {"type": "衰", "fortune": "凶", "description": "エネルギーが低下する日。休息が必要。"},
    7: {"type": "安", "fortune": "吉", "description": "安定した日。ルーティンワークに向く。"},
    8: {"type": "危", "fortune": "凶", "description": "予期せぬトラブルに注意。"},
    9: {"type": "成", "fortune": "中吉", "description": "努力が実を結ぶ日。"},
    10: {"type": "壊", "fortune": "大凶", "description": "災難に注意。重要な決断は避ける。"},
}


# ============================================
# 経度法パラメータ
# ============================================

# 1宿 = 360° / 27 = 13.333...°
MANSION_SPAN = 360.0 / 27.0

# 昴宿の起点（トロピカル黄道）
MANSION_START_OFFSET = 26.0

# 宿の境界線
MANSION_BOUNDARIES = [
    (MANSION_START_OFFSET + i * MANSION_SPAN) % 360.0
    for i in range(27)
]


# ============================================
# 九曜
# ============================================

NINE_LUMINARIES = ["日", "月", "火", "水", "木", "金", "土", "羅睺", "計都"]


# ============================================
# Webフロント用角度計算
# ============================================

def get_mandala_angle(mansion_index: int) -> float:
    """円盤上の角度を取得（0度が上、時計回り）"""
    return (360.0 / 27.0) * mansion_index
