"""
マヤ暦モジュール
ツォルキン暦（260日周期）の計算
"""
from datetime import datetime
from typing import Dict, Tuple

from ...core.time_manager import TimeManager
from ...models.output_schema import MayanResult


class MayanCalculator:
    """
    マヤ暦計算クラス
    GMT対照法（584283）を使用
    """
    
    # GMT相関定数
    GMT_CORRELATION = 584283
    
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
    
    def __init__(self):
        pass
    
    def calculate(self, birth_dt: datetime) -> MayanResult:
        """
        マヤ暦を計算
        
        Args:
            birth_dt: 生年月日
            
        Returns:
            MayanResult
        """
        # ユリウス日を計算
        jd = TimeManager.to_julian_day(birth_dt)
        
        # KIN番号を計算
        kin = self._calc_kin(jd)
        
        # 太陽の紋章（KIN % 20）
        seal_index = (kin - 1) % 20
        solar_seal = self.SOLAR_SEALS[seal_index]
        
        # 銀河の音（(KIN - 1) % 13 + 1）
        tone = ((kin - 1) % 13) + 1
        
        # ウェイブスペル（13日周期の始まりの紋章）
        wavespell_kin = ((kin - 1) // 13) * 13 + 1
        wavespell_index = (wavespell_kin - 1) % 20
        wavespell = self.WAVESPELLS[wavespell_index]
        
        # ガイドキン
        guide = self._calc_guide(kin, tone, seal_index)
        
        return MayanResult(
            kin_number=kin,
            solar_seal=solar_seal,
            wavespell=wavespell,
            galactic_tone=tone,
            guide=guide
        )
    
    def _calc_kin(self, jd: float) -> int:
        """
        ユリウス日からKIN番号を計算
        
        KIN = (JD - GMT相関定数) % 260 + 1
        """
        # JDを整数に（日の境界は0時）
        jd_int = int(jd + 0.5)
        
        # KIN計算
        kin = ((jd_int - self.GMT_CORRELATION) % 260) + 1
        
        return kin
    
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
