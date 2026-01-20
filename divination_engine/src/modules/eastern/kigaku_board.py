"""
九星気学 - 方位盤生成と吉凶判定

このモジュールは方位盤（年盤・月盤・日盤・時盤）の生成と、
吉凶方位の判定を行います。
"""

import sys
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ...const import kigaku_const as kc

# Windows環境でのUTF-8出力対応（安全版）
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ============================================
# データクラス
# ============================================

@dataclass
class DirectionInfo:
    """方位の情報"""
    direction: str  # "N", "NE", etc.
    name_jp: str  # "北", "北東", etc.
    star: int  # 九星番号（1-9）
    star_name: str  # 九星名
    element: str  # 五行
    status: str  # 吉凶ステータス
    notes: List[str]  # 特記事項（五黄殺、暗剣殺など）


@dataclass
class KigakuBoardData:
    """方位盤データ"""
    center_star: int  # 中宮の星
    directions: Dict[str, DirectionInfo]  # 各方位の情報


# ============================================
# KigakuBoard: 方位盤生成クラス
# ============================================

class KigakuBoard:
    """
    方位盤（年盤・月盤・日盤・時盤）を生成するクラス
    """
    
    @staticmethod
    def create_board(center_star: int) -> Dict[str, int]:
        """
        中宮の星から8方位への飛泊を計算
        
        Args:
            center_star: 中宮に配置する星（1-9）
        
        Returns:
            各方位の星のマッピング
        """
        # 九星と宮の対応（後天定位）
        # 1:坎(N), 2:坤(SW), 3:震(E), 4:巽(SE), 5:中宮, 
        # 6:乾(NW), 7:兌(W), 8:艮(NE), 9:離(S)
        
        board = {}
        
        # 中宮からの飛泊計算
        # 後天定位の宮に、中宮の星からの相対位置で星を配置
        for direction, palace in kc.DIRECTION_TO_PALACE.items():
            # 宮の位置（1-9）から中宮（5）への距離
            offset = palace - 5
            
            # 中宮の星から距離だけずらした星を配置
            star = ((center_star - 1) + offset) % 9 + 1
            board[direction] = star
        
        return board
    
    @staticmethod
    def get_opposite_direction(direction: str) -> str:
        """
        対中方位を取得
        
        Args:
            direction: 方位（"N", "NE", etc.）
        
        Returns:
            対中方位
        """
        return kc.OPPOSITE_DIRECTION.get(direction, direction)


# ============================================
# DirectionJudge: 吉凶判定クラス
# ============================================

class DirectionJudge:
    """
    方位の吉凶を判定するクラス
    """
    
    @staticmethod
    def find_goo_satsu(board: Dict[str, int]) -> List[str]:
        """
        五黄殺の方位を見つける
        
        五黄土星が回座する方位
        
        Args:
            board: 方位盤
        
        Returns:
            五黄殺の方位リスト
        """
        goo_satsu_directions = []
        for direction, star in board.items():
            if star == 5:  # 五黄土星
                goo_satsu_directions.append(direction)
        return goo_satsu_directions
    
    @staticmethod
    def find_anken_satsu(board: Dict[str, int]) -> List[str]:
        """
        暗剣殺の方位を見つける
        
        五黄土星の対中方位
        
        Args:
            board: 方位盤
        
        Returns:
            暗剣殺の方位リスト
        """
        goo_satsu_dirs = DirectionJudge.find_goo_satsu(board)
        anken_satsu_directions = []
        
        for direction in goo_satsu_dirs:
            opposite = KigakuBoard.get_opposite_direction(direction)
            anken_satsu_directions.append(opposite)
        
        return anken_satsu_directions
    
    @staticmethod
    def find_saiha(year_branch: str = None, month_branch: str = None, 
                   day_branch: str = None) -> List[str]:
        """
        歳破・月破・日破の方位を見つける
        
        太歳と対中になる方位
        
        Args:
            year_branch: 年支
            month_branch: 月支
            day_branch: 日支
        
        Returns:
            破の方位リスト
        """
        # 地支と方位の対応（簡易版）
        branch_to_direction = {
            "子": "N",
            "丑": "NE",
            "寅": "NE",
            "卯": "E",
            "辰": "SE",
            "巳": "SE",
            "午": "S",
            "未": "SW",
            "申": "SW",
            "酉": "W",
            "戌": "NW",
            "亥": "NW"
        }
        
        saiha_directions = []
        
        if year_branch and year_branch in branch_to_direction:
            direction = branch_to_direction[year_branch]
            opposite = KigakuBoard.get_opposite_direction(direction)
            saiha_directions.append(opposite)
        
        return saiha_directions
    
    @staticmethod
    def judge_lucky_directions(user_year_star: int, board: Dict[str, int]) -> Tuple[List[str], str]:
        """
        吉方位を判定
        
        本命星と相生関係にある星の方位
        
        Args:
            user_year_star: ユーザーの本命星
            board: 方位盤
        
        Returns:
            (吉方位リスト, 最大吉方)
        """
        user_element = kc.NINE_STAR_ELEMENTS[user_year_star]
        lucky_dirs = []
        best_dir = None
        
        for direction, star in board.items():
            star_element = kc.NINE_STAR_ELEMENTS[star]
            
            # 相生関係をチェック
            # 自分が生む（洩気）は吉だが弱い
            if kc.SHENG_CYCLE.get(user_element) == star_element:
                lucky_dirs.append(direction)
            
            # 相手が自分を生む（受生）は最大吉
            elif kc.SHENG_CYCLE.get(star_element) == user_element:
                lucky_dirs.append(direction)
                if not best_dir:
                    best_dir = direction
        
        return lucky_dirs, best_dir


