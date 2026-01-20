"""
紫微斗数 旧暦コアモジュール
Lunisolar Calendar Core Module

pyswissephを使用した精密な朔（新月）計算と旧暦変換
市販のテーブルではなく天文計算に基づく動的な旧暦生成
"""

import math
from datetime import datetime, timedelta
from typing import Tuple, List, Optional, NamedTuple
from dataclasses import dataclass
from enum import Enum

try:
    import swisseph as swe
except ImportError:
    raise ImportError("pyswissephがインストールされていません: pip install pyswisseph")


# ============================================
# データ構造
# ============================================

@dataclass
class LunarDate:
    """旧暦日付"""
    year: int           # 旧暦年
    month: int          # 旧暦月（1-12）
    day: int            # 旧暦日（1-30）
    is_leap_month: bool # 閏月フラグ
    
    def __str__(self):
        leap_str = "閏" if self.is_leap_month else ""
        return f"旧暦{self.year}年{leap_str}{self.month}月{self.day}日"


class LeapMonthMode(Enum):
    """閏月の処理モード"""
    MODE_A = "A"  # 15日までを前月、16日以降を翌月（一般的）
    MODE_B = "B"  # 全て前月として扱う
    MODE_C = "C"  # 全て翌月として扱う


@dataclass
class ChineseHour:
    """時辰（十二支時刻）"""
    branch_index: int   # 0-11（子〜亥）
    branch_name: str    # 漢字名
    is_early_rat: bool  # 早子時（23-24時）かどうか


# ============================================
# LunisolarEngine: 天文学ベース旧暦計算
# ============================================

