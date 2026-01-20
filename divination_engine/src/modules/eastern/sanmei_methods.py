    
    def _calc_void_period(self, void_branches: List[str]) -> Dict[str, str]:
        """
        天中殺期間を計算
        
        Args:
            void_branches: 天中殺の地支（2つ）
        
        Returns:
            天中殺期間の辞書
        """
        # 天中殺の期間マッピング
        void_periods = {
            ("戌", "亥"): {"年": "戌年・亥年", "月": "10月・11月", "日": "戌日・亥日"},
            ("申", "酉"): {"年": "申年・酉年", "月": "8月・9月", "日": "申日・酉日"},
            ("午", "未"): {"年": "午年・未年", "月": "6月・7月", "日": "午日・未日"},
            ("辰", "巳"): {"年": "辰年・巳年", "月": "4月・5月", "日": "辰日・巳日"},
            ("寅", "卯"): {"年": "寅年・卯年", "月": "2月・3月", "日": "寅日・卯日"},
            ("子", "丑"): {"年": "子年・丑年", "月": "12月・1月", "日": "子日・丑日"},
        }
        
        key = tuple(void_branches)
        return void_periods.get(key, {"年": "不明", "月": "不明", "日": "不明"})
    
    def _calc_energy_values(self, fp: FourPillars) -> Dict[str, int]:
        """
        数理法：エネルギー数値を計算
        
        気図法：天干・地支の数値化
        八門法：八門のエネルギー配分
        
        Args:
            fp: 四柱
        
        Returns:
            エネルギー数値の辞書
        """
        # 天干の数値（1-10）
        stem_values = {
            "甲": 1, "乙": 2, "丙": 3, "丁": 4, "戊": 5,
            "己": 6, "庚": 7, "辛": 8, "壬": 9, "癸": 10
        }
        
        # 地支の数値（1-12）
        branch_values = {
            "子": 1, "丑": 2, "寅": 3, "卯": 4, "辰": 5, "巳": 6,
            "午": 7, "未": 8, "申": 9, "酉": 10, "戌": 11, "亥": 12
        }
        
        # 各柱のエネルギー値
        year_energy = stem_values.get(fp.year.stem, 0) + branch_values.get(fp.year.branch, 0)
        month_energy = stem_values.get(fp.month.stem, 0) + branch_values.get(fp.month.branch, 0)
        day_energy = stem_values.get(fp.day.stem, 0) + branch_values.get(fp.day.branch, 0)
        hour_energy = stem_values.get(fp.hour.stem, 0) + branch_values.get(fp.hour.branch, 0)
        
        # 合計エネルギー
        total_energy = year_energy + month_energy + day_energy + hour_energy
        
        # 気図法の値
        ki_value = total_energy % 9
        if ki_value == 0:
            ki_value = 9
        
        return {
            "年柱": year_energy,
            "月柱": month_energy,
            "日柱": day_energy,
            "時柱": hour_energy,
            "合計": total_energy,
            "気図値": ki_value,
        }
    
    def _calc_phases(self, fp: FourPillars) -> Dict[str, List[str]]:
        """
        位相法：合法と散法を計算
        
        合法：支合、三合、方合
        散法：対冲、刑、害
        
        Args:
            fp: 四柱
        
        Returns:
            位相の辞書
        """
        合法 = []
        散法 = []
        
        branches = [
            ("年支", fp.year.branch),
            ("月支", fp.month.branch),
            ("日支", fp.day.branch),
            ("時支", fp.hour.branch)
        ]
        
        # 支合（六合）
        六合 = {
            ("子", "丑"): "土", ("寅", "亥"): "木", ("卯", "戌"): "火",
            ("辰", "酉"): "金", ("巳", "申"): "水", ("午", "未"): "火"
        }
        
        # 三合
        三合 = {
            ("申", "子", "辰"): "水局", ("亥", "卯", "未"): "木局",
            ("寅", "午", "戌"): "火局", ("巳", "酉", "丑"): "金局"
        }
        
        # 対冲（六冲）
        六冲 = {
            "子": "午", "丑": "未", "寅": "申", "卯": "酉",
            "辰": "戌", "巳": "亥", "午": "子", "未": "丑",
            "申": "寅", "酉": "卯", "戌": "辰", "亥": "巳"
        }
        
        # 支合をチェック
        for i in range(len(branches)):
            for j in range(i + 1, len(branches)):
                name1, branch1 = branches[i]
                name2, branch2 = branches[j]
                
                # 六合
                pair = tuple(sorted([branch1, branch2]))
                if pair in 六合:
                    合法.append(f"{name1}・{name2}：六合（{六合[pair]}化）")
                
                # 対冲
                if 六冲.get(branch1) == branch2:
                    散法.append(f"{name1}・{name2}：対冲")
        
        # 三合をチェック（簡易版）
        all_branches = [b for _, b in branches]
        for combo, nature in 三合.items():
            if all(b in all_branches for b in combo):
                合法.append(f"三合：{nature}")
        
        return {
            "合法": 合法 if 合法 else ["なし"],
            "散法": 散法 if 散法 else ["なし"]
        }
