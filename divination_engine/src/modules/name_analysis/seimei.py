"""
姓名判断モジュール
五格（天格・人格・地格・外格・総格）の計算
"""
from typing import Dict, List, Optional, Tuple
import json
import os

from ...models.output_schema import SeimeiResult


class SeimeiCalculator:
    """
    姓名判断計算クラス
    康熙字典に基づく旧字体画数で計算
    """
    
    # 基本的な画数マッピング（一部）
    # 実際には外部JSONファイルから読み込む
    DEFAULT_STROKES = {
        # 部首の旧字体画数
        "氵": 4,  # さんずい → 水(4画)
        "扌": 4,  # てへん → 手(4画)
        "忄": 4,  # りっしんべん → 心(4画)
        "艹": 6,  # くさかんむり → 艸(6画)
        "辶": 7,  # しんにょう → 辵(7画)
        "阝": 8,  # こざとへん/おおざと → 阜/邑(8画)
        "犭": 4,  # けものへん → 犬(4画)
        "礻": 5,  # しめすへん → 示(5画)
        "衤": 6,  # ころもへん → 衣(6画)
        "月": 4,  # にくづき → 肉と同じ扱いの場合も
        
        # よく使われる漢字
        "一": 1, "二": 2, "三": 3, "四": 5, "五": 4, "六": 4, "七": 2, "八": 2, "九": 2, "十": 2,
        "山": 3, "川": 3, "田": 5, "木": 4, "水": 4, "火": 4, "土": 3, "金": 8, "日": 4, "月": 4,
        "人": 2, "口": 3, "目": 5, "手": 4, "足": 7, "心": 4, "言": 7, "糸": 6,
        
        # 名前に頻出する漢字
        "安": 6, "瀬": 19, "諒": 15, "理": 11, "明": 8, "美": 9, "子": 3, "太": 4, "郎": 14,
        "大": 3, "小": 3, "中": 4, "上": 3, "下": 3, "本": 5, "正": 5,
        "佐": 7, "藤": 21, "田": 5, "中": 4, "村": 7, "井": 4, "高": 10, "橋": 16,
        "健": 11, "一": 1, "二": 2, "男": 7, "女": 3, "介": 4, "也": 3, "雄": 12,
        "和": 8, "幸": 8, "彦": 9, "恵": 12, "真": 10, "直": 8, "俊": 9, "浩": 11
    }
    
    def __init__(self, strokes_file: Optional[str] = None):
        """
        Args:
            strokes_file: 画数データJSONファイルのパス
        """
        self.strokes = self.DEFAULT_STROKES.copy()
        
        if strokes_file and os.path.exists(strokes_file):
            with open(strokes_file, 'r', encoding='utf-8') as f:
                external_strokes = json.load(f)
                self.strokes.update(external_strokes)
    
    def calculate(self, family_name: str, given_name: str) -> SeimeiResult:
        """
        姓名判断を計算
        
        Args:
            family_name: 姓（漢字）
            given_name: 名（漢字）
            
        Returns:
            SeimeiResult
        """
        # 各文字の画数を取得
        family_strokes = [self._get_stroke(c) for c in family_name]
        given_strokes = [self._get_stroke(c) for c in given_name]
        
        # 霊数の処理（一文字姓・名の場合）
        family_strokes_calc = family_strokes.copy()
        given_strokes_calc = given_strokes.copy()
        
        if len(family_name) == 1:
            family_strokes_calc = [1] + family_strokes_calc  # 霊数1を加算
        if len(given_name) == 1:
            given_strokes_calc = given_strokes_calc + [1]    # 霊数1を加算
        
        # 五格の計算
        tenkaku = sum(family_strokes_calc)           # 天格
        chikaku = sum(given_strokes_calc)            # 地格
        
        # 人格（姓の最後 + 名の最初）
        jinkaku = family_strokes[-1] + given_strokes[0]
        
        # 総格
        soukaku = sum(family_strokes) + sum(given_strokes)
        
        # 外格（総格 - 人格）
        gaikaku = soukaku - jinkaku
        if gaikaku <= 0:
            gaikaku = 1
        
        # 画数の詳細を辞書に
        strokes_detail = {}
        for i, c in enumerate(family_name):
            strokes_detail[f"姓{i+1}:{c}"] = family_strokes[i]
        for i, c in enumerate(given_name):
            strokes_detail[f"名{i+1}:{c}"] = given_strokes[i]
        
        return SeimeiResult(
            strokes=strokes_detail,
            tenkaku=tenkaku,
            jinkaku=jinkaku,
            chikaku=chikaku,
            gaikaku=gaikaku,
            soukaku=soukaku
        )
    
    def _get_stroke(self, char: str) -> int:
        """
        文字の画数を取得
        辞書にない場合はUnicodeストローク情報等から推定
        """
        if char in self.strokes:
            return self.strokes[char]
        
        # 未知の文字は概算（CJK統合漢字の場合）
        # 本番では外部データベースを参照
        return 10  # デフォルト値
    
    def get_number_meaning(self, number: int) -> Dict:
        """画数の意味を取得"""
        # 吉凶判定（簡易版）
        LUCKY_NUMBERS = {1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25, 29, 31, 32, 33, 35, 37, 38, 39, 41, 45, 47, 48}
        UNLUCKY_NUMBERS = {2, 4, 9, 10, 12, 14, 19, 20, 22, 26, 27, 28, 34, 36, 40, 42, 43, 44, 46, 49, 50}
        
        if number in LUCKY_NUMBERS:
            fortune = "吉"
        elif number in UNLUCKY_NUMBERS:
            fortune = "凶"
        else:
            fortune = "中"
        
        # 五行
        element_cycle = ["木", "火", "土", "金", "水"]
        element = element_cycle[(number - 1) % 5] if number > 0 else "水"
        
        return {
            "number": number,
            "fortune": fortune,
            "element": element
        }
    
    def analyze_compatibility(self, result: SeimeiResult) -> Dict:
        """五格間の相性を分析"""
        # 天格と地格のバランス
        # 人格との調和
        # など詳細な分析ロジック
        return {
            "overall": "詳細分析は実装予定"
        }
