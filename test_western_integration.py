import sys
import os
from datetime import datetime

# パス設定
sys.path.append(os.path.join(os.path.dirname(__file__), 'divination_engine'))

try:
    from src.modules.western.western import WesternAstrologyCalculator
except ImportError:
    # ローカル実行時のパス調整
    sys.path.append(os.path.join(os.getcwd(), 'divination_engine'))
    from src.modules.western.western import WesternAstrologyCalculator

def test_integration():
    calc = WesternAstrologyCalculator()
    dt = datetime(2024, 1, 1, 12, 0, 0)
    lat = 35.6895
    lon = 139.6917
    
    print(f"Calculating for {dt} at ({lat}, {lon})...")
    result = calc.calculate(dt, lat, lon)
    
    print(f"\n=== Western Astrology Result ===")
    print(f"ASC: {result.ascendant}")
    print(f"MC: {result.midheaven}")
    
    print(f"\n--- Planets ---")
    for p in result.planets:
        print(f"{p.planet}: {p.sign} {p.degree_in_sign:.2f}° (House {p.house}) R:{p.retrograde}")
        
    print(f"\n--- Aspects (First 5) ---")
    for a in result.aspects[:5]:
        state = "Applying" if a.applying else "Separating"
        print(f"{a.planet1} - {a.planet2}: {a.aspect_type} ({a.orb:.2f}°) [{state}]")
        
    print("\nIntegration Test Passed!")

if __name__ == "__main__":
    test_integration()
