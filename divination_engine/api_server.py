"""
占いバックエンドAPI (FastAPI)
高度占術エンドポイント追加版
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel
from typing import Optional
import os
import json

from src.main import DivinationController
from src.models.input_schema import DivinationType, UserProfile
from src.modules.numerology.num_api import NumerologyAPI
from src.modules.eastern.ziwei_api import ZiweiAPI
from src.modules.indian.jyotish_engine import JyotishAPI

# ===== ログ設定 =====
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, "requests.log")

def log_request(endpoint: str, data: dict):
    """
    APIリクエストをログファイルに記録
    
    Args:
        endpoint: APIエンドポイント名
        data: ログに記録するデータ（個人情報を含む）
    """
    try:
        # ログディレクトリ作成
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # ログエントリ作成
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "data": data
        }
        
        # ファイルに追記
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"ログ記録エラー: {e}")

app = FastAPI(title="Divination Engine API", version="2.0.0")

# CORS設定（開発用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# コントローラーのインスタンス
controller = DivinationController()

# ===== リクエストモデル =====

class BaZiRequest(BaseModel):
    """四柱推命リクエスト"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: Optional[float] = 35.6762
    longitude: Optional[float] = 139.6503

class NumerologyRequest(BaseModel):
    """数秘術リクエスト"""
    name: str
    birth_date: str  # ISO format: "1992-02-17T12:00:00"
    system: Optional[str] = "pythagorean"  # or "chaldean"
    target_year: Optional[int] = None

class ZiweiRequest(BaseModel):
    """紫微斗数リクエスト"""
    birth_datetime: str  # ISO format
    latitude: Optional[float] = 35.68
    longitude: Optional[float] = 139.76
    gender: Optional[str] = "male"

class JyotishRequest(BaseModel):
    """インド占星術リクエスト"""
    birth_datetime: str  # ISO format
    latitude: Optional[float] = 35.68
    longitude: Optional[float] = 139.76

class WesternRequest(BaseModel):
    """西洋占星術リクエスト"""
    birth_datetime: str  # ISO format
    latitude: Optional[float] = 35.68
    longitude: Optional[float] = 139.76

class FullDivinationRequest(BaseModel):
    """全占術統合リクエスト"""
    name_kanji: str
    name_kana: Optional[str] = ""
    birth_datetime: str  # ISO format
    birth_place: Optional[str] = ""
    latitude: Optional[float] = 35.68
    longitude: Optional[float] = 139.76
    gender: Optional[str] = "male"

# ===== エンドポイント =====

@app.get("/")
def root():
    """ヘルスチェック"""
    return {"status": "ok", "message": "Divination Engine API v2.0"}

@app.get("/health")
def health_check():
    """詳細ヘルスチェック"""
    return {
        "status": "ok",
        "version": "2.0.0",
        "endpoints": [
            "/api/bazi",
            "/api/numerology",
            "/api/ziwei",
            "/api/jyotish",
            "/api/western",
            "/api/calculate-all"
        ]
    }

