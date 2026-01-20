"""
九星気学コアロジック - 陽遁・隠遁の厳密実装

このモジュールは九星気学の核心となる計算を実装します：
- 陽遁・隠遁の動的な切り替え判定（冬至・夏至基準の甲子日）
- 年盤・月盤・日盤・時盤の九星計算
- 既存のpyswissephを活用した天体計算
"""

import sys
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import swisseph as swe

from ...core.calendar_cn import ChineseCalendar
from ...core.astro_precise import PrecisionAstroEngine
from ...const import kigaku_const as kc

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
class SolsticeInfo:
    """至点（冬至・夏至）の情報"""
    name: str  # "冬至" or "夏至"
    jd_ut: float  # ユリウス日（UT）
    datetime_jst: datetime  # JST日時
    nearest_koshi_jd: float  # 最寄りの甲子日のJD
    nearest_koshi_date: datetime  # 最寄りの甲子日の日付
    days_diff: int  # 至点と甲子日の日数差


@dataclass
class TonPeriod:
    """陽遁・隠遁期間の情報"""
    ton_type: str  # "陽遁" or "隠遁"
    start_jd: float  # 開始日のJD
    end_jd: float  # 終了日のJD
    start_date: datetime  # 開始日
    end_date: datetime  # 終了日


# ============================================
# KigakuCalendar: 九星気学の暦計算クラス
# ============================================

