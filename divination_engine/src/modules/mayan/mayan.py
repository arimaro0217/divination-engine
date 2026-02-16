"""
マヤ暦モジュール（高性能版）
ツォルキン暦（260日周期）の計算

対応機能:
- 古代マヤ（Classic）モード: JDN + GMT相関定数による厳密計算
- ドリームスペル（Dreamspell）モード: 閏年調整付き現代版
- 閏年2月29日: フナブ・クの日（Kin番号なし）
- GAPキン（黒キン）: 52日間のポータル日
- 日の出切り替え: オプションで日の出時刻を考慮
"""
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass

from ...core.time_manager import TimeManager
from ...models.output_schema import MayanResult


class MayanMode(Enum):
    """マヤ暦計算モード"""
    DREAMSPELL = "dreamspell"  # 現代版（閏年調整あり）
    CLASSIC = "classic"        # 古代マヤ（JDN純粋計算）


@dataclass
class MayanFullResult:
    """マヤ暦の完全な計算結果"""
    kin_number: Optional[int]           # KIN番号（フナブ・クの日はNone）
    solar_seal: Optional[str]           # 太陽の紋章
    solar_seal_en: Optional[str]        # 太陽の紋章（英語）
    wavespell: str                      # ウェイブスペル
    galactic_tone: Optional[int]        # 銀河の音
    galactic_tone_name: str             # 銀河の音の名前
    galactic_tone_keyword: str          # 銀河の音のキーワード
    guide: Optional[str]                # ガイドキン
    is_gap_kin: bool                    # GAPキン（黒キン）かどうか
    is_hunab_ku: bool                   # フナブ・クの日かどうか
    mode: str                           # 使用モード
    calculation_note: str               # 計算に関する注記


