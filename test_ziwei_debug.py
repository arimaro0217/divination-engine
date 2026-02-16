import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.join(os.getcwd(), 'divination_engine'))

from src.modules.eastern.ziwei_api import generate_ziwei_chart

def main():
    # 1992年2月17日 12:00
    try:
        result = generate_ziwei_chart(1992, 2, 17, 12, 0)
        palaces = result.get('palaces', [])
        print(f"Total Palaces: {len(palaces)}")
        
        for p in palaces:
            major = len(p.get('major_stars', []))
            minor = len(p.get('minor_stars', []))
            bad = len(p.get('bad_stars', []))
            print(f"Palace: {p['name']}, Major: {major}, Minor: {minor}, Bad: {bad}")
            if minor > 0:
                print(f"  Minor example: {p['minor_stars'][0]}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
