"""
統合占い計算エンジン - メインコントローラー

12種類の占術を統合して計算するエントリーポイント
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from zoneinfo import ZoneInfo
import json

from .models.input_schema import UserProfile, DivinationRequest, DivinationType
from .models.output_schema import (
    DivinationResult, BaZiResult, SanmeiResult, 
    KyuseiResult, ZiWeiResult, SukuyouResult, 
    WesternResult, VedicResult, MayanResult, 
    NumerologyResult, SeimeiResult, SexagenaryResult, KabbalahResult
)
from .core.time_manager import TimeManager
from .core.ephemeris import AstroEngine
from .core.calendar_cn import ChineseCalendar

# 各占術モジュール
from .modules.eastern.bazi import BaZiCalculator
from .modules.eastern.sanmei import SanmeiCalculator
from .modules.eastern.kyusei import KyuseiCalculator
from .modules.eastern.sexagenary import SexagenaryCalculator
from .modules.eastern.ziwei import ZiWeiEngine
from .modules.eastern.sukuyou import SukuyouEngine
from .modules.western.western import WesternAstrologyCalculator
from .modules.western.vedic import VedicAstrologyCalculator
from .modules.mayan.mayan import MayanCalculator
from .modules.numerology.num_api import NumerologyAPI  # 高度版に変更
from .modules.numerology.kabbalah import KabbalahCalculator
from .modules.name_analysis.seimei import SeimeiCalculator


class DivinationController:
    """
    統合占い計算コントローラー
    
    全12種類の占術計算を統合管理し、
    ユーザー入力から包括的な占い結果を生成する
    """
    
    def __init__(self):
        # コアエンジン
        self.astro = AstroEngine()
        self.calendar = ChineseCalendar()
        
        # 各占術計算クラス
        self.bazi = BaZiCalculator()
        # self.sanmei は calculate_all で都度生成
        self.kyusei = KyuseiCalculator()
        self.sexagenary = SexagenaryCalculator()
        self.ziwei = ZiWeiEngine()
        self.sukuyou = SukuyouEngine()
        self.western = WesternAstrologyCalculator()
        self.vedic = VedicAstrologyCalculator()
        self.mayan = MayanCalculator()
        self.numerology = NumerologyAPI()  # 高度版APIを使用
        self.kabbalah = KabbalahCalculator()
        self.seimei = SeimeiCalculator()
    
    def calculate_all(self, user: UserProfile, 
                      types: Optional[List[DivinationType]] = None) -> DivinationResult:
        """
        全占術を計算
        
        Args:
            user: ユーザープロフィール
            types: 計算する占術タイプのリスト（Noneで全て）
            
        Returns:
            DivinationResult: 全占術の結果
        """
        if types is None:
            types = list(DivinationType)
        
        result = DivinationResult(
            user_name=user.name_kanji,
            birth_datetime=user.birth_datetime
        )
        
        # 東洋占術（生年月日時のみで計算可能）
        if DivinationType.BAZI in types:
            result.bazi = self.bazi.calculate(user.birth_datetime)
        
        if DivinationType.SANMEI in types:
            try:
                # 算命学計算クラスはユーザーごとにインスタンス化が必要
                sanmei = SanmeiCalculator(user.birth_datetime, user.latitude or 35.68, user.longitude or 139.76)
                analysis = sanmei.get_full_analysis()
                
                # 結果の詳細なマッピング
                jintai = analysis.get("jintai_seizu", [])
                
                result.sanmei = SanmeiResult(
                    four_pillars=self.bazi._convert_pillars_to_schema(sanmei.four_pillars),
                    void_branches=analysis.get("tenchusatsu", {}).get("branches", []),
                    void_group_name=analysis.get("tenchusatsu", {}).get("type", "不明"),
                    main_stars={s["position"]: s["star_name"] for s in jintai if s["star_type"] == "main_star"},
                    sub_stars={s["position"]: s["star_name"] for s in jintai if s["star_type"] == "sub_star"},
                    body_chart={s["position"]: s["star_name"] for s in jintai},
                    energy_values=analysis.get("energy_score", {}),
                    phases=analysis.get("interactions", {})
                )
            except Exception as e:
                print(f"Sanmei calculation error: {e}")
                result.sanmei = SanmeiResult(
                    error_message=str(e),
                    success=False
                )
        
        if DivinationType.KYUSEI in types:
            result.kyusei = self.kyusei.calculate(user.birth_datetime)
        
        if DivinationType.SEXAGENARY in types:
            result.sexagenary = self.sexagenary.calculate(user.birth_datetime)
        
        if DivinationType.ZIWEI in types:
            result.ziwei = self.ziwei.calculate(user.birth_datetime)
        
        if DivinationType.SUKUYOU in types:
            result.sukuyou = self.sukuyou.calculate(user.birth_datetime)
        
        # 西洋・インド占星術（緯度経度が必要）
        if user.latitude is not None and user.longitude is not None:
            if DivinationType.WESTERN in types:
                result.western = self.western.calculate(
                    user.birth_datetime, user.latitude, user.longitude
                )
            
            if DivinationType.VEDIC in types:
                result.vedic = self.vedic.calculate(
                    user.birth_datetime, user.latitude, user.longitude
                )
        
        # マヤ暦
        if DivinationType.MAYAN in types:
            result.mayan = self.mayan.calculate(user.birth_datetime)
        
        # 数秘術・カバラ
        if DivinationType.NUMEROLOGY in types:
            try:
                # 名前処理（カナ → ローマ字変換は高度APIが自動で行う）
                name_input = user.name_kana if hasattr(user, 'name_kana') and user.name_kana else user.name_kanji
                
                # 高度API使用: generate_full_report
                full_report = self.numerology.generate_full_report(
                    name_input=name_input,
                    birth_date=user.birth_datetime,
                    system='pythagorean',
                    latitude=user.latitude or 35.68,
                    longitude=user.longitude or 139.76
                )
                
                # スキーマに合わせたマッピング
                core = full_report["core_numbers"]
                result.numerology = NumerologyResult(
                    life_path=core["life_path"]["number"],
                    birthday_number=core["birthday"]["number"],
                    expression_number=core["destiny"]["number"], # APIでは destiny と呼称
                    soul_urge=core["soul_urge"]["number"],
                    personality_number=core["personality"]["number"],
                    life_path_meaning=core["life_path"].get("meaning", {}).get("description", ""),
                    birthday_meaning=core["birthday"].get("meaning", [])[0] if core["birthday"].get("meaning") else ""
                )
            except Exception as e:
                print(f"Numerology calculation error: {e}")
        
        if DivinationType.KABBALAH in types:
            name_roman = ""
            result.kabbalah = self.kabbalah.calculate(user.birth_datetime, name_roman)
        
        # 姓名判断
        if DivinationType.SEIMEI in types:
            # 姓名を分割
            name_parts = user.name_kanji.split()
            if len(name_parts) >= 2:
                result.seimei = self.seimei.calculate(name_parts[0], name_parts[1])
            elif len(name_parts) == 1:
                # 姓名が分割されていない場合は2文字ずつ仮定
                name = name_parts[0]
                mid = len(name) // 2
                result.seimei = self.seimei.calculate(name[:mid], name[mid:])
        
        return result
    
    def to_json(self, result: DivinationResult) -> str:
        """結果をJSON文字列に変換"""
        return result.model_dump_json(indent=2, exclude_none=True)
    
    def to_markdown(self, result: DivinationResult) -> str:
        """結果をMarkdown形式に変換"""
        lines = [
            f"# 占い結果: {result.user_name}",
            f"**生年月日時**: {result.birth_datetime.strftime('%Y年%m月%d日 %H時%M分')}",
            f"**計算日時**: {result.calculated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        
        # 四柱推命
        if result.bazi:
            lines.extend([
                "## 四柱推命",
                f"- **日主**: {result.bazi.day_master}",
                f"- **四柱**: {result.bazi.four_pillars.year.full} {result.bazi.four_pillars.month.full} {result.bazi.four_pillars.day.full} {result.bazi.four_pillars.hour.full}",
                f"- **空亡**: {', '.join(result.bazi.void_branches)}",
                ""
            ])
        
        # 算命学
        if result.sanmei:
            lines.extend([
                "## 算命学",
                f"- **天中殺**: {', '.join(result.sanmei.void_branches)}",
                f"- **十大主星**: {', '.join(f'{k}:{v}' for k, v in result.sanmei.main_stars.items())}",
                ""
            ])
        
        # 九星気学
        if result.kyusei:
            lines.extend([
                "## 九星気学",
                f"- **本命星**: {result.kyusei.year_star}",
                f"- **月命星**: {result.kyusei.month_star}",
                f"- **日命星**: {result.kyusei.day_star}",
                f"- **傾斜宮**: {result.kyusei.inclination}",
                ""
            ])
        
        # 紫微斗数
        if result.ziwei:
            lines.extend([
                "## 紫微斗数",
                f"- **旧暦**: {result.ziwei.lunar_date}",
                f"- **命宮**: {result.ziwei.ming_palace}",
                f"- **身宮**: {result.ziwei.body_palace}",
                ""
            ])
        
        # 宿曜
        if result.sukuyou:
            lines.extend([
                "## 宿曜占星術",
                f"- **本命宿**: {result.sukuyou.natal_mansion}（第{result.sukuyou.mansion_number}宿）",
                f"- **属性**: {result.sukuyou.element}",
                ""
            ])
        
        # 西洋占星術
        if result.western:
            lines.extend([
                "## 西洋占星術",
                f"- **ASC**: {result.western.ascendant:.2f}°",
                f"- **MC**: {result.western.midheaven:.2f}°",
                ""
            ])
            for planet in result.western.planets[:5]:  # 太陽〜火星
                lines.append(f"- **{planet.planet}**: {planet.sign} {planet.degree_in_sign:.1f}°")
            lines.append("")
        
        # インド占星術
        if result.vedic:
            lines.extend([
                "## インド占星術（ヴェーダ）",
                f"- **アヤナムサ**: {result.vedic.ayanamsa}°",
                f"- **月のナクシャトラ**: {result.vedic.nakshatra}",
                f"- **ナクシャトラ支配星**: {result.vedic.nakshatra_lord}",
                ""
            ])
        
        # マヤ暦
        if result.mayan:
            lines.extend([
                "## マヤ暦",
                f"- **KIN**: {result.mayan.kin_number}",
                f"- **太陽の紋章**: {result.mayan.solar_seal}",
                f"- **銀河の音**: {result.mayan.galactic_tone}",
                f"- **ウェイブスペル**: {result.mayan.wavespell}",
                f"- **ガイドキン**: {result.mayan.guide}",
                ""
            ])
        
        # 姓名判断
        if result.seimei:
            lines.extend([
                "## 姓名判断",
                f"- **天格**: {result.seimei.tenkaku}",
                f"- **人格**: {result.seimei.jinkaku}",
                f"- **地格**: {result.seimei.chikaku}",
                f"- **外格**: {result.seimei.gaikaku}",
                f"- **総格**: {result.seimei.soukaku}",
                ""
            ])
        
        # 数秘術
        if result.numerology:
            lines.extend([
                "## 数秘術",
                f"- **ライフパス数**: {result.numerology.life_path}",
                f"- **バースデー数**: {result.numerology.birthday_number}",
                ""
            ])
        
        return "\n".join(lines)


def main():
    """テスト実行"""
    # テストケース: 安瀬諒さん
    user = UserProfile(
        name_kanji="安瀬 諒",
        name_kana="アンゼ リョウ",
        birth_datetime=datetime(1992, 2, 17, 17, 18, tzinfo=ZoneInfo("Asia/Tokyo")),
        birth_place="東京都足立区",
        latitude=35.7756,
        longitude=139.8044,
        gender="male"
    )
    
    controller = DivinationController()
    result = controller.calculate_all(user)
    
    # Markdown出力
    print(controller.to_markdown(result))
    print("\n" + "="*50 + "\n")
    
    # JSON出力（一部）
    print("=== JSON出力（四柱推命部分）===")
    if result.bazi:
        print(result.bazi.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
