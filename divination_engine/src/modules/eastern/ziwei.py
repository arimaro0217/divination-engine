"""
紫微斗数モジュール
命盤の作成（12宮、14主星配置）

v2.0: pyswissephベースの天文学的旧暦計算に切り替え
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ...core.time_manager import TimeManager
from ...models.output_schema import ZiWeiResult
from ...const import ziwei_const as zw

# 天文学ベースの旧暦計算エンジン
try:
    from ...core.lunar_core import LunisolarEngine, LunarDate as AstroLunarDate
    HAS_LUNISOLAR_ENGINE = True
except ImportError:
    HAS_LUNISOLAR_ENGINE = False
    print("警告: LunisolarEngineが見つかりません。")

# フォールバック: lunardate
HAS_LUNARDATE = False
if not HAS_LUNISOLAR_ENGINE:
    try:
        from lunardate import LunarDate
        HAS_LUNARDATE = True
    except ImportError:
        print("警告: lunardateもインストールされていません。旧暦変換が簡易計算になります。")


class ZiWeiEngine:
    """
    紫微斗数計算エンジン
    旧暦に基づいて命盤を作成
    
    v2.0: pyswissephによる天文学的朔望計算を使用
    
    主な機能：
    - 太陽暦から旧暦への変換（天文学的精度）
    - 命宮・身宮の算出
    - 五行局の決定
    - 紫微星位置の計算
    - 14主星の配置
    - 四化星の取得
    """
    
    def __init__(self):
        """初期化"""
        self.lunar_engine = None
        if HAS_LUNISOLAR_ENGINE:
            self.lunar_engine = LunisolarEngine(use_jst=True)
        elif not HAS_LUNARDATE:
            print("警告: 高精度な紫微斗数計算にはpyswissephまたはlunardateライブラリが必要です。")
    
    def calculate(self, birth_dt: datetime) -> ZiWeiResult:
        """
        紫微斗数を計算
        
        Args:
            birth_dt: 生年月日時（タイムゾーン付き）
            
        Returns:
            ZiWeiResult: 紫微斗数計算結果
            
        Raises:
            ValueError: 計算に失敗した場合
        """
        try:
            # 旧暦に変換
            lunar_date = self._convert_to_lunar(birth_dt)
            
            # 時支を取得
            hour_branch = self._get_hour_branch(birth_dt)
            
            # 命宮位置を計算
            ming_palace = self._calc_ming_palace(lunar_date['month'], hour_branch)
            
            # 身宮位置を計算
            body_palace = self._calc_body_palace(lunar_date['month'], hour_branch)
            
            # 五行局を決定
            ju = self._calc_ju(ming_palace, lunar_date['year_stem_index'])
            
            # 紫微星の位置を計算
            ziwei_pos = self._calc_ziwei_position(lunar_date['day'], ju)
            
            # 全主星を配置
            main_stars = self._place_all_stars(ziwei_pos)
            
            # 四化星を取得
            year_stem = zw.STEMS[lunar_date['year_stem_index']]
            four_trans = zw.FOUR_TRANSFORMATIONS.get(year_stem, {})
            
            return ZiWeiResult(
                lunar_date=f"{lunar_date['year']}年{lunar_date['month']}月{lunar_date['day']}日",
                ming_palace=zw.BRANCHES[ming_palace],
                body_palace=zw.BRANCHES[body_palace],
                main_stars=main_stars,
                four_transformations=four_trans
            )
        except Exception as e:
            # エラー時は失敗結果を返す
            return ZiWeiResult(
                divination_type="ziwei",
                success=False,
                error_message=f"紫微斗数計算エラー: {str(e)}",
                lunar_date="",
                ming_palace="",
                body_palace="",
                main_stars={},
                four_transformations={}
            )
    
    def _convert_to_lunar(self, dt: datetime) -> Dict:
        """
        太陽暦から旧暦に変換
        
        優先順位:
        1. LunisolarEngine (pyswisseph天文学計算)
        2. lunardate (テーブルベース)
        3. 簡易計算 (非推奨)
        
        Args:
            dt: 太陽暦の日時
            
        Returns:
            旧暦情報の辞書（year, month, day, year_stem_index, is_leap_month）
        """
        # 優先: pyswissephベースの天文学的計算
        if self.lunar_engine is not None:
            try:
                lunar = self.lunar_engine.convert_to_lunar(dt)
                
                # 年干支のインデックスを計算
                # 1984年が甲子年（インデックス0）
                year_offset = (lunar.year - 1984) % 60
                year_stem_index = year_offset % 10
                
                return {
                    'year': lunar.year,
                    'month': lunar.month,
                    'day': lunar.day,
                    'is_leap_month': lunar.is_leap_month,
                    'year_stem_index': year_stem_index
                }
            except Exception as e:
                print(f"LunisolarEngine変換エラー: {e}、フォールバック")
        
        # フォールバック: lunardate
        if HAS_LUNARDATE:
            try:
                lunar = LunarDate.fromSolarDate(dt.year, dt.month, dt.day)
                
                year_offset = (lunar.year - 1984) % 60
                year_stem_index = year_offset % 10
                
                return {
                    'year': lunar.year,
                    'month': lunar.month,
                    'day': lunar.day,
                    'is_leap_month': False,  # lunardateは閏月情報を持たない場合あり
                    'year_stem_index': year_stem_index
                }
            except Exception as e:
                print(f"lunardate変換エラー: {e}、簡易計算にフォールバック")
        
        # 最終フォールバック: 簡易計算（非推奨）
        # 注意: これは近似値であり、正確な旧暦変換ではない
        year_offset = (dt.year - 1984) % 60
        year_stem_index = year_offset % 10
        
        return {
            'year': dt.year,
            'month': dt.month,
            'day': dt.day,
            'is_leap_month': False,
            'year_stem_index': year_stem_index
        }
    
    def _get_hour_branch(self, dt: datetime) -> int:
        """
        出生時刻から時支インデックスを取得
        
        時支は2時間ごとに変わる：
        子（23-01）、丑（01-03）、寅（03-05）...
        
        Args:
            dt: 日時
            
        Returns:
            時支インデックス（0-11）
        """
        hour = dt.hour
        # 23:00-01:00が子の刻（インデックス0）
        # (hour + 1) // 2で計算
        return (hour + 1) // 2 % 12
    
    def _calc_ming_palace(self, lunar_month: int, hour_branch: int) -> int:
        """
        命宮位置を計算
        
        計算式: (寅宮 + 月数 - 時支 - 1) % 12
        寅宮はインデックス2
        
        Args:
            lunar_month: 旧暦月（1-12）
            hour_branch: 時支インデックス（0-11）
            
        Returns:
            命宮のインデックス（0-11）
        """
        # 寅宮(=2)を起点に、月を加え、時を引く
        position = (2 + lunar_month - 1 - hour_branch) % 12
        return position
    
    def _calc_body_palace(self, lunar_month: int, hour_branch: int) -> int:
        """
        身宮位置を計算
        
        計算式: (寅宮 + 月数 + 時支 - 1) % 12
        
        Args:
            lunar_month: 旧暦月（1-12）
            hour_branch: 時支インデックス（0-11）
            
        Returns:
            身宮のインデックス（0-11）
        """
        position = (2 + lunar_month - 1 + hour_branch) % 12
        return position
    
    def _calc_ju(self, ming_palace: int, year_stem_index: int) -> int:
        """
        五行局を計算
        
        命宮の地支と年干から五行局を決定。
        五行局は2（水二局）から6（火六局）までの5種類。
        
        Args:
            ming_palace: 命宮インデックス（0-11）
            year_stem_index: 年干インデックス（0-9）
            
        Returns:
            局数（2=水二局, 3=木三局, 4=金四局, 5=土五局, 6=火六局）
        """
        # 命宮の地支を2つずつグループ化（子丑、寅卯、辰巳...）
        palace_group = ming_palace // 2  # 0-5のグループ
        
        # 年干を2つずつグループ化（甲乙、丙丁、戊己...）
        stem_group = year_stem_index // 2  # 0-4のグループ
        
        # 五行局判定テーブルから取得
        ju = zw.JU_TABLE[palace_group][stem_group]
        
        return ju
    
    def _calc_ziwei_position(self, lunar_day: int, ju: int) -> int:
        """
        紫微星の位置を計算
        
        旧暦の日と五行局から紫微星の位置を決定。
        
        Args:
            lunar_day: 旧暦の日（1-30）
            ju: 五行局（2-6）
            
        Returns:
            紫微星の地支インデックス（0-11）
        """
        if ju in zw.ZIWEI_POSITION_TABLE:
            table = zw.ZIWEI_POSITION_TABLE[ju]
            if 1 <= lunar_day <= 30:
                return table[lunar_day - 1]
        
        # デフォルト（テーブルにない場合の簡易計算）
        return (lunar_day + ju - 1) % 12
    
    def _place_all_stars(self, ziwei_pos: int) -> Dict[str, List[str]]:
        """
        全主星を12宮に配置
        
        紫微星の位置を基準に、紫微星群と天府星群を配置する。
        
        Args:
            ziwei_pos: 紫微星の地支インデックス（0-11）
            
        Returns:
            各地支に配置された星のリスト
        """
        # 12宮の初期化
        result = {zw.BRANCHES[i]: [] for i in range(12)}
        
        # 紫微星群を配置
        for star, offset in zw.ZIWEI_GROUP_OFFSETS.items():
            pos = (ziwei_pos + offset) % 12
            result[zw.BRANCHES[pos]].append(star)
        
        # 天府星の位置を計算（紫微と対称関係）
        # 紫微星と天府星は互いに対照的な位置に配置される
        tianfu_pos = (12 - ziwei_pos + 4) % 12
        
        # 天府星群を配置
        for star, offset in zw.TIANFU_GROUP_OFFSETS.items():
            pos = (tianfu_pos + offset) % 12
            result[zw.BRANCHES[pos]].append(star)
        
        return result
    
    def get_palace_details(self, ming_palace_index: int) -> Dict[str, str]:
        """
        宮の詳細情報を取得
        
        Args:
            ming_palace_index: 命宮のインデックス（0-11）
            
        Returns:
            宮の詳細情報
        """
        palace_mapping = {}
        for i in range(12):
            palace_index = (ming_palace_index + i) % 12
            palace_mapping[zw.BRANCHES[palace_index]] = zw.PALACES[i]
        
        return palace_mapping
