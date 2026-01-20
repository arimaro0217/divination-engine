"""
数秘術定数定義
Numerology Constants

- Pythagorean / Chaldean変換テーブル
- 惑星支配星マッピング
- 品位テーブル
- 数字の意味
"""
import sys
import io

# Windows環境でのUTF-8出力対応（安全版）
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ============================================
# アルファベット変換テーブル
# ============================================

# Pythagorean (Modern) System
# A=1, B=2, C=3... 繰り返し
PYTHAGOREAN_TABLE = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
}

# Chaldean (Ancient) System
# 音韻に基づく配置、9は神聖数として除外
CHALDEAN_TABLE = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
    # 9は含まない（神聖数）
}

# 母音（Soul Urge計算用）
VOWELS = {'A', 'E', 'I', 'O', 'U'}


# ============================================
# マスターナンバー・カルマナンバー
# ============================================

MASTER_NUMBERS = {11, 22, 33, 44}

# Karmic Debt Numbers
KARMIC_NUMBERS = {13, 14, 16, 19}


# ============================================
# 惑星支配星マッピング
# ============================================

PLANET_RULERS = {
    1: 'Sun',       # 太陽 - リーダーシップ
    2: 'Moon',      # 月 - 感受性、直感
    3: 'Jupiter',   # 木星 - 拡大、楽観
    4: 'Uranus',    # 天王星 - 革新、突然の変化（一部で土星とする流派も）
    5: 'Mercury',   # 水星 - コミュニケーション、変化
    6: 'Venus',     # 金星 - 愛、調和
    7: 'Neptune',   # 海王星 - 神秘、精神性（一部で海王星とする流派も）
    8: 'Saturn',    # 土星 - 制限、カルマ、達成
    9: 'Mars',      # 火星 - 行動、完成
    11: 'Moon',     # Master Number - 強化された月
    22: 'Uranus',   # Master Builder - 強化された天王星
    33: 'Neptune'   # Master Teacher - 強化された海王星
}


# ============================================
# pyswisseph 惑星ID
# ============================================

PLANET_IDS = {
    'Sun': 0,
    'Moon': 1,
    'Mercury': 2,
    'Venus': 3,
    'Mars': 4,
    'Jupiter': 5,
    'Saturn': 6,
    'Uranus': 7,
    'Neptune': 8,
    'Pluto': 9
}


# ============================================
# 黄道12サイン
# ============================================

ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer',
    'Leo', 'Virgo', 'Libra', 'Scorpio',
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

ZODIAC_SIGNS_JA = [
    '牡羊座', '牡牛座', '双子座', '蟹座',
    '獅子座', '乙女座', '天秤座', '蠍座',
    '射手座', '山羊座', '水瓶座', '魚座'
]


# ============================================
# 惑星の品位テーブル
# ============================================

# Domicile（ドミサイル：本来の座）
DOMICILE = {
    'Sun': ['Leo'],
    'Moon': ['Cancer'],
    'Mercury': ['Gemini', 'Virgo'],
    'Venus': ['Taurus', 'Libra'],
    'Mars': ['Aries', 'Scorpio'],
    'Jupiter': ['Sagittarius', 'Pisces'],
    'Saturn': ['Capricorn', 'Aquarius'],
    'Uranus': ['Aquarius'],
    'Neptune': ['Pisces'],
    'Pluto': ['Scorpio']
}

# Exaltation（エグザルテーション：高揚）
EXALTATION = {
    'Sun': 'Aries',
    'Moon': 'Taurus',
    'Mercury': 'Virgo',
    'Venus': 'Pisces',
    'Mars': 'Capricorn',
    'Jupiter': 'Cancer',
    'Saturn': 'Libra',
    'Uranus': 'Scorpio',
    'Neptune': 'Leo',  # 一部流派により異なる
    'Pluto': 'Aries'    # 一部流派により異なる
}

# Detriment（デトリメント：障害）
DETRIMENT = {
    'Sun': ['Aquarius'],
    'Moon': ['Capricorn'],
    'Mercury': ['Sagittarius', 'Pisces'],
    'Venus': ['Aries', 'Scorpio'],
    'Mars': ['Taurus', 'Libra'],
    'Jupiter': ['Gemini', 'Virgo'],
    'Saturn': ['Cancer', 'Leo'],
    'Uranus': ['Leo'],
    'Neptune': ['Virgo'],
    'Pluto': ['Taurus']
}

