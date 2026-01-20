"""
姓名判断（熊崎式）ロジッククラス
厳密なアルゴリズム実装
"""
from typing import Dict, List


class SeimeiLogic:
    """
    熊崎式姓名判断の厳密な計算ロジック
    
    霊数（仮数：1）の扱いと五格の計算を、古典的なルールに則って実装。
    画数辞書は外部から受け取る設計。
    """
    
    # 霊数（仮想数）
    GHOST_NUMBER: int = 1
    
    # 五行（五元素）の判定テーブル
    FIVE_ELEMENTS_TABLE: Dict[int, str] = {
        1: "木", 2: "木",
        3: "火", 4: "火",
        5: "土", 6: "土",
        7: "金", 8: "金",
        9: "水", 0: "水"
    }
    
    # 五行の相生・相剋関係
    # 相生（生み出す関係）: 木→火→土→金→水→木
    SHENG_CYCLE: Dict[str, str] = {
        "木": "火",
        "火": "土",
        "土": "金",
        "金": "水",
        "水": "木"
    }
    
    # 相剋（抑制する関係）: 木→土、土→水、水→火、火→金、金→木
    KE_CYCLE: Dict[str, str] = {
        "木": "土",
        "土": "水",
        "水": "火",
        "火": "金",
        "金": "木"
    }
    
    def __init__(self, stroke_dict: Dict[str, int]):
        """
        初期化
        
        Args:
            stroke_dict: 漢字と画数のマッピング辞書 {"亜": 7, "哀": 9, ...}
        """
        self.stroke_dict = stroke_dict
    
    def validate_name(self, name: str) -> bool:
        """
        入力された名前に辞書にない文字がないか確認
        
        Args:
            name: 検証する名前（文字列）
            
        Returns:
            すべての文字が辞書に存在すればTrue
            
        Raises:
            ValueError: 辞書にない文字が含まれている場合
        """
        for char in name:
            if char not in self.stroke_dict:
                raise ValueError(f"画数辞書に文字 '{char}' が見つかりません")
        return True
    
    def calculate_strokes(self, text: str) -> List[int]:
        """
        文字列を画数リストに変換
        
        Args:
            text: 変換する文字列
            
        Returns:
            各文字の画数のリスト
            
        Raises:
            ValueError: 辞書にない文字が含まれている場合
        """
        self.validate_name(text)
        return [self.stroke_dict[char] for char in text]
    
    def calc_five_elements(self, surname: str, firstname: str) -> Dict:
        """
        五格（天格・人格・地格・外格・総格）を計算
        
        霊数（1）の扱いを厳密に実装：
        - 天格: 姓1文字の場合のみ霊数を加算
        - 地格: 名1文字の場合のみ霊数を加算
        - 人格: 霊数は加算しない（姓の最後 + 名の最初）
        - 外格: 4パターンの分岐処理
        - 総格: 霊数は加算しない（純粋な合計）
        
        Args:
            surname: 姓（漢字）
            firstname: 名（漢字）
            
        Returns:
            五格の辞書
        """
        # 画数リストを取得
        S_list = self.calculate_strokes(surname)
        N_list = self.calculate_strokes(firstname)
        
        s_len = len(S_list)
        n_len = len(N_list)
        
        # A. 天格 (Ten-kaku)
        if s_len >= 2:
            ten_kaku = sum(S_list)
        else:  # s_len == 1
            ten_kaku = S_list[0] + self.GHOST_NUMBER
        
        # B. 地格 (Chi-kaku)
        if n_len >= 2:
            chi_kaku = sum(N_list)
        else:  # n_len == 1
            chi_kaku = N_list[0] + self.GHOST_NUMBER
        
        # C. 人格 (Jin-kaku)
        # 常に: 姓の最後 + 名の最初（霊数は加算しない）
        jin_kaku = S_list[-1] + N_list[0]
        
        # D. 外格 (Gai-kaku) - 4パターン分岐
        if s_len >= 2 and n_len >= 2:
            # 1. 通常（姓2文字以上, 名2文字以上）
            gai_kaku = S_list[0] + N_list[-1]
        elif s_len == 1 and n_len >= 2:
            # 2. 姓1文字, 名2文字以上
            gai_kaku = self.GHOST_NUMBER + N_list[-1]
        elif s_len >= 2 and n_len == 1:
            # 3. 姓2文字以上, 名1文字
            gai_kaku = S_list[0] + self.GHOST_NUMBER
        else:  # s_len == 1 and n_len == 1
            # 4. 姓1文字, 名1文字
            gai_kaku = self.GHOST_NUMBER + self.GHOST_NUMBER
        
        # E. 総格 (Sou-kaku)
        # 純粋な合計画数（霊数は加算しない）
        sou_kaku = sum(S_list) + sum(N_list)
        
        return {
            "ten_kaku": ten_kaku,
            "jin_kaku": jin_kaku,
            "chi_kaku": chi_kaku,
            "gai_kaku": gai_kaku,
            "sou_kaku": sou_kaku
        }
    
    def get_element(self, number: int) -> str:
        """
        数値から五行（五元素）を判定
        
        1の位の数字で判定：
        1,2→木、3,4→火、5,6→土、7,8→金、9,0→水
        
        Args:
            number: 判定する数値
            
        Returns:
            五行（"木"/"火"/"土"/"金"/"水"）
        """
        last_digit = number % 10
        return self.FIVE_ELEMENTS_TABLE[last_digit]
    
    def judge_relation(self, element1: str, element2: str) -> str:
        """
        二つの五行の関係を判定
        
        Args:
            element1: 前の五行
            element2: 後の五行
            
        Returns:
            関係性（"相生"/"相剋"/"比和"）
        """
        if element1 == element2:
            return "比和"
        elif self.SHENG_CYCLE.get(element1) == element2:
            return "相生"
        elif self.KE_CYCLE.get(element1) == element2:
            return "相剋"
        else:
            # 上記以外の組み合わせも相剋と見なす
            return "相剋"
    
    def get_san_sai(self, ten_kaku: int, jin_kaku: int, chi_kaku: int) -> Dict:
        """
        三才配置（天格・人格・地格の五行関係）を判定
        
        Args:
            ten_kaku: 天格の数値
            jin_kaku: 人格の数値
            chi_kaku: 地格の数値
            
        Returns:
            三才配置の辞書（五行と吉凶関係）
        """
        # 各格の五行を取得
        ten_element = self.get_element(ten_kaku)
        jin_element = self.get_element(jin_kaku)
        chi_element = self.get_element(chi_kaku)
        
        # 成功運: 天格→人格の関係
        success_luck = self.judge_relation(ten_element, jin_element)
        
        # 基礎運: 人格→地格の関係
        foundation_luck = self.judge_relation(jin_element, chi_element)
        
        return {
            "ten_element": ten_element,
            "jin_element": jin_element,
            "chi_element": chi_element,
            "success_luck": success_luck,
            "foundation_luck": foundation_luck
        }
    
    def get_yin_yang(self, surname_strokes: List[int], firstname_strokes: List[int]) -> str:
        """
        陰陽配列を判定
        
        奇数を○、偶数を●で表現
        
        Args:
            surname_strokes: 姓の画数リスト
            firstname_strokes: 名の画数リスト
            
        Returns:
            陰陽配列文字列（例: "○●○●"）
        """
        all_strokes = surname_strokes + firstname_strokes
        
        yin_yang_str = ""
        for stroke in all_strokes:
            if stroke % 2 == 1:
                yin_yang_str += "○"  # 奇数（陽）
            else:
                yin_yang_str += "●"  # 偶数（陰）
        
        return yin_yang_str
    
    def analyze(self, surname: str, firstname: str) -> Dict:
        """
        姓名判断の総合分析
        
        Args:
            surname: 姓
            firstname: 名
            
        Returns:
            JSON互換の分析結果辞書
        """
        # 画数リストを取得
        surname_strokes = self.calculate_strokes(surname)
        firstname_strokes = self.calculate_strokes(firstname)
        
        # 五格を計算
        five_grids = self.calc_five_elements(surname, firstname)
        
        # 三才配置を判定
        san_sai = self.get_san_sai(
            five_grids["ten_kaku"],
            five_grids["jin_kaku"],
            five_grids["chi_kaku"]
        )
        
        # 陰陽配列を判定
        yin_yang = self.get_yin_yang(surname_strokes, firstname_strokes)
        
        return {
            "surface": {
                "surname": surname,
                "firstname": firstname
            },
            "strokes": {
                "surname": surname_strokes,
                "firstname": firstname_strokes
            },
            "five_grids": five_grids,
            "san_sai": san_sai,
            "yin_yang": yin_yang
        }


