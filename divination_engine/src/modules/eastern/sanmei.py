"""
算命学（Sanmeigaku）計算エンジン

人体星図（陽占）、宇宙盤、エネルギースコアなどを算出し、
Webフロントエンドでの可視化に対応したJSON構造を出力します。

主要クラス:
- SanmeiCalculator: メイン計算クラス
- JintaiSeizu: 人体星図の計算
- UchuBan: 宇宙盤の幾何学計算
- EnergyScore: 五行エネルギースコア
"""

import sys
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

from .sexagenary import SexagenaryCalculator
from ...core.calendar_cn import ChineseCalendar
from ...const import sanmei_const as sc

# Windows環境でのUTF-8出力対応（安全版）
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ============================================
# データクラス定義
# ============================================

@dataclass
class JintaiSlot:
    """人体星図の1スロット"""
    position: str  # "north", "center", etc.
    star_type: str  # "main_star" or "sub_star"
    star_name: str  # 星の名称
    meaning: str  # この位置の意味
    score: Optional[int] = None  # 従星のスコア（0-12）


@dataclass
class UchuBanPoint:
    """宇宙盤上の点（年・月・日の干支位置）"""
    label: str  # "Year", "Month", "Day"
    ganzhi: str  # 干支
    angle: float  # 角度（度）
    x: float  # 正規化されたX座標（-1.0 ~ 1.0）
    y: float  # 正規化されたY座標（-1.0 ~ 1.0）


# ============================================
# JintaiSeizu: 人体星図クラス
# ============================================