class KigakuCalendar:
    """
    九星気学の厳密な暦計算クラス
    
    陽遁・隠遁の動的計算を含む完全な実装
    """
    
    def __init__(self):
        """初期化"""
        self.calendar = ChineseCalendar()
        self.astro_engine = PrecisionAstroEngine()
        
        # 六十干支
        self.sixty_ganzhi = [
            f"{kc.STEMS[i % 10]}{kc.BRANCHES[i % 12]}" 
            for i in range(60)
        ]
    
    # ========================================
    # 陽遁・隠遁の判定（最重要）
    # ========================================
    
    def find_solstice_and_koshi(self, year: int, solstice_type: str) -> SolsticeInfo:
        """
        冬至または夏至と、その最寄りの甲子日を見つける
        
        Args:
            year: 年
            solstice_type: "冬至" or "夏至"
        
        Returns:
            SolsticeInfo: 至点と甲子日の情報
        """
        # 至点の太陽黄経
        if solstice_type == "冬至":
            target_lon = kc.YOTON_REFERENCE_LONGITUDE  # 270度
            search_month = 12
        else:  # 夏至
            target_lon = kc.INTON_REFERENCE_LONGITUDE  # 90度
            search_month = 6
        
        # 至点の正確な日時を計算
        jd_solstice, dt_utc, dt_jst = self.astro_engine.find_exact_solar_term_time(
            target_lon, year, search_month
        )
        
        # 至点の前後30日間で甲子日を探す
        search_start_jd = jd_solstice - 30
        search_end_jd = jd_solstice + 30
        
        # 甲子日を探す（甲子は六十干支の0番目）
        koshi_candidates = []
        
        current_jd = search_start_jd
        while current_jd <= search_end_jd:
            # この日の干支を取得
            year_cal, month_cal, day_cal, hour_cal = swe.revjul(current_jd)
            dt = datetime(year_cal, month_cal, day_cal)
            
            # 日干支を計算（既存のロジックを使用）
            four_pillars = self.calendar.get_four_pillars(dt, 35.68, 139.76)
            day_ganzhi = f"{four_pillars.day.stem}{four_pillars.day.branch}"
            
            if day_ganzhi == "甲子":
                days_from_solstice = int(current_jd - jd_solstice)
                koshi_candidates.append((current_jd, days_from_solstice, dt))
            
            current_jd += 1.0
        
        # 最も至点に近い甲子日を選択
        if not koshi_candidates:
            raise ValueError(f"{year}年の{solstice_type}前後に甲子日が見つかりません")
        
        nearest_koshi = min(koshi_candidates, key=lambda x: abs(x[1]))
        nearest_koshi_jd, days_diff, nearest_koshi_date = nearest_koshi
        
        return SolsticeInfo(
            name=solstice_type,
            jd_ut=jd_solstice,
            datetime_jst=dt_jst,
            nearest_koshi_jd=nearest_koshi_jd,
            nearest_koshi_date=nearest_koshi_date,
            days_diff=days_diff
        )
    
    def determine_ton_type(self, target_date: datetime) -> Tuple[str, SolsticeInfo, SolsticeInfo]:
        """
        指定日が陽遁期間か隠遁期間かを判定
        
        Args:
            target_date: 判定対象の日時
        
        Returns:
            (陽遁 or 隠遁, 直前の冬至情報, 直前の夏至情報)
        """
        year = target_date.year
        
        # 当年と前年の冬至・夏至を取得
        try:
            winter_current = self.find_solstice_and_koshi(year, "冬至")
        except:
            winter_current = None
        
        try:
            winter_prev = self.find_solstice_and_koshi(year - 1, "冬至")
        except:
            winter_prev = None
        
        try:
            summer_current = self.find_solstice_and_koshi(year, "夏至")
        except:
            summer_current = None
        
        # ユリウス日に変換
        target_jd = swe.julday(target_date.year, target_date.month, target_date.day, 0.0)
        
        # 判定ロジック
        # 1. 直近の冬至と夏至を特定
        # 2. 冬至の最寄り甲子日 〜 夏至の最寄り甲子日：陽遁
        # 3. 夏至の最寄り甲子日 〜 次の冬至の最寄り甲子日：隠遁
        
        ton_periods = []
        
        # 前年冬至 → 当年夏至（陽遁）
        if winter_prev and summer_current:
            ton_periods.append(TonPeriod(
                ton_type="陽遁",
                start_jd=winter_prev.nearest_koshi_jd,
                end_jd=summer_current.nearest_koshi_jd,
                start_date=winter_prev.nearest_koshi_date,
                end_date=summer_current.nearest_koshi_date
            ))
        
        # 当年夏至 → 当年冬至（隠遁）
        if summer_current and winter_current:
            ton_periods.append(TonPeriod(
                ton_type="隠遁",
                start_jd=summer_current.nearest_koshi_jd,
                end_jd=winter_current.nearest_koshi_jd,
                start_date=summer_current.nearest_koshi_date,
                end_date=winter_current.nearest_koshi_date
            ))
        
        # 判定
        for period in ton_periods:
            if period.start_jd <= target_jd < period.end_jd:
                if period.ton_type == "陽遁":
                    return ("陽遁", winter_prev, summer_current)
                else:
                    return ("隠遁", winter_current, summer_current)
        
        # 当年冬至以降の場合は次の夏至まで陽遁
        if winter_current and target_jd >= winter_current.nearest_koshi_jd:
            return ("陽遁", winter_current, summer_current)
        
        # デフォルト（到達しないはず）
        return ("陽遁", winter_prev, summer_current)
    
    # ========================================
    # 九星の計算
    # ========================================
    
    def get_year_star(self, date: datetime) -> int:
        """
        本命星（年命星）を計算
        
        立春基準で切り替わる
        
        Args:
            date: 日時
        
        Returns:
            九星番号（1-9）
        """
        year = date.year
        
        # 立春のJDを取得
        jd_lichun, _, dt_lichun = self.astro_engine.find_exact_solar_term_time(
            315.0, year, 2
        )
        
        # 判定日のJD
        jd_target = swe.julday(date.year, date.month, date.day, 0.0)
        
        # 立春前なら前年扱い
        if jd_target < jd_lichun:
            year -= 1
        
        # 本命星の計算式: (11 - (year - 3) % 9) % 9
        # ※ 0になる場合は9
        star = (11 - (year - 3) % 9) % 9
        if star == 0:
            star = 9
        
        return star
    
    def get_month_star(self, date: datetime) -> int:
        """
        月命星を計算
        
        節入り基準で切り替わる
        
        Args:
            date: 日時
        
        Returns:
            九星番号（1-9）
        """
        # 立春基準の年を取得
        year = date.year
        jd_lichun, _, _ = self.astro_engine.find_exact_solar_term_time(315.0, year, 2)
        jd_target = swe.julday(date.year, date.month, date.day, 0.0)
        
        if jd_target < jd_lichun:
            year -= 1
        
        # 本命星を取得
        year_star = self.get_year_star(date)
        
        # 月番号を取得（節気基準）
        # 寅月（立春）を1として12まで
        month_num = self._get_kigaku_month_number(date)
        
        # 月命星の起算値（本命星により異なる）
        base_star = kc.MONTH_STAR_BASE[year_star]
        
        # 月命星の計算（逆順）
        month_star = (base_star - (month_num - 1)) % 9
        if month_star == 0:
            month_star = 9
        
        return month_star
    
    def get_day_star(self, date: datetime) -> Tuple[int, str]:
        """
        日命星を計算（陽遁・隠遁対応）
        
        Args:
            date: 日時
        
        Returns:
            (九星番号, 陽遁 or 隠遁)
        """
        # 陽遁・隠遁を判定
        ton_type, winter_info, summer_info = self.determine_ton_type(date)
        
        # 判定日のJD
        target_jd = swe.julday(date.year, date.month, date.day, 0.0)
        
        # 基準となる甲子日のJDを取得
        if ton_type == "陽遁":
            base_koshi_jd = winter_info.nearest_koshi_jd
        else:
            base_koshi_jd = summer_info.nearest_koshi_jd
        
        # 基準日からの経過日数
        days_from_base = int(target_jd - base_koshi_jd)
        
        # 九星は9日周期
        cycle_pos = days_from_base % 9
        
        if ton_type == "陽遁":
            # 陽遁：1 → 2 → 3 → ... → 9 → 1 ...
            day_star = (cycle_pos % 9) + 1
        else:
            # 隠遁：9 → 8 → 7 → ... → 1 → 9 ...
            day_star = 9 - (cycle_pos % 9)
        
        if day_star == 0:
            day_star = 9
        
        return day_star, ton_type
    
    def get_hour_star(self, date: datetime) -> int:
        """
        時命星を計算
        
        Args:
            date: 日時
        
        Returns:
            九星番号（1-9）
        """
        # 簡易実装：日命星に時刻による補正を加える
        # ※ より正確には日干支と季節で決まるが、ここでは簡略化
        
        day_star, _ = self.get_day_star(date)
        hour = date.hour
        
        # 時刻による補正（2時間ごとに星が変わる）
        # 23-01時: +0, 01-03時: +1, ... 21-23時: +11
        hour_index = ((hour + 1) // 2) % 12
        
        # 九星に変換
        hour_star = ((day_star - 1) + hour_index) % 9 + 1
        
        return hour_star
    
    # ========================================
    # 補助メソッド
    # ========================================
    
    def _get_kigaku_month_number(self, date: datetime) -> int:
        """
        節気基準の月番号を取得（1-12）
        
        寅月（立春〜啓蟄）を1として12まで
        """
        # 二十四節気のリスト（節のみ）
        jieqi_list = [
            (315, 2),  # 立春
            (345, 3),  # 啓蟄
            (15, 4),   # 清明
            (45, 5),   # 立夏
            (75, 6),   # 芒種
            (105, 7),  # 小暑
            (135, 8),  # 立秋
            (165, 9),  # 白露
            (195, 10), # 寒露
            (225, 11), # 立冬
            (255, 12), # 大雪
            (285, 1),  # 小寒
        ]
        
        target_jd = swe.julday(date.year, date.month, date.day, 0.0)
        year = date.year
        
        # 各節気のJDを計算して判定
        for i, (longitude, _) in enumerate(jieqi_list):
            # 節気の月を推定
            est_month = (i + 2) if (i + 2) <= 12 else (i + 2 - 12)
            
            jd_jieqi, _, _ = self.astro_engine.find_exact_solar_term_time(
                longitude, year, est_month
            )
            
            # 次の節気
            next_i = (i + 1) % 12
            next_lon, _ = jieqi_list[next_i]
            next_est_month = (i + 3) if (i + 3) <= 12 else (i + 3 - 12)
            next_year = year if next_est_month > est_month else year + 1
            
            jd_next_jieqi, _, _ = self.astro_engine.find_exact_solar_term_time(
                next_lon, next_year, next_est_month
            )
            
            if jd_jieqi <= target_jd < jd_next_jieqi:
                return (i + 1) if (i + 1) <= 12 else (i + 1 - 12)
        
        # デフォルト
        return 1


# 定数として六十干支の天干・地支を定義（再利用のため）
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
