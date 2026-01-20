"""
四柱推命 - 刑冲会合・神殺・蔵干深浅の判定ロジック

このモジュールは四柱推命の高度な判定ロジックを実装します：
- 蔵干深浅の精密計算（節入りからの進捗率による按分）
- 刑冲会合（三合・方合・六合・対冲・三刑など）
- 神殺（特殊星）の判定
- 五行バランスの計算
"""

import sys
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import swisseph as swe

from ...const import bazi_const as bc
from ...core.astro_precise import PrecisionAstroEngine

# Windows環境でのUTF-8出力対応（安全版）
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ============================================
# 蔵干深浅の計算クラス
# ============================================

class ZoganCalculator:
    """
    蔵干深浅の精密計算クラス
    
    阿部泰山流に基づき、月支蔵干を節入りからの経過率で決定します。
    固定日数テーブルは使用せず、節入り間の総分数による按分計算を行います。
    """
    
    def __init__(self):
        """初期化"""
        self.astro_engine = PrecisionAstroEngine()
    
    def calc_month_zogan(
        self, 
        birth_datetime: datetime,
        month_branch: str,
        latitude: float,
        longitude: float
    ) -> Tuple[str, float]:
        """
        月支蔵干を精密に計算
        
        節入りから次の節入りまでの総分数を分母とし、
        出生時点の経過分数を分子として進捗率を計算します。
        
        Args:
            birth_datetime: 出生日時
            month_branch: 月支
            latitude: 緯度
            longitude: 経度
        
        Returns:
            (蔵干, 進捗率)
        """
        # 出生日のJDを計算
        birth_jd = swe.julday(
            birth_datetime.year, 
            birth_datetime.month, 
            birth_datetime.day,
            birth_datetime.hour + birth_datetime.minute / 60.0
        )
        
        # 現在の節入り日時を取得
        current_jieqi_jd, _ = self._find_previous_jieqi(birth_jd)
        
        # 次の節入り日時を取得
        next_jieqi_jd, _ = self._find_next_jieqi(birth_jd)
        
        # 節入り間の総時間（分）
        total_minutes = (next_jieqi_jd - current_jieqi_jd) * 24 * 60
        
        # 経過時間（分）
        elapsed_minutes = (birth_jd - current_jieqi_jd) * 24 * 60
        
        # 進捗率
        progress_ratio = elapsed_minutes / total_minutes if total_minutes > 0 else 0.0
        
        # 蔵干を決定
        zogan = self._determine_zogan_by_ratio(month_branch, progress_ratio)
        
        return zogan, progress_ratio
    
    def _determine_zogan_by_ratio(self, branch: str, ratio: float) -> str:
        """
        進捗率に基づいて蔵干を決定
        
        Args:
            branch: 地支
            ratio: 進捗率（0.0〜1.0）
        
        Returns:
            蔵干（天干）
        """
        depth_table = bc.ZOGAN_DEPTH_RATIO.get(branch, [("本気", 0.0, 1.0)])
        zogan_table = bc.ZOGAN_TABLE.get(branch, {"本気": None})
        
        for zogan_type, start_ratio, end_ratio in depth_table:
            if start_ratio <= ratio < end_ratio:
                return zogan_table.get(zogan_type, zogan_table.get("本気"))
        
        # デフォルトは本気
        return zogan_table.get("本気")
    
    def _find_previous_jieqi(self, target_jd: float) -> Tuple[float, int]:
        """直前の節入りを探す"""
        # 簡易実装：現在の太陽黄経から節入りを逆算
        sun_lon = swe.calc_ut(target_jd, swe.SUN)[0][0]
        
        # 節入りの太陽黄経（15度刻み、節気のみ）
        jieqi_angles = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]
        
        # 直前の節入り角度を見つける
        prev_angle = None
        for angle in sorted(jieqi_angles, reverse=True):
            if sun_lon >= angle or (angle == 315 and sun_lon < 45):
                prev_angle = angle
                break
        
        if prev_angle is None:
            prev_angle = 285
        
        # その角度になったJDを計算
        year = swe.revjul(target_jd)[0]
        month = swe.revjul(target_jd)[1]
        
        jd, _, _ = self.astro_engine.find_exact_solar_term_time(prev_angle, year, month)
        
        return jd, prev_angle
    
    def _find_next_jieqi(self, target_jd: float) -> Tuple[float, int]:
        """次の節入りを探す"""
        sun_lon = swe.calc_ut(target_jd, swe.SUN)[0][0]
        
        jieqi_angles = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]
        
        # 次の節入り角度を見つける
        next_angle = None
        for angle in sorted(jieqi_angles):
            if sun_lon < angle:
                next_angle = angle
                break
        
        if next_angle is None:
            next_angle = 315  # 次は立春
        
        year = swe.revjul(target_jd)[0]
        month = swe.revjul(target_jd)[1]
        
        jd, _, _ = self.astro_engine.find_exact_solar_term_time(next_angle, year, month)
        
        return jd, next_angle