# ============================================
# サンプル実行コード
# ============================================

if __name__ == "__main__":
    """
    動作デモ
    """
    # ダミーの画数辞書（実際は外部JSONから読み込む）
    sample_stroke_dict = {
        # 姓
        "安": 6, "瀬": 19,
        "佐": 7, "藤": 18,
        "田": 5, "中": 4,
        "山": 3, "本": 5,
        "高": 10, "橋": 16,
        "鈴": 13, "木": 4,
        
        # 名
        "諒": 15, "太": 4, "郎": 9,
        "一": 1, "二": 2, "三": 3,
        "健": 11, "介": 4, "也": 3,
        "美": 9, "子": 3, "花": 7,
        "明": 8, "彦": 9, "恵": 10
    }
    
    # インスタンス化
    logic = SeimeiLogic(sample_stroke_dict)
    
    # テストケース1: 安瀬 諒（2文字 + 1文字）
    print("=" * 60)
    print("テストケース1: 安瀬 諒（姓2文字 + 名1文字）")
    print("=" * 60)
    result1 = logic.analyze("安瀬", "諒")
    
    print(f"\n【基本情報】")
    print(f"姓: {result1['surface']['surname']}")
    print(f"名: {result1['surface']['firstname']}")
    print(f"姓の画数: {result1['strokes']['surname']} （合計: {sum(result1['strokes']['surname'])}画）")
    print(f"名の画数: {result1['strokes']['firstname']} （合計: {sum(result1['strokes']['firstname'])}画）")
    
    print(f"\n【五格】")
    print(f"天格: {result1['five_grids']['ten_kaku']}画")
    print(f"人格: {result1['five_grids']['jin_kaku']}画")
    print(f"地格: {result1['five_grids']['chi_kaku']}画 （名1文字なので霊数+1）")
    print(f"外格: {result1['five_grids']['gai_kaku']}画 （姓の最初 + 霊数）")
    print(f"総格: {result1['five_grids']['sou_kaku']}画")
    
    print(f"\n【三才配置】")
    print(f"天格の五行: {result1['san_sai']['ten_element']}")
    print(f"人格の五行: {result1['san_sai']['jin_element']}")
    print(f"地格の五行: {result1['san_sai']['chi_element']}")
    print(f"成功運（天→人）: {result1['san_sai']['success_luck']}")
    print(f"基礎運（人→地）: {result1['san_sai']['foundation_luck']}")
    
    print(f"\n【陰陽配列】")
    print(f"{result1['yin_yang']}")
    
    # テストケース2: 佐藤 太郎（2文字 + 2文字）
    print("\n\n" + "=" * 60)
    print("テストケース2: 佐藤 太郎（姓2文字 + 名2文字）")
    print("=" * 60)
    result2 = logic.analyze("佐藤", "太郎")
    
    print(f"\n【基本情報】")
    print(f"姓: {result2['surface']['surname']}")
    print(f"名: {result2['surface']['firstname']}")
    print(f"姓の画数: {result2['strokes']['surname']} （合計: {sum(result2['strokes']['surname'])}画）")
    print(f"名の画数: {result2['strokes']['firstname']} （合計: {sum(result2['strokes']['firstname'])}画）")
    
    print(f"\n【五格】")
    print(f"天格: {result2['five_grids']['ten_kaku']}画")
    print(f"人格: {result2['five_grids']['jin_kaku']}画")
    print(f"地格: {result2['five_grids']['chi_kaku']}画")
    print(f"外格: {result2['five_grids']['gai_kaku']}画 （姓の最初 + 名の最後）")
    print(f"総格: {result2['five_grids']['sou_kaku']}画")
    
    print(f"\n【三才配置】")
    print(f"天格の五行: {result2['san_sai']['ten_element']}")
    print(f"人格の五行: {result2['san_sai']['jin_element']}")
    print(f"地格の五行: {result2['san_sai']['chi_element']}")
    print(f"成功運（天→人）: {result2['san_sai']['success_luck']}")
    print(f"基礎運（人→地）: {result2['san_sai']['foundation_luck']}")
    
    print(f"\n【陰陽配列】")
    print(f"{result2['yin_yang']}")
    
    # テストケース3: 田 一（1文字 + 1文字）
    print("\n\n" + "=" * 60)
    print("テストケース3: 田 一（姓1文字 + 名1文字）")
    print("=" * 60)
    result3 = logic.analyze("田", "一")
    
    print(f"\n【基本情報】")
    print(f"姓: {result3['surface']['surname']}")
    print(f"名: {result3['surface']['firstname']}")
    print(f"姓の画数: {result3['strokes']['surname']} （合計: {sum(result3['strokes']['surname'])}画）")
    print(f"名の画数: {result3['strokes']['firstname']} （合計: {sum(result3['strokes']['firstname'])}画）")
    
    print(f"\n【五格】")
    print(f"天格: {result3['five_grids']['ten_kaku']}画 （姓1文字なので霊数+1）")
    print(f"人格: {result3['five_grids']['jin_kaku']}画")
    print(f"地格: {result3['five_grids']['chi_kaku']}画 （名1文字なので霊数+1）")
    print(f"外格: {result3['five_grids']['gai_kaku']}画 （霊数 + 霊数 = 2）")
    print(f"総格: {result3['five_grids']['sou_kaku']}画")
    
    print(f"\n【三才配置】")
    print(f"天格の五行: {result3['san_sai']['ten_element']}")
    print(f"人格の五行: {result3['san_sai']['jin_element']}")
    print(f"地格の五行: {result3['san_sai']['chi_element']}")
    print(f"成功運（天→人）: {result3['san_sai']['success_luck']}")
    print(f"基礎運（人→地）: {result3['san_sai']['foundation_luck']}")
    
    print(f"\n【陰陽配列】")
    print(f"{result3['yin_yang']}")
    
    print("\n\n" + "=" * 60)
    print("JSON出力例（テストケース1）")
    print("=" * 60)
    import json
    print(json.dumps(result1, ensure_ascii=False, indent=2))
