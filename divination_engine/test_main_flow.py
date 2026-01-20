"""
実際のメインフロー(main.py経由)で1992年2月17日17時18分を計算
"""
import sys
import io
from datetime import datetime
from zoneinfo import ZoneInfo

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# メインコントローラーを使用
from src.main import DivinationController
from src.models.input_schema import UserProfile, DivinationType

# 安瀬諒さんのプロフィール
profile = UserProfile(
    name_kanji="安瀬諒",
    name_kana="アンゼリョウ",
    birth_datetime=datetime(1992, 2, 17, 17, 18, tzinfo=ZoneInfo("Asia/Tokyo")),
    gender="male",
    latitude=35.6762,
    longitude=139.6503
)

# コントローラーを初期化
controller = DivinationController()

# 四柱推命のみ計算
result = controller.calculate_all(profile, types=[DivinationType.BAZI])

print("="*60)
print("メインフロー経由での四柱推命計算")
print("="*60)
print(f"\n生年月日時: 1992年2月17日 17:18 JST")
print(f"氏名: 安瀬 諒\n")

if result.bazi:
    print("【四柱】")
    print(f"年柱: {result.bazi.four_pillars.year.heavenly_stem}{result.bazi.four_pillars.year.earthly_branch}")
    print(f"月柱: {result.bazi.four_pillars.month.heavenly_stem}{result.bazi.four_pillars.month.earthly_branch}")
    print(f"日柱: {result.bazi.four_pillars.day.heavenly_stem}{result.bazi.four_pillars.day.earthly_branch}")
    print(f"時柱: {result.bazi.four_pillars.hour.heavenly_stem}{result.bazi.four_pillars.hour.earthly_branch}")
    
    day_pillar = f"{result.bazi.four_pillars.day.heavenly_stem}{result.bazi.four_pillars.day.earthly_branch}"
    
    print(f"\n【検証】")
    print(f"日柱: {day_pillar}")
    print(f"期待: 癸亥")
    
    if day_pillar == "癸亥":
        print("✓ 正しい")
    else:
        print(f"✗ 間違っている！ ({day_pillar}が計算されている)")
else:
    print("エラー: 四柱推命の計算結果がありません")

print("\n" + "="*60)