# ============================================
# BoardAnalyzer: 総合分析クラス
# ============================================

class BoardAnalyzer:
    """
    年月日時の全方位盤を分析し、総合的な吉凶を判定
    """
    
    def __init__(self):
        """初期化"""
        self.board_gen = KigakuBoard()
        self.judge = DirectionJudge()
    
    def analyze_direction(
        self,
        direction: str,
        year_board: Dict[str, int],
        month_board: Dict[str, int],
        day_board: Dict[str, int],
        user_year_star: int,
        year_branch: str = None
    ) -> DirectionInfo:
        """
        特定方位の吉凶を総合分析
        
        Args:
            direction: 方位
            year_board, month_board, day_board: 各盤
            user_year_star: ユーザーの本命星
            year_branch: 年支
        
        Returns:
            DirectionInfo
        """
        # その方位の星（日盤を優先）
        day_star = day_board.get(direction, 5)
        month_star = month_board.get(direction, 5)
        year_star = year_board.get(direction, 5)
        
        # 凶方位判定
        notes = []
        status = "neutral"
        
        # 五黄殺チェック（年・月・日）
        if year_star == 5:
            notes.append("年五黄殺")
            status = "worst"
        if month_star == 5:
            notes.append("月五黄殺")
            status = "worst"
        if day_star == 5:
            notes.append("日五黄殺")
            status = "worst"
        
        # 暗剣殺チェック
        goo_satsu_year = self.judge.find_goo_satsu(year_board)
        goo_satsu_month = self.judge.find_goo_satsu(month_board)
        goo_satsu_day = self.judge.find_goo_satsu(day_board)
        
        for goo_dir in goo_satsu_year:
            if direction == self.board_gen.get_opposite_direction(goo_dir):
                notes.append("年暗剣殺")
                status = "worst"
        
        for goo_dir in goo_satsu_month:
            if direction == self.board_gen.get_opposite_direction(goo_dir):
                notes.append("月暗剣殺")
                status = "worst"
        
        for goo_dir in goo_satsu_day:
            if direction == self.board_gen.get_opposite_direction(goo_dir):
                notes.append("日暗剣殺")
                status = "worst"
        
        # 歳破チェック
        if year_branch:
            saiha_dirs = self.judge.find_saiha(year_branch=year_branch)
            if direction in saiha_dirs:
                notes.append("歳破")
                status = "bad"
        
        # 吉方位チェック（凶がない場合のみ）
        if status == "neutral":
            lucky_dirs, best_dir = self.judge.judge_lucky_directions(user_year_star, day_board)
            if direction == best_dir:
                notes.append("最大吉方")
                status = "best"
            elif direction in lucky_dirs:
                notes.append("吉方")
                status = "good"
        
        return DirectionInfo(
            direction=direction,
            name_jp=kc.DIRECTION_NAMES_JP[direction],
            star=day_star,
            star_name=kc.NINE_STAR_NAMES[day_star],
            element=kc.NINE_STAR_ELEMENTS[day_star],
            status=status,
            notes=notes
        )
    
    def get_best_directions(
        self,
        year_board: Dict[str, int],
        month_board: Dict[str, int],
        day_board: Dict[str, int],
        user_year_star: int,
        year_branch: str = None
    ) -> List[str]:
        """
        最適な方位のリストを取得
        
        Returns:
            方位のリスト（吉方位のみ）
        """
        best_directions = []
        
        for direction in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
            info = self.analyze_direction(
                direction, year_board, month_board, day_board,
                user_year_star, year_branch
            )
            
            if info.status in ["best", "good"]:
                best_directions.append(direction)
        
        return best_directions
    
    def get_avoid_directions(
        self,
        year_board: Dict[str, int],
        month_board: Dict[str, int],
        day_board: Dict[str, int],
        user_year_star: int,
        year_branch: str = None
    ) -> List[str]:
        """
        避けるべき方位のリストを取得
        
        Returns:
            方位のリスト（凶方位のみ）
        """
        avoid_directions = []
        
        for direction in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
            info = self.analyze_direction(
                direction, year_board, month_board, day_board,
                user_year_star, year_branch
            )
            
            if info.status in ["bad", "worst"]:
                avoid_directions.append(direction)
        
        return avoid_directions
