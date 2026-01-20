import swisseph as swe
from typing import List, Dict, Any, Optional
from ...const.astro_const import HouseSystem, PlanetId, SIGNS_EN, SIGNS_JP
from .astro_core import AstroCore

class ChartBuilder:
    """
    ホロスコープチャート構築クラス
    """
    
    def __init__(self, core: AstroCore):
        self.core = core
        
    def calculate_houses(
        self, 
        julian_day: float, 
        lat: float, 
        lon: float, 
        system: HouseSystem = HouseSystem.PLACIDUS
    ) -> Dict[str, Any]:
        """
        ハウスカスプとアングルを計算
        
        Args:
            system: HouseSystem Enum (PLACIDUS, KOCH, WHOLE_SIGN etc.)
            
        Returns:
            {
                "cusps": [cusp1, cusp2, ..., cusp12],
                "angles": { "asc": val, "mc": val, "dsc": val, "ic": val },
                "system": 使用されたシステム（フォールバック時は変更される可能性あり）
            }
        """
        
        # システムID (byte char)
        hsys = system.value.encode('ascii')
        
        try:
            # cusps: array of 13 doubles (index 0 is 0.0, 1-12 are cusps)
            cusps, ascmc = swe.houses(julian_day, lat, lon, hsys)
            # print(f"DEBUG: raw cusps len={len(cusps)}")  # For debugging
            
            cusps_list = list(cusps)
            if len(cusps_list) == 13:
                final_cusps = cusps_list[1:]
            else:
                final_cusps = cusps_list
            
            if system in [HouseSystem.PLACIDUS, HouseSystem.KOCH] and (len(final_cusps) > 1 and final_cusps[1] == 0.0):
                 # Porphyryへフォールバック
                 hsys = HouseSystem.PORPHYRY.value.encode('ascii')
                 cusps, ascmc = swe.houses(julian_day, lat, lon, hsys)
                 used_system = HouseSystem.PORPHYRY
            else:
                 used_system = system
                 
            return {
                "cusps": final_cusps, 
                "angles": {
                    "asc": ascmc[0],
                    "mc": ascmc[1],
                    "dsc": (ascmc[0] + 180) % 360, # DSCはASCの対向
                    "ic": (ascmc[1] + 180) % 360,  # ICはMCの対向
                    "vertex": ascmc[3],
                    "armc": ascmc[2]
                },
                "system": used_system
            }
            
        except swe.Error:
             # 安全策: Equalハウス
             hsys = HouseSystem.EQUAL.value.encode('ascii')
             cusps, ascmc = swe.houses(julian_day, lat, lon, hsys)
             return {
                "cusps": list(cusps)[1:],
                "angles": {
                    "asc": ascmc[0],
                    "mc": ascmc[1],
                    "dsc": (ascmc[0] + 180) % 360,
                    "ic": (ascmc[1] + 180) % 360
                },
                "system": HouseSystem.EQUAL
             }

    def _get_sign_info(self, longitude: float) -> Dict[str, Any]:
        """
        黄経からサイン情報を取得
        """
        sign_idx = int(longitude // 30)
        relative_deg = longitude % 30
        return {
            "sign_id": sign_idx,
            "sign_en": SIGNS_EN[sign_idx],
            "sign_jp": SIGNS_JP[sign_idx],
            "relative_degree": relative_deg
        }

    def _determine_house(self, longitude: float, cusps: List[float], five_deg_rule: bool = False) -> int:
        """
        天体がどのハウスにあるか判定
        Args:
           cusps: 12要素のカストリスト (index 0 = 1st House Cusp)
        """
        # ハウス判定は複雑（カスプが360度をまたぐ場合など）
        # 単純化のため、各カスプ間の領域チェックを行う
        # 実際にはswe.house_posという関数があるが、ハウスシステム依存のため、
        # ここでは計算済みのカスプを使って判定する。
        
        # 簡易実装: 全探索
        # 注意: 高緯度や特定システムではハウス順序が逆転することは稀だが、
        # 360度境界の処理が必要。
        
        # 正規化関数
        def norm(deg): return deg % 360
        
        target_long = longitude
        if five_deg_rule:
             # 5度前ルール: 天体の位置を+5度して判定させる（＝次のハウスに入りやすくする）
             # ただし、厳密には「次のカスプの手前5度以内なら」
             pass 
             
        # Swiss Ephemerisのハウスポジション計算を使用するのが最も確実
        # ただし、API呼び出しコストがあるため、幾何計算でやる
        
        if len(cusps) < 12:
             # 安全策: デフォルト値を返すかエラーログ
             print(f"Error: Not enough cusps. len={len(cusps)}")
             return 0

        for i in range(12):
            cusp_curr = cusps[i]
            cusp_next = cusps[(i + 1) % 12]
            
            # 領域が360度をまたぐ場合の補正
            if cusp_next < cusp_curr:
                cusp_next += 360
                
            check_long = target_long
            if check_long < cusp_curr and (check_long + 360) < cusp_next:
                 check_long += 360
            
            if cusp_curr <= check_long < cusp_next:
                # 5度前ルール適用チェック
                # 次のカスプ(cusp_next)に近いか？
                # 現在位置が「次のカスプ - 5度」より大きいなら、次のハウス(i+2)へ
                # ※ iは0始まりなので、1ハウス=i+1
                
                house_num = i + 1
                
                if five_deg_rule:
                    dist_to_next = cusp_next - check_long
                    if dist_to_next <= 5.0:
                        house_num = (i + 2)
                        if house_num > 12: house_num = 1
                
                return house_num
                
        return 0 # Error fallback

    def build_chart(
        self, 
        julian_day: float, 
        lat: float, 
        lon: float, 
        alt: float = 0.0,
        house_system: HouseSystem = HouseSystem.PLACIDUS,
        topocentric: bool = False,
        true_node: bool = True,
        five_deg_rule: bool = False
    ) -> Dict[str, Any]:
        """
        チャートデータを一括構築
        """
        # 1. ハウス計算
        house_data = self.calculate_houses(julian_day, lat, lon, house_system)
        
        # 2. 天体計算
        bodies = []
        target_ids = [
            PlanetId.SUN, PlanetId.MOON, PlanetId.MERCURY, PlanetId.VENUS, PlanetId.MARS,
            PlanetId.JUPITER, PlanetId.SATURN, PlanetId.URANUS, PlanetId.NEPTUNE, PlanetId.PLUTO,
            PlanetId.CHIRON
        ]
        
        # ノード (True/Mean)
        node_id = PlanetId.TRUE_NODE if true_node else PlanetId.MEAN_NODE
        
        # リリス (True/Mean) - デフォルトはMeanが多いが、指定に合わせて
        lilith_id = PlanetId.MEAN_APOGEE 
        
        all_targets = target_ids + [node_id, lilith_id]
        
        for bid in all_targets:
            data = self.core.calculate_body(julian_day, bid, lat, lon, alt, topocentric)
            sign_info = self._get_sign_info(data['longitude'])
            house_num = self._determine_house(data['longitude'], house_data['cusps'], five_deg_rule)
            
            # ID文字列化
            name_map = {
                PlanetId.SUN: 'Sun', PlanetId.MOON: 'Moon', PlanetId.MERCURY: 'Mercury',
                PlanetId.VENUS: 'Venus', PlanetId.MARS: 'Mars', PlanetId.JUPITER: 'Jupiter',
                PlanetId.SATURN: 'Saturn', PlanetId.URANUS: 'Uranus', PlanetId.NEPTUNE: 'Neptune',
                PlanetId.PLUTO: 'Pluto', PlanetId.CHIRON: 'Chiron',
                PlanetId.TRUE_NODE: 'NorthNode', PlanetId.MEAN_NODE: 'NorthNode',
                PlanetId.MEAN_APOGEE: 'Lilith', PlanetId.OSCU_APOGEE: 'Lilith'
            }
            
            body_name = name_map.get(bid, str(bid))
            
            bodies.append({
                "id": body_name,
                "name": body_name, # 日本語化などは別途
                **data, # longitude, speed etc
                **sign_info, # sign_id, sign_en
                "house": house_num
            })
            
        return {
            "bodies": bodies,
            "houses": house_data,
            "options": {
                "house_system": house_data["system"],
                "topocentric": topocentric,
                "true_node": true_node
            }
        }