# Fall（フォール：下降）
FALL = {
    'Sun': 'Libra',
    'Moon': 'Scorpio',
    'Mercury': 'Pisces',
    'Venus': 'Virgo',
    'Mars': 'Cancer',
    'Jupiter': 'Capricorn',
    'Saturn': 'Aries',
    'Uranus': 'Taurus',
    'Neptune': 'Aquarius',
    'Pluto': 'Libra'
}


# ============================================
# 数字の意味・キーワード
# ============================================

NUMBER_MEANINGS = {
    1: {
        'keywords': ['リーダーシップ', '独立', '開拓', '自信'],
        'traits': '独立心が強く、リーダーシップを発揮します。創造的で革新的なアイデアを持ち、他者に先駆けて行動する勇気があります。',
        'challenges': '孤独になりやすく、頑固で自己中心的になる傾向があります。他者との協調を学ぶ必要があります。',
        'career': 'CEO、起業家、パイオニア、アーティスト',
        'planet': 'Sun（太陽）',
        'element': '火'
    },
    2: {
        'keywords': ['協調', '調和', 'パートナーシップ', '感受性'],
        'traits': '他者との協力を重視し、調和を大切にします。直感力が鋭く、周囲の感情を敏感に察知できます。',
        'challenges': '優柔不断で依存的になりやすく、自己主張が弱い傾向があります。自信を持つことが課題です。',
        'career': 'カウンセラー、外交官、調停者、チームプレーヤー',
        'planet': 'Moon（月）',
        'element': '水'
    },
    3: {
        'keywords': ['創造性', '表現', 'コミュニケーション', '楽観性'],
        'traits': '表現力豊かで社交的、創造的なエネルギーに満ちています。芸術的才能があり、人を楽しませる能力に長けています。',
        'challenges': '散漫になりやすく、深刻さに欠ける傾向があります。焦点を絞ることが重要です。',
        'career': 'アーティスト、作家、エンターテイナー、広報担当',
        'planet': 'Jupiter（木星）',
        'element': '火'
    },
    4: {
        'keywords': ['安定', '実用性', '勤勉', '基盤'],
        'traits': '実践的で組織的、信頼性が高く責任感があります。堅実に目標を達成する力があります。',
        'challenges': '柔軟性に欠け、変化を恐れる傾向があります。完璧主義すぎることもあります。',
        'career': '建築家、会計士、プロジェクトマネージャー、エンジニア',
        'planet': 'Uranus（天王星）/ Saturn（土星）',
        'element': '土'
    },
    5: {
        'keywords': ['自由', '変化', '冒険', '多様性'],
        'traits': '自由を愛し、変化と冒険を求めます。適応力が高く、多才で好奇心旺盛です。',
        'challenges': '落ち着きがなく、衝動的で無責任になりやすい傾向があります。',
        'career': '旅行ガイド、ジャーナリスト、営業、起業家',
        'planet': 'Mercury（水星）',
        'element': '風'
    },
    6: {
        'keywords': ['責任', '愛', '家庭', '奉仕'],
        'traits': '愛情深く、責任感が強く、他者をケアする能力があります。調和と美を重視します。',
        'challenges': '過保護になりやすく、他者のために自分を犠牲にしすぎることがあります。',
        'career': 'カウンセラー、看護師、教師、ソーシャルワーカー',
        'planet': 'Venus（金星）',
        'element': '土'
    },
    7: {
        'keywords': ['分析', '内省', '精神性', '知恵'],
        'traits': '知的で分析的、精神的な探求を好みます。直感力があり、深い洞察力を持ちます。',
        'challenges': '孤立しやすく、冷淡に見られることがあります。実践性に欠けることもあります。',
        'career': '研究者、哲学者、スピリチュアルカウンセラー、科学者',
        'planet': 'Neptune（海王星）',
        'element': '水'
    },
    8: {
        'keywords': ['権力', '物質的成功', 'カルマ', '達成'],
        'traits': '野心的で実行力があり、物質的成功を収める能力があります。強いリーダーシップを持ちます。',
        'challenges': '物質主義に偏りやすく、権力を濫用する危険があります。バランスが重要です。',
        'career': 'CEO、投資家、政治家、経営者',
        'planet': 'Saturn（土星）',
        'element': '土'
    },
    9: {
        'keywords': ['人道主義', '完成', '知恵', '無私'],
        'traits': '慈悲深く、人道的で理想主義的です。完成と終わりを象徴し、高い精神性を持ちます。',
        'challenges': '非実用的で夢想的になりやすく、現実から離れることがあります。',
        'career': 'チャリティー活動家、芸術家、ヒーラー、教師',
        'planet': 'Mars（火星）',
        'element': '火'
    },
    11: {
        'keywords': ['直感', '霊感', '啓示', 'マスターナンバー'],
        'traits': '非常に直感的で霊的な洞察力があります。他者にインスピレーションを与える力を持ちます。',
        'challenges': '神経質で不安定になりやすく、理想と現実のギャップに苦しむことがあります。',
        'career': 'スピリチュアルガイド、発明家、革新者、インフルエンサー',
        'planet': 'Moon（月）',
        'element': '水'
    },
    22: {
        'keywords': ['マスタービルダー', '大きな夢の実現', '影響力'],
        'traits': '実践的な理想主義者で、大規模なプロジェクトを実現する能力があります。ビジョンと実行力を兼ね備えています。',
        'challenges': 'プレッシャーに弱く、完璧主義が過ぎて行動できないことがあります。',
        'career': '建築家、大企業のリーダー、社会改革者',
        'planet': 'Uranus（天王星）',
        'element': '土'
    },
    33: {
        'keywords': ['マスターティーチャー', '癒し', '奉仕', '無条件の愛'],
        'traits': '最も高い精神性を持ち、他者を癒し教える使命があります。無条件の愛と奉仕を体現します。',
        'challenges': '自己犠牲が過ぎて燃え尽きやすく、現実逃避する傾向があります。',
        'career': 'マスターティーチャー、ヒーラー、精神的リーダー',
        'planet': 'Neptune（海王星）',
        'element': '水'
    }
}


