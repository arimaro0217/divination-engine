"""
カバラ数秘術モジュール
生命の樹に基づく計算
"""
from datetime import datetime
from typing import Dict, List

from ...models.output_schema import KabbalahResult


class KabbalahCalculator:
    """
    カバラ数秘術計算クラス
    """
    
    # ヘブライ文字の数値（ゲマトリア）
    HEBREW_VALUES = {
        'A': 1, 'B': 2, 'G': 3, 'D': 4, 'H': 5, 'V': 6, 'Z': 7, 'CH': 8, 'T': 9,
        'Y': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'S': 60, 'O': 70, 'P': 80,
        'TZ': 90, 'Q': 100, 'R': 200, 'SH': 300, 'TH': 400
    }
    
    # 英語→ヘブライ音素変換（簡易版）
    ENGLISH_TO_HEBREW = {
        'A': 1, 'B': 2, 'C': 20, 'D': 4, 'E': 5, 'F': 80, 'G': 3, 'H': 5,
        'I': 10, 'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 70, 'P': 80,
        'Q': 100, 'R': 200, 'S': 60, 'T': 9, 'U': 6, 'V': 6, 'W': 6, 'X': 60,
        'Y': 10, 'Z': 7
    }
    
    # 生命の樹のセフィロト
    SEPHIROT = [
        "ケテル（王冠）",
        "コクマー（知恵）",
        "ビナー（理解）",
        "ケセド（慈悲）",
        "ゲブラー（峻厳）",
        "ティファレト（美）",
        "ネツァク（勝利）",
        "ホド（栄光）",
        "イェソド（基盤）",
        "マルクト（王国）"
    ]
    
    # パス（22本）
    PATHS = [
        "アレフ", "ベト", "ギメル", "ダレト", "ヘー", "ヴァヴ", "ザイン",
        "ケト", "テト", "ヨッド", "カフ", "ラメド", "メム", "ヌン",
        "サメフ", "アイン", "ペー", "ツァディ", "コフ", "レーシュ", "シン", "タヴ"
    ]
    
    def __init__(self):
        pass
    
    def calculate(self, birth_dt: datetime, name_roman: str = "") -> KabbalahResult:
        """
        カバラ数秘を計算
        
        Args:
            birth_dt: 生年月日
            name_roman: ローマ字名
            
        Returns:
            KabbalahResult
        """
        # 生年月日から魂数を計算
        soul_number = self._calc_soul_from_date(birth_dt)
        
        # 名前から計算
        if name_roman:
            personality = self._calc_from_name(name_roman)
            destiny = self._calc_destiny(birth_dt, name_roman)
        else:
            personality = soul_number
            destiny = soul_number
        
        # 生命の樹上のパス位置
        path_positions = self._find_path_positions(soul_number, personality, destiny)
        
        return KabbalahResult(
            soul_number=soul_number,
            personality_number=personality,
            destiny_number=destiny,
            path_positions=path_positions
        )
    
    def _calc_soul_from_date(self, birth_dt: datetime) -> int:
        """生年月日から魂数を計算"""
        total = birth_dt.year + birth_dt.month + birth_dt.day
        return self._reduce_to_single(total)
    
    def _calc_from_name(self, name: str) -> int:
        """名前からカバラ数を計算（ゲマトリア）"""
        name = name.upper().replace(' ', '')
        total = sum(self.ENGLISH_TO_HEBREW.get(c, 0) for c in name)
        return self._reduce_to_single(total)
    
    def _calc_destiny(self, birth_dt: datetime, name: str) -> int:
        """運命数を計算（生年月日 + 名前）"""
        soul = self._calc_soul_from_date(birth_dt)
        name_num = self._calc_from_name(name)
        return self._reduce_to_single(soul + name_num)
    
    def _reduce_to_single(self, num: int) -> int:
        """1-9に還元（ただし22は保持）"""
        if num == 22:
            return 22
        while num > 9:
            num = sum(int(d) for d in str(num))
        return num if num > 0 else 1
    
    def _find_path_positions(self, soul: int, personality: int, destiny: int) -> List[str]:
        """生命の樹上のパス位置を特定"""
        positions = []
        
        # 魂数がセフィロトに対応
        if 1 <= soul <= 10:
            positions.append(f"魂: {self.SEPHIROT[soul - 1]}")
        
        # 人格数がパスに対応
        if 1 <= personality <= 22:
            path_idx = min(personality - 1, 21)
            positions.append(f"人格: パス{personality} ({self.PATHS[path_idx]})")
        
        return positions
    
    def get_sephira_meaning(self, number: int) -> str:
        """セフィラの意味を取得"""
        meanings = {
            1: "神性・根源・無限の光",
            2: "知恵・始まり・男性原理",
            3: "理解・形成・女性原理",
            4: "慈悲・拡大・恵み",
            5: "力・厳格・制限",
            6: "調和・美・中心",
            7: "勝利・永遠・感情",
            8: "栄光・輝き・知性",
            9: "基盤・夢・無意識",
            10: "王国・物質界・顕現"
        }
        return meanings.get(number, "")
