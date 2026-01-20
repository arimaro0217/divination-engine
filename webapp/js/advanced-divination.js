/**
 * 高度占術モジュール（JavaScript版）
 * 四柱推命・算命学・九星気学の天文学ベースフルスペック機能
 */

const AdvancedDivinationModules = {

    // ===== 四柱推命高度機能 =====
    BaziAdvanced: {
        // 蔵干表（阿部泰山流）
        ZOGAN_TABLE: {
            "子": { "余気": null, "中気": null, "本気": "癸" },
            "丑": { "余気": "癸", "中気": "辛", "本気": "己" },
            "寅": { "余気": "戊", "中気": "丙", "本気": "甲" },
            "卯": { "余気": null, "中気": null, "本気": "乙" },
            "辰": { "余気": "乙", "中気": "癸", "本気": "戊" },
            "巳": { "余気": "戊", "中気": "庚", "本気": "丙" },
            "午": { "余気": null, "中気": "己", "本気": "丁" },
            "未": { "余気": "丁", "中気": "乙", "本気": "己" },
            "申": { "余気": "戊", "中気": "壬", "本気": "庚" },
            "酉": { "余気": null, "中気": null, "本気": "辛" },
            "戌": { "余気": "辛", "中気": "丁", "本気": "戊" },
            "亥": { "余気": null, "中気": "甲", "本気": "壬" }
        },

        // 蔵干深浅の割合（節入りからの進捗率）
        ZOGAN_DEPTH_RATIO: {
            "子": [["本気", 0.0, 1.0]],
            "丑": [["余気", 0.0, 0.30], ["中気", 0.30, 0.60], ["本気", 0.60, 1.0]],
            "寅": [["余気", 0.0, 0.23], ["中気", 0.23, 0.47], ["本気", 0.47, 1.0]],
            "卯": [["本気", 0.0, 1.0]],
            "辰": [["余気", 0.0, 0.30], ["中気", 0.30, 0.60], ["本気", 0.60, 1.0]],
            "巳": [["余気", 0.0, 0.23], ["中気", 0.23, 0.47], ["本気", 0.47, 1.0]],
            "午": [["中気", 0.0, 0.33], ["本気", 0.33, 1.0]],
            "未": [["余気", 0.0, 0.30], ["中気", 0.30, 0.60], ["本気", 0.60, 1.0]],
            "申": [["余気", 0.0, 0.23], ["中気", 0.23, 0.47], ["本気", 0.47, 1.0]],
            "酉": [["本気", 0.0, 1.0]],
            "戌": [["余気", 0.0, 0.30], ["中気", 0.30, 0.60], ["本気", 0.60, 1.0]],
            "亥": [["中気", 0.0, 0.40], ["本気", 0.40, 1.0]]
        },

        // 干合ペア
        KANGO_PAIRS: [["甲", "己"], ["乙", "庚"], ["丙", "辛"], ["丁", "壬"], ["戊", "癸"]],

        // 六合ペア  
        ZHIHE_PAIRS: [["子", "丑"], ["寅", "亥"], ["卯", "戌"], ["辰", "酉"], ["巳", "申"], ["午", "未"]],

        // 三合会局
        SANGO: {
            "水局": ["申", "子", "辰"],
            "木局": ["亥", "卯", "未"],
            "火局": ["寅", "午", "戌"],
            "金局": ["巳", "酉", "丑"]
        },

        // 対冲ペア
        CHU_PAIRS: [["子", "午"], ["丑", "未"], ["寅", "申"], ["卯", "酉"], ["辰", "戌"], ["巳", "亥"]],

        // 三刑
        SANKEI: {
            "無恩の刑": ["寅", "巳", "申"],
            "無礼の刑": ["丑", "戌", "未"],
            "持勢の刑": ["子", "卯"]
        },

        // 自刑
        JIKEI: ["辰", "午", "酉", "亥"],

        // 天乙貴人
        TENOTSU_KIJIN: {
            "甲": ["丑", "未"], "乙": ["子", "申"], "丙": ["亥", "酉"],
            "丁": ["亥", "酉"], "戊": ["丑", "未"], "己": ["子", "申"],
            "庚": ["丑", "未"], "辛": ["寅", "午"], "壬": ["卯", "巳"], "癸": ["卯", "巳"]
        },

        // 駅馬
        EKIBA: {
            "寅": "申", "午": "申", "戌": "申",
            "申": "寅", "子": "寅", "辰": "寅",
            "巳": "亥", "酉": "亥", "丑": "亥",
            "亥": "巳", "卯": "巳", "未": "巳"
        },

        // 桃花
        TOUKA: {
            "寅": "卯", "午": "卯", "戌": "卯",
            "申": "酉", "子": "酉", "辰": "酉",
            "巳": "午", "酉": "午", "丑": "午",
            "亥": "子", "卯": "子", "未": "子"
        },

        // 五行マッピング
        STEM_WUXING: {
            "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
            "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
        },

        /**
         * 蔵干深浅を計算
         */
        calcZoganDepth(monthBranch, progressRatio) {
            const depthTable = this.ZOGAN_DEPTH_RATIO[monthBranch];
            const zoganTable = this.ZOGAN_TABLE[monthBranch];

            for (const [type, start, end] of depthTable) {
                if (progressRatio >= start && progressRatio < end) {
                    return zoganTable[type] || zoganTable["本気"];
                }
            }
            return zoganTable["本気"];
        },

        /**
         * 刑冲会合を検出
         */
        findInteractions(stems, branches) {
            const result = {
                kango: [],
                zhihe: [],
                sango: [],
                chu: [],
                kei: []
            };

            // 干合
            for (const [s1, s2] of this.KANGO_PAIRS) {
                if (stems.includes(s1) && stems.includes(s2)) {
                    result.kango.push(`${s1}${s2}干合`);
                }
            }

            // 六合
            for (const [b1, b2] of this.ZHIHE_PAIRS) {
                if (branches.includes(b1) && branches.includes(b2)) {
                    result.zhihe.push(`${b1}${b2}支合`);
                }
            }

            // 三合会局
            for (const [name, req] of Object.entries(this.SANGO)) {
                if (req.every(b => branches.includes(b))) {
                    result.sango.push(`${req.join('')} (${name})`);
                }
            }

            // 対冲
            for (const [b1, b2] of this.CHU_PAIRS) {
                if (branches.includes(b1) && branches.includes(b2)) {
                    result.chu.push(`${b1}${b2}の冲`);
                }
            }

            // 三刑
            for (const [name, req] of Object.entries(this.SANKEI)) {
                const matched = req.filter(b => branches.includes(b));
                if (matched.length >= 2) {
                    result.kei.push(`${name}（${matched.join('')}）`);
                }
            }

            return result;
        },

        /**
         * 神殺を検出
         */
        findSpecialStars(dayStem, yearBranch, branches) {
            const stars = {};

            // 天乙貴人
            const kijin = this.TENOTSU_KIJIN[dayStem] || [];
            const foundKijin = branches.filter(b => kijin.includes(b));
            if (foundKijin.length > 0) stars["天乙貴人"] = foundKijin;

            // 駅馬
            const ekiba = this.EKIBA[yearBranch];
            if (ekiba && branches.includes(ekiba)) stars["駅馬"] = [ekiba];

            // 桃花
            const touka = this.TOUKA[yearBranch];
            if (touka && branches.includes(touka)) stars["桃花"] = [touka];

            return stars;
        },

        /**
         * 五行バランスを計算
         */
        calcGogyoBalance(stems, branches) {
            const balance = { "木": 0, "火": 0, "土": 0, "金": 0, "水": 0 };

            // 天干のエネルギー
            for (const stem of stems) {
                if (stem && this.STEM_WUXING[stem]) {
                    balance[this.STEM_WUXING[stem]] += 1;
                }
            }

            // 地支の蔵干エネルギー
            for (const branch of branches) {
                if (branch && this.ZOGAN_TABLE[branch]) {
                    const zogan = this.ZOGAN_TABLE[branch];
                    if (zogan["本気"]) balance[this.STEM_WUXING[zogan["本気"]]] += 1.0;
                    if (zogan["中気"]) balance[this.STEM_WUXING[zogan["中気"]]] += 0.5;
                    if (zogan["余気"]) balance[this.STEM_WUXING[zogan["余気"]]] += 0.3;
                }
            }

            return balance;
        },

        /**
         * 高度計算を実行
         */
        calculate(fourPillars, progressRatio = 0.5) {
            const stems = [fourPillars.year.stem, fourPillars.month.stem,
            fourPillars.day.stem, fourPillars.hour?.stem].filter(Boolean);
            const branches = [fourPillars.year.branch, fourPillars.month.branch,
            fourPillars.day.branch, fourPillars.hour?.branch].filter(Boolean);

            const monthZogan = this.calcZoganDepth(fourPillars.month.branch, progressRatio);
            const interactions = this.findInteractions(stems, branches);
            const specialStars = this.findSpecialStars(
                fourPillars.day.stem,
                fourPillars.year.branch,
                branches
            );
            const gogyoBalance = this.calcGogyoBalance(stems, branches);

            return {
                monthZogan,
                zoganProgress: progressRatio,
                interactions,
                specialStars,
                gogyoBalance
            };
        }
    },

    // ===== 算命学高度機能 =====
    SanmeiAdvanced: {
        // 十大主星
        TEN_MAIN_STARS: {
            "比肩": "貫索星", "劫財": "石門星",
            "食神": "鳳閣星", "傷官": "調舒星",
            "偏財": "禄存星", "正財": "司禄星",
            "偏官": "車騎星", "正官": "牽牛星",
            "偏印": "龍高星", "正印": "玉堂星"
        },

        // 十二大従星とエネルギー
        TWELVE_SUB_STARS: {
            "天報星": 0, "天印星": 2, "天貴星": 4, "天恍星": 6,
            "天南星": 8, "天禄星": 10, "天将星": 12, "天堂星": 10,
            "天胡星": 8, "天極星": 6, "天庫星": 4, "天馳星": 2
        },

        // 異常干支
        ABNORMAL_GANZHI: [
            "甲戌", "乙亥", "丙戌", "丁亥", "戊戌",
            "辛亥", "壬午", "癸巳", "癸丑", "甲午"
        ],

        // 人体星図の位置
        JINTAI_POSITIONS: ["頭", "左肩", "右手", "胸", "左手", "腹", "右足", "左足"],

        /**
         * 宇宙盤の角度を計算
         */
        getUchubanAngle(ganzhi) {
            const SIXTY_GANZHI = [
                "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
                "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
                "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
                "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
                "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
                "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"
            ];
            const index = SIXTY_GANZHI.indexOf(ganzhi);
            if (index === -1) return 0;
            return (90 - index * 6 + 360) % 360;
        },

        /**
         * 宇宙盤データを生成
         */
        createUchuban(yearGanzhi, monthGanzhi, dayGanzhi) {
            const toCoord = (angle) => {
                const rad = angle * Math.PI / 180;
                return { x: Math.cos(rad), y: Math.sin(rad) };
            };

            const yearAngle = this.getUchubanAngle(yearGanzhi);
            const monthAngle = this.getUchubanAngle(monthGanzhi);
            const dayAngle = this.getUchubanAngle(dayGanzhi);

            const yearCoord = toCoord(yearAngle);
            const monthCoord = toCoord(monthAngle);
            const dayCoord = toCoord(dayAngle);

            // 三角形の面積
            const area = Math.abs(
                (yearCoord.x * (monthCoord.y - dayCoord.y) +
                    monthCoord.x * (dayCoord.y - yearCoord.y) +
                    dayCoord.x * (yearCoord.y - monthCoord.y)) / 2
            );

            // パターン分類
            let patternType = "小領域型（集中型）";
            if (area >= 1.5) patternType = "超大領域型（多方面型）";
            else if (area >= 1.0) patternType = "大領域型（拡散型）";
            else if (area >= 0.5) patternType = "中領域型（バランス型）";

            return {
                points: [
                    { label: "年", ganzhi: yearGanzhi, angle: yearAngle, ...yearCoord },
                    { label: "月", ganzhi: monthGanzhi, angle: monthAngle, ...monthCoord },
                    { label: "日", ganzhi: dayGanzhi, angle: dayAngle, ...dayCoord }
                ],
                area: Math.round(area * 10000) / 10000,
                patternType
            };
        },

        /**
         * 異常干支を検出
         */
        checkAbnormalGanzhi(ganzhiList) {
            return ganzhiList.filter(gz => this.ABNORMAL_GANZHI.includes(gz));
        },

        /**
         * 高度計算を実行
         */
        calculate(fourPillars, tenGods) {
            const yearGanzhi = fourPillars.year.stem + fourPillars.year.branch;
            const monthGanzhi = fourPillars.month.stem + fourPillars.month.branch;
            const dayGanzhi = fourPillars.day.stem + fourPillars.day.branch;

            // 十大主星に変換
            const mainStars = {};
            for (const [pos, god] of Object.entries(tenGods || {})) {
                if (god && this.TEN_MAIN_STARS[god]) {
                    mainStars[pos] = this.TEN_MAIN_STARS[god];
                }
            }

            // 宇宙盤
            const uchuban = this.createUchuban(yearGanzhi, monthGanzhi, dayGanzhi);

            // 異常干支
            const abnormalGanzhi = this.checkAbnormalGanzhi([yearGanzhi, monthGanzhi, dayGanzhi]);

            return {
                mainStars,
                uchuban,
                abnormalGanzhi
            };
        }
    },

    // ===== 九星気学高度機能 =====
    KyuseiAdvanced: {
        NINE_STARS: ["一白水星", "二黒土星", "三碧木星", "四緑木星", "五黄土星",
            "六白金星", "七赤金星", "八白土星", "九紫火星"],

        STAR_ELEMENTS: {
            1: "水", 2: "土", 3: "木", 4: "木", 5: "土",
            6: "金", 7: "金", 8: "土", 9: "火"
        },

        // 方位の角度（標準方式：30/60度）
        DIRECTION_ANGLES: {
            "N": { start: 345, end: 15, width: 30 },
            "NE": { start: 15, end: 75, width: 60 },
            "E": { start: 75, end: 105, width: 30 },
            "SE": { start: 105, end: 165, width: 60 },
            "S": { start: 165, end: 195, width: 30 },
            "SW": { start: 195, end: 255, width: 60 },
            "W": { start: 255, end: 285, width: 30 },
            "NW": { start: 285, end: 345, width: 60 }
        },

        // 方位の日本語名
        DIRECTION_NAMES: {
            "N": "北", "NE": "北東", "E": "東", "SE": "南東",
            "S": "南", "SW": "南西", "W": "西", "NW": "北西"
        },

        // 対中方位
        OPPOSITE: { "N": "S", "NE": "SW", "E": "W", "SE": "NW", "S": "N", "SW": "NE", "W": "E", "NW": "SE" },

        /**
         * 方位盤を生成
         */
        createBoard(centerStar) {
            const DIRECTION_TO_PALACE = { "N": 1, "SW": 2, "E": 3, "SE": 4, "NW": 6, "W": 7, "NE": 8, "S": 9 };
            const board = {};

            for (const [dir, palace] of Object.entries(DIRECTION_TO_PALACE)) {
                const offset = palace - 5;
                let star = ((centerStar - 1) + offset) % 9 + 1;
                if (star <= 0) star += 9;
                board[dir] = star;
            }

            return board;
        },

        /**
         * 吉凶方位を判定
         */
        judgeDirections(board, userStar) {
            const gooSatsu = [];
            const ankenSatsu = [];
            const luckyDirs = [];

            for (const [dir, star] of Object.entries(board)) {
                // 五黄殺
                if (star === 5) {
                    gooSatsu.push(dir);
                    ankenSatsu.push(this.OPPOSITE[dir]);
                }

                // 吉方位（相生関係）
                const userElement = this.STAR_ELEMENTS[userStar];
                const dirElement = this.STAR_ELEMENTS[star];
                const SHENG = { "木": "火", "火": "土", "土": "金", "金": "水", "水": "木" };

                if (SHENG[userElement] === dirElement || SHENG[dirElement] === userElement) {
                    if (!gooSatsu.includes(dir) && !ankenSatsu.includes(dir)) {
                        luckyDirs.push(dir);
                    }
                }
            }

            return { gooSatsu, ankenSatsu, luckyDirs };
        },

        /**
         * 磁気偏角を計算（日本国内簡易版）
         */
        calcMagneticDeclination(lat, lon) {
            return -7.0 + (lat - 35) * 0.1 + (lon - 140) * 0.05;
        },

        /**
         * 地図オーバーレイデータを生成
         */
        createMapOverlay(centerLat, centerLon, board, judgment, useMagnetic = false) {
            const declination = useMagnetic ? this.calcMagneticDeclination(centerLat, centerLon) : 0;
            const sectors = [];

            for (const [dir, angles] of Object.entries(this.DIRECTION_ANGLES)) {
                let startAngle = angles.start;
                let endAngle = angles.end;

                if (useMagnetic) {
                    startAngle = (startAngle - declination + 360) % 360;
                    endAngle = (endAngle - declination + 360) % 360;
                }

                let status = "neutral";
                const notes = [];

                if (judgment.gooSatsu.includes(dir)) {
                    status = "worst";
                    notes.push("五黄殺");
                }
                if (judgment.ankenSatsu.includes(dir)) {
                    status = "worst";
                    notes.push("暗剣殺");
                }
                if (status === "neutral" && judgment.luckyDirs.includes(dir)) {
                    status = "good";
                    notes.push("吉方");
                }

                sectors.push({
                    label: dir,
                    nameJp: this.DIRECTION_NAMES[dir],
                    startAngle: Math.round(startAngle * 10) / 10,
                    endAngle: Math.round(endAngle * 10) / 10,
                    star: board[dir],
                    starName: this.NINE_STARS[board[dir] - 1],
                    status,
                    notes
                });
            }

            return {
                centerLat,
                centerLon,
                magneticDeclination: Math.round(declination * 10) / 10,
                useMagneticNorth: useMagnetic,
                sectors
            };
        },

        /**
         * 高度計算を実行
         */
        calculate(yearStar, monthStar, dayStar, userStar, lat, lon) {
            const dayBoard = this.createBoard(dayStar);
            const monthBoard = this.createBoard(monthStar);
            const yearBoard = this.createBoard(yearStar);

            const dayJudgment = this.judgeDirections(dayBoard, userStar);
            const mapOverlay = this.createMapOverlay(lat, lon, dayBoard, dayJudgment, true);

            return {
                boards: {
                    year: { center: yearStar, directions: yearBoard },
                    month: { center: monthStar, directions: monthBoard },
                    day: { center: dayStar, directions: dayBoard }
                },
                judgment: dayJudgment,
                mapOverlay
            };
        }
    }
};

// グローバルに公開
if (typeof window !== 'undefined') {
    window.AdvancedDivinationModules = AdvancedDivinationModules;
}