class JintaiSeizu:
    """
    人体星図（陽占）の計算クラス
    
    8つのスロットに十大主星と十二大従星を配置します。
    """
    
    @staticmethod
    def calculate_main_star(day_stem: str, target_stem: str) -> str:
        """
        十大主星を計算
        
        Args:
            day_stem: 日干
            target_stem: 対象の天干
        
        Returns:
            主星の名称
        """
        if day_stem not in sc.STEM_WUXING or target_stem not in sc.STEM_WUXING:
            raise ValueError(f"無効な天干: {day_stem} または {target_stem}")
        
        day_element, day_yinyang = sc.STEM_WUXING[day_stem]
        target_element, target_yinyang = sc.STEM_WUXING[target_stem]
        
        key = (day_element, target_element, day_yinyang, target_yinyang)
        
        if key in sc.MAIN_STAR_TABLE:
            return sc.MAIN_STAR_TABLE[key]
        else:
            raise ValueError(f"主星テーブルにキーが見つかりません: {key}")
    
    @staticmethod
    def calculate_sub_star(day_stem: str, target_branch: str) -> Tuple[str, int]:
        """
        十二大従星を計算
        
        Args:
            day_stem: 日干
            target_branch: 対象の地支
        
        Returns:
            (従星の名称, エネルギー点数)
        """
        if day_stem not in sc.STEM_WUXING:
            raise ValueError(f"無効な天干: {day_stem}")
        if target_branch not in sc.BRANCH_WUXING:
            raise ValueError(f"無効な地支: {target_branch}")
        
        day_element, day_yinyang = sc.STEM_WUXING[day_stem]
        
        # 長生位置を取得
        changshen_key = (day_element, day_yinyang)
        if changshen_key not in sc.CHANGSHEN_POSITIONS:
            raise ValueError(f"長生位置が見つかりません: {changshen_key}")
        
        changshen_branch = sc.CHANGSHEN_POSITIONS[changshen_key]
        changshen_index = sc.BRANCHES.index(changshen_branch)
        target_index = sc.BRANCHES.index(target_branch)
        
        # 長生からの距離を計算
        if day_yinyang == "陽":
            # 陽干は順行
            distance = (target_index - changshen_index) % 12
        else:
            # 陰干は逆行
            distance = (changshen_index - target_index) % 12
        
        # 十二運を取得
        juniunsei = sc.TWELVE_POSITIONS[distance]
        
        # 従星に変換
        sub_star = sc.JUNIUNSEI_TO_SUBSTAR[juniunsei]
        score = sc.SUBSTAR_SCORES[sub_star]
        
        return sub_star, score
    
    @staticmethod
    def create_jintai_seizu(
        year_stem: str, year_branch: str,
        month_stem: str, month_branch: str,
        day_stem: str, day_branch: str
    ) -> List[JintaiSlot]:
        """
        人体星図の8スロットを作成
        
        配置:
        - 頭（北）: 年干 vs 日干（主星）
        - 左肩: 年支 vs 日干（従星）
        - 右手: 月干 vs 日干（主星）
        - 胸（中央）: 月支蔵干 vs 日干（主星）
        - 左手: 日支蔵干 vs 日干（主星）
        - 腹（南）: 年支蔵干 vs 日干（主星）
        - 右足: 日支 vs 日干（従星）
        - 左足: 月支 vs 日干（従星）
        
        Args:
            year_stem, year_branch: 年柱の干支
            month_stem, month_branch: 月柱の干支
            day_stem, day_branch: 日柱の干支
        
        Returns:
            JintaiSlotのリスト
        """
        slots = []
        
        # 蔵干を取得
        month_zanggan = sc.get_zanggan_hongen(month_branch)
        day_zanggan = sc.get_zanggan_hongen(day_branch)
        year_zanggan = sc.get_zanggan_hongen(year_branch)
        
        # 頭（北）: 年干 vs 日干
        north_star = JintaiSeizu.calculate_main_star(day_stem, year_stem)
        slots.append(JintaiSlot(
            position=sc.JintaiPosition.NORTH,
            star_type="main_star",
            star_name=north_star,
            meaning=sc.JINTAI_POSITION_MEANINGS[sc.JintaiPosition.NORTH]
        ))
        
        # 左肩: 年支 vs 日干
        left_shoulder_star, left_shoulder_score = JintaiSeizu.calculate_sub_star(day_stem, year_branch)
        slots.append(JintaiSlot(
            position=sc.JintaiPosition.LEFT_SHOULDER,
            star_type="sub_star",
            star_name=left_shoulder_star,
            meaning=sc.JINTAI_POSITION_MEANINGS[sc.JintaiPosition.LEFT_SHOULDER],
            score=left_shoulder_score
        ))
        
        # 右手: 月干 vs 日干
        right_hand_star = JintaiSeizu.calculate_main_star(day_stem, month_stem)
        slots.append(JintaiSlot(
            position=sc.JintaiPosition.RIGHT_HAND,
            star_type="main_star",
            star_name=right_hand_star,
            meaning=sc.JINTAI_POSITION_MEANINGS[sc.JintaiPosition.RIGHT_HAND]
        ))
        
        # 胸（中央）: 月支蔵干 vs 日干
        center_star = JintaiSeizu.calculate_main_star(day_stem, month_zanggan)
        slots.append(JintaiSlot(
            position=sc.JintaiPosition.CENTER,
            star_type="main_star",
            star_name=center_star,
            meaning=sc.JINTAI_POSITION_MEANINGS[sc.JintaiPosition.CENTER]
        ))
        
        # 左手: 日支蔵干 vs 日干
        left_hand_star = JintaiSeizu.calculate_main_star(day_stem, day_zanggan)
        slots.append(JintaiSlot(
            position=sc.JintaiPosition.LEFT_HAND,
            star_type="main_star",
            star_name=left_hand_star,
            meaning=sc.JINTAI_POSITION_MEANINGS[sc.JintaiPosition.LEFT_HAND]
        ))
        
        # 腹（南）: 年支蔵干 vs 日干
        south_star = JintaiSeizu.calculate_main_star(day_stem, year_zanggan)
        slots.append(JintaiSlot(
            position=sc.JintaiPosition.SOUTH,
            star_type="main_star",
            star_name=south_star,
            meaning=sc.JINTAI_POSITION_MEANINGS[sc.JintaiPosition.SOUTH]
        ))
        
        # 右足: 日支 vs 日干
        right_foot_star, right_foot_score = JintaiSeizu.calculate_sub_star(day_stem, day_branch)
        slots.append(JintaiSlot(
            position=sc.JintaiPosition.RIGHT_FOOT,
            star_type="sub_star",
            star_name=right_foot_star,
            meaning=sc.JINTAI_POSITION_MEANINGS[sc.JintaiPosition.RIGHT_FOOT],
            score=right_foot_score
        ))
        
        # 左足: 月支 vs 日干
        left_foot_star, left_foot_score = JintaiSeizu.calculate_sub_star(day_stem, month_branch)
        slots.append(JintaiSlot(
            position=sc.JintaiPosition.LEFT_FOOT,
            star_type="sub_star",
            star_name=left_foot_star,
            meaning=sc.JINTAI_POSITION_MEANINGS[sc.JintaiPosition.LEFT_FOOT],
            score=left_foot_score
        ))
        
        return slots