# ============================================
# 刑冲会合の判定クラス
# ============================================

class InteractionLogic:
    """
    命式内の干支相互作用を判定するクラス
    
    - 干合（天干の合）
    - 六合（地支の合）
    - 三合会局
    - 半会
    - 方合
    - 対冲
    - 三刑・自刑
    - 六害・六破
    """
    
    @staticmethod
    def find_kango(stems: List[str]) -> List[Tuple[str, str, str]]:
        """
        干合を検出
        
        Args:
            stems: 天干のリスト（年干、月干、日干、時干）
        
        Returns:
            [(干1, 干2, 化気五行), ...]
        """
        kango_found = []
        
        for pair in bc.KANGO_PAIRS:
            if pair[0] in stems and pair[1] in stems:
                transform = bc.KANGO_TRANSFORM.get(pair, "")
                kango_found.append((pair[0], pair[1], transform))
        
        return kango_found
    
    @staticmethod
    def find_zhihe(branches: List[str]) -> List[Tuple[str, str]]:
        """
        六合（支合）を検出
        
        Args:
            branches: 地支のリスト
        
        Returns:
            [(支1, 支2), ...]
        """
        zhihe_found = []
        
        for pair in bc.ZHIHE_PAIRS:
            if pair[0] in branches and pair[1] in branches:
                zhihe_found.append(pair)
        
        return zhihe_found
    
    @staticmethod
    def find_sango(branches: List[str]) -> List[Tuple[str, List[str]]]:
        """
        三合会局を検出
        
        Args:
            branches: 地支のリスト
        
        Returns:
            [(局名, 構成支), ...]
        """
        sango_found = []
        
        for name, (required_branches, element) in bc.SANGO_CORRECT.items():
            if all(b in branches for b in required_branches):
                sango_found.append((name, required_branches))
        
        return sango_found
    
    @staticmethod
    def find_hange(branches: List[str]) -> List[Tuple[str, Tuple[str, str]]]:
        """
        半会を検出
        
        Args:
            branches: 地支のリスト
        
        Returns:
            [(局名, (支1, 支2)), ...]
        """
        hange_found = []
        
        for name, pairs in bc.HANGE_SETS.items():
            for pair in pairs:
                if pair[0] in branches and pair[1] in branches:
                    hange_found.append((name, pair))
        
        return hange_found
    
    @staticmethod
    def find_hosani(branches: List[str]) -> List[Tuple[str, List[str]]]:
        """
        方合（方三位）を検出
        
        Args:
            branches: 地支のリスト
        
        Returns:
            [(方名, 構成支), ...]
        """
        hosani_found = []
        
        for name, required_branches in bc.HOSANI_SETS.items():
            if all(b in branches for b in required_branches):
                hosani_found.append((name, required_branches))
        
        return hosani_found
    
    @staticmethod
    def find_chu(branches: List[str]) -> List[Tuple[str, str]]:
        """
        対冲を検出
        
        Args:
            branches: 地支のリスト
        
        Returns:
            [(支1, 支2), ...]
        """
        chu_found = []
        
        for pair in bc.CHU_PAIRS:
            if pair[0] in branches and pair[1] in branches:
                chu_found.append(pair)
        
        return chu_found
    
    @staticmethod
    def find_kei(branches: List[str]) -> List[Tuple[str, List[str]]]:
        """
        三刑・自刑を検出
        
        Args:
            branches: 地支のリスト
        
        Returns:
            [(刑の種類, 構成支), ...]
        """
        kei_found = []
        
        # 三刑
        for name, required_branches in bc.SANKEI.items():
            matched = [b for b in required_branches if b in branches]
            if len(matched) >= 2:
                kei_found.append((name, matched))
        
        # 自刑
        for branch in branches:
            if branch in bc.JIKEI and branches.count(branch) >= 2:
                kei_found.append(("自刑", [branch, branch]))
        
        return kei_found
    
    @staticmethod
    def find_gai(branches: List[str]) -> List[Tuple[str, str]]:
        """
        六害を検出
        """
        gai_found = []
        
        for pair in bc.GAIKEKI_PAIRS:
            if pair[0] in branches and pair[1] in branches:
                gai_found.append(pair)
        
        return gai_found
    
    @staticmethod
    def find_ha(branches: List[str]) -> List[Tuple[str, str]]:
        """
        六破を検出
        """
        ha_found = []
        
        for pair in bc.ROKUHA_PAIRS:
            if pair[0] in branches and pair[1] in branches:
                ha_found.append(pair)
        
        return ha_found
    
    @staticmethod
    def analyze_all_interactions(stems: List[str], branches: List[str]) -> Dict:
        """
        全ての相互作用を分析
        
        Returns:
            相互作用の辞書
        """
        return {
            "kango": InteractionLogic.find_kango(stems),
            "zhihe": InteractionLogic.find_zhihe(branches),
            "sango": InteractionLogic.find_sango(branches),
            "hange": InteractionLogic.find_hange(branches),
            "hosani": InteractionLogic.find_hosani(branches),
            "chu": InteractionLogic.find_chu(branches),
            "kei": InteractionLogic.find_kei(branches),
            "gai": InteractionLogic.find_gai(branches),
            "ha": InteractionLogic.find_ha(branches),
        }