# ============================================
# カルマナンバーの意味
# ============================================

KARMIC_MEANINGS = {
    13: {
        'lesson': '怠惰と無責任からの解放',
        'description': '前世で責任を放棄したカルマ。今生では勤勉と忍耐が求められます。',
        'challenge': '努力を厭わず、困難に立ち向かうこと'
    },
    14: {
        'lesson': '放縦と過度の自由からの解放',
        'description': '前世で自制心を欠いたカルマ。今生では節度とバランスが必要です。',
        'challenge': '自己管理と中庸を学ぶこと'
    },
    16: {
        'lesson': '高慢と堕落からの解放',
        'description': '前世で傲慢さや不誠実さがあったカルマ。今生では謙虚さが求められます。',
        'challenge': '自我を手放し、真実を受け入れること'
    },
    19: {
        'lesson': '権力の濫用からの解放',
        'description': '前世で他者を支配または利用したカルマ。今生では奉仕と無私が必要です。',
        'challenge': '他者を尊重し、共感を持って接すること'
    }
}


# ============================================
# Personal Year の意味 (1-9サイクル)
# ============================================

PERSONAL_YEAR_MEANINGS = {
    1: {'theme': '新しい始まり', 'description': '新しいサイクルが始まります。行動を起こし、計画を立て、種を蒔く時期です。'},
    2: {'theme': '協力と忍耐', 'description': '成長には時間がかかります。人間関係を育み、協力することが重要です。'},
    3: {'theme': '創造性と社交', 'description': '表現と楽しみの年。創造的プロジェクトに取り組み、社交活動を楽しみましょう。'},
    4: {'theme': '基盤固め', 'description': '勤勉と忍耐が求められます。基盤を固め、実践的な仕事に専念する時期です。'},
    5: {'theme': '変化と自由', 'description': '予期せぬ変化の年。自由を求め、新しい経験を受け入れましょう。'},
    6: {'theme': '責任と愛', 'description': '家族や責任に焦点を当てる年。愛と調和を育む時期です。'},
    7: {'theme': '内省と精神性', 'description': '内面を見つめ、精神的成長を求める年。rest and reflectionが必要です。'},
    8: {'theme': '達成と成功', 'description': '努力が報われる年。物質的成功を収める可能性が高まります。'},
    9: {'theme': '完成と手放し', 'description': 'サイクルの終わり。古いものを手放し、新しいサイクルに備える時期です。'}
}