class MayanCalculator:
    """
    マヤ暦計算クラス（高性能版）
    
    古代マヤ（Classic）:
    - GMT相関法（584283）を使用
    - 閏年を無視してカウントし続ける
    - JDN（ユリウス通日）による厳密計算
    
    ドリームスペル（Dreamspell）:
    - 閏年2月29日を「フナブ・クの日」として特別扱い
    - 2月29日にはKIN番号を付与しない
    - 2月28日と3月1日の間に挿入される日
    """
    
    # GMT相関定数（Goodman-Martinez-Thompson）
    # 考古学的・天文学的証拠に基づく最も標準的な値
    GMT_CORRELATION = 584283
    
    # ドリームスペル基準日（1987年7月26日 = KIN 1）
    # 「ハーモニック・コンバージェンス」の開始日
    DREAMSPELL_EPOCH = datetime(1987, 7, 26)
    
    # 20の太陽の紋章
    SOLAR_SEALS = [
        "赤い竜", "白い風", "青い夜", "黄色い種", "赤い蛇",
        "白い世界の橋渡し", "青い手", "黄色い星", "赤い月", "白い犬",
        "青い猿", "黄色い人", "赤い空歩く者", "白い魔法使い", "青い鷲",
        "黄色い戦士", "赤い地球", "白い鏡", "青い嵐", "黄色い太陽"
    ]
    
    # 太陽の紋章の英語名
    SOLAR_SEALS_EN = [
        "Red Dragon", "White Wind", "Blue Night", "Yellow Seed", "Red Serpent",
        "White World-Bridger", "Blue Hand", "Yellow Star", "Red Moon", "White Dog",
        "Blue Monkey", "Yellow Human", "Red Skywalker", "White Wizard", "Blue Eagle",
        "Yellow Warrior", "Red Earth", "White Mirror", "Blue Storm", "Yellow Sun"
    ]
    
    # ウェイブスペル（紋章と同じ20種）
    WAVESPELLS = SOLAR_SEALS
    
    # 銀河の音のキーワード
    GALACTIC_TONES = {
        1: ("磁気の", "目的・統一"),
        2: ("月の", "挑戦・極性"),
        3: ("電気の", "奉仕・活性化"),
        4: ("自己存在の", "形・定義"),
        5: ("倍音の", "輝き・力"),
        6: ("律動の", "組織・平等"),
        7: ("共振の", "調整・チャンネル"),
        8: ("銀河の", "調和・完全性"),
        9: ("太陽の", "意図・脈動"),
        10: ("惑星の", "顕現・完成"),
        11: ("スペクトルの", "解放・溶解"),
        12: ("水晶の", "協力・普遍化"),
        13: ("宇宙の", "存在・超越")
    }
    
    # GAPキン（黒キン / Galactic Activation Portal）
    # ツォルキンの織物パターンに基づく52日間
    # これらの日は「宇宙のポータルが開く日」とされる
    GAP_KINS = {
        1, 20, 22, 39, 43, 50, 51, 58, 64, 69,
        72, 77, 85, 88, 93, 96, 106, 107, 108, 109,
        110, 111, 112, 113, 114, 115, 146, 147, 148, 149,
        150, 151, 152, 153, 154, 155, 165, 168, 173, 176,
        184, 189, 192, 197, 203, 210, 211, 218, 222, 239,
        241, 260
    }
    
    def __init__(self, mode: MayanMode = MayanMode.DREAMSPELL):
        """
        初期化
        
        Args:
            mode: 計算モード（ドリームスペル or 古代マヤ）
        """
        self.mode = mode
    
    def calculate(
        self, 
        birth_dt: datetime,
        mode: Optional[MayanMode] = None,
        sunrise_hour: float = 6.0  # 日の出時刻（デフォルト6時）
    ) -> MayanResult:
        """
        マヤ暦を計算（下位互換性のため）
        
        Args:
            birth_dt: 生年月日
            mode: 計算モード（省略時はインスタンスのモード）
            sunrise_hour: 日の出時刻（マヤの日切り替え用）
            
        Returns:
            MayanResult
        """
        result = self.calculate_full(birth_dt, mode, sunrise_hour)
        
        return MayanResult(
            kin_number=result.kin_number or 0,
            solar_seal=result.solar_seal or "フナブ・クの日",
            wavespell=result.wavespell,
            galactic_tone=result.galactic_tone or 0,
            guide=result.guide or ""
        )
    
    def calculate_full(
        self, 
        birth_dt: datetime,
        mode: Optional[MayanMode] = None,
        sunrise_hour: float = 6.0
    ) -> MayanFullResult:
        """
        マヤ暦を完全計算
        
        Args:
            birth_dt: 生年月日時
            mode: 計算モード
            sunrise_hour: 日の出時刻（0-24）
            
        Returns:
            MayanFullResult: 完全な計算結果
        """
        calc_mode = mode or self.mode
        
        # 日の出切り替え: 指定時刻より前なら前日として扱う
        effective_date = birth_dt
        if birth_dt.hour < sunrise_hour:
            effective_date = birth_dt - timedelta(days=1)
        
        # === ドリームスペルモード ===
        if calc_mode == MayanMode.DREAMSPELL:
            # 閏年2月29日のチェック（フナブ・クの日）
            if effective_date.month == 2 and effective_date.day == 29:
                return MayanFullResult(
                    kin_number=None,
                    solar_seal=None,
                    solar_seal_en=None,
                    wavespell="フナブ・ク（時間を超えた日）",
                    galactic_tone=None,
                    galactic_tone_name="フナブ・ク",
                    galactic_tone_keyword="創造主・一なるもの",
                    guide=None,
                    is_gap_kin=False,
                    is_hunab_ku=True,
                    mode="dreamspell",
                    calculation_note="2月29日はフナブ・クの日です。KIN番号は付与されず、時間を超えた特別な日として扱われます。"
                )
            
            # ドリームスペル計算
            kin = self._calc_kin_dreamspell(effective_date)
            note = "ドリームスペル方式で計算。閏年調整あり。"
        
        # === 古代マヤモード ===
        else:
            # JDN + GMT相関定数による計算
            kin = self._calc_kin_classic(effective_date)
            note = f"古代マヤ方式で計算。GMT相関定数({self.GMT_CORRELATION})使用。閏年調整なし。"
        
        # 太陽の紋章（KIN % 20）
        seal_index = (kin - 1) % 20
        solar_seal = self.SOLAR_SEALS[seal_index]
        solar_seal_en = self.SOLAR_SEALS_EN[seal_index]
        
        # 銀河の音（(KIN - 1) % 13 + 1）
        tone = ((kin - 1) % 13) + 1
        tone_name, tone_keyword = self.GALACTIC_TONES[tone]
        
        # ウェイブスペル（13日周期の始まりの紋章）
        wavespell_kin = ((kin - 1) // 13) * 13 + 1
        wavespell_index = (wavespell_kin - 1) % 20
        wavespell = self.WAVESPELLS[wavespell_index]
        
        # ガイドキン
        guide = self._calc_guide(kin, tone, seal_index)
        
        # GAPキン判定
        is_gap = kin in self.GAP_KINS
        
        return MayanFullResult(
            kin_number=kin,
            solar_seal=solar_seal,
            solar_seal_en=solar_seal_en,
            wavespell=wavespell,
            galactic_tone=tone,
            galactic_tone_name=tone_name,
            galactic_tone_keyword=tone_keyword,
            guide=guide,
            is_gap_kin=is_gap,
            is_hunab_ku=False,
            mode=calc_mode.value,
            calculation_note=note
        )
    
    def _calc_kin_classic(self, dt: datetime) -> int:
        """
        古代マヤ式KIN計算
        
        JDN（ユリウス通日）とGMT相関定数を使用した厳密計算
        閏年は考慮せず、純粋な日数カウント
        
        計算式: KIN = (JDN - GMT_CORRELATION) mod 260 + 1
        """
        # ユリウス日を計算
        jd = TimeManager.to_julian_day(dt)
        
        # JDを整数に（ユリウス通日）
        jdn = int(jd + 0.5)
        
        # KIN計算
        kin = ((jdn - self.GMT_CORRELATION) % 260) + 1
        
        return kin
    
    def _calc_kin_dreamspell(self, dt: datetime) -> int:
        """
        ドリームスペル式KIN計算
        
        基準日（1987年7月26日 = KIN 1）からの日数で計算
        閏年2月29日はスキップ（フナブ・クの日として別処理）
        """
        # 基準日からの日数を計算
        days_diff = (dt.date() - self.DREAMSPELL_EPOCH.date()).days
        
        # 閏年2月29日の数を引く（スキップされた日数）
        leap_days = self._count_leap_days(self.DREAMSPELL_EPOCH, dt)
        adjusted_days = days_diff - leap_days
        
        # KIN計算（1から260の循環）
        kin = (adjusted_days % 260) + 1
        if kin <= 0:
            kin += 260
        
        return kin
    
    def _count_leap_days(self, start: datetime, end: datetime) -> int:
        """
        期間内の閏年2月29日の数をカウント
        """
        count = 0
        # タイムゾーンの有無を統一して比較
        start_naive = start.replace(tzinfo=None)
        end_naive = end.replace(tzinfo=None)
        year = start_naive.year
        
        while year <= end_naive.year:
            # 閏年かどうか
            if self._is_leap_year(year):
                leap_day = datetime(year, 2, 29)
                if start_naive <= leap_day < end_naive:
                    count += 1
            year += 1
        
        return count
    
    def _is_leap_year(self, year: int) -> bool:
        """閏年判定"""
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    
    def _calc_kin(self, jd: float) -> int:
        """
        ユリウス日からKIN番号を計算（下位互換性のため維持）
        """
        return self._calc_kin_classic(datetime.now())
    
    def _calc_guide(self, kin: int, tone: int, seal_index: int) -> str:
        """
        ガイドキンを計算
        銀河の音によって決まる
        """
        # 音ごとのガイド計算オフセット
        guide_offsets = {
            1: 0, 6: 0, 11: 0,      # 同じ紋章
            2: 12, 7: 12, 12: 12,   # +12（実質-8）
            3: 4, 8: 4, 13: 4,      # +4
            4: 16, 9: 16,           # +16（実質-4）
            5: 8, 10: 8             # +8
        }
        
        offset = guide_offsets.get(tone, 0)
        guide_index = (seal_index + offset) % 20
        
        return self.SOLAR_SEALS[guide_index]
    
    def get_tone_info(self, tone: int) -> Tuple[str, str]:
        """銀河の音の詳細情報を取得"""
        return self.GALACTIC_TONES.get(tone, ("", ""))
    
    def calc_relationship(self, kin1: int, kin2: int) -> Dict:
        """二つのKIN間の関係を計算"""
        seal1 = (kin1 - 1) % 20
        seal2 = (kin2 - 1) % 20
        
        diff = (seal2 - seal1) % 20
        
        relationships = {
            0: "同じ紋章",
            10: "反対キン（補完関係）",
            4: "類似キン",
            16: "類似キン",
            6: "神秘キン",
            14: "神秘キン",
            19: "ガイドキン",
            1: "挑戦キン"
        }
        
        return {
            "relationship": relationships.get(diff, "その他"),
            "seal_diff": diff
        }
    
    def is_gap_kin(self, kin: int) -> bool:
        """指定KINがGAPキン（黒キン）かどうか判定"""
        return kin in self.GAP_KINS
    
    def get_all_gap_kins(self) -> list:
        """すべてのGAPキンを取得"""
        return sorted(list(self.GAP_KINS))
    
    def compare_modes(self, dt: datetime) -> Dict[str, Any]:
        """
        同じ日付で古代マヤとドリームスペルを比較
        
        Returns:
            両モードの計算結果と差分
        """
        classic = self.calculate_full(dt, MayanMode.CLASSIC)
        dreamspell = self.calculate_full(dt, MayanMode.DREAMSPELL)
        
        kin_diff = None
        if classic.kin_number and dreamspell.kin_number:
            kin_diff = classic.kin_number - dreamspell.kin_number
            if kin_diff < -130:
                kin_diff += 260
            elif kin_diff > 130:
                kin_diff -= 260
        
        return {
            "date": dt.strftime("%Y-%m-%d"),
            "classic": {
                "kin": classic.kin_number,
                "seal": classic.solar_seal,
                "tone": classic.galactic_tone
            },
            "dreamspell": {
                "kin": dreamspell.kin_number,
                "seal": dreamspell.solar_seal,
                "tone": dreamspell.galactic_tone,
                "is_hunab_ku": dreamspell.is_hunab_ku
            },
            "kin_difference": kin_diff,
            "note": "古代マヤとドリームスペルでは閏年の扱いが異なるため、KIN番号にズレが生じます。"
        }