# ============================================
# 神殺（特殊星）判定クラス
# ============================================

class SpecialStars:
    """
    神殺（特殊星）を判定するクラス
    
    天乙貴人、駅馬、桃花、華蓋、羊刃、魁罡などを判定します。
    """
    
    @staticmethod
    def find_tenotsu_kijin(day_stem: str, branches: List[str]) -> List[str]:
        """
        天乙貴人を検出
        
        Args:
            day_stem: 日干
            branches: 全地支のリスト
        
        Returns:
            天乙貴人が成立する地支のリスト
        """
        kijin_branches = bc.TENOTSU_KIJIN.get(day_stem, [])
        return [b for b in branches if b in kijin_branches]
    
    @staticmethod
    def find_ekiba(year_branch: str, branches: List[str]) -> List[str]:
        """
        駅馬を検出
        
        Args:
            year_branch: 年支（または日支）
            branches: 全地支のリスト
        
        Returns:
            駅馬が成立する地支のリスト
        """
        ekiba_branch = bc.EKIBA.get(year_branch)
        if ekiba_branch and ekiba_branch in branches:
            return [ekiba_branch]
        return []
    
    @staticmethod
    def find_touka(year_branch: str, branches: List[str]) -> List[str]:
        """
        桃花（咸池）を検出
        """
        touka_branch = bc.TOUKA.get(year_branch)
        if touka_branch and touka_branch in branches:
            return [touka_branch]
        return []
    
    @staticmethod
    def find_kagai(year_branch: str, branches: List[str]) -> List[str]:
        """
        華蓋を検出
        """
        kagai_branch = bc.KAGAI.get(year_branch)
        if kagai_branch and kagai_branch in branches:
            return [kagai_branch]
        return []
    
    @staticmethod
    def find_youjin(day_stem: str, branches: List[str]) -> List[str]:
        """
        羊刃を検出（陽干のみ）
        """
        youjin_branch = bc.YOUJIN.get(day_stem)
        if youjin_branch and youjin_branch in branches:
            return [youjin_branch]
        return []
    
    @staticmethod
    def find_kaigou(ganzhi_list: List[str]) -> List[str]:
        """
        魁罡を検出
        """
        return [gz for gz in ganzhi_list if gz in bc.KAIGOU]
    
    @staticmethod
    def find_kouen(day_stem: str, branches: List[str]) -> List[str]:
        """
        紅艶を検出
        """
        kouen_branch = bc.KOUEN.get(day_stem)
        if kouen_branch and kouen_branch in branches:
            return [kouen_branch]
        return []
    
    @staticmethod
    def find_kinyoroku(day_stem: str, branches: List[str]) -> List[str]:
        """
        金與禄を検出
        """
        kinyoroku_branch = bc.KINYOROKU.get(day_stem)
        if kinyoroku_branch and kinyoroku_branch in branches:
            return [kinyoroku_branch]
        return []
    
    @staticmethod
    def analyze_all_stars(
        day_stem: str,
        year_branch: str,
        branches: List[str],
        ganzhi_list: List[str]
    ) -> Dict[str, List[str]]:
        """
        全ての神殺を分析
        """
        return {
            "天乙貴人": SpecialStars.find_tenotsu_kijin(day_stem, branches),
            "駅馬": SpecialStars.find_ekiba(year_branch, branches),
            "桃花": SpecialStars.find_touka(year_branch, branches),
            "華蓋": SpecialStars.find_kagai(year_branch, branches),
            "羊刃": SpecialStars.find_youjin(day_stem, branches),
            "魁罡": SpecialStars.find_kaigou(ganzhi_list),
            "紅艶": SpecialStars.find_kouen(day_stem, branches),
            "金與禄": SpecialStars.find_kinyoroku(day_stem, branches),
        }


