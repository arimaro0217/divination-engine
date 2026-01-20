# 統合占いエンジン - デプロイガイド

## 概要

12種類の占術を統合したWebアプリケーション。
- **フロントエンド**: 静的HTML/CSS/JavaScript
- **バックエンド**: FastAPI (Python)

## 高度計算対応占術

| 占術 | 高度機能 |
|------|----------|
| 四柱推命 | 節入り精密計算、蔵干、通変星 |
| 算命学 | 宇宙盤、十大主星、天中殺 |
| 九星気学 | 九星盤、方位吉凶 |
| 紫微斗数 | 十二宮、四化星、大限 |
| 宿曜 | 二十七宿、相性 |
| 数秘術 | Y判定、Chaldean、天体連携 |
| インド占星術 | D1/D9分割図、Dasha |
| 西洋占星術 | Swiss Eph、ハウス、アスペクト |

## ローカル開発

```bash
# バックエンド起動
cd divination_engine
pip install -r requirements.txt
python api_server.py
# → http://localhost:8000

# フロントエンド
cd webapp
python -m http.server 3000
# → http://localhost:3000
```

## 本番デプロイ

### バックエンド → Render.com

1. GitHubにpush
2. Render Dashboard → New Web Service
3. 設定:
   - Root Directory: `divination_engine`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

### フロントエンド → Vercel

1. Vercel CLIでデプロイ:
```bash
cd webapp
npx vercel
```

2. `api-client.js`のBASE_URLを本番APIに変更

## APIエンドポイント

| エンドポイント | 説明 |
|---------------|------|
| GET `/health` | ヘルスチェック |
| POST `/api/bazi` | 四柱推命 |
| POST `/api/numerology` | 数秘術（高度版） |
| POST `/api/ziwei` | 紫微斗数 |
| POST `/api/jyotish` | インド占星術 |
| POST `/api/western` | 西洋占星術 |
| POST `/api/calculate-all` | 全占術統合 |

## ライセンス

Private - All rights reserved
