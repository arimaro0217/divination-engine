"""
四柱推命モジュール
通変星、十二運、神殺の計算
"""
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from .sexagenary import SexagenaryCalculator
from ...core.calendar_cn import ChineseCalendar, FourPillars, Pillar
from ...models.output_schema import BaZiResult, Pillar as PillarSchema


class BaZiCalculator(SexagenaryCalculator):
    """
    四柱推命計算クラス
    干支ベースの運勢計算を行う
    """
    
    # 通変星（十神）
    # 日干から各干への関係
    TEN_GODS = {
        # (日干五行, 対象干五行, 日干陰陽==対象干陰陽) -> 通変星
        ("木", "木", True): "比肩",
        ("木", "木", False): "劫財",
        ("木", "火", True): "食神",
        ("木", "火", False): "傷官",
        ("木", "土", True): "偏財",
        ("木", "土", False): "正財",
        ("木", "金", True): "偏官",
        ("木", "金", False): "正官",
        ("木", "水", True): "偏印",
        ("木", "水", False): "印綬",
        
        ("火", "火", True): "比肩",
        ("火", "火", False): "劫財",
        ("火", "土", True): "食神",
        ("火", "土", False): "傷官",
        ("火", "金", True): "偏財",
        ("火", "金", False): "正財",
        ("火", "水", True): "偏官",
        ("火", "水", False): "正官",
        ("火", "木", True): "偏印",
        ("火", "木", False): "印綬",
        
        ("土", "土", True): "比肩",
        ("土", "土", False): "劫財",
        ("土", "金", True): "食神",
        ("土", "金", False): "傷官",
        ("土", "水", True): "偏財",
        ("土", "水", False): "正財",
        ("土", "木", True): "偏官",
        ("土", "木", False): "正官",
        ("土", "火", True): "偏印",
        ("土", "火", False): "印綬",
        
        ("金", "金", True): "比肩",
        ("金", "金", False): "劫財",
        ("金", "水", True): "食神",
        ("金", "水", False): "傷官",
        ("金", "木", True): "偏財",
        ("金", "木", False): "正財",
        ("金", "火", True): "偏官",
        ("金", "火", False): "正官",
        ("金", "土", True): "偏印",
        ("金", "土", False): "印綬",
        
        ("水", "水", True): "比肩",
        ("水", "水", False): "劫財",
        ("水", "木", True): "食神",
        ("水", "木", False): "傷官",
        ("水", "火", True): "偏財",
        ("水", "火", False): "正財",
        ("水", "土", True): "偏官",
        ("水", "土", False): "正官",
        ("水", "金", True): "偏印",
        ("水", "金", False): "印綬",
    }
    
    # 十二運（十二長生）
    # 日干の五行ごとに、地支に対応する十二運
    TWELVE_STAGES = {
        "甲": {"亥": "長生", "子": "沐浴", "丑": "冠帯", "寅": "建禄", "卯": "帝旺", "辰": "衰", "巳": "病", "午": "死", "未": "墓", "申": "絶", "酉": "胎", "戌": "養"},
        "乙": {"午": "長生", "巳": "沐浴", "辰": "冠帯", "卯": "建禄", "寅": "帝旺", "丑": "衰", "子": "病", "亥": "死", "戌": "墓", "酉": "絶", "申": "胎", "未": "養"},
        "丙": {"寅": "長生", "卯": "沐浴", "辰": "冠帯", "巳": "建禄", "午": "帝旺", "未": "衰", "申": "病", "酉": "死", "戌": "墓", "亥": "絶", "子": "胎", "丑": "養"},
        "丁": {"酉": "長生", "申": "沐浴", "未": "冠帯", "午": "建禄", "巳": "帝旺", "辰": "衰", "卯": "病", "寅": "死", "丑": "墓", "子": "絶", "亥": "胎", "戌": "養"},
        "戊": {"寅": "長生", "卯": "沐浴", "辰": "冠帯", "巳": "建禄", "午": "帝旺", "未": "衰", "申": "病", "酉": "死", "戌": "墓", "亥": "絶", "子": "胎", "丑": "養"},
        "己": {"酉": "長生", "申": "沐浴", "未": "冠帯", "午": "建禄", "巳": "帝旺", "辰": "衰", "卯": "病", "寅": "死", "丑": "墓", "子": "絶", "亥": "胎", "戌": "養"},
        "庚": {"巳": "長生", "午": "沐浴", "未": "冠帯", "申": "建禄", "酉": "帝旺", "戌": "衰", "亥": "病", "子": "死", "丑": "墓", "寅": "絶", "卯": "胎", "辰": "養"},
        "辛": {"子": "長生", "亥": "沐浴", "戌": "冠帯", "酉": "建禄", "申": "帝旺", "未": "衰", "午": "病", "巳": "死", "辰": "墓", "卯": "絶", "寅": "胎", "丑": "養"},
        "壬": {"申": "長生", "酉": "沐浴", "戌": "冠帯", "亥": "建禄", "子": "帝旺", "丑": "衰", "寅": "病", "卯": "死", "辰": "墓", "巳": "絶", "午": "胎", "未": "養"},
        "癸": {"卯": "長生", "寅": "沐浴", "丑": "冠帯", "子": "建禄", "亥": "帝旺", "戌": "衰", "酉": "病", "申": "死", "未": "墓", "午": "絶", "巳": "胎", "辰": "養"},
    }
    
    def __init__(self):
        super().__init__()
    
    def calculate(self, birth_dt: datetime) -> BaZiResult:
        """
        四柱推命を計算
        
        Args:
            birth_dt: 生年月日時（タイムゾーン付き）
            
        Returns:
            BaZiResult
        """
        # 四柱を計算（子の刻は00:00-01:00）
        four_pillars = self.calendar.calc_four_pillars(birth_dt, use_early_rat=False)
        
        # 日主（日干）
        day_master = four_pillars.day.stem
        
        # 空亡（天中殺）
        void_branches = list(self.calendar.calc_void_branches(four_pillars.day))
        
        # 通変星を計算
        ten_gods = self._calc_ten_gods(four_pillars, day_master)
        
        # 十二運を計算
        twelve_stages = self._calc_twelve_stages(four_pillars, day_master)
        
        return BaZiResult(
            four_pillars=self._convert_pillars_to_schema(four_pillars),
            void_branches=void_branches,
            day_master=day_master,
            ten_gods=ten_gods,
            twelve_stages=twelve_stages
        )
    
    def _convert_pillars_to_schema(self, fp: FourPillars):
        """FourPillarsを出力スキーマの形式に変換"""
        from ...models.output_schema import FourPillars as FourPillarsSchema
        
        return FourPillarsSchema(
            year=PillarSchema(heavenly_stem=fp.year.stem, earthly_branch=fp.year.branch),
            month=PillarSchema(heavenly_stem=fp.month.stem, earthly_branch=fp.month.branch),
            day=PillarSchema(heavenly_stem=fp.day.stem, earthly_branch=fp.day.branch),
            hour=PillarSchema(heavenly_stem=fp.hour.stem, earthly_branch=fp.hour.branch)
        )
    
    def _calc_ten_gods(self, fp: FourPillars, day_master: str) -> Dict[str, str]:
        """
        通変星を計算
        日干から見た各柱の天干の関係
        """
        result = {}
        
        day_element = self.get_stem_element(day_master)
        day_yy = self.get_stem_yin_yang(day_master)
        
        for pillar_name, pillar in [("年", fp.year), ("月", fp.month), ("時", fp.hour)]:
            stem = pillar.stem
            stem_element = self.get_stem_element(stem)
            stem_yy = self.get_stem_yin_yang(stem)
            
            is_same_yy = (day_yy == stem_yy)
            key = (day_element, stem_element, is_same_yy)
            
            god = self.TEN_GODS.get(key, "不明")
            result[f"{pillar_name}干"] = god
        
        return result
    
    def _calc_twelve_stages(self, fp: FourPillars, day_master: str) -> Dict[str, str]:
        """
        十二運を計算
        日干から見た各柱の地支の状態
        """
        result = {}
        
        stages_map = self.TWELVE_STAGES.get(day_master, {})
        
        for pillar_name, pillar in [("年", fp.year), ("月", fp.month), ("日", fp.day), ("時", fp.hour)]:
            branch = pillar.branch
            stage = stages_map.get(branch, "不明")
            result[f"{pillar_name}支"] = stage
        
        return result
    
    def get_day_master_strength(self, four_pillars: FourPillars) -> str:
        """
        日主の強弱を判定（簡易版）
        """
        day_master = four_pillars.day.stem
        day_element = self.get_stem_element(day_master)
        
        # 月支の蔵干で令（旺相）を判定
        month_branch = four_pillars.month.branch
        month_hidden = self.get_hidden_stems(month_branch)
        
        support_count = 0
        
        # 月令の判定
        for hidden in month_hidden:
            hidden_element = self.get_stem_element(hidden)
            if hidden_element == day_element:
                support_count += 2
            # 印（生じる五行）
            elif self._generates(hidden_element, day_element):
                support_count += 1
        
        # 他の柱からのサポート
        for pillar in [four_pillars.year, four_pillars.month, four_pillars.hour]:
            if self.get_stem_element(pillar.stem) == day_element:
                support_count += 1
            if self.get_branch_element(pillar.branch) == day_element:
                support_count += 1
        
        if support_count >= 4:
            return "身強"
        elif support_count <= 2:
            return "身弱"
        else:
            return "中和"
    
    def _generates(self, element1: str, element2: str) -> bool:
        """五行の相生関係を判定"""
        generation = {
            "木": "火", "火": "土", "土": "金", "金": "水", "水": "木"
        }
        return generation.get(element1) == element2