# ============================================
# 五行バランス計算クラス
# ============================================

class GogyoBalance:
    """
    五行バランスを計算するクラス
    
    レーダーチャート表示用の数値化を行います。
    """
    
    @staticmethod
    def calculate_balance(
        stems: List[str],
        branches: List[str],
        month_zogan: str = None
    ) -> Dict[str, float]:
        """
        五行のエネルギーバランスを計算
        
        Args:
            stems: 天干のリスト
            branches: 地支のリスト
            month_zogan: 月支蔵干（深浅計算済み）
        
        Returns:
            {"木": 2.0, "火": 1.5, ...}
        """
        balance = {"木": 0.0, "火": 0.0, "土": 0.0, "金": 0.0, "水": 0.0}
        
        # 天干のエネルギー
        for stem in stems:
            if stem:
                element, _ = bc.STEM_WUXING.get(stem, (None, None))
                if element:
                    balance[element] += bc.STEM_ENERGY
        
        # 地支のエネルギー（蔵干を含む）
        for branch in branches:
            if branch:
                zogan_info = bc.ZOGAN_TABLE.get(branch, {})
                
                # 本気
                honki = zogan_info.get("本気")
                if honki:
                    element, _ = bc.STEM_WUXING.get(honki, (None, None))
                    if element:
                        balance[element] += bc.BRANCH_ENERGY["本気"]
                
                # 中気
                chuki = zogan_info.get("中気")
                if chuki:
                    element, _ = bc.STEM_WUXING.get(chuki, (None, None))
                    if element:
                        balance[element] += bc.BRANCH_ENERGY["中気"]
                
                # 余気
                yoki = zogan_info.get("余気")
                if yoki:
                    element, _ = bc.STEM_WUXING.get(yoki, (None, None))
                    if element:
                        balance[element] += bc.BRANCH_ENERGY["余気"]
        
        return balance
