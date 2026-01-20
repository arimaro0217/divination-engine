"""
時間管理エンジン
UTC/JST/LMT変換、均時差計算
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from zoneinfo import ZoneInfo
import math


class TimeManager:
    """時間管理クラス"""
    
    # 日本標準時
    JST = ZoneInfo("Asia/Tokyo")
    UTC = timezone.utc
    
    # 日本標準時の基準経度（東経135度）
    JST_STANDARD_LONGITUDE = 135.0
    
    @classmethod
    def to_utc(cls, dt: datetime) -> datetime:
        """任意のタイムゾーン付き日時をUTCに変換"""
        if dt.tzinfo is None:
            # タイムゾーン情報がない場合はJSTと仮定
            dt = dt.replace(tzinfo=cls.JST)
        return dt.astimezone(cls.UTC)
    
    @classmethod
    def to_jst(cls, dt: datetime) -> datetime:
        """任意のタイムゾーン付き日時をJSTに変換"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=cls.UTC)
        return dt.astimezone(cls.JST)
    
    @classmethod
    def to_julian_day(cls, dt: datetime) -> float:
        """
        日時をユリウス通日（JD）に変換
        天体計算の基準となる連続した日数
        """
        dt_utc = cls.to_utc(dt)
        
        year = dt_utc.year
        month = dt_utc.month
        day = dt_utc.day
        hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
        
        # グレゴリオ暦からユリウス日への変換（Meeus式）
        if month <= 2:
            year -= 1
            month += 12
        
        a = int(year / 100)
        b = 2 - a + int(a / 4)
        
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + hour / 24.0 + b - 1524.5
        
        return jd
    
    @classmethod
    def from_julian_day(cls, jd: float, tz: Optional[ZoneInfo] = None) -> datetime:
        """ユリウス通日から日時に変換"""
        if tz is None:
            tz = cls.UTC
            
        # ユリウス日から日時への逆変換
        jd = jd + 0.5
        z = int(jd)
        f = jd - z
        
        if z < 2299161:
            a = z
        else:
            alpha = int((z - 1867216.25) / 36524.25)
            a = z + 1 + alpha - int(alpha / 4)
        
        b = a + 1524
        c = int((b - 122.1) / 365.25)
        d = int(365.25 * c)
        e = int((b - d) / 30.6001)
        
        day = b - d - int(30.6001 * e) + f
        
        if e < 14:
            month = e - 1
        else:
            month = e - 13
            
        if month > 2:
            year = c - 4716
        else:
            year = c - 4715
        
        # 小数部分を時分秒に変換
        day_int = int(day)
        day_frac = day - day_int
        hours = day_frac * 24
        hour = int(hours)
        minutes = (hours - hour) * 60
        minute = int(minutes)
        second = int((minutes - minute) * 60)
        
        dt = datetime(year, month, day_int, hour, minute, second, tzinfo=cls.UTC)
        return dt.astimezone(tz)
    
    @classmethod
    def equation_of_time(cls, jd: float) -> float:
        """
        均時差（分単位）を計算
        真太陽時と平均太陽時の差
        
        参考: Meeus "Astronomical Algorithms" Chapter 28
        """
        # ユリウス世紀
        t = (jd - 2451545.0) / 36525.0
        
        # 太陽の平均黄経
        l0 = 280.4664567 + 360007.6982779 * t + 0.03032028 * t**2
        l0 = l0 % 360
        
        # 太陽の平均近点角
        m = 357.5291092 + 35999.0502909 * t - 0.0001536 * t**2
        m = math.radians(m % 360)
        
        # 黄道傾斜角
        eps = 23.439291 - 0.0130042 * t
        eps = math.radians(eps)
        
        # 離心率
        e = 0.016708634 - 0.000042037 * t
        
        # 計算
        y = math.tan(eps / 2) ** 2
        
        eq = y * math.sin(2 * math.radians(l0)) \
             - 2 * e * math.sin(m) \
             + 4 * e * y * math.sin(m) * math.cos(2 * math.radians(l0)) \
             - 0.5 * y * y * math.sin(4 * math.radians(l0)) \
             - 1.25 * e * e * math.sin(2 * m)
        
        # ラジアンから分に変換（1ラジアン = 229.18分角）
        eq_minutes = math.degrees(eq) * 4
        
        return eq_minutes
    
    @classmethod
    def local_mean_time(cls, dt: datetime, longitude: float) -> datetime:
        """
        地方平均時（LMT）を計算
        経度に基づいた地方時
        """
        dt_utc = cls.to_utc(dt)
        
        # 経度1度 = 4分の時差
        offset_minutes = longitude * 4
        offset = timedelta(minutes=offset_minutes)
        
        return dt_utc + offset
    
    @classmethod
    def local_apparent_time(cls, dt: datetime, longitude: float) -> datetime:
        """
        地方真太陽時（LAT）を計算
        実際の太陽の位置に基づいた時刻
        """
        jd = cls.to_julian_day(dt)
        eot = cls.equation_of_time(jd)
        
        lmt = cls.local_mean_time(dt, longitude)
        lat = lmt + timedelta(minutes=eot)
        
        return lat
    
    @classmethod
    def get_hour_branch(cls, dt: datetime, use_early_rat: bool = False) -> Tuple[int, str]:
        """
        時刻から十二支時を取得
        
        Args:
            dt: 日時
            use_early_rat: True=早子時（23:00-01:00）、False=晩子時（00:00-01:00）
            
        Returns:
            (時支番号0-11, 時支名)
        """
        branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        hour = dt.hour
        
        if use_early_rat:
            # 早子時：23:00以降は翌日の子の刻
            if hour >= 23:
                branch_idx = 0
            else:
                branch_idx = (hour + 1) // 2
        else:
            # 晩子時：00:00-01:00が子の刻（デフォルト設定）
            branch_idx = (hour + 1) // 2 % 12
        
        return branch_idx, branches[branch_idx]
