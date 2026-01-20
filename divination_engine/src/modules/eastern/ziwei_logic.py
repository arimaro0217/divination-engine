"""
紫微斗数 命盤構築ロジック
Zi Wei Dou Shu Chart Building Logic

命宮・身宮の決定、五行局算出、主星・副星配置、四化星付与
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

try:
    from ...const import ziwei_const as zc
    from ...core.lunar_core import LunarDate, ChineseHour
except ImportError:
    # 直接実行時のフォールバック
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from src.const import ziwei_const as zc
    from src.core.lunar_core import LunarDate, ChineseHour


# ============================================
# データ構造
# ============================================

@dataclass
class Star:
    """星の情報"""
    name: str                      # 星名
    palace_index: int              # 配置された宮のインデックス（0-11）
    brightness: Optional[int] = None  # 輝度（1-6）
    sihua: Optional[str] = None    # 四化（化禄/化権/化科/化忌）
    category: str = "主星"         # カテゴリ


@dataclass
class Palace:
    """宮の情報"""
    index: int                     # 宮のインデックス（0-11、子=0）
    branch: str                    # 地支名（子丑寅...）
    stem: str                      # 天干名（甲乙丙...）
    palace_type: str               # 宮の種類（命宮、兄弟宮...）
    major_stars: List[Star] = field(default_factory=list)   # 主星
    minor_stars: List[Star] = field(default_factory=list)   # 副星
    bad_stars: List[Star] = field(default_factory=list)     # 煞星
    twelve_phase: str = ""         # 十二長生
    decade_luck: str = ""          # 大限期間
    grid_coords: Tuple[int, int] = (0, 0)  # グリッド座標


@dataclass
class ZiweiChart:
    """紫微斗数命盤"""
    # 基本情報
    birth_datetime: datetime
    lunar_date: LunarDate
    hour_branch: ChineseHour
    gender: str                    # "male" or "female"
    
    # 命盤構成要素
    bureau: int                    # 五行局（2-6）
    bureau_name: str               # 五行局名
    life_palace_index: int         # 命宮位置
    body_palace_index: int         # 身宮位置
    
    # 年月日時の干支
    year_stem: str
    year_branch: str
    
    # 十二宮
    palaces: List[Palace] = field(default_factory=list)
    
    # 主要な星の位置
    ziwei_position: int = 0        # 紫微星の位置
    tianfu_position: int = 0       # 天府星の位置


# ============================================
# ZiweiBuilder: 命盤構築クラス
# ============================================

class ZiweiBuilder:
    """
    紫微斗数 命盤構築クラス
    
    旧暦情報から完全な命盤を構築する
    """
    
    def __init__(self):
        """初期化"""
        self.branches = zc.BRANCHES
        self.stems = zc.STEMS
    
    # ========================================
    # Step 1: 命宮・身宮の決定
    # ========================================
    
    def determine_life_palace(self, lunar_month: int, hour_branch_idx: int) -> int:
        """
        命宮の位置を決定
        
        Args:
            lunar_month: 旧暦月（1-12）
            hour_branch_idx: 時辰インデックス（0-11、子=0）
            
        Returns:
            命宮の地支インデックス（0-11）
        """
        # テーブルから取得
        return zc.LIFE_PALACE_TABLE[lunar_month - 1][hour_branch_idx]
    
    def determine_body_palace(self, lunar_month: int, hour_branch_idx: int) -> int:
        """
        身宮の位置を決定
        
        Args:
            lunar_month: 旧暦月（1-12）
            hour_branch_idx: 時辰インデックス（0-11）
            
        Returns:
            身宮の地支インデックス（0-11）
        """
        return zc.BODY_PALACE_TABLE[lunar_month - 1][hour_branch_idx]
    
    def assign_twelve_palaces(self, life_palace_idx: int) -> List[Tuple[int, str]]:
        """
        命宮を起点に十二宮を配置
        
        Args:
            life_palace_idx: 命宮の地支インデックス
            
        Returns:
            [(地支インデックス, 宮名), ...] のリスト
        """
        palaces = []
        for i, palace_name in enumerate(zc.PALACES):
            # 反時計回りに配置（インデックスを減らす）
            branch_idx = (life_palace_idx - i + 12) % 12
            palaces.append((branch_idx, palace_name))
        return palaces
    
    # ========================================
    # Step 2: 五行局の算出
    # ========================================
    
    def calculate_palace_stem(self, life_palace_idx: int, year_stem_idx: int) -> str:
        """
        命宮の天干を計算
        
        Args:
            life_palace_idx: 命宮の地支インデックス
            year_stem_idx: 年干インデックス
            
        Returns:
            命宮の天干
        """
        # 年干から寅宮の天干を求める
        # 甲己年：寅宮は丙から
        # 乙庚年：寅宮は戊から
        # 丙辛年：寅宮は庚から
        # 丁壬年：寅宮は壬から
        # 戊癸年：寅宮は甲から
        
        yin_stem_base = [
            2,  # 甲年 -> 丙
            4,  # 乙年 -> 戊
            6,  # 丙年 -> 庚
            8,  # 丁年 -> 壬
            0,  # 戊年 -> 甲
            2,  # 己年 -> 丙
            4,  # 庚年 -> 戊
            6,  # 辛年 -> 庚
            8,  # 壬年 -> 壬
            0,  # 癸年 -> 甲
        ]
        
        # 寅宮（インデックス2）からの差分
        palace_offset = (life_palace_idx - 2 + 12) % 12
        stem_idx = (yin_stem_base[year_stem_idx] + palace_offset) % 10
        
        return self.stems[stem_idx]
    
    def calculate_bureau(self, palace_stem: str, palace_branch_idx: int) -> int:
        """
        五行局を計算（納音ベース）
        
        Args:
            palace_stem: 命宮の天干
            palace_branch_idx: 命宮の地支インデックス
            
        Returns:
            五行局（2-6）
        """
        # 地支グループを決定
        branch_group = palace_branch_idx // 2  # 0-5
        
        # 天干グループを決定
        stem_idx = zc.STEM_INDICES[palace_stem]
        stem_group = stem_idx % 5  # 0-4
        
        # テーブルから五行局を取得
        return zc.JU_TABLE[branch_group][stem_group]
    
    # ========================================
    # Step 3: 紫微星・天府星の配置
    # ========================================
    
    def calculate_ziwei_position(self, lunar_day: int, bureau: int) -> int:
        """
        紫微星の位置を計算
        
        紫微斗数の核心となる計算式
        
        Args:
            lunar_day: 旧暦日（1-30）
            bureau: 五行局（2-6）
            
        Returns:
            紫微星の地支インデックス（0-11）
        """
        # テーブルから取得（検証済みの正確な配置）
        if lunar_day <= len(zc.ZIWEI_POSITION_TABLE.get(bureau, [])):
            return zc.ZIWEI_POSITION_TABLE[bureau][lunar_day - 1]
        
        # テーブル外の場合は数式で計算
        # 公式: (日数 + 補正) / 局数
        quotient = (lunar_day - 1) // bureau
        remainder = (lunar_day - 1) % bureau
        
        # 偶数商と奇数商で処理が異なる
        if quotient % 2 == 0:
            position = 2 + quotient + remainder  # 寅からスタート
        else:
            position = 2 + quotient + (bureau - 1 - remainder)
        
        return position % 12
    
    def calculate_tianfu_position(self, ziwei_position: int) -> int:
        """
        天府星の位置を計算
        
        天府星は紫微星と寅申軸で対称の位置
        
        Args:
            ziwei_position: 紫微星の地支インデックス
            
        Returns:
            天府星の地支インデックス
        """
        # 紫微と天府は寅申軸（2-8）で対称
        # 天府 = 4 - 紫微（調整あり）
        tianfu_pos = (4 - ziwei_position + 12) % 12
        
        # 実際の配置テーブル
        tianfu_table = {
            0: 4,   # 子 -> 辰
            1: 3,   # 丑 -> 卯
            2: 2,   # 寅 -> 寅
            3: 1,   # 卯 -> 丑
            4: 0,   # 辰 -> 子
            5: 11,  # 巳 -> 亥
            6: 10,  # 午 -> 戌
            7: 9,   # 未 -> 酉
            8: 8,   # 申 -> 申
            9: 7,   # 酉 -> 未
            10: 6,  # 戌 -> 午
            11: 5,  # 亥 -> 巳
        }
        
        return tianfu_table[ziwei_position]
    
    def place_ziwei_group(self, ziwei_position: int) -> Dict[str, int]:
        """
        紫微星系を配置
        
        Args:
            ziwei_position: 紫微星の位置
            
        Returns:
            {星名: 位置インデックス} の辞書
        """
        positions = {}
        for star, offset in zc.ZIWEI_GROUP_OFFSETS.items():
            positions[star] = (ziwei_position + offset + 12) % 12
        return positions
    
    def place_tianfu_group(self, tianfu_position: int) -> Dict[str, int]:
        """
        天府星系を配置
        
        Args:
            tianfu_position: 天府星の位置
            
        Returns:
            {星名: 位置インデックス} の辞書
        """
        positions = {}
        for star, offset in zc.TIANFU_GROUP_OFFSETS.items():
            positions[star] = (tianfu_position + offset) % 12
        return positions
    
    # ========================================
    # Step 4: 副星の配置
    # ========================================
    
    def place_auxiliary_stars(
        self,
        year_stem_idx: int,
        year_branch_idx: int,
        lunar_month: int,
        lunar_day: int,
        hour_branch_idx: int
    ) -> Dict[str, int]:
        """
        副星・雑星を配置
        
        Args:
            year_stem_idx: 年干インデックス
            year_branch_idx: 年支インデックス
            lunar_month: 旧暦月
            lunar_day: 旧暦日
            hour_branch_idx: 時辰インデックス
            
        Returns:
            {星名: 位置インデックス} の辞書
        """
        positions = {}
        year_stem = self.stems[year_stem_idx]
        
        # === 年干系の星 ===
        
        # 禄存
        positions["禄存"] = zc.LUCUN_TABLE[year_stem]
        
        # 擎羊（禄存 + 1）
        positions["擎羊"] = (positions["禄存"] + 1) % 12
        
        # 陀羅（禄存 - 1）
        positions["陀羅"] = (positions["禄存"] - 1 + 12) % 12
        
        # 天魁
        positions["天魁"] = zc.TIANKUI_TABLE[year_stem]
        
        # 天鉞
        positions["天鉞"] = zc.TIANYUE_TABLE[year_stem]
        
        # === 月系の星 ===
        
        # 左輔（辰から月数分進む）
        positions["左輔"] = (zc.ZUOFU_BASE + lunar_month - 1) % 12
        
        # 右弼（戌から月数分戻る）
        positions["右弼"] = (zc.YOUBI_BASE - lunar_month + 1 + 12) % 12
        
        # 天刑（酉から月数分進む）
        positions["天刑"] = (9 + lunar_month - 1) % 12
        
        # 天姚（丑から月数分進む）
        positions["天姚"] = (1 + lunar_month - 1) % 12
        
        # === 時系の星 ===
        
        # 文昌（戌から時辰分戻る）
        positions["文昌"] = (zc.WENCHANG_BASE - hour_branch_idx + 12) % 12
        
        # 文曲（辰から時辰分進む）
        positions["文曲"] = (zc.WENQU_BASE + hour_branch_idx) % 12
        
        # 地空（亥から時辰分戻る）
        positions["地空"] = (11 - hour_branch_idx + 12) % 12
        
        # 地劫（亥から時辰分進む）
        positions["地劫"] = (11 + hour_branch_idx) % 12
        
        # 火星・鈴星（年支 + 時支法）
        year_group = zc.get_year_branch_group(year_branch_idx)
        positions["火星"] = zc.HUOXING_TABLE[year_group][hour_branch_idx]
        positions["鈴星"] = zc.LINGXING_TABLE[year_group][hour_branch_idx]
        
        # === 年支系の星 ===
        
        # 天喜（卯から年支分戻る）
        positions["天喜"] = (3 - year_branch_idx + 12) % 12
        
        # 紅鸞（卯から年支分進む）
        positions["紅鸞"] = (9 - year_branch_idx + 12) % 12
        
        # 天馬（寅 -> 巳 -> 申 -> 亥の順）
        tian_ma_table = [2, 11, 8, 5, 2, 11, 8, 5, 2, 11, 8, 5]
        positions["天馬"] = tian_ma_table[year_branch_idx]
        
        # 孤辰・寡宿
        guchen_table = [2, 2, 5, 5, 5, 8, 8, 8, 11, 11, 11, 2]
        guasu_table = [10, 10, 1, 1, 1, 4, 4, 4, 7, 7, 7, 10]
        positions["孤辰"] = guchen_table[year_branch_idx]
        positions["寡宿"] = guasu_table[year_branch_idx]
        
        # === 日系の星 ===
        
        # 三台（左輔から日数分進む）
        positions["三台"] = (positions["左輔"] + lunar_day - 1) % 12
        
        # 八座（右弼から日数分戻る）
        positions["八座"] = (positions["右弼"] - lunar_day + 1 + 12) % 12
        
        return positions
    
    # ========================================
    # Step 5: 四化星の付与
    # ========================================
    
    def apply_sihua(self, year_stem: str) -> Dict[str, str]:
        """
        四化星を付与
        
        Args:
            year_stem: 年干
            
        Returns:
            {星名: 四化名} の辞書
        """
        sihua = {}
        transforms = zc.FOUR_TRANSFORMATIONS.get(year_stem, {})
        
        for transform_type, star_name in transforms.items():
            sihua[star_name] = transform_type
        
        return sihua
    
    # ========================================
    # 命盤の構築
    # ========================================
    
    def build_chart(
        self,
        birth_datetime: datetime,
        lunar_date: LunarDate,
        hour_branch: ChineseHour,
        year_stem: str,
        year_branch: str,
        gender: str = "male"
    ) -> ZiweiChart:
        """
        完全な命盤を構築
        
        Args:
            birth_datetime: 生年月日時
            lunar_date: 旧暦日付
            hour_branch: 時辰
            year_stem: 年干
            year_branch: 年支
            gender: 性別
            
        Returns:
            ZiweiChart: 完成した命盤
        """
        year_stem_idx = zc.STEM_INDICES[year_stem]
        year_branch_idx = zc.BRANCH_INDICES[year_branch]
        hour_idx = hour_branch.branch_index
        
        # Step 1: 命宮・身宮の決定
        life_palace_idx = self.determine_life_palace(lunar_date.month, hour_idx)
        body_palace_idx = self.determine_body_palace(lunar_date.month, hour_idx)
        
        # Step 2: 五行局の算出
        palace_stem = self.calculate_palace_stem(life_palace_idx, year_stem_idx)
        bureau = self.calculate_bureau(palace_stem, life_palace_idx)
        bureau_name = zc.JU_NAMES[bureau]
        
        # Step 3: 主星の配置
        ziwei_pos = self.calculate_ziwei_position(lunar_date.day, bureau)
        tianfu_pos = self.calculate_tianfu_position(ziwei_pos)
        
        ziwei_stars = self.place_ziwei_group(ziwei_pos)
        tianfu_stars = self.place_tianfu_group(tianfu_pos)
        all_major_stars = {**ziwei_stars, **tianfu_stars}
        
        # Step 4: 副星の配置
        auxiliary_stars = self.place_auxiliary_stars(
            year_stem_idx, year_branch_idx,
            lunar_date.month, lunar_date.day, hour_idx
        )
        
        # Step 5: 四化の付与
        sihua = self.apply_sihua(year_stem)
        
        # 十二宮を構築
        palace_assignments = self.assign_twelve_palaces(life_palace_idx)
        palaces = []
        
        for branch_idx, palace_name in palace_assignments:
            branch_name = self.branches[branch_idx]
            
            # 宮の天干を計算
            palace_offset = (branch_idx - 2 + 12) % 12
            yin_stem_base_map = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]
            stem_idx = (yin_stem_base_map[year_stem_idx] + palace_offset) % 10
            palace_stem_name = self.stems[stem_idx]
            
            # この宮に入る主星を収集
            major_star_list = []
            for star_name, pos in all_major_stars.items():
                if pos == branch_idx:
                    brightness = None
                    if star_name in zc.STAR_BRIGHTNESS:
                        brightness = zc.STAR_BRIGHTNESS[star_name][branch_idx]
                    
                    star = Star(
                        name=star_name,
                        palace_index=branch_idx,
                        brightness=brightness,
                        sihua=sihua.get(star_name),
                        category="主星"
                    )
                    major_star_list.append(star)
            
            # 副星を収集
            minor_star_list = []
            bad_star_list = []
            
            for star_name, pos in auxiliary_stars.items():
                if pos == branch_idx:
                    star = Star(
                        name=star_name,
                        palace_index=branch_idx,
                        sihua=sihua.get(star_name),
                        category="副星"
                    )
                    
                    # 凶星かどうかで分類
                    if star_name in ["擎羊", "陀羅", "火星", "鈴星", "地空", "地劫"]:
                        bad_star_list.append(star)
                    else:
                        minor_star_list.append(star)
            
            # グリッド座標を取得
            coords = zc.PALACE_GRID_COORDS.get(branch_name, (0, 0))
            
            palace = Palace(
                index=branch_idx,
                branch=branch_name,
                stem=palace_stem_name,
                palace_type=palace_name,
                major_stars=major_star_list,
                minor_stars=minor_star_list,
                bad_stars=bad_star_list,
                grid_coords=coords
            )
            palaces.append(palace)
        
        # ZiweiChartを構築
        chart = ZiweiChart(
            birth_datetime=birth_datetime,
            lunar_date=lunar_date,
            hour_branch=hour_branch,
            gender=gender,
            bureau=bureau,
            bureau_name=bureau_name,
            life_palace_index=life_palace_idx,
            body_palace_index=body_palace_idx,
            year_stem=year_stem,
            year_branch=year_branch,
            palaces=palaces,
            ziwei_position=ziwei_pos,
            tianfu_position=tianfu_pos
        )
        
        return chart


# ============================================
# 大限・小限計算
# ============================================

class DecadeLuckCalculator:
    """
    大限・小限の計算クラス
    """
    
    def __init__(self):
        self.branches = zc.BRANCHES
    
    def calculate_decade_luck(
        self,
        bureau: int,
        gender: str,
        year_stem: str,
        life_palace_idx: int
    ) -> List[Dict[str, Any]]:
        """
        大限（10年運）を計算
        
        Args:
            bureau: 五行局（2-6）
            gender: 性別
            year_stem: 年干
            life_palace_idx: 命宮の位置
            
        Returns:
            各宮の大限期間リスト
        """
        # 年干の陰陽
        is_yang_stem = zc.STEM_YIN_YANG.get(year_stem, "陽") == "陽"
        is_male = gender.lower() == "male"
        
        # 順行・逆行の判定
        # 陽男陰女: 順行（時計回り）
        # 陰男陽女: 逆行（反時計回り）
        if (is_yang_stem and is_male) or (not is_yang_stem and not is_male):
            direction = 1  # 順行
        else:
            direction = -1  # 逆行
        
        # 大限の開始年齢
        start_age = bureau
        
        decade_luck = []
        current_palace = life_palace_idx
        
        for i in range(12):
            end_age = start_age + 9
            
            decade_luck.append({
                "palace_index": current_palace,
                "branch": self.branches[current_palace],
                "start_age": start_age,
                "end_age": end_age,
                "period": f"{start_age}-{end_age}歳"
            })
            
            # 次の宮へ移動
            current_palace = (current_palace + direction + 12) % 12
            start_age = end_age + 1
        
        return decade_luck
    
    def calculate_yearly_luck(
        self,
        birth_year_branch_idx: int,
        target_year: int,
        birth_year: int
    ) -> int:
        """
        小限（年運）の宮を計算
        
        Args:
            birth_year_branch_idx: 生まれ年支インデックス
            target_year: 対象年
            birth_year: 生まれ年
            
        Returns:
            小限の宮インデックス
        """
        age = target_year - birth_year + 1
        
        # 年支に基づく開始宮
        start_palace = birth_year_branch_idx
        
        # 年齢分進む
        yearly_palace = (start_palace + age - 1) % 12
        
        return yearly_palace
