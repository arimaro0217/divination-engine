"""
干支計算モジュール（基底クラス）
六十干支の計算を担当
"""
from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from ...core.calendar_cn import ChineseCalendar, FourPillars, Pillar
from ...core.time_manager import TimeManager
from ...models.output_schema import SexagenaryResult, Pillar as PillarSchema


class SexagenaryCalculator:
    """
    干支計算クラス
    四柱推命・算命学の基底となる干支計算を提供
    """
    
    # 五行
    FIVE_ELEMENTS = ["木", "火", "土", "金", "水"]
    
    # 天干の五行
    STEM_ELEMENTS = {
        "甲": "木", "乙": "木",
        "丙": "火", "丁": "火",
        "戊": "土", "己": "土",
        "庚": "金", "辛": "金",
        "壬": "水", "癸": "水"
    }
    
    # 天干の陰陽
    STEM_YIN_YANG = {
        "甲": "陽", "乙": "陰",
        "丙": "陽", "丁": "陰",
        "戊": "陽", "己": "陰",
        "庚": "陽", "辛": "陰",
        "壬": "陽", "癸": "陰"
    }
    
    # 地支の五行
    BRANCH_ELEMENTS = {
        "子": "水", "丑": "土", "寅": "木", "卯": "木",
        "辰": "土", "巳": "火", "午": "火", "未": "土",
        "申": "金", "酉": "金", "戌": "土", "亥": "水"
    }
    
    # 地支の陰陽
    BRANCH_YIN_YANG = {
        "子": "陽", "丑": "陰", "寅": "陽", "卯": "陰",
        "辰": "陽", "巳": "陰", "午": "陽", "未": "陰",
        "申": "陽", "酉": "陰", "戌": "陽", "亥": "陰"
    }
    
    # 地支の蔵干（内包する天干）
    HIDDEN_STEMS = {
        "子": ["癸"],
        "丑": ["己", "癸", "辛"],
        "寅": ["甲", "丙", "戊"],
        "卯": ["乙"],
        "辰": ["戊", "乙", "癸"],
        "巳": ["丙", "庚", "戊"],
        "午": ["丁", "己"],
        "未": ["己", "丁", "乙"],
        "申": ["庚", "壬", "戊"],
        "酉": ["辛"],
        "戌": ["戊", "辛", "丁"],
        "亥": ["壬", "甲"]
    }
    
    # 六十干支表
    SEXAGENARY_CYCLE = [
        "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
        "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
        "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
        "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
        "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
        "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"
    ]
    
    def __init__(self):
        self.calendar = ChineseCalendar()
    
    def calculate(self, birth_dt: datetime) -> SexagenaryResult:
        """
        干支を計算
        
        Args:
            birth_dt: 生年月日時（タイムゾーン付き）
            
        Returns:
            SexagenaryResult
        """
        # 四柱を計算（子の刻は00:00-01:00）
        four_pillars = self.calendar.calc_four_pillars(birth_dt, use_early_rat=False)
        
        # 年干支の六十干支番号
        year_sexagenary = self._get_sexagenary_number(four_pillars.year)
        
        return SexagenaryResult(
            four_pillars=self._convert_pillars(four_pillars),
            sexagenary_year=year_sexagenary
        )
    
    def _convert_pillars(self, fp: FourPillars) -> Dict:
        """FourPillarsをスキーマ形式に変換"""
        return {
            "year": PillarSchema(
                heavenly_stem=fp.year.stem,
                earthly_branch=fp.year.branch
            ),
            "month": PillarSchema(
                heavenly_stem=fp.month.stem,
                earthly_branch=fp.month.branch
            ),
            "day": PillarSchema(
                heavenly_stem=fp.day.stem,
                earthly_branch=fp.day.branch
            ),
            "hour": PillarSchema(
                heavenly_stem=fp.hour.stem,
                earthly_branch=fp.hour.branch
            )
        }
    
    def _get_sexagenary_number(self, pillar: Pillar) -> int:
        """干支から六十干支番号（1-60）を取得"""
        full = pillar.full
        try:
            return self.SEXAGENARY_CYCLE.index(full) + 1
        except ValueError:
            return 0
    
    def get_stem_element(self, stem: str) -> str:
        """天干の五行を取得"""
        return self.STEM_ELEMENTS.get(stem, "")
    
    def get_branch_element(self, branch: str) -> str:
        """地支の五行を取得"""
        return self.BRANCH_ELEMENTS.get(branch, "")
    
    def get_hidden_stems(self, branch: str) -> list:
        """地支の蔵干を取得"""
        return self.HIDDEN_STEMS.get(branch, [])
    
    def get_stem_yin_yang(self, stem: str) -> str:
        """天干の陰陽を取得"""
        return self.STEM_YIN_YANG.get(stem, "")
