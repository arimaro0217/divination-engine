"""
九星気学モジュール
本命星、月命星、日命星、傾斜の計算
"""
from datetime import datetime
from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo

from .sexagenary import SexagenaryCalculator
from ...core.calendar_cn import ChineseCalendar
from ...core.time_manager import TimeManager
from ...models.output_schema import KyuseiResult


class KyuseiCalculator(SexagenaryCalculator):
    """
    九星気学計算クラス
    """
    
    # 九星
    NINE_STARS = [
        "一白水星", "二黒土星", "三碧木星", "四緑木星", "五黄土星",
        "六白金星", "七赤金星", "八白土星", "九紫火星"
    ]
    
    # 九星の五行
    STAR_ELEMENTS = {
        "一白水星": "水", "二黒土星": "土", "三碧木星": "木",
        "四緑木星": "木", "五黄土星": "土", "六白金星": "金",
        "七赤金星": "金", "八白土星": "土", "九紫火星": "火"
    }
    
    # 傾斜宮（本命星と月命星の組み合わせ）
    INCLINATION_PALACES = {
        (1, 1): "坎宮", (1, 2): "坤宮", (1, 3): "震宮", (1, 4): "巽宮",
        (1, 5): "中宮", (1, 6): "乾宮", (1, 7): "兌宮", (1, 8): "艮宮", (1, 9): "離宮",
        # 他の組み合わせも同様に定義...
    }
    
    def __init__(self):
        super().__init__()
    
    def calculate(self, birth_dt: datetime) -> KyuseiResult:
        """
        九星気学を計算
        
        Args:
            birth_dt: 生年月日時（タイムゾーン付き）
            
        Returns:
            KyuseiResult
        """
        jd = TimeManager.to_julian_day(birth_dt)
        
        # 立春を基準とした年
        year = self._get_kyusei_year(birth_dt)
        
        # 立春を基準とした月
        month = self._get_kyusei_month(birth_dt)
        
        # 本命星
        year_star = self._calc_year_star(year)
        
        # 月命星
        month_star = self._calc_month_star(year, month)
        
        # 日命星
        day_star = self._calc_day_star(birth_dt)
        
        # 傾斜宮
        inclination = self._calc_inclination(year_star, month_star)
        
        return KyuseiResult(
            year_star=self.NINE_STARS[year_star - 1],
            month_star=self.NINE_STARS[month_star - 1],
            day_star=self.NINE_STARS[day_star - 1],
            inclination=inclination
        )
    
    def _get_kyusei_year(self, dt: datetime) -> int:
        """立春を基準とした年を取得"""
        jd = TimeManager.to_julian_day(dt)
        year = dt.year
        
        # 立春のJD
        lichun_jd = self.calendar.get_lichun_jd(year)
        
        if jd < lichun_jd:
            return year - 1
        return year
    
    def _get_kyusei_month(self, dt: datetime) -> int:
        """節気を基準とした月番号（1-12）を取得"""
        jd = TimeManager.to_julian_day(dt)
        month_num, _ = self.calendar.get_previous_jieqi(jd)
        return month_num
    
    def _calc_year_star(self, year: int) -> int:
        """
        本命星を計算
        
        計算式: (11 - (year - 3) % 9) % 9
        ※ 0になる場合は9
        """
        star = (11 - (year - 3) % 9) % 9
        if star == 0:
            star = 9
        return star
    
    def _calc_month_star(self, year: int, month: int) -> int:
        """
        月命星を計算
        
        年の本命星によって起算が異なる
        """
        year_star = self._calc_year_star(year)
        
        # 年盤の中央値（本命星）から月盤の起算値を決定
        # 1, 4, 7の年は8から逆順
        # 2, 5, 8の年は5から逆順
        # 3, 6, 9の年は2から逆順
        if year_star in [1, 4, 7]:
            base = 8
        elif year_star in [2, 5, 8]:
            base = 5
        else:  # 3, 6, 9
            base = 2
        
        # 月（2月=寅月が1）からのオフセット
        star = (base - (month - 1)) % 9
        if star == 0:
            star = 9
        
        return star
    
    def _calc_day_star(self, dt: datetime) -> int:
        """
        日命星を計算
        
        上元甲子日を起点として計算
        """
        jd = TimeManager.to_julian_day(dt)
        
        # 基準日: 1984年2月4日（甲子日、かつ一白水星日）
        base_jd = 2445735.5
        
        # 180日周期（九星が9日ずつ3巡）
        days = int(jd - base_jd)
        
        # 陽遁・陰遁を考慮した計算
        cycle_pos = days % 180
        
        if cycle_pos < 90:
            # 陽遁（1から9へ）
            star = ((cycle_pos % 9) + 1)
        else:
            # 陰遁（9から1へ）
            star = (9 - (cycle_pos % 9))
        
        if star == 0:
            star = 9
        
        return star
    
    def _calc_inclination(self, year_star: int, month_star: int) -> str:
        """
        傾斜宮を計算
        """
        # 傾斜は月命星から本命星への方向で決まる
        # 九宮図上での位置関係
        
        PALACE_NAMES = {
            1: "坎宮（北）",
            2: "坤宮（南西）",
            3: "震宮（東）",
            4: "巽宮（南東）",
            5: "中宮（中央）",
            6: "乾宮（北西）",
            7: "兌宮（西）",
            8: "艮宮（北東）",
            9: "離宮（南）",
        }
        
        # 傾斜宮の計算（月命星の宮を基準）
        # 簡易版として月命星の宮を返す
        return PALACE_NAMES.get(month_star, "中宮（中央）")
    
    def get_compatibility(self, star1: int, star2: int) -> str:
        """
        相性を判定
        """
        element1 = self.STAR_ELEMENTS[self.NINE_STARS[star1 - 1]]
        element2 = self.STAR_ELEMENTS[self.NINE_STARS[star2 - 1]]
        
        # 相生関係
        generation = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        
        # 相剋関係  
        destruction = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
        
        if element1 == element2:
            return "比和（同じ気質）"
        elif generation.get(element1) == element2:
            return "相生（自分が生じる）"
        elif generation.get(element2) == element1:
            return "相生（相手から生じられる）"
        elif destruction.get(element1) == element2:
            return "相剋（自分が剋す）"
        elif destruction.get(element2) == element1:
            return "相剋（相手から剋される）"
        else:
            return "中立"
