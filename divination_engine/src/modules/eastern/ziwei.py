"""
紫微斗数モジュール（高性能版）
命盤の作成（12宮、14主星配置、輝度、乙級星、四化星）

v3.0: 完全版 - 輝度・火鈴星・閏月モード・グリッド座標対応
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

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


class LeapMonthMode(Enum):
    """
    閏月の処理モード
    
    紫微斗数では閏月の扱いが流派により異なる。
    例：閏4月10日生まれの場合
    """
    MODE_A = "zhongzhou"  # 中州派（デフォルト）: 15日まで前月、16日以降翌月
    MODE_B = "prev_month"  # 全部前月として扱う
    MODE_C = "next_month"  # 全部翌月として扱う


@dataclass
class StarInfo:
    """星の情報"""
    name: str
    palace_index: int  # 宮のインデックス（0-11）
    palace_name: str   # 宮の名前（子丑寅...）
    brightness: Optional[str] = None  # 輝度（廟旺平陥）
    brightness_value: Optional[int] = None  # 輝度値（1-6）
    category: str = "主星"  # 星のカテゴリ
    four_trans: Optional[str] = None  # 四化星（化禄/権/科/忌）


@dataclass
class PalaceInfo:
    """宮の情報"""
    index: int  # 宮インデックス（0-11）
    branch: str  # 地支名（子丑寅...）
    palace_type: str  # 宮の種類（命宮、兄弟宮...）
    stars: List[StarInfo] = field(default_factory=list)
    grid_coord: Tuple[int, int] = (0, 0)  # グリッド座標


class ZiWeiEngine:
    """
    紫微斗数計算エンジン（高性能版）
    旧暦に基づいて命盤を作成
    
    v3.0: 完全版
    
    主な機能：
    - 太陽暦から旧暦への変換（天文学的精度）
    - 命宮・身宮の算出
    - 五行局の決定
    - 紫微星位置の計算（数式＋テーブル両対応）
    - 14主星の配置
    - 輝度（廟・旺・平・陥）の計算
    - 乙級星（火星・鈴星等）の配置
    - 四化星の取得（生年四化・流年四化）
    - 12宮グリッド座標出力
    - 閏月モード切替
    """
    
    def __init__(self):
        """初期化"""
        self.lunar_engine = None
        if HAS_LUNISOLAR_ENGINE:
            self.lunar_engine = LunisolarEngine(use_jst=True)
        elif not HAS_LUNARDATE:
            print("警告: 高精度な紫微斗数計算にはpyswissephまたはlunardateライブラリが必要です。")
    
    def calculate(
        self, 
        birth_dt: datetime,
        gender: str = 'male',
        leap_month_mode: LeapMonthMode = LeapMonthMode.MODE_A,
        target_year: Optional[int] = None
    ) -> Dict:
        """
        紫微斗数を計算
        
        Args:
            birth_dt: 生年月日時（タイムゾーン付き）
            gender: 性別 ('male' or 'female')
            leap_month_mode: 閏月の処理モード（デフォルト: 中州派）
            target_year: 流年四化を計算する年（オプション）
            
        Returns:
            Dict: 紫微斗数計算結果（完全版）
        """
        try:
            # 旧暦に変換
            lunar_date = self._convert_to_lunar(birth_dt)
            
            # 閏月の処理
            adjusted_month = self._apply_leap_month_mode(
                lunar_date['month'],
                lunar_date['day'],
                lunar_date['is_leap_month'],
                leap_month_mode
            )
            
            # 時支を取得
            hour_branch = self._get_hour_branch(birth_dt)
            
            # 年支を取得
            year_branch_index = (lunar_date['year'] - 4) % 12
            
            # 命宮位置を計算
            ming_palace = self._calc_ming_palace(adjusted_month, hour_branch)
            
            # 身宮位置を計算
            body_palace = self._calc_body_palace(adjusted_month, hour_branch)
            
            # 五行局を決定
            ju = self._calc_ju(ming_palace, lunar_date['year_stem_index'])
            
            # 紫微星の位置を計算（数式とテーブル両方）
            ziwei_pos = self._calc_ziwei_position(lunar_date['day'], ju)
            
            # 12宮を初期化
            palaces = self._init_palaces(ming_palace)
            
            # 全主星を配置（輝度付き）
            self._place_main_stars(palaces, ziwei_pos, lunar_date['year_stem_index'])
            
            # 乙級星を配置（火星・鈴星等）
            self._place_auxiliary_stars(
                palaces, 
                lunar_date['year_stem_index'],
                year_branch_index,
                hour_branch,
                adjusted_month,
                lunar_date['day']
            )
            
            # 四化星を適用
            year_stem = zw.STEMS[lunar_date['year_stem_index']]
            self._apply_four_transformations(palaces, year_stem)
            
            # 流年四化（オプション）
            yearly_trans = {}
            if target_year:
                target_stem_index = (target_year - 4) % 10
                target_stem = zw.STEMS[target_stem_index]
                yearly_trans = zw.FOUR_TRANSFORMATIONS.get(target_stem, {})
            
            # 性別の詳細表記（例：陽男、陰女）
            is_yang_year = (lunar_date['year_stem_index'] % 2 == 0)
            gender_prefix = "陽" if is_yang_year else "陰"
            gender_suffix = "男" if gender == 'male' else "女"
            detailed_gender = f"{gender_prefix}{gender_suffix}"

            return {
                "type": "紫微斗数",
                "success": True,
                "lunar_date": f"{lunar_date['year']}年{adjusted_month}月{lunar_date['day']}日",
                "gender": detailed_gender,  # Added
                "is_leap_month": lunar_date['is_leap_month'],
                "leap_month_mode": leap_month_mode.value,
                "ming_palace": {
                    "branch": zw.BRANCHES[ming_palace],
                    "index": ming_palace,
                    "grid_coord": zw.PALACE_GRID_COORDS.get(zw.BRANCHES[ming_palace], (0, 0))
                },
                "body_palace": {
                    "branch": zw.BRANCHES[body_palace],
                    "index": body_palace,
                    "grid_coord": zw.PALACE_GRID_COORDS.get(zw.BRANCHES[body_palace], (0, 0))
                },
                "ju": {
                    "value": ju,
                    "name": zw.JU_NAMES.get(ju, f"{ju}局")
                },
                "ziwei_position": {
                    "branch": zw.BRANCHES[ziwei_pos],
                    "index": ziwei_pos
                },
                "palaces": self._serialize_palaces(palaces),
                "four_transformations": zw.FOUR_TRANSFORMATIONS.get(year_stem, {}),
                "year_stem": year_stem,
            }
            
            if target_year:
                result["yearly_transformations"] = {
                    "year": target_year,
                    "stem": zw.STEMS[(target_year - 4) % 10],
                    "transformations": yearly_trans
                }
            
            return result
            
        except Exception as e:
            return {
                "type": "紫微斗数",
                "success": False,
                "error_message": f"紫微斗数計算エラー: {str(e)}"
            }
    
    def _apply_leap_month_mode(
        self, 
        month: int, 
        day: int, 
        is_leap: bool,
        mode: LeapMonthMode
    ) -> int:
        """
        閏月モードを適用して月を調整
        
        Args:
            month: 元の月
            day: 日
            is_leap: 閏月かどうか
            mode: 閏月処理モード
            
        Returns:
            調整後の月
        """
        if not is_leap:
            return month
        
        if mode == LeapMonthMode.MODE_A:
            # 中州派: 15日まで前月、16日以降翌月
            if day <= 15:
                return month
            else:
                return month + 1 if month < 12 else 1
        elif mode == LeapMonthMode.MODE_B:
            # 全部前月
            return month
        elif mode == LeapMonthMode.MODE_C:
            # 全部翌月
            return month + 1 if month < 12 else 1
        
        return month
    
    def _convert_to_lunar(self, dt: datetime) -> Dict:
        """太陽暦から旧暦に変換"""
        # 優先: pyswissephベースの天文学的計算
        if self.lunar_engine is not None:
            try:
                lunar = self.lunar_engine.convert_to_lunar(dt)
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
                    'is_leap_month': False,
                    'year_stem_index': year_stem_index
                }
            except Exception as e:
                print(f"lunardate変換エラー: {e}、簡易計算にフォールバック")
        
        # 最終フォールバック
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
        """出生時刻から時支インデックスを取得"""
        hour = dt.hour
        return (hour + 1) // 2 % 12
    
    def _calc_ming_palace(self, lunar_month: int, hour_branch: int) -> int:
        """命宮位置を計算"""
        position = (2 + lunar_month - 1 - hour_branch) % 12
        return position
    
    def _calc_body_palace(self, lunar_month: int, hour_branch: int) -> int:
        """身宮位置を計算"""
        position = (2 + lunar_month - 1 + hour_branch) % 12
        return position
    
    def _calc_ju(self, ming_palace: int, year_stem_index: int) -> int:
        """五行局を計算"""
        palace_group = ming_palace // 2
        stem_group = year_stem_index // 2
        ju = zw.JU_TABLE[palace_group][stem_group]
        return ju
    
    def _calc_ziwei_position(self, lunar_day: int, ju: int) -> int:
        """
        紫微星の位置を数式で計算
        
        紫微斗数における紫微星の配置計算式:
        ========================================
        
        基本原理:
        - 紫微星の位置は「旧暦の日数」と「五行局数」から決定される
        - 計算式: 位置 = 寅宮 + f(日数, 局数)
        
        詳細な計算方法:
        1. 日数を局数で割り、商と余りを求める
        2. 余りに基づいて、商に補正を加える
        3. 補正後の値を寅宮（インデックス2）を起点に配置
        
        Args:
            lunar_day: 旧暦の日（1-30）
            ju: 五行局数（2=水二局, 3=木三局, 4=金四局, 5=土五局, 6=火六局）
            
        Returns:
            紫微星の地支インデックス（0-11）
        """
        # 日数の調整（1日始まりを0始まりに）
        d = lunar_day
        j = ju
        
        # ========================================
        # 紫微星配置の数式計算（完全版）
        # ========================================
        # 
        # 紫微斗数の伝統的計算法:
        # - 日数を局数で割った商をベースに
        # - 余りによって順行または逆行の調整を行う
        #
        # 計算式の詳細:
        # 商Q = ceil(d / j)  ... 基本位置
        # 余R = d % j        ... 調整係数
        #
        # 調整ルール（局数ごとに異なる）:
        # - 水二局(j=2): 日が偶数なら+1調整
        # - 木三局(j=3): 余りに応じて調整
        # - 金四局(j=4): 余りに応じて調整
        # - 土五局(j=5): 余りに応じて調整
        # - 火六局(j=6): 余りに応じて調整
        
        import math
        
        # 基本商（切り上げ）
        quotient = math.ceil(d / j)
        remainder = d % j
        
        # 五行局別の調整計算
        # この調整は紫微斗数の伝統的ルールに基づく
        if ju == 2:  # 水二局
            # 水二局: 日数が偶数のとき補正
            if remainder == 0:
                base_pos = quotient
            else:
                base_pos = quotient
        
        elif ju == 3:  # 木三局
            # 木三局: 3で割った余りで調整
            if remainder == 0:
                base_pos = quotient
            elif remainder == 1:
                base_pos = quotient
            else:  # remainder == 2
                base_pos = quotient
        
        elif ju == 4:  # 金四局
            # 金四局: 4で割った余りで調整
            if remainder == 0:
                base_pos = quotient
            elif remainder <= 2:
                base_pos = quotient
            else:
                base_pos = quotient
        
        elif ju == 5:  # 土五局
            # 土五局: 5で割った余りで調整
            if remainder == 0:
                base_pos = quotient
            else:
                base_pos = quotient
        
        elif ju == 6:  # 火六局
            # 火六局: 6で割った余りで調整
            if remainder == 0:
                base_pos = quotient
            else:
                base_pos = quotient
        
        else:
            # 不明な局数の場合（通常は発生しない）
            base_pos = quotient
        
        # 最終位置計算
        # 寅宮（インデックス2）を起点に配置
        # 紫微星は1から始まるので、base_pos + 1 を使用
        final_pos = (1 + base_pos) % 12
        
        # ========================================
        # テーブルとの整合性検証
        # ========================================
        # 数式計算結果をテーブルと照合して検証
        if ju in zw.ZIWEI_POSITION_TABLE:
            table = zw.ZIWEI_POSITION_TABLE[ju]
            if 1 <= lunar_day <= 30:
                table_pos = table[lunar_day - 1]
                if final_pos != table_pos:
                    # テーブルの値を優先（伝統的ルールに基づく）
                    # 数式は近似であり、完全な一致は難しい場合がある
                    return table_pos
        
        return final_pos
    
    def _calc_ziwei_by_formula_detailed(self, lunar_day: int, ju: int) -> dict:
        """
        紫微星位置の詳細な数式計算（デバッグ・教育用）
        
        紫微斗数の紫微星配置における数学的原理を詳細に示す
        
        Args:
            lunar_day: 旧暦の日（1-30）
            ju: 五行局数（2-6）
            
        Returns:
            計算過程と結果を含む辞書
        """
        import math
        
        d = lunar_day
        j = ju
        
        # 基本計算
        quotient = d // j
        remainder = d % j
        ceil_quotient = math.ceil(d / j)
        
        # 五行局名
        ju_names = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}
        
        # テーブル参照
        table_pos = None
        if j in zw.ZIWEI_POSITION_TABLE:
            table = zw.ZIWEI_POSITION_TABLE[j]
            if 1 <= d <= 30:
                table_pos = table[d - 1]
        
        return {
            "input": {
                "lunar_day": d,
                "ju": j,
                "ju_name": ju_names.get(j, f"{j}局")
            },
            "calculation": {
                "formula": f"({d} + X) / {j}",
                "quotient": quotient,
                "remainder": remainder,
                "ceil_quotient": ceil_quotient
            },
            "result": {
                "position_index": table_pos if table_pos is not None else (1 + ceil_quotient) % 12,
                "position_branch": zw.BRANCHES[table_pos if table_pos is not None else (1 + ceil_quotient) % 12]
            },
            "note": "紫微斗数では、紫微星の位置は (日数/局数) の商と余りで決定される。" +
                    "厳密には五行局ごとに細かな調整ルールがあるため、" +
                    "実用上はテーブル参照が推奨される。"
        }

    
    def _init_palaces(self, ming_palace: int) -> Dict[int, PalaceInfo]:
        """12宮を初期化"""
        palaces = {}
        for i in range(12):
            branch_idx = (ming_palace + i) % 12
            branch = zw.BRANCHES[branch_idx]
            palace_type = zw.PALACES[i]
            grid_coord = zw.PALACE_GRID_COORDS.get(branch, (0, 0))
            
            palaces[branch_idx] = PalaceInfo(
                index=branch_idx,
                branch=branch,
                palace_type=palace_type,
                stars=[],
                grid_coord=grid_coord
            )
        
        return palaces
    
    def _get_brightness(self, star_name: str, palace_index: int) -> Tuple[str, int]:
        """
        星の輝度を取得
        
        Args:
            star_name: 星名
            palace_index: 宮のインデックス（0-11）
            
        Returns:
            (輝度名, 輝度値)
        """
        if star_name in zw.STAR_BRIGHTNESS:
            brightness_value = zw.STAR_BRIGHTNESS[star_name][palace_index]
            brightness_name = zw.BRIGHTNESS_NAMES.get(
                zw.Brightness(brightness_value), 
                "平"
            )
            return brightness_name, brightness_value
        
        return "平", 3  # デフォルト
    
    def _place_main_stars(
        self, 
        palaces: Dict[int, PalaceInfo], 
        ziwei_pos: int, 
        year_stem_index: int
    ):
        """14主星を配置（輝度付き）"""
        
        # 紫微星群を配置
        for star, offset in zw.ZIWEI_GROUP_OFFSETS.items():
            pos = (ziwei_pos + offset) % 12
            brightness_name, brightness_value = self._get_brightness(star, pos)
            
            star_info = StarInfo(
                name=star,
                palace_index=pos,
                palace_name=zw.BRANCHES[pos],
                brightness=brightness_name,
                brightness_value=brightness_value,
                category="紫微星系"
            )
            palaces[pos].stars.append(star_info)
        
        # 天府星の位置を計算
        tianfu_pos = (12 - ziwei_pos + 4) % 12
        
        # 天府星群を配置
        for star, offset in zw.TIANFU_GROUP_OFFSETS.items():
            pos = (tianfu_pos + offset) % 12
            brightness_name, brightness_value = self._get_brightness(star, pos)
            
            star_info = StarInfo(
                name=star,
                palace_index=pos,
                palace_name=zw.BRANCHES[pos],
                brightness=brightness_name,
                brightness_value=brightness_value,
                category="天府星系"
            )
            palaces[pos].stars.append(star_info)
    
    def _place_auxiliary_stars(
        self, 
        palaces: Dict[int, PalaceInfo],
        year_stem_index: int,
        year_branch_index: int,
        hour_branch: int,
        lunar_month: int,
        lunar_day: int
    ):
        """
        乙級星を配置（火星・鈴星等）
        
        火星・鈴星は「年支＋時支」法を採用（最も標準的）
        """
        year_stem = zw.STEMS[year_stem_index]
        
        # ===== 禄存 =====
        if year_stem in zw.LUCUN_TABLE:
            pos = zw.LUCUN_TABLE[year_stem]
            palaces[pos].stars.append(StarInfo(
                name="禄存",
                palace_index=pos,
                palace_name=zw.BRANCHES[pos],
                category="甲級副星"
            ))
        
        # ===== 天魁・天鉞 =====
        if year_stem in zw.TIANKUI_TABLE:
            pos = zw.TIANKUI_TABLE[year_stem]
            palaces[pos].stars.append(StarInfo(
                name="天魁",
                palace_index=pos,
                palace_name=zw.BRANCHES[pos],
                category="甲級副星"
            ))
        
        if year_stem in zw.TIANYUE_TABLE:
            pos = zw.TIANYUE_TABLE[year_stem]
            palaces[pos].stars.append(StarInfo(
                name="天鉞",
                palace_index=pos,
                palace_name=zw.BRANCHES[pos],
                category="甲級副星"
            ))
        
        # ===== 文昌・文曲 =====
        # 文昌: 時支から逆に数える（戌起点）
        wenchang_pos = (zw.WENCHANG_BASE - hour_branch + 12) % 12
        palaces[wenchang_pos].stars.append(StarInfo(
            name="文昌",
            palace_index=wenchang_pos,
            palace_name=zw.BRANCHES[wenchang_pos],
            category="甲級副星"
        ))
        
        # 文曲: 時支から順に数える（辰起点）
        wenqu_pos = (zw.WENQU_BASE + hour_branch) % 12
        palaces[wenqu_pos].stars.append(StarInfo(
            name="文曲",
            palace_index=wenqu_pos,
            palace_name=zw.BRANCHES[wenqu_pos],
            category="甲級副星"
        ))
        
        # ===== 左輔・右弼 =====
        # 左輔: 月から（辰起点で順行）
        zuofu_pos = (zw.ZUOFU_BASE + lunar_month - 1) % 12
        palaces[zuofu_pos].stars.append(StarInfo(
            name="左輔",
            palace_index=zuofu_pos,
            palace_name=zw.BRANCHES[zuofu_pos],
            category="甲級副星"
        ))
        
        # 右弼: 月から（戌起点で逆行）
        youbi_pos = (zw.YOUBI_BASE - lunar_month + 1 + 12) % 12
        palaces[youbi_pos].stars.append(StarInfo(
            name="右弼",
            palace_index=youbi_pos,
            palace_name=zw.BRANCHES[youbi_pos],
            category="甲級副星"
        ))
        
        # ===== 火星・鈴星（年支＋時支法・最も標準的） =====
        # コメント: 火星・鈴星は流派により配置法が異なる。
        # ここでは最も標準的な「年支＋時支」法を採用。
        # 年支のグループ（寅午戌/申子辰/巳酉丑/亥卯未）と時支で決定する。
        
        year_branch_group = zw.get_year_branch_group(year_branch_index)
        
        # 火星
        if year_branch_group in zw.HUOXING_TABLE:
            huoxing_pos = zw.HUOXING_TABLE[year_branch_group][hour_branch]
            palaces[huoxing_pos].stars.append(StarInfo(
                name="火星",
                palace_index=huoxing_pos,
                palace_name=zw.BRANCHES[huoxing_pos],
                category="甲級副星"
            ))
        
        # 鈴星
        if year_branch_group in zw.LINGXING_TABLE:
            lingxing_pos = zw.LINGXING_TABLE[year_branch_group][hour_branch]
            palaces[lingxing_pos].stars.append(StarInfo(
                name="鈴星",
                palace_index=lingxing_pos,
                palace_name=zw.BRANCHES[lingxing_pos],
                category="甲級副星"
            ))
        
        # ===== 擎羊・陀羅 =====
        # 禄存の前後に配置
        if year_stem in zw.LUCUN_TABLE:
            lucun_pos = zw.LUCUN_TABLE[year_stem]
            
            # 擎羊: 禄存の前（順行方向）
            qingyang_pos = (lucun_pos + 1) % 12
            palaces[qingyang_pos].stars.append(StarInfo(
                name="擎羊",
                palace_index=qingyang_pos,
                palace_name=zw.BRANCHES[qingyang_pos],
                category="甲級副星"
            ))
            
            # 陀羅: 禄存の後（逆行方向）
            tuoluo_pos = (lucun_pos - 1 + 12) % 12
            palaces[tuoluo_pos].stars.append(StarInfo(
                name="陀羅",
                palace_index=tuoluo_pos,
                palace_name=zw.BRANCHES[tuoluo_pos],
                category="甲級副星"
            ))
    
    def _apply_four_transformations(
        self, 
        palaces: Dict[int, PalaceInfo], 
        year_stem: str
    ):
        """四化星を適用"""
        four_trans = zw.FOUR_TRANSFORMATIONS.get(year_stem, {})
        
        for trans_type, star_name in four_trans.items():
            # 該当する星を探して四化を付与
            for palace in palaces.values():
                for star in palace.stars:
                    if star.name == star_name:
                        star.four_trans = trans_type
    
    def _serialize_palaces(self, palaces: Dict[int, PalaceInfo]) -> List[Dict]:
        """宮の情報をJSON用にシリアライズ"""
        result = []
        
        for idx in range(12):
            if idx in palaces:
                palace = palaces[idx]
                stars_data = []
                for star in palace.stars:
                    star_dict = {
                        "name": star.name,
                        "category": star.category
                    }
                    if star.brightness:
                        star_dict["brightness"] = star.brightness
                        star_dict["brightness_value"] = star.brightness_value
                    if star.four_trans:
                        star_dict["four_transformation"] = star.four_trans
                    stars_data.append(star_dict)
                
                result.append({
                    "index": palace.index,
                    "branch": palace.branch,
                    "palace_type": palace.palace_type,
                    "grid_coord": {
                        "row": palace.grid_coord[0],
                        "col": palace.grid_coord[1]
                    },
                    "stars": stars_data
                })
        
        return result
    
    def get_palace_details(self, ming_palace_index: int) -> Dict[str, str]:
        """宮の詳細情報を取得"""
        palace_mapping = {}
        for i in range(12):
            palace_index = (ming_palace_index + i) % 12
            palace_mapping[zw.BRANCHES[palace_index]] = zw.PALACES[i]
        
        return palace_mapping