class LunisolarEngine:
    """
    pyswissephを使用した精密な旧暦計算エンジン
    
    特徴：
    - 固定テーブルではなく天文計算による朔（新月）の精密計算
    - 中気による閏月判定
    - 真太陽時による時辰決定
    """
    
    # 定数
    SYNODIC_MONTH = 29.530588853  # 朔望月（日）
    JST_OFFSET = 9.0 / 24.0       # JST = UTC + 9時間
    
    # 十二支
    BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    def __init__(self, use_jst: bool = True):
        """
        初期化
        
        Args:
            use_jst: 日本標準時を使用するかどうか
        """
        self.use_jst = use_jst
        # Swiss Ephemerisの初期化
        swe.set_ephe_path(None)  # デフォルトのエフェメリスを使用
    
    # ========================================
    # 朔（新月）計算
    # ========================================
    
    def _get_jd(self, dt: datetime) -> float:
        """datetimeからユリウス日を取得"""
        hour_decimal = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        jd = swe.julday(dt.year, dt.month, dt.day, hour_decimal)
        if self.use_jst:
            jd -= self.JST_OFFSET  # JSTからUTへ変換
        return jd
    
    def _jd_to_datetime(self, jd: float) -> datetime:
        """ユリウス日からdatetimeを取得"""
        if self.use_jst:
            jd += self.JST_OFFSET  # UTからJSTへ変換
        year, month, day, hour_frac = swe.revjul(jd)
        hour = int(hour_frac)
        minute = int((hour_frac - hour) * 60)
        second = int(((hour_frac - hour) * 60 - minute) * 60)
        return datetime(int(year), int(month), int(day), hour, minute, second)
    
    def _get_sun_longitude(self, jd: float) -> float:
        """太陽の視黄経を取得"""
        sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
        return sun_pos[0][0]  # 黄経（度）
    
    def _get_moon_longitude(self, jd: float) -> float:
        """月の視黄経を取得"""
        moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)
        return moon_pos[0][0]  # 黄経（度）
    
    def _find_new_moon(self, approx_jd: float) -> float:
        """
        指定した近似JD付近の朔（新月）を精密計算
        
        朔 = 太陽と月の視黄経が等しくなる瞬間
        """
        # ニュートン法で収束させる
        jd = approx_jd
        for _ in range(50):  # 最大50回反復
            sun_lon = self._get_sun_longitude(jd)
            moon_lon = self._get_moon_longitude(jd)
            
            # 月と太陽の黄経差（-180〜180度に正規化）
            diff = moon_lon - sun_lon
            while diff > 180:
                diff -= 360
            while diff < -180:
                diff += 360
            
            # 収束判定（0.0001度以下）
            if abs(diff) < 0.0001:
                break
            
            # 月の平均運動は約13.2度/日
            jd -= diff / 13.2
        
        return jd
    
    def calc_new_moon_dates(self, year: int) -> List[datetime]:
        """
        指定年のすべての新月日時（朔）を計算
        
        Args:
            year: 西暦年
            
        Returns:
            その年の全朔日（datetime）のリスト
        """
        new_moons = []
        
        # 前年11月から翌年2月までの朔を計算（旧暦年境界をカバー）
        start_jd = self._get_jd(datetime(year - 1, 11, 1))
        end_jd = self._get_jd(datetime(year + 1, 2, 28))
        
        # 朔望月で概算しながら朔を探索
        current_jd = start_jd
        while current_jd < end_jd:
            new_moon_jd = self._find_new_moon(current_jd)
            new_moon_dt = self._jd_to_datetime(new_moon_jd)
            new_moons.append(new_moon_dt)
            current_jd = new_moon_jd + self.SYNODIC_MONTH
        
        return new_moons
    
    # ========================================
    # 中気計算（閏月判定用）
    # ========================================
    
    def _find_solar_term(self, target_longitude: float, year: int, month: int) -> float:
        """
        特定の太陽黄経になる瞬間のJDを計算
        
        Args:
            target_longitude: 目標黄経（度）
            year: 西暦年
            month: 概算月
            
        Returns:
            そのJD
        """
        # 概算日を設定
        approx_jd = self._get_jd(datetime(year, month, 21))
        
        jd = approx_jd
        for _ in range(50):
            sun_lon = self._get_sun_longitude(jd)
            
            # 差分を計算（-180〜180度に正規化）
            diff = target_longitude - sun_lon
            while diff > 180:
                diff -= 360
            while diff < -180:
                diff += 360
            
            if abs(diff) < 0.0001:
                break
            
            # 太陽の平均運動は約1度/日
            jd += diff / 0.9856
        
        return jd
    
    def get_zhongqi_in_month(self, new_moon_jd: float, next_new_moon_jd: float) -> Optional[int]:
        """
        指定した朔月に含まれる中気の番号を取得
        
        中気 = 太陽黄経が30の倍数になる瞬間
        旧暦11月 = 冬至（270度）を含む月
        
        Args:
            new_moon_jd: 朔のJD
            next_new_moon_jd: 次の朔のJD
            
        Returns:
            中気番号（0-11）または None（中気なし = 閏月候補）
        """
        # 朔の期間内の太陽黄経範囲を計算
        start_lon = self._get_sun_longitude(new_moon_jd)
        end_lon = self._get_sun_longitude(next_new_moon_jd)
        
        # 中気は30度刻み
        for i in range(12):
            zhongqi_lon = i * 30  # 0, 30, 60, ..., 330度
            
            # 黄経が範囲内にあるかチェック
            if self._is_longitude_in_range(zhongqi_lon, start_lon, end_lon):
                return i
        
        return None  # 中気なし = 閏月候補
    
    def _is_longitude_in_range(self, target: float, start: float, end: float) -> bool:
        """黄経が範囲内にあるかチェック（360度境界を考慮）"""
        if start <= end:
            return start < target <= end
        else:  # 360度境界をまたぐ場合
            return target > start or target <= end
    
    # ========================================
    # 旧暦変換
    # ========================================
    
    def convert_to_lunar(
        self, 
        gregorian_dt: datetime,
        leap_mode: LeapMonthMode = LeapMonthMode.MODE_A
    ) -> LunarDate:
        """
        グレゴリオ暦を旧暦に変換
        
        Args:
            gregorian_dt: 変換するグレゴリオ暦日時
            leap_mode: 閏月の処理モード
            
        Returns:
            LunarDate: 旧暦日付
        """
        target_jd = self._get_jd(gregorian_dt)
        year = gregorian_dt.year
        
        # 前年から翌年までの朔を計算
        all_new_moons = []
        for y in [year - 1, year, year + 1]:
            all_new_moons.extend(self.calc_new_moon_dates(y))
        
        # 重複を除去してソート
        all_new_moons = sorted(set(all_new_moons))
        new_moon_jds = [self._get_jd(nm) for nm in all_new_moons]
        
        # 対象日がどの朔月に属するか特定
        month_index = -1
        for i, jd in enumerate(new_moon_jds[:-1]):
            if jd <= target_jd < new_moon_jds[i + 1]:
                month_index = i
                break
        
        if month_index == -1:
            raise ValueError(f"旧暦変換に失敗しました: {gregorian_dt}")
        
        # 旧暦日を計算
        lunar_day = int(target_jd - new_moon_jds[month_index]) + 1
        
        # 冬至を含む月（旧暦11月）を特定
        winter_solstice_jd = self._find_solar_term(270, year, 12)
        
        # 冬至を含む朔月のインデックスを特定
        winter_month_idx = -1
        for i, jd in enumerate(new_moon_jds[:-1]):
            if jd <= winter_solstice_jd < new_moon_jds[i + 1]:
                winter_month_idx = i
                break
        
        # 閏月の判定
        # 冬至月から次の冬至月までに13朔ある場合、閏月が存在
        # 中気を含まない最初の月を閏月とする
        
        # 簡易版：月番号を計算
        months_from_winter = month_index - winter_month_idx
        lunar_month = ((months_from_winter + 11 - 1) % 12) + 1  # 11月が基準
        
        # 年の判定（冬至月の前月以前は前年）
        if months_from_winter < -1:
            lunar_year = year - 1
        else:
            lunar_year = year
        
        # 閏月判定（簡易版：中気がない月を探す）
        is_leap = False
        zhongqi = self.get_zhongqi_in_month(
            new_moon_jds[month_index], 
            new_moon_jds[month_index + 1]
        )
        
        if zhongqi is None:
            is_leap = True
            # 閏月の処理モードに応じて月番号を調整
            if leap_mode == LeapMonthMode.MODE_A:
                if lunar_day <= 15:
                    pass  # 閏月として扱う
                else:
                    is_leap = False
                    lunar_month = (lunar_month % 12) + 1
            elif leap_mode == LeapMonthMode.MODE_B:
                pass  # 閏月として扱う
            elif leap_mode == LeapMonthMode.MODE_C:
                is_leap = False
                lunar_month = (lunar_month % 12) + 1
        
        return LunarDate(
            year=lunar_year,
            month=lunar_month,
            day=lunar_day,
            is_leap_month=is_leap
        )
    
    # ========================================
    # 真太陽時計算
    # ========================================
    
    def get_equation_of_time(self, jd: float) -> float:
        """
        均時差（Equation of Time）を計算
        
        均時差 = 視太陽時 - 平均太陽時
        
        Args:
            jd: ユリウス日
            
        Returns:
            均時差（分）
        """
        # 簡易計算式
        # より精密にはpyswissephのsider_time関数を使用
        
        # ユリウス世紀
        t = (jd - 2451545.0) / 36525.0
        
        # 平均近点離角
        m = math.radians(357.5291 + 35999.0503 * t)
        
        # 黄道傾斜角
        eps = math.radians(23.439 - 0.0130 * t)
        
        # 均時差の成分
        y = math.tan(eps / 2) ** 2
        
        # 太陽の平均黄経
        l0 = math.radians(280.46646 + 36000.76983 * t)
        
        # 離心率
        e = 0.016708634 - 0.000042037 * t
        
        # 均時差（ラジアン）
        eot = y * math.sin(2 * l0) - 2 * e * math.sin(m) + \
              4 * e * y * math.sin(m) * math.cos(2 * l0) - \
              0.5 * y * y * math.sin(4 * l0) - \
              1.25 * e * e * math.sin(2 * m)
        
        # 分に変換
        return math.degrees(eot) * 4
    
    def get_true_solar_time(self, local_dt: datetime, longitude: float) -> datetime:
        """
        真太陽時を計算
        
        Args:
            local_dt: 地方時（JSTなど）
            longitude: 出生地の経度（東経が正）
            
        Returns:
            真太陽時
        """
        jd = self._get_jd(local_dt)
        
        # 均時差（分）
        eot = self.get_equation_of_time(jd)
        
        # 標準子午線からの経度差（日本は東経135度が標準）
        if self.use_jst:
            standard_meridian = 135.0
        else:
            standard_meridian = 0.0  # UTC
        
        lon_correction = (longitude - standard_meridian) * 4  # 分
        
        # 真太陽時
        true_solar_time = local_dt + timedelta(minutes=(lon_correction + eot))
        
        return true_solar_time
    
    # ========================================
    # 時辰（十二支時刻）
    # ========================================
    
    def get_chinese_hour(
        self, 
        true_solar_time: datetime,
        use_early_rat: bool = True
    ) -> ChineseHour:
        """
        真太陽時から十二支時刻を取得
        
        Args:
            true_solar_time: 真太陽時
            use_early_rat: 23-24時を「早子時」として当日扱いにする（紫微斗数標準）
            
        Returns:
            ChineseHour: 時辰情報
        """
        hour = true_solar_time.hour
        minute = true_solar_time.minute
        
        # 時刻から時辰インデックスを計算
        # 23:00-01:00 = 子（0）
        # 01:00-03:00 = 丑（1）
        # ...
        # 21:00-23:00 = 亥（11）
        
        total_minutes = hour * 60 + minute
        
        # 23:00以降は子の刻
        if hour >= 23:
            branch_idx = 0
            is_early_rat = True
        elif hour < 1:
            branch_idx = 0
            is_early_rat = False
        else:
            branch_idx = (hour + 1) // 2
            is_early_rat = False
        
        return ChineseHour(
            branch_index=branch_idx,
            branch_name=self.BRANCHES[branch_idx],
            is_early_rat=is_early_rat
        )
    
    def get_chinese_hour_index(self, hour: int) -> int:
        """
        時刻（0-23）から時辰インデックス（0-11）を取得
        """
        if hour >= 23 or hour < 1:
            return 0  # 子
        return (hour + 1) // 2


# ============================================
# ユーティリティ関数
# ============================================

def gregorian_to_lunar(
    year: int, 
    month: int, 
    day: int,
    leap_mode: str = "A"
) -> LunarDate:
    """
    グレゴリオ暦を旧暦に変換（簡易関数）
    
    Args:
        year: 西暦年
        month: 月
        day: 日
        leap_mode: 閏月モード（"A", "B", "C"）
        
    Returns:
        LunarDate: 旧暦日付
    """
    engine = LunisolarEngine()
    dt = datetime(year, month, day)
    mode = LeapMonthMode(leap_mode)
    return engine.convert_to_lunar(dt, mode)


def get_hour_branch(hour: int, minute: int = 0) -> Tuple[int, str]:
    """
    時刻から時辰を取得
    
    Args:
        hour: 時（0-23）
        minute: 分（0-59）
        
    Returns:
        (時辰インデックス, 時辰名)
    """
    branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    if hour >= 23 or hour < 1:
        idx = 0
    else:
        idx = (hour + 1) // 2
    
    return idx, branches[idx]
