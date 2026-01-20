"""
高精度四柱推命計算エンジン (Precision BaZi Calculator)
蔵干深浅の按分計算、真太陽時による時柱決定を実装
"""
import sys
import io
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Windows環境でのUTF-8出力対応（安全版）
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# 天干・地支の定義
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五行
ELEMENTS = ["木", "火", "土", "金", "水"]


# 蔵干の配分パターン（時間按分用）
# 各月支における蔵干の配分比率
# 形式: {地支インデックス: [(蔵干, 配分比率), ...]}
# 比率の合計は1.0
HIDDEN_STEMS_PATTERN = {
    0: [("癸", 1.0)],  # 子 - 単一蔵干
    1: [("癸", 0.3), ("辛", 0.3), ("己", 0.4)],  # 丑 - 余気・中気・正気
    2: [("戊", 0.233), ("丙", 0.233), ("甲", 0.534)],  # 寅
    3: [("乙", 1.0)],  # 卯
    4: [("乙", 0.3), ("癸", 0.3), ("戊", 0.4)],  # 辰
    5: [("戊", 0.233), ("庚", 0.233), ("丙", 0.534)],  # 巳
    6: [("丁", 1.0)],  # 午
    7: [("丁", 0.3), ("乙", 0.3), ("己", 0.4)],  # 未
    8: [("戊", 0.233), ("壬", 0.233), ("庚", 0.534)],  # 申
    9: [("辛", 1.0)],  # 酉
    10: [("辛", 0.3), ("丁", 0.3), ("戊", 0.4)],  # 戌
    11: [("戊", 0.233), ("甲", 0.233), ("壬", 0.534)],  # 亥
}


@dataclass
class HiddenStemResult:
    """蔵干の計算結果"""
    primary_stem: str  # 主蔵干
    depth_ratio: float  # 深さ比率（0.0-1.0）
    all_stems: List[Tuple[str, float]]  # [(蔵干, 比率), ...]
    elapsed_ratio: float  # 節気間の経過比率


class PrecisionBaZiCalculator:
    """
    高精度四柱推命計算クラス
    
    蔵干の時間按分計算を実装
    """
    
    def __init__(self):
        pass
    
    def calculate_zogan_ratio(
        self,
        birth_jd: float,
        prev_term_jd: float,
        next_term_jd: float,
        month_branch_index: int
    ) -> HiddenStemResult:
        """
        蔵干を節気間の経過時間で按分計算
        
        Args:
            birth_jd: 出生時のユリウス日
            prev_term_jd: 直前の節入りのユリウス日
            next_term_jd: 次の節入りのユリウス日
            month_branch_index: 月支のインデックス（0-11）
            
        Returns:
            HiddenStemResult: 蔵干の計算結果
        """
        # 1. 節気間の総時間（日単位）
        total_duration = next_term_jd - prev_term_jd
        
        # 2. 経過時間（日単位）
        elapsed = birth_jd - prev_term_jd
        
        # 3. 経過比率（0.0 ~ 1.0）
        elapsed_ratio = elapsed / total_duration if total_duration > 0 else 0.0
        
        # 4. 月支の蔵干パターンを取得
        hidden_pattern = HIDDEN_STEMS_PATTERN.get(month_branch_index, [])
        
        if not hidden_pattern:
            # パターンが定義されていない場合
            return HiddenStemResult(
                primary_stem="不明",
                depth_ratio=0.0,
                all_stems=[],
                elapsed_ratio=elapsed_ratio
            )
        
        # 5. 経過比率から該当する蔵干を特定
        accumulated_ratio = 0.0
        primary_stem = hidden_pattern[-1][0]  # デフォルトは正気
        depth_ratio = 1.0
        
        for stem, weight in hidden_pattern:
            accumulated_ratio += weight
            if elapsed_ratio <= accumulated_ratio:
                primary_stem = stem
                # この蔵干内での深さ比率
                depth_in_stem = (accumulated_ratio - elapsed_ratio) / weight
                depth_ratio = depth_in_stem
                break
        
        return HiddenStemResult(
            primary_stem=primary_stem,
            depth_ratio=depth_ratio,
            all_stems=hidden_pattern,
            elapsed_ratio=elapsed_ratio
        )
    
    def get_stem_element(self, stem: str) -> str:
        """天干から五行を取得"""
        elements_map = {
            "甲": "木", "乙": "木",
            "丙": "火", "丁": "火",
            "戊": "土", "己": "土",
            "庚": "金", "辛": "金",
            "壬": "水", "癸": "水"
        }
        return elements_map.get(stem, "不明")
    
    def get_branch_element(self, branch: str) -> str:
        """地支から五行を取得"""
        elements_map = {
            "寅": "木", "卯": "木",
            "巳": "火", "午": "火",
            "辰": "土", "戌": "土", "丑": "土", "未": "土",
            "申": "金", "酉": "金",
            "子": "水", "亥": "水"
        }
        return elements_map.get(branch, "不明")
    
    def explain_zogan_calculation(
        self,
        birth_jd: float,
        prev_term_name: str,
        prev_term_jd: float,
        next_term_name: str,
        next_term_jd: float,
        month_branch: str
    ) -> str:
        """
        蔵干計算の詳細説明を生成
        
        Args:
            birth_jd: 出生時のユリウス日
            prev_term_name: 直前の節入り名
            prev_term_jd: 直前の節入りのユリウス日
            next_term_name: 次の節入り名
            next_term_jd: 次の節入りのユリウス日
            month_branch: 月支
            
        Returns:
            説明文
        """
        import swisseph as swe
        
        # 時間情報の取得
        prev_year, prev_month, prev_day, prev_hour = swe.revjul(prev_term_jd)
        next_year, next_month, next_day, next_hour = swe.revjul(next_term_jd)
        birth_year, birth_month, birth_day, birth_hour = swe.revjul(birth_jd)
        
        # 経過時間の計算
        total_days = next_term_jd - prev_term_jd
        elapsed_days = birth_jd - prev_term_jd
        elapsed_ratio = elapsed_days / total_days if total_days > 0 else 0.0
        
        explanation = f"""
【蔵干深浅の按分計算】

1. 節気の範囲:
   前節入り: {prev_term_name} ({prev_year}年{prev_month}月{prev_day}日 {prev_hour:.2f}時 UT)
   次節入り: {next_term_name} ({next_year}年{next_month}月{next_day}日 {next_hour:.2f}時 UT)
   
2. 節気間の総時間: {total_days:.4f}日 = {total_days * 24:.2f}時間

3. 出生時刻: {birth_year}年{birth_month}月{birth_day}日 {birth_hour:.2f}時 UT
   
4. 経過時間: {elapsed_days:.4f}日 = {elapsed_days * 24:.2f}時間
   経過比率: {elapsed_ratio * 100:.2f}%

5. 月支「{month_branch}」の蔵干配分:
"""
        
        # 蔵干パターンの表示
        branch_index = BRANCHES.index(month_branch) if month_branch in BRANCHES else 0
        pattern = HIDDEN_STEMS_PATTERN.get(branch_index, [])
        
        accumulated = 0.0
        for stem, ratio in pattern:
            start_pct = accumulated * 100
            end_pct = (accumulated + ratio) * 100
            explanation += f"   {stem}: {start_pct:.1f}% ~ {end_pct:.1f}%"
            
            if start_pct / 100 <= elapsed_ratio < end_pct / 100:
                explanation += " ← [該当]"
            
            explanation += "\n"
            accumulated += ratio
        
        return explanation


