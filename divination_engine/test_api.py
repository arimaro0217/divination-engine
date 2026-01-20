"""
APIをテスト
"""
import sys
import io
import requests
import json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


url = "http://localhost:8000/api/test"
data = {
    "year": 1992,
    "month": 2,
    "day": 17,
    "hour": 17,
    "minute": 18
}

response = requests.post(url, json=data)
print("Status:", response.status_code)
print("\nResponse:")
result = response.json()
print(json.dumps(result, ensure_ascii=False, indent=2))

# 日柱を確認
day_pillar = result["day_pillar"]["full"]
print(f"\n日柱: {day_pillar}")
print(f"期待: 癸亥")
print(f"一致: {'✓' if day_pillar == '癸亥' else '✗'}")
