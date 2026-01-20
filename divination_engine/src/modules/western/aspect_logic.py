from typing import List, Dict, Any, Tuple
from ...const.astro_const import AspectType, ASPECT_ANGLES, DEFAULT_ORBS

class AspectEngine:
    """
    アスペクト計算エンジン
    """
    
    def __init__(self, orbs: Dict[Tuple[AspectType, bool], float] = DEFAULT_ORBS):
        """
        Args:
            orbs: (AspectType, is_luminary) -> orb_deg の辞書
        """
        self.orbs = orbs

    def _get_orb(self, aspect_type: AspectType, is_luminary: bool) -> float:
        return self.orbs.get((aspect_type, is_luminary), 1.0) # デフォルト1度

    def calculate_aspects(self, bodies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        天体リストから全アスペクトを計算
        
        bodies: [{id, longitude, speed_long, ...}, ...]
        """
        aspects = []
        n = len(bodies)
        
        for i in range(n):
            for j in range(i + 1, n):
                body_a = bodies[i]
                body_b = bodies[j]
                
                # 自分自身とのアスペクトは除外（念のため）
                if body_a['id'] == body_b['id']:
                    continue
                    
                res = self._check_aspect(body_a, body_b)
                if res:
                    aspects.append(res)
                    
        return aspects

    def _check_aspect(self, body_a: Dict[str, Any], body_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        2天体間のアスペクト判定
        """
        long_a = body_a['longitude']
        long_b = body_b['longitude']
        
        # 角度差 (0-180)
        diff = abs(long_a - long_b)
        if diff > 180:
            diff = 360 - diff
            
        # ルミナリー（太陽・月）が含まれるか？
        is_luminary = (body_a['id'] in ['Sun', 'Moon']) or (body_b['id'] in ['Sun', 'Moon'])
        
        # 全アスペクト定義をチェック
        for aspect_type, angle in ASPECT_ANGLES.items():
            orb_limit = self._get_orb(aspect_type, is_luminary)
            
            # オーブ内か？
            current_orb = abs(diff - angle)
            if current_orb <= orb_limit:
                # 状態判定 (Applying/Separating)
                state = self._determine_state(body_a, body_b, angle, diff)
                
                return {
                    "body_a": body_a['id'],
                    "body_b": body_b['id'],
                    "type": aspect_type,
                    "angle": angle, # 定義上の角度 (120 etc)
                    "actual_angle": diff, # 実測角度
                    "orb": round(current_orb, 4),      # 誤差
                    "state": state
                }
                
        return None

    def _determine_state(self, body_a: Dict[str, Any], body_b: Dict[str, Any], aspect_angle: float, current_diff: float) -> str:
        """
        Applying (形成中) か Separating (分離中) かを判定
        
        Logic:
        1. 速い天体と遅い天体を特定
        2. 相対速度を計算
        3. 角度差が「これから定義角(strict)に近づく」ならApplying
        """
        speed_a = body_a['speed_long']
        speed_b = body_b['speed_long']
        pos_a = body_a['longitude']
        pos_b = body_b['longitude']
        
        # 相対的な動きを見るために、Bを静止させてAの相対速度を見るアプローチ
        # しかし、円環上なので「差分が縮まる方向か」を見るのが確実
        
        # 現在の誤差
        orb_now = abs(current_diff - aspect_angle)
        
        # 未来（例えば1時間後 = 1/24日後）の位置で誤差を再計算
        dt = 1.0 / 24.0
        
        future_pos_a = (pos_a + speed_a * dt) % 360
        future_pos_b = (pos_b + speed_b * dt) % 360
        
        future_diff = abs(future_pos_a - future_pos_b)
        if future_diff > 180:
            future_diff = 360 - future_diff
            
        orb_future = abs(future_diff - aspect_angle)
        
        if orb_future < orb_now:
            return "Applying"
        else:
            return "Separating"