# ============================================
# テストコード
# ============================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("高精度四柱推命計算エンジン - 蔵干深浅テスト")
    print("="*80)
    
    import swisseph as swe
    from .astro_precise import PrecisionAstroEngine
    
    # 天体計算エンジンを初期化
    astro_engine = PrecisionAstroEngine()
    bazi_calc = PrecisionBaZiCalculator()
    
    # テストケース: 1992年2月17日 17:18 JST
    test_year = 1992
    test_month = 2
    test_day = 17
    test_hour = 17
    test_minute = 18
    
    print(f"\n【テストケース】")
    print(f"出生日時: {test_year}年{test_month}月{test_day}日 {test_hour}:{test_minute:02d} JST")
    
    # 出生時のユリウス日（UT）
    birth_jd = swe.julday(test_year, test_month, test_day, test_hour + test_minute / 60.0 - 9.0)
    
    # 1992年の節気を計算
    print("\n【節気の精密計算】")
    all_terms = astro_engine.calculate_all_solar_terms(test_year)
    
    # 立春と啓蟄を見つける
    lichun = None
    keichitsu = None
    
    for term in all_terms:
        if term.name == "立春":
            lichun = term
        elif term.name == "啓蟄":
            keichitsu = term
    
    if lichun and keichitsu:
        print(f"立春: {lichun.datetime_jst.strftime('%Y年%m月%d日 %H:%M:%S')} JST")
        print(f"啓蟄: {keichitsu.datetime_jst.strftime('%Y年%m月%d日 %H:%M:%S')} JST")
        
        # 月支は「寅」（立春〜啓蟄）
        month_branch = "寅"
        month_branch_index = BRANCHES.index(month_branch)
        
        print(f"\n月支: {month_branch}")
        
        # 蔵干を計算
        zogan_result = bazi_calc.calculate_zogan_ratio(
            birth_jd,
            lichun.jd_ut,
            keichitsu.jd_ut,
            month_branch_index
        )
        
        print(f"\n【蔵干の計算結果】")
        print(f"主蔵干: {zogan_result.primary_stem}")
        print(f"深さ比率: {zogan_result.depth_ratio * 100:.2f}%")
        print(f"経過比率: {zogan_result.elapsed_ratio * 100:.2f}%")
        print(f"\n全蔵干:")
        for stem, ratio in zogan_result.all_stems:
            print(f"  {stem}: {ratio * 100:.1f}%")
        
        # 詳細説明を表示
        explanation = bazi_calc.explain_zogan_calculation(
            birth_jd,
            "立春",
            lichun.jd_ut,
            "啓蟄",
            keichitsu.jd_ut,
            month_branch
        )
        
        print(explanation)
    
    print("\n" + "="*80)
    print("テスト完了")
    print("="*80 + "\n")