@app.post("/api/bazi")
def calculate_bazi(request: BaZiRequest):
    """
    四柱推命を計算
    
    Example:
        POST /api/bazi
        {
            "year": 1992,
            "month": 2,
            "day": 17,
            "hour": 17,
            "minute": 18
        }
    """
    # ログ記録
    log_request("bazi", {
        "birth": f"{request.year}-{request.month:02d}-{request.day:02d} {request.hour:02d}:{request.minute:02d}",
        "latitude": request.latitude,
        "longitude": request.longitude
    })
    
    try:
        birth_dt = datetime(
            request.year,
            request.month,
            request.day,
            request.hour,
            request.minute,
            tzinfo=ZoneInfo("Asia/Tokyo")
        )
        
        profile = UserProfile(
            name_kanji="テストユーザー",
            name_kana="テストユーザー",
            birth_datetime=birth_dt,
            gender="male",
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        result = controller.calculate_all(profile, types=[DivinationType.BAZI])
        
        if not result.bazi:
            raise HTTPException(status_code=500, detail="計算エラー")
        
        bazi = result.bazi
        response = {
            "four_pillars": {
                "year": {
                    "stem": bazi.four_pillars.year.heavenly_stem,
                    "branch": bazi.four_pillars.year.earthly_branch
                },
                "month": {
                    "stem": bazi.four_pillars.month.heavenly_stem,
                    "branch": bazi.four_pillars.month.earthly_branch
                },
                "day": {
                    "stem": bazi.four_pillars.day.heavenly_stem,
                    "branch": bazi.four_pillars.day.earthly_branch
                },
                "hour": {
                    "stem": bazi.four_pillars.hour.heavenly_stem,
                    "branch": bazi.four_pillars.hour.earthly_branch
                }
            },
            "day_master": bazi.day_master.heavenly_stem,
            "void_branches": bazi.void_branches
        }
        
        return {"success": True, "data": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/numerology")
def calculate_numerology(request: NumerologyRequest):
    """
    高度数秘術を計算（Y判定、Chaldean、天体連携）
    
    Example:
        POST /api/numerology
        {
            "name": "Mary Johnson",
            "birth_date": "1992-02-17T12:00:00",
            "system": "pythagorean"
        }
    """
    # ログ記録
    log_request("numerology", {
        "name": request.name,
        "birth_date": request.birth_date,
        "system": request.system
    })
    
    try:
        api = NumerologyAPI()
        
        result = api.generate_full_report(
            name_input=request.name,
            birth_date=datetime.fromisoformat(request.birth_date),
            system=request.system,
            target_year=request.target_year
        )
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ziwei")
def calculate_ziwei(request: ZiweiRequest):
    """
    紫微斗数完全計算（十二宮、四化星、大限）
    
    Example:
        POST /api/ziwei
        {
            "birth_datetime": "1992-02-17T17:18:00",
            "latitude": 35.68,
            "longitude": 139.76,
            "gender": "male"
        }
    """
    # ログ記録
    log_request("ziwei", {
        "birth_datetime": request.birth_datetime,
        "latitude": request.latitude,
        "longitude": request.longitude,
        "gender": request.gender
    })
    
    try:
        api = ZiweiAPI()
        birth_dt = datetime.fromisoformat(request.birth_datetime)
        
        result = api.generate_chart(
            birth_year=birth_dt.year,
            birth_month=birth_dt.month,
            birth_day=birth_dt.day,
            birth_hour=birth_dt.hour,
            birth_minute=birth_dt.minute,
            longitude=request.longitude,
            latitude=request.latitude,
            gender=request.gender
        )
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jyotish")
def calculate_jyotish(request: JyotishRequest):
    """
    インド占星術完全計算（D1/D9分割図、Vimshottari Dasha）
    
    Example:
        POST /api/jyotish
        {
            "birth_datetime": "1992-02-17T17:18:00",
            "latitude": 35.68,
            "longitude": 139.76
        }
    """
    # ログ記録
    log_request("jyotish", {
        "birth_datetime": request.birth_datetime,
        "latitude": request.latitude,
        "longitude": request.longitude
    })
    
    try:
        api = JyotishAPI()
        birth_dt = datetime.fromisoformat(request.birth_datetime)
        
        result = api.generate_chart(
            birth_datetime=birth_dt,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_offset=9.0  # JST
        )
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/western")
def calculate_western(request: WesternRequest):
    """
    西洋占星術計算（Swiss Ephemeris、ハウス、アスペクト）
    
    Example:
        POST /api/western
        {
            "birth_datetime": "1992-02-17T17:18:00",
            "latitude": 35.68,
            "longitude": 139.76
        }
    """
    # ログ記録
    log_request("western", {
        "birth_datetime": request.birth_datetime,
        "latitude": request.latitude,
        "longitude": request.longitude
    })
    
    try:
        from src.modules.western.astro_core import AstroCore
        
        birth_dt = datetime.fromisoformat(request.birth_datetime)
        
        # AstroCore使用
        astro = AstroCore()
        
        # ホロスコープ計算
        chart = astro.calculate_chart(
            birth_dt,
            request.latitude,
            request.longitude
        )
        
        # 結果を辞書に変換
        result = {
            "planets": [
                {
                    "name": p.planet,
                    "longitude": p.longitude,
                    "sign": p.sign,
                    "degree": p.degree_in_sign,
                    "retrograde": p.retrograde
                } for p in chart.planets
            ],
            "houses": [
                {
                    "house": i + 1,
                    "cusp": cusp,
                    "sign": AstroCore.get_sign_from_longitude(cusp)
                } for i, cusp in enumerate(chart.houses.cusps)
            ],
            "ascendant": chart.houses.asc,
            "midheaven": chart.houses.mc,
            "aspects": astro.calculate_aspects(chart.planets)
        }
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calculate-all")
def calculate_all_divinations(request: FullDivinationRequest):
    """
    全占術統合計算
    
    Example:
        POST /api/calculate-all
        {
            "name_kanji": "安瀬 諒",
            "name_kana": "アンゼ リョウ",
            "birth_datetime": "1992-02-17T17:18:00",
            "latitude": 35.68,
            "longitude": 139.76,
            "gender": "male"
        }
    """
    # ログ記録
    log_request("calculate-all", {
        "name_kanji": request.name_kanji,
        "name_kana": request.name_kana,
        "birth_datetime": request.birth_datetime,
        "birth_place": request.birth_place,
        "latitude": request.latitude,
        "longitude": request.longitude,
        "gender": request.gender
    })
    
    try:
        profile = UserProfile(
            name_kanji=request.name_kanji,
            name_kana=request.name_kana or request.name_kanji,
            birth_datetime=datetime.fromisoformat(request.birth_datetime),
            birth_place=request.birth_place,
            latitude=request.latitude,
            longitude=request.longitude,
            gender=request.gender
        )
        
        result = controller.calculate_all(profile)
        
        return {"success": True, "data": result.model_dump(exclude_none=True)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test")
def test_day_pillar(request: BaZiRequest):
    """日柱のみをテスト"""
    try:
        from src.core.calendar_cn import ChineseCalendar
        from src.core.time_manager import TimeManager
        
        calendar = ChineseCalendar()
        
        birth_dt = datetime(
            request.year,
            request.month,
            request.day,
            request.hour,
            request.minute,
            tzinfo=ZoneInfo("Asia/Tokyo")
        )
        
        jd = TimeManager.to_julian_day(birth_dt)
        day_pillar = calendar.calc_day_pillar(jd)
        
        return {
            "date": f"{request.year}年{request.month}月{request.day}日 {request.hour}:{request.minute:02d}",
            "day_pillar": {
                "stem": day_pillar.stem,
                "branch": day_pillar.branch,
                "full": f"{day_pillar.stem}{day_pillar.branch}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("  統合占いAPIサーバー (FastAPI)")
    print("="*60)
    print("  バージョン: 2.0.0")
    print("  URL: http://localhost:8000")
    print("  Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