# ============================================
# UchuBan: 宇宙盤クラス
# ============================================

class UchuBan:
    """
    宇宙盤（Uchu-ban）の幾何学計算クラス
    
    60干支を円形に配置し、年・月・日の三角形を描画するための座標を計算します。
    """
    
    @staticmethod
    def ganzhi_to_coordinates(ganzhi: str, radius: float = 1.0) -> Tuple[float, float]:
        """
        干支を円形座標に変換
        
        Args:
            ganzhi: 干支（例: "甲子"）
            radius: 円の半径（デフォルト1.0で正規化）
        
        Returns:
            (x, y) 座標
        """
        angle_deg = sc.get_ganzhi_angle(ganzhi)
        # 度をラジアンに変換
        angle_rad = math.radians(angle_deg)
        
        # 極座標から直交座標へ変換
        x = radius * math.cos(angle_rad)
        y = radius * math.sin(angle_rad)
        
        return x, y
    
    @staticmethod
    def calculate_triangle_area(p1: Tuple[float, float], 
                                 p2: Tuple[float, float], 
                                 p3: Tuple[float, float]) -> float:
        """
        三角形の面積を計算（外積法）
        
        Args:
            p1, p2, p3: 3つの頂点座標
        
        Returns:
            面積
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        # 外積を使った面積計算
        area = abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)
        return area
    
    @staticmethod
    def determine_pattern_type(area: float) -> str:
        """
        三角形の面積から行動パターンを分類
        
        Args:
            area: 三角形の面積
        
        Returns:
            パターン分類
        """
        # 面積の閾値で分類
        if area < 0.5:
            return "小領域型（集中型）"
        elif area < 1.0:
            return "中領域型（バランス型）"
        elif area < 1.5:
            return "大領域型（拡散型）"
        else:
            return "超大領域型（多方面型）"
    
    @staticmethod
    def create_uchuban(
        year_ganzhi: str,
        month_ganzhi: str,
        day_ganzhi: str
    ) -> Dict:
        """
        宇宙盤データを作成
        
        Args:
            year_ganzhi: 年干支
            month_ganzhi: 月干支
            day_ganzhi: 日干支
        
        Returns:
            宇宙盤データの辞書
        """
        # 各干支の座標を計算
        year_x, year_y = UchuBan.ganzhi_to_coordinates(year_ganzhi)
        month_x, month_y = UchuBan.ganzhi_to_coordinates(month_ganzhi)
        day_x, day_y = UchuBan.ganzhi_to_coordinates(day_ganzhi)
        
        # 三点の座標リスト
        points = [
            UchuBanPoint(
                label="Year",
                ganzhi=year_ganzhi,
                angle=sc.get_ganzhi_angle(year_ganzhi),
                x=year_x,
                y=year_y
            ),
            UchuBanPoint(
                label="Month",
                ganzhi=month_ganzhi,
                angle=sc.get_ganzhi_angle(month_ganzhi),
                x=month_x,
                y=month_y
            ),
            UchuBanPoint(
                label="Day",
                ganzhi=day_ganzhi,
                angle=sc.get_ganzhi_angle(day_ganzhi),
                x=day_x,
                y=day_y
            )
        ]
        
        # 三角形の面積を計算
        area = UchuBan.calculate_triangle_area(
            (year_x, year_y),
            (month_x, month_y),
            (day_x, day_y)
        )
        
        # パターン分類
        pattern_type = UchuBan.determine_pattern_type(area)
        
        return {
            "points": points,
            "area_size": round(area, 4),
            "pattern_type": pattern_type,
            "radius": 1.0
        }


# ============================================
# EnergyScore: エネルギースコアクラス
# ============================================

class EnergyScore:
    """
    数理法・気図法の計算クラス
    
    五行エネルギー値を算出します。
    """
    
    @staticmethod
    def calculate_energy(
        year_stem: str, year_branch: str,
        month_stem: str, month_branch: str,
        day_stem: str, day_branch: str,
        hour_stem: Optional[str] = None, hour_branch: Optional[str] = None
    ) -> Dict[str, int]:
        """
        五行エネルギーを計算
        
        天干 = 1点
        地支 = 本元3点 + 中元2点 + 初元1点
        
        Args:
            year_stem, year_branch: 年柱
            month_stem, month_branch: 月柱
            day_stem, day_branch: 日柱
            hour_stem, hour_branch: 時柱（オプション）
        
        Returns:
            五行別のエネルギー点数
        """
        energy = {
            sc.WuXing.WOOD: 0,
            sc.WuXing.FIRE: 0,
            sc.WuXing.EARTH: 0,
            sc.WuXing.METAL: 0,
            sc.WuXing.WATER: 0,
        }
        
        # 天干のエネルギー加算
        for stem in [year_stem, month_stem, day_stem]:
            if stem:
                element, _ = sc.STEM_WUXING[stem]
                energy[element] += sc.STEM_ENERGY_SCORE
        
        if hour_stem:
            element, _ = sc.STEM_WUXING[hour_stem]
            energy[element] += sc.STEM_ENERGY_SCORE
        
        # 地支のエネルギー加算（蔵干）
        for branch in [year_branch, month_branch, day_branch]:
            if branch:
                zanggan = sc.SANMEI_ZANGGAN[branch]
                
                # 本元
                if zanggan["本元"]:
                    element, _ = sc.STEM_WUXING[zanggan["本元"]]
                    energy[element] += sc.BRANCH_ENERGY_SCORES["本元"]
                
                # 中元
                if zanggan["中元"]:
                    element, _ = sc.STEM_WUXING[zanggan["中元"]]
                    energy[element] += sc.BRANCH_ENERGY_SCORES["中元"]
                
                # 初元
                if zanggan["初元"]:
                    element, _ = sc.STEM_WUXING[zanggan["初元"]]
                    energy[element] += sc.BRANCH_ENERGY_SCORES["初元"]
        
        if hour_branch:
            zanggan = sc.SANMEI_ZANGGAN[hour_branch]
            if zanggan["本元"]:
                element, _ = sc.STEM_WUXING[zanggan["本元"]]
                energy[element] += sc.BRANCH_ENERGY_SCORES["本元"]
            if zanggan["中元"]:
                element, _ = sc.STEM_WUXING[zanggan["中元"]]
                energy[element] += sc.BRANCH_ENERGY_SCORES["中元"]
            if zanggan["初元"]:
                element, _ = sc.STEM_WUXING[zanggan["初元"]]
                energy[element] += sc.BRANCH_ENERGY_SCORES["初元"]
        
        return energy


# ============================================
# SanmeiCalculator: メインクラス
# ============================================

class SanmeiCalculator(SexagenaryCalculator):
    """
    算命学計算メインクラス
    
    すべての算命学要素を統合し、JSON出力を提供します。
    """
    
    def __init__(self, birth_datetime: datetime, latitude: float, longitude: float):
        """
        初期化
        
        Args:
            birth_datetime: 生年月日時
            latitude: 緯度
            longitude: 経度
        """
        super().__init__()
        self.birth_datetime = birth_datetime
        self.latitude = latitude
        self.longitude = longitude
        
        # 中国暦の計算
        self.calendar = ChineseCalendar()
        self.four_pillars = self.calendar.calc_four_pillars(birth_datetime)
    
    def get_tenchusatsu_info(self) -> Dict[str, any]:
        """
        天中殺情報を取得
        
        Returns:
            天中殺の詳細情報
        """
        year_branch = self.four_pillars.year.branch
        month_branch = self.four_pillars.month.branch
        day_branch = self.four_pillars.day.branch
        
        # 年支から天中殺のタイプを判定
        tenchusatsu_type = sc.get_tenchusatsu_type(year_branch)
        tenchusatsu_branches = sc.TENCHUSATSU_TYPES[tenchusatsu_type]
        
        # 宿命天中殺の判定
        shukumei_tenchusatsu = []
        
        # 生月中殺: 月支が天中殺に含まれる
        if month_branch in tenchusatsu_branches:
            shukumei_tenchusatsu.append("生月中殺")
        
        # 生日中殺: 日支が天中殺に含まれる
        if day_branch in tenchusatsu_branches:
            shukumei_tenchusatsu.append("生日中殺")
        
        return {
            "type": tenchusatsu_type,
            "branches": tenchusatsu_branches,
            "shukumei": shukumei_tenchusatsu if shukumei_tenchusatsu else None
        }
    
    def get_abnormal_ganzhi_info(self) -> List[str]:
        """
        異常干支情報を取得
        
        Returns:
            異常干支のリスト
        """
        abnormal_list = []
        
        year_ganzhi = f"{self.four_pillars.year.stem}{self.four_pillars.year.branch}"
        month_ganzhi = f"{self.four_pillars.month.stem}{self.four_pillars.month.branch}"
        day_ganzhi = f"{self.four_pillars.day.stem}{self.four_pillars.day.branch}"
        
        # 通常異常の判定
        for label, ganzhi in [("年柱", year_ganzhi), ("月柱", month_ganzhi), ("日柱", day_ganzhi)]:
            if sc.is_normal_abnormal(ganzhi):
                abnormal_list.append(f"{label}が通常異常干支（{ganzhi}）")
        
        # 暗合異常の判定
        ganzhi_pairs = [
            ("年柱-月柱", year_ganzhi, month_ganzhi),
            ("年柱-日柱", year_ganzhi, day_ganzhi),
            ("月柱-日柱", month_ganzhi, day_ganzhi),
        ]
        
        for label, gz1, gz2 in ganzhi_pairs:
            if sc.is_angoui_abnormal(gz1, gz2):
                abnormal_list.append(f"{label}が暗合異常（{gz1}-{gz2}）")
        
        return abnormal_list if abnormal_list else None
    
    def get_full_analysis(self) -> Dict:
        """
        完全な算命学分析結果を取得
        
        Returns:
            全分析結果のJSON形式辞書
        """
        # 基本情報
        year_ganzhi = f"{self.four_pillars.year.stem}{self.four_pillars.year.branch}"
        month_ganzhi = f"{self.four_pillars.month.stem}{self.four_pillars.month.branch}"
        day_ganzhi = f"{self.four_pillars.day.stem}{self.four_pillars.day.branch}"
        
        hour_ganzhi = None
        if self.four_pillars.hour:
            hour_ganzhi = f"{self.four_pillars.hour.stem}{self.four_pillars.hour.branch}"
        
        # 人体星図
        jintai_slots = JintaiSeizu.create_jintai_seizu(
            self.four_pillars.year.stem, self.four_pillars.year.branch,
            self.four_pillars.month.stem, self.four_pillars.month.branch,
            self.four_pillars.day.stem, self.four_pillars.day.branch
        )
        
        # 宇宙盤
        uchuban_data = UchuBan.create_uchuban(
            year_ganzhi, month_ganzhi, day_ganzhi
        )
        
        # エネルギースコア
        hour_stem = self.four_pillars.hour.stem if self.four_pillars.hour else None
        hour_branch = self.four_pillars.hour.branch if self.four_pillars.hour else None
        
        energy = EnergyScore.calculate_energy(
            self.four_pillars.year.stem, self.four_pillars.year.branch,
            self.four_pillars.month.stem, self.four_pillars.month.branch,
            self.four_pillars.day.stem, self.four_pillars.day.branch,
            hour_stem, hour_branch
        )
        
        # 天中殺情報
        tenchusatsu = self.get_tenchusatsu_info()
        
        # 異常干支
        abnormal = self.get_abnormal_ganzhi_info()
        
        return {
            "basic": {
                "birth_datetime": self.birth_datetime.isoformat(),
                "year_ganzhi": year_ganzhi,
                "month_ganzhi": month_ganzhi,
                "day_ganzhi": day_ganzhi,
                "hour_ganzhi": hour_ganzhi,
                "year_stem": self.four_pillars.year.stem,
                "year_branch": self.four_pillars.year.branch,
                "month_stem": self.four_pillars.month.stem,
                "month_branch": self.four_pillars.month.branch,
                "day_stem": self.four_pillars.day.stem,
                "day_branch": self.four_pillars.day.branch,
            },
            "jintai_seizu": [
                {
                    "position": slot.position,
                    "star_type": slot.star_type,
                    "star_name": slot.star_name,
                    "meaning": slot.meaning,
                    "score": slot.score
                }
                for slot in jintai_slots
            ],
            "uchuban": {
                "points": [
                    {
                        "label": p.label,
                        "ganzhi": p.ganzhi,
                        "angle": p.angle,
                        "x": p.x,
                        "y": p.y
                    }
                    for p in uchuban_data["points"]
                ],
                "area_size": uchuban_data["area_size"],
                "pattern_type": uchuban_data["pattern_type"],
                "radius": uchuban_data["radius"]
            },
            "energy_score": energy,
            "tenchusatsu": tenchusatsu,
            "special_notes": abnormal
        }
