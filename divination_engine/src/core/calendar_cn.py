"""
東洋暦エンジン
二十四節気、干支、旧暦変換
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from .ephemeris import AstroEngine
from .time_manager import TimeManager


@dataclass
class SolarTerm:
    """二十四節気"""
    name: str
    longitude: float  # 太陽黄経
    jd: float         # ユリウス日
    datetime_jst: datetime


@dataclass
class Pillar:
    """干支の柱"""
    stem: str         # 天干
    branch: str       # 地支
    stem_index: int   # 天干インデックス（0-9）
    branch_index: int # 地支インデックス（0-11）
    
    @property
    def full(self) -> str:
        return f"{self.stem}{self.branch}"
    
    @property
    def sexagenary_index(self) -> int:
        """六十干支インデックス（0-59）"""
        return (self.stem_index * 6 + self.branch_index // 2 * 5 + self.branch_index) % 60


@dataclass
class FourPillars:
    """四柱"""
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar
    
    def to_dict(self) -> Dict:
        return {
            "year": self.year.full,
            "month": self.month.full,
            "day": self.day.full,
            "hour": self.hour.full
        }


class ChineseCalendar:
    """
    東洋暦計算クラス
    - 二十四節気の正確な日時計算（太陽黄経ベース）
    - 干支（年・月・日・時）の算出
    - 空亡（天中殺）の計算
    """
    
    # 天干（十干）
    STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    
    # 地支（十二支）
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    # 二十四節気（太陽黄経との対応）
    SOLAR_TERMS = [
        ("小寒", 285), ("大寒", 300), ("立春", 315), ("雨水", 330),
        ("啓蟄", 345), ("春分", 0), ("清明", 15), ("穀雨", 30),
        ("立夏", 45), ("小満", 60), ("芒種", 75), ("夏至", 90),
        ("小暑", 105), ("大暑", 120), ("立秋", 135), ("処暑", 150),
        ("白露", 165), ("秋分", 180), ("寒露", 195), ("霜降", 210),
        ("立冬", 225), ("小雪", 240), ("大雪", 255), ("冬至", 270)
    ]
    
    # 節気（月の境界となる12節気のインデックス）
    # 立春(2), 啓蟄(4), 清明(6), 立夏(8), 芒種(10), 小暑(12),
    # 立秋(14), 白露(16), 寒露(18), 立冬(20), 大雪(22), 小寒(0)
    JIEQI_INDICES = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 0]
    
    # 月干起算：年干から月干を求める表
    # 年干(甲己/乙庚/丙辛/丁壬/戊癸) → 寅月の天干
    MONTH_STEM_START = {
        0: 2,   # 甲年・己年 → 寅月は丙
        5: 2,
        1: 4,   # 乙年・庚年 → 寅月は戊
        6: 4,
        2: 6,   # 丙年・辛年 → 寅月は庚
        7: 6,
        3: 8,   # 丁年・壬年 → 寅月は壬
        8: 8,
        4: 0,   # 戊年・癸年 → 寅月は甲
        9: 0
    }
    
    # 時干起算：日干から子の刻の天干を求める
    HOUR_STEM_START = {
        0: 0,   # 甲日・己日 → 子刻は甲
        5: 0,
        1: 2,   # 乙日・庚日 → 子刻は丙
        6: 2,
        2: 4,   # 丙日・辛日 → 子刻は戊
        7: 4,
        3: 6,   # 丁日・壬日 → 子刻は庚
        8: 6,
        4: 8,   # 戊日・癸日 → 子刻は壬
        9: 8
    }
    
    # 空亡（天中殺）対応表：日干支の順番から空亡の地支を求める
    VOID_BRANCHES = [
        ("戌", "亥"),  # 甲子〜癸酉 (0-9)
        ("申", "酉"),  # 甲戌〜癸未 (10-19)
        ("午", "未"),  # 甲申〜癸巳 (20-29)
        ("辰", "巳"),  # 甲午〜癸卯 (30-39)
        ("寅", "卯"),  # 甲辰〜癸丑 (40-49)
        ("子", "丑"),  # 甲寅〜癸亥 (50-59)
    ]
    
    def __init__(self):
        self.astro = AstroEngine()
        self._solar_term_cache: Dict[int, List[SolarTerm]] = {}
    
    def get_solar_terms_for_year(self, year: int) -> List[SolarTerm]:
        """
        指定年の全二十四節気を計算
        
        Returns:
            SolarTermのリスト（時系列順）
        """
        if year in self._solar_term_cache:
            return self._solar_term_cache[year]
        
        terms = []
        jst = ZoneInfo("Asia/Tokyo")
        
        # 前年12月の冬至から翌年1月の小寒まで計算
        # 年の始まりは立春なので、前年の節気も必要
        for i, (name, longitude) in enumerate(self.SOLAR_TERMS):
            # 概算開始日を設定
            if longitude >= 270:  # 冬至以降
                search_year = year - 1 if i < 2 else year
            else:
                search_year = year
            
            # 概算日（太陽は1年で360度移動）
            days_from_spring = ((longitude - 315) % 360) / 360 * 365.25
            approx_jd = self.astro.calc_julian_day(search_year, 2, 4, 0) + days_from_spring
            
            # 正確な時刻を計算
            jd = self.astro.find_solar_term_time(search_year, longitude, approx_jd - 15)
            
            dt = TimeManager.from_julian_day(jd, jst)
            
            terms.append(SolarTerm(
                name=name,
                longitude=longitude,
                jd=jd,
                datetime_jst=dt
            ))
        
        # 時系列順にソート
        terms.sort(key=lambda t: t.jd)
        
        self._solar_term_cache[year] = terms
        return terms
    
    def get_lichun_jd(self, year: int) -> float:
        """立春のユリウス日を取得"""
        terms = self.get_solar_terms_for_year(year)
        for term in terms:
            if term.name == "立春":
                return term.jd
        raise ValueError(f"立春が見つかりません: {year}年")
    
    def get_previous_jieqi(self, jd: float) -> Tuple[int, SolarTerm]:
        """
        指定日より前の直近の節気を取得
        
        Returns:
            (月番号1-12, 節気データ)
        """
        # 節気のみ（中気を除く）
        jieqi_names = ["立春", "啓蟄", "清明", "立夏", "芒種", "小暑",
                       "立秋", "白露", "寒露", "立冬", "大雪", "小寒"]
        
        dt = TimeManager.from_julian_day(jd)
        year = dt.year
        
        # 現在年と前年の節気を取得
        all_terms = []
        for y in [year - 1, year, year + 1]:
            all_terms.extend(self.get_solar_terms_for_year(y))
        
        # 節気のみをフィルタリング
        jieqi_list = [(t, jieqi_names.index(t.name) + 1) 
                      for t in all_terms if t.name in jieqi_names]
        
        # 指定日より前の最も近い節気を検索
        jieqi_list.sort(key=lambda x: x[0].jd, reverse=True)
        
        for term, month_num in jieqi_list:
            if term.jd <= jd:
                return month_num, term
        
        raise ValueError("節気が見つかりません")
    
    def calc_day_pillar(self, jd: float, use_23h_boundary: bool = True) -> Pillar:
        """
        日干支を計算
        
        基準日: 1992年2月17日 JST = 癸亥
        日の境界: デフォルトで23時JST（晩子時方式）
        
        Args:
            jd: ユリウス日（UT）
            use_23h_boundary: True なら23時以降は翌日の干支を使用（デフォルト）
        
        Returns:
            Pillar: 日柱
        """
        # JDをJSTのdatetimeに変換
        dt_jst = TimeManager.from_julian_day(jd, ZoneInfo("Asia/Tokyo"))
        
        # 23時以降は翌日の干支を使用（晩子時方式）
        if use_23h_boundary and dt_jst.hour >= 23:
            dt_jst = dt_jst + timedelta(days=1)
        
        # 基準日: 1992年2月17日 JST午前0時 = 癸亥
        # (ユーザー確認済み: 1992年2月17日17時18分生まれ = 日柱癸亥)
        base_date = datetime(1992, 2, 17, tzinfo=ZoneInfo("Asia/Tokyo"))
        
        # 日数差を計算
        days_diff = (dt_jst.date() - base_date.date()).days
        
        # 癸亥のインデックス: 59 (60干支中)
        kuikai_index = 59
        
        # 60干支のインデックスを計算
        index = (kuikai_index + days_diff) % 60
        
        stem_index = index % 10
        branch_index = index % 12
        
        return Pillar(
            stem=self.STEMS[stem_index],
            branch=self.BRANCHES[branch_index],
            stem_index=stem_index,
            branch_index=branch_index
        )

    def calc_year_pillar(self, jd: float) -> Pillar:
        """
        年干支を計算（立春を基準）
        """
        dt = TimeManager.from_julian_day(jd, ZoneInfo("Asia/Tokyo"))
        year = dt.year
        
        # 立春のJDを取得
        lichun_jd = self.get_lichun_jd(year)
        
        # 立春前なら前年
        if jd < lichun_jd:
            year -= 1
        
        # 年干支の計算（1984年が甲子年）
        # 1984年を基準にオフセット計算
        offset = (year - 1984) % 60
        
        stem_index = offset % 10
        branch_index = offset % 12
        
        return Pillar(
            stem=self.STEMS[stem_index],
            branch=self.BRANCHES[branch_index],
            stem_index=stem_index,
            branch_index=branch_index
        )
    
    def calc_month_pillar(self, jd: float, year_stem_index: int) -> Pillar:
        """
        月干支を計算（節気を基準）
        """
        month_num, _ = self.get_previous_jieqi(jd)
        
        # 寅月(1月) = 地支インデックス2
        branch_index = (month_num + 1) % 12
        
        # 年干から月干を計算
        base_stem = self.MONTH_STEM_START[year_stem_index]
        stem_index = (base_stem + month_num - 1) % 10
        
        return Pillar(
            stem=self.STEMS[stem_index],
            branch=self.BRANCHES[branch_index],
            stem_index=stem_index,
            branch_index=branch_index
        )
    
    def calc_hour_pillar(self, jd: float, day_stem_index: int, 
                         use_early_rat: bool = False) -> Pillar:
        """
        時干支を計算
        
        Args:
            jd: ユリウス日
            day_stem_index: 日干インデックス
            use_early_rat: 早子時（23:00-01:00）を使用するか
                          False = 00:00-01:00を子の刻とする（デフォルト）
        """
        dt = TimeManager.from_julian_day(jd, ZoneInfo("Asia/Tokyo"))
        hour = dt.hour
        
        # 時支（十二支）を決定
        # use_early_rat=False（晩子時）: 00:00-01:00が子の刻
        if use_early_rat:
            if hour >= 23:
                branch_index = 0
            else:
                branch_index = (hour + 1) // 2
        else:
            branch_index = (hour + 1) // 2 % 12
        
        # 日干から子の刻の天干を決定し、時支に応じてオフセット
        base_stem = self.HOUR_STEM_START[day_stem_index]
        stem_index = (base_stem + branch_index) % 10
        
        return Pillar(
            stem=self.STEMS[stem_index],
            branch=self.BRANCHES[branch_index],
            stem_index=stem_index,
            branch_index=branch_index
        )
    
    def calc_four_pillars(self, dt: datetime, 
                          use_early_rat: bool = False) -> FourPillars:
        """
        四柱（年月日時の干支）を計算
        
        Args:
            dt: 生年月日時（タイムゾーン付き）
            use_early_rat: 早子時を使用するか（デフォルト: False = 00:00切り替え）
        """
        jd = TimeManager.to_julian_day(dt)
        
        # 年柱
        year_pillar = self.calc_year_pillar(jd)
        
        # 月柱
        month_pillar = self.calc_month_pillar(jd, year_pillar.stem_index)
        
        # 日柱
        day_pillar = self.calc_day_pillar(jd)
        
        # 時柱
        hour_pillar = self.calc_hour_pillar(jd, day_pillar.stem_index, use_early_rat)
        
        return FourPillars(
            year=year_pillar,
            month=month_pillar,
            day=day_pillar,
            hour=hour_pillar
        )
    
    def calc_void_branches(self, day_pillar: Pillar) -> Tuple[str, str]:
        """
        空亡（天中殺）を計算
        日干支から空亡となる地支を求める
        """
        # 日干支のインデックス（0-59）
        sexagenary = day_pillar.sexagenary_index
        
        # 10日周期のどこにいるかで空亡が決まる
        group = sexagenary // 10
        
        return self.VOID_BRANCHES[group]
    
    def get_nine_star(self, year: int, use_lichun: bool = True) -> int:
        """
        九星を計算（年九星）
        
        Args:
            year: 西暦年
            use_lichun: 立春を年の境界とするか
            
        Returns:
            九星番号（1=一白, 2=二黒, ... 9=九紫）
        """
        # 立春基準の場合は調整が必要（ここでは年のみで簡易計算）
        # 1927年は五黄土星
        base_year = 1927
        offset = (base_year - year) % 9
        
        star = offset
        if star == 0:
            star = 9
        
        return star


# テスト用のサンプルデータ
TEST_CASE = {
    "name_kanji": "安瀬 諒",
    "name_kana": "アンゼ リョウ",
    "birth_datetime": datetime(1992, 2, 17, 17, 18, tzinfo=ZoneInfo("Asia/Tokyo")),
    "birth_place": "東京都足立区",
    "latitude": 35.7756,
    "longitude": 139.8044,
    "gender": "male"
}
