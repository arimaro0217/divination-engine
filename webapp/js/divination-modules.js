/**
 * 占術計算モジュール（JavaScript版）
 * 12種類の占術計算を提供
 */

const DivinationModules = {

    // ===== 四柱推命 =====
    BaZi: {
        // 通変星（十神）テーブル
        TEN_GODS: {
            '木木同': '比肩', '木木異': '劫財',
            '木火同': '食神', '木火異': '傷官',
            '木土同': '偏財', '木土異': '正財',
            '木金同': '偏官', '木金異': '正官',
            '木水同': '偏印', '木水異': '印綬',

            '火火同': '比肩', '火火異': '劫財',
            '火土同': '食神', '火土異': '傷官',
            '火金同': '偏財', '火金異': '正財',
            '火水同': '偏官', '火水異': '正官',
            '火木同': '偏印', '火木異': '印綬',

            '土土同': '比肩', '土土異': '劫財',
            '土金同': '食神', '土金異': '傷官',
            '土水同': '偏財', '土水異': '正財',
            '土木同': '偏官', '土木異': '正官',
            '土火同': '偏印', '土火異': '印綬',

            '金金同': '比肩', '金金異': '劫財',
            '金水同': '食神', '金水異': '傷官',
            '金木同': '偏財', '金木異': '正財',
            '金火同': '偏官', '金火異': '正官',
            '金土同': '偏印', '金土異': '印綬',

            '水水同': '比肩', '水水異': '劫財',
            '水木同': '食神', '水木異': '傷官',
            '水火同': '偏財', '水火異': '正財',
            '水土同': '偏官', '水土異': '正官',
            '水金同': '偏印', '水金異': '印綬'
        },

        // 十二運
        TWELVE_STAGES: {
            '甲': { '亥': '長生', '子': '沐浴', '丑': '冠帯', '寅': '建禄', '卯': '帝旺', '辰': '衰', '巳': '病', '午': '死', '未': '墓', '申': '絶', '酉': '胎', '戌': '養' },
            '乙': { '午': '長生', '巳': '沐浴', '辰': '冠帯', '卯': '建禄', '寅': '帝旺', '丑': '衰', '子': '病', '亥': '死', '戌': '墓', '酉': '絶', '申': '胎', '未': '養' },
            '丙': { '寅': '長生', '卯': '沐浴', '辰': '冠帯', '巳': '建禄', '午': '帝旺', '未': '衰', '申': '病', '酉': '死', '戌': '墓', '亥': '絶', '子': '胎', '丑': '養' },
            '丁': { '酉': '長生', '申': '沐浴', '未': '冠帯', '午': '建禄', '巳': '帝旺', '辰': '衰', '卯': '病', '寅': '死', '丑': '墓', '子': '絶', '亥': '胎', '戌': '養' },
            '戊': { '寅': '長生', '卯': '沐浴', '辰': '冠帯', '巳': '建禄', '午': '帝旺', '未': '衰', '申': '病', '酉': '死', '戌': '墓', '亥': '絶', '子': '胎', '丑': '養' },
            '己': { '酉': '長生', '申': '沐浴', '未': '冠帯', '午': '建禄', '巳': '帝旺', '辰': '衰', '卯': '病', '寅': '死', '丑': '墓', '子': '絶', '亥': '胎', '戌': '養' },
            '庚': { '巳': '長生', '午': '沐浴', '未': '冠帯', '申': '建禄', '酉': '帝旺', '戌': '衰', '亥': '病', '子': '死', '丑': '墓', '寅': '絶', '卯': '胎', '辰': '養' },
            '辛': { '子': '長生', '亥': '沐浴', '戌': '冠帯', '酉': '建禄', '申': '帝旺', '未': '衰', '午': '病', '巳': '死', '辰': '墓', '卯': '絶', '寅': '胎', '丑': '養' },
            '壬': { '申': '長生', '酉': '沐浴', '戌': '冠帯', '亥': '建禄', '子': '帝旺', '丑': '衰', '寅': '病', '卯': '死', '辰': '墓', '巳': '絶', '午': '胎', '未': '養' },
            '癸': { '卯': '長生', '寅': '沐浴', '丑': '冠帯', '子': '建禄', '亥': '帝旺', '戌': '衰', '酉': '病', '申': '死', '未': '墓', '午': '絶', '巳': '胎', '辰': '養' }
        },

        calculate(date, use23Switch = true) {
            // SolarTermEngineを優先使用（精密計算）
            let pillars, voidBranches, hiddenStems, monthInfo;

            if (typeof SolarTermEngine !== 'undefined') {
                const reading = SolarTermEngine.generateFullReading(date, use23Switch);
                pillars = reading.pillars;
                voidBranches = reading.voidBranches.branches;
                hiddenStems = reading.hiddenStems;
                monthInfo = reading.monthInfo;
            } else {
                // フォールバック
                pillars = ChineseCalendar.calcFourPillars(date);
                voidBranches = ChineseCalendar.calcVoidBranches(pillars.day);
            }

            const dayMaster = pillars.day.stem;

            // 通変星を計算
            const tenGods = {};
            const dayElement = ChineseCalendar.STEM_ELEMENTS[dayMaster];
            const dayYinYang = ChineseCalendar.STEM_YIN_YANG[dayMaster];

            [['年', pillars.year], ['月', pillars.month], ['時', pillars.hour]].forEach(([name, pillar]) => {
                const stemElement = ChineseCalendar.STEM_ELEMENTS[pillar.stem];
                const stemYinYang = ChineseCalendar.STEM_YIN_YANG[pillar.stem];
                const sameYinYang = dayYinYang === stemYinYang ? '同' : '異';
                const key = dayElement + stemElement + sameYinYang;
                tenGods[name + '干'] = this.TEN_GODS[key] || '比肩';
            });

            // 十二運を計算
            const twelveStages = {};
            const stageMap = this.TWELVE_STAGES[dayMaster] || {};
            [['年', pillars.year], ['月', pillars.month], ['日', pillars.day], ['時', pillars.hour]].forEach(([name, pillar]) => {
                twelveStages[name + '支'] = stageMap[pillar.branch] || '';
            });

            return {
                type: '四柱推命',
                pillars,
                dayMaster,
                dayMasterElement: dayElement,
                dayMasterYinYang: dayYinYang,
                voidBranches,
                tenGods,
                twelveStages,
                hiddenStems: hiddenStems || null,
                monthInfo: monthInfo || null,
                use23Switch
            };
        }
    },

    // ===== 算命学 =====
    Sanmei: {
        TEN_MAIN_STARS: {
            '比肩': '貫索星', '劫財': '石門星',
            '食神': '鳳閣星', '傷官': '調舒星',
            '偏財': '禄存星', '正財': '司禄星',
            '偏官': '車騎星', '正官': '牽牛星',
            '偏印': '龍高星', '印綬': '玉堂星'
        },

        // 十二大従星マッピング（算命学標準）
        // 四柱推命の十二運 → 算命学の従星
        TWELVE_SUB_STARS: {
            '胎': '天報星',   // 初期のエネルギー
            '養': '天印星',   // 成長期
            '長生': '天貴星', // 誕生の星
            '沐浴': '天恍星', // 青春期
            '冠帯': '天南星', // 成人期
            '建禄': '天禄星', // 安定期
            '帝旺': '天将星', // 最盛期（最強）
            '衰': '天堂星',   // 晩年期
            '病': '天胡星',   // 衰退期
            '死': '天極星',   // 精神的な深さ
            '墓': '天庫星',   // 蓄積期
            '絶': '天馳星'    // 転換期
        },

        VOID_GROUP_NAMES: {
            '戌亥': '戌亥天中殺', '申酉': '申酉天中殺',
            '午未': '午未天中殺', '辰巳': '辰巳天中殺',
            '寅卯': '寅卯天中殺', '子丑': '子丑天中殺'
        },

        calculate(date) {
            const baziResult = DivinationModules.BaZi.calculate(date);

            // 十大主星に変換
            const mainStars = {};
            Object.entries(baziResult.tenGods).forEach(([key, value]) => {
                mainStars[key] = this.TEN_MAIN_STARS[value] || value;
            });

            // 十二大従星に変換
            const subStars = {};
            Object.entries(baziResult.twelveStages).forEach(([key, value]) => {
                subStars[key] = this.TWELVE_SUB_STARS[value] || value;
            });

            // 天中殺グループ名
            const voidKey = baziResult.voidBranches.join('');
            const voidGroupName = this.VOID_GROUP_NAMES[voidKey] || voidKey + '天中殺';

            return {
                type: '算命学',
                pillars: baziResult.pillars,
                voidBranches: baziResult.voidBranches,
                voidGroupName,
                mainStars,
                subStars
            };
        }
    },

    // ===== 九星気学 =====
    Kyusei: {
        NINE_STARS: ['一白水星', '二黒土星', '三碧木星', '四緑木星', '五黄土星',
            '六白金星', '七赤金星', '八白土星', '九紫火星'],

        PALACE_NAMES: {
            1: '坎宮（北）', 2: '坤宮（南西）', 3: '震宮（東）',
            4: '巽宮（南東）', 5: '中宮（中央）', 6: '乾宮（北西）',
            7: '兌宮（西）', 8: '艮宮（北東）', 9: '離宮（南）'
        },

        // 月命星の2月開始位置テーブル（これは占術の定義なので固定）
        MONTH_START: {
            1: 8, 4: 8, 7: 8,
            2: 2, 5: 2, 8: 2,
            3: 5, 6: 5, 9: 5
        },

        // 甲子日の基準JD
        BASE_JD: 2445731,

        /**
         * グレゴリオ暦からユリウス日を計算
         */
        calcJD(year, month, day, hour = 12) {
            const a = Math.floor((14 - month) / 12);
            const y = year + 4800 - a;
            const m = month + 12 * a - 3;
            return day + Math.floor((153 * m + 2) / 5) + 365 * y +
                Math.floor(y / 4) - Math.floor(y / 100) +
                Math.floor(y / 400) - 32045 + (hour - 12) / 24;
        },

        /**
         * ユリウス日からグレゴリオ暦を計算
         */
        jdToGregorian(jd) {
            const z = Math.floor(jd + 0.5);
            const a = Math.floor((z - 1867216.25) / 36524.25);
            const aa = z + 1 + a - Math.floor(a / 4);
            const b = aa + 1524;
            const c = Math.floor((b - 122.1) / 365.25);
            const d = Math.floor(365.25 * c);
            const e = Math.floor((b - d) / 30.6001);
            const day = b - d - Math.floor(30.6001 * e);
            const month = e < 14 ? e - 1 : e - 13;
            const year = month > 2 ? c - 4716 : c - 4715;
            return { year, month, day };
        },

        /**
         * 太陽の黄経を計算（簡易版VSOP87）
         * @param {number} jd - ユリウス日
         * @returns {number} 太陽黄経（度）
         */
        calcSunLongitude(jd) {
            // ユリウス世紀（J2000.0基準）
            const T = (jd - 2451545.0) / 36525;

            // 平均黄経
            const L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T;

            // 太陽の平均近点角
            const M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T;
            const Mrad = M * Math.PI / 180;

            // 中心差
            const C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * Math.sin(Mrad)
                + (0.019993 - 0.000101 * T) * Math.sin(2 * Mrad)
                + 0.000289 * Math.sin(3 * Mrad);

            // 真黄経
            let sunLon = L0 + C;

            // 0-360度に正規化
            sunLon = sunLon % 360;
            if (sunLon < 0) sunLon += 360;

            return sunLon;
        },

        /**
         * 太陽が特定の黄経に達する日時を二分法で求める
         * @param {number} targetLon - 目標黄経（度）
         * @param {number} year - 対象年
         * @returns {number} ユリウス日
         */
        findSolarLongitudeDate(targetLon, year) {
            // 初期推定値（冬至=270度は12月22日頃、夏至=90度は6月21日頃）
            let jdLow, jdHigh;
            if (targetLon === 270) {
                // 冬至
                jdLow = this.calcJD(year, 12, 15);
                jdHigh = this.calcJD(year, 12, 28);
            } else if (targetLon === 90) {
                // 夏至
                jdLow = this.calcJD(year, 6, 15);
                jdHigh = this.calcJD(year, 6, 28);
            } else {
                // 汎用
                const daysInYear = 365.25;
                const approxDay = (targetLon / 360) * daysInYear;
                const baseJD = this.calcJD(year, 1, 1);
                jdLow = baseJD + approxDay - 15;
                jdHigh = baseJD + approxDay + 15;
            }

            // 二分法で精度を上げる
            const tolerance = 0.0001; // 約8.6秒の精度
            while (jdHigh - jdLow > tolerance) {
                const jdMid = (jdLow + jdHigh) / 2;
                const lonMid = this.calcSunLongitude(jdMid);

                // 黄経が360度→0度をまたぐ場合の処理
                let diff = lonMid - targetLon;
                if (diff > 180) diff -= 360;
                if (diff < -180) diff += 360;

                if (diff < 0) {
                    jdLow = jdMid;
                } else {
                    jdHigh = jdMid;
                }
            }

            return (jdLow + jdHigh) / 2;
        },

        /**
         * 指定年の冬至のユリウス日を計算
         */
        calcWinterSolstice(year) {
            return this.findSolarLongitudeDate(270, year);
        },

        /**
         * 指定年の夏至のユリウス日を計算
         */
        calcSummerSolstice(year) {
            return this.findSolarLongitudeDate(90, year);
        },

        /**
         * 二十四節気の黄経から節入り日を動的に計算
         * @param {number} year - 対象年
         * @param {number} month - 対象月
         * @returns {number} 節入り日
         */
        calcSetsuiriDay(year, month) {
            // 各月の節気と対応する太陽黄経
            const solarTermsLon = {
                1: 285,   // 小寒（黄経285度）
                2: 315,   // 立春（黄経315度）
                3: 345,   // 啓蟄（黄経345度）
                4: 15,    // 清明（黄経15度）
                5: 45,    // 立夏（黄経45度）
                6: 75,    // 芒種（黄経75度）
                7: 105,   // 小暑（黄経105度）
                8: 135,   // 立秋（黄経135度）
                9: 165,   // 白露（黄経165度）
                10: 195,  // 寒露（黄経195度）
                11: 225,  // 立冬（黄経225度）
                12: 255   // 大雪（黄経255度）
            };

            const targetLon = solarTermsLon[month];

            // 節気が前年にまたがる場合の処理
            let searchYear = year;
            if (month === 1 || month === 2) {
                // 1月、2月の節気は前年12月〜当年2月に発生
            }

            // 節入り日を計算
            const jd = this.findSolarLongitudeDate(targetLon, searchYear);
            const date = this.jdToGregorian(jd);

            return date.day;
        },

        /**
         * 気学上の月を取得（動的計算版）
         */
        getKigakuMonth(year, month, day) {
            // 当月の節入り日を動的に計算
            const setsuiriDay = this.calcSetsuiriDay(year, month);

            if (day < setsuiriDay) {
                // 節入り前なので前月
                return month === 1 ? 12 : month - 1;
            }
            return month;
        },

        /**
         * 本命星を計算（男女共通）
         */
        calcYearStar(year) {
            let digitSum = year.toString().split('').reduce((sum, d) => sum + parseInt(d), 0);
            while (digitSum > 9) {
                digitSum = digitSum.toString().split('').reduce((sum, d) => sum + parseInt(d), 0);
            }
            let star = 11 - digitSum;
            if (star > 9) star -= 9;
            return star;
        },

        /**
         * 月命星を計算
         */
        calcMonthStar(yearStar, kigakuMonth) {
            const februaryStart = this.MONTH_START[yearStar] || 5;
            let monthOffset = kigakuMonth - 2;
            if (monthOffset < 0) monthOffset += 12;

            let star = februaryStart - monthOffset;
            while (star <= 0) star += 9;
            while (star > 9) star -= 9;
            return star;
        },

        /**
         * 陽遁始め（冬至に最も近い甲子日）を計算
         */
        calcYotonStart(year) {
            const winterSolsticeJD = this.calcWinterSolstice(year);

            // 冬至に最も近い甲子日（ganzhiIdx=0）を探す
            const daysSinceJiazi = ((winterSolsticeJD - this.BASE_JD) % 60 + 60) % 60;
            const daysToNextJiazi = daysSinceJiazi === 0 ? 0 : 60 - daysSinceJiazi;
            const daysToPrevJiazi = daysSinceJiazi;

            // より近い方を選択
            if (daysToNextJiazi <= daysToPrevJiazi) {
                return Math.floor(winterSolsticeJD) + daysToNextJiazi;
            } else {
                return Math.floor(winterSolsticeJD) - daysToPrevJiazi;
            }
        },

        /**
         * 陰遁始め（夏至に最も近い甲午日）を計算
         */
        calcIntonStart(year) {
            const summerSolsticeJD = this.calcSummerSolstice(year);

            // 夏至に最も近い甲午日（ganzhiIdx=30）を探す
            const offset = ((summerSolsticeJD - this.BASE_JD - 30) % 60 + 60) % 60;
            const daysToNextJiawu = offset === 0 ? 0 : 60 - offset;
            const daysToPrevJiawu = offset;

            // より近い方を選択
            if (daysToNextJiawu <= daysToPrevJiawu) {
                return Math.floor(summerSolsticeJD) + daysToNextJiawu;
            } else {
                return Math.floor(summerSolsticeJD) - daysToPrevJiawu;
            }
        },

        /**
         * 日命星を計算（高精度版）
         */
        calcDayStar(year, month, day) {
            const jdTarget = this.calcJD(year, month, day);
            const ganzhiIdx = ((jdTarget - this.BASE_JD) % 60 + 60) % 60;

            // 当年と前年の陽遁始め・陰遁始めを計算
            const yotonStartCurrent = this.calcYotonStart(year);
            const intonStartCurrent = this.calcIntonStart(year);
            const yotonStartPrev = this.calcYotonStart(year - 1);

            // 陽遁/陰遁の判定
            // 当年の陽遁始め以降、または前年の陽遁始め以降で当年の陰遁始め前
            let isYoton;
            if (jdTarget >= yotonStartCurrent) {
                // 当年の陽遁始め以降は陽遁
                isYoton = true;
            } else if (jdTarget >= intonStartCurrent) {
                // 当年の陰遁始め以降、陽遁始め前は陰遁
                isYoton = false;
            } else if (jdTarget >= yotonStartPrev) {
                // 前年の陽遁始め以降、当年の陰遁始め前は陽遁
                isYoton = true;
            } else {
                // それ以外は陰遁
                isYoton = false;
            }

            let dayStarNum;
            if (isYoton) {
                // 陽遁: 一白から順に増加
                dayStarNum = (ganzhiIdx % 9) + 1;
            } else {
                // 陰遁: 九紫から順に減少
                dayStarNum = 9 - (ganzhiIdx % 9);
                if (dayStarNum <= 0) dayStarNum += 9;
            }

            return { dayStarNum, isYoton, yotonStartCurrent, intonStartCurrent };
        },

        calculate(date, gender = 'male') {
            const year = date.getFullYear();
            const month = date.getMonth() + 1;
            const day = date.getDate();

            // --- 1. 気学上の年を判定（立春基準・動的計算） ---
            const risshunJD = this.findSolarLongitudeDate(315, year);
            const currentJD = this.calcJD(year, month, day);
            let targetYear = year;
            if (currentJD < risshunJD) {
                targetYear = year - 1;
            }

            // --- 2. 本命星を計算 ---
            const yearStarNum = this.calcYearStar(targetYear);

            // --- 3. 気学上の月を判定（動的計算） ---
            let kigakuMonth = this.getKigakuMonth(year, month, day);

            // --- 4. 月命星を計算 ---
            const monthStarNum = this.calcMonthStar(yearStarNum, kigakuMonth);

            // --- 5. 日命星を計算（高精度版） ---
            const dayResult = this.calcDayStar(year, month, day);
            const dayStarNum = dayResult.dayStarNum;

            return {
                type: '九星気学',
                targetYear,
                kigakuMonth,
                yearStar: this.NINE_STARS[yearStarNum - 1],
                yearStarNum,
                monthStar: this.NINE_STARS[monthStarNum - 1],
                monthStarNum,
                dayStar: this.NINE_STARS[dayStarNum - 1],
                dayStarNum,
                inclination: this.PALACE_NAMES[monthStarNum],
                // デバッグ情報
                _debug: {
                    isYoton: dayResult.isYoton,
                    yotonStart: this.jdToGregorian(dayResult.yotonStartCurrent),
                    intonStart: this.jdToGregorian(dayResult.intonStartCurrent)
                }
            };
        }
    },

    // ===== 紫微斗数 =====
    ZiWei: {
        PALACES: ['命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮',
            '遷移宮', '奴僕宮', '官禄宮', '田宅宮', '福徳宮', '父母宮'],

        // 五行局判定テーブル (地支グループ x 天干グループ)
        JU_TABLE: [
            [4, 4, 3, 3, 2], // 子丑
            [2, 3, 3, 5, 5], // 寅卯
            [3, 5, 5, 4, 4], // 辰巳
            [4, 4, 6, 6, 2], // 午未
            [2, 6, 6, 3, 3], // 申酉
            [3, 3, 2, 2, 5]  // 戌亥
        ],

        // 天府星系の紫微星からの相対位置
        TIANFU_MAP: { 0: 4, 1: 3, 2: 2, 3: 1, 4: 0, 5: 11, 6: 10, 7: 9, 8: 8, 9: 7, 10: 6, 11: 5 },

        // 命主（命宮の地支による）
        LIFE_MASTERS: ['貪狼', '巨門', '禄存', '文曲', '廉貞', '武曲', '破軍', '武曲', '廉貞', '文曲', '禄存', '巨門'],
        // 身主（生年の地支による）
        BODY_MASTERS: ['火星', '天相', '天梁', '天同', '文昌', '天機', '火星', '天相', '天梁', '天同', '文昌', '天機'],

        calculate(date, gender = 'male') {
            const lunarDate = ChineseCalendar.toLunarDate(date);
            const hourBranch = Math.floor((date.getHours() + 1) / 2) % 12;
            const yearStemIdx = ChineseCalendar.STEM_INDICES[ChineseCalendar.calcFourPillars(date).year.stem];
            const yearBranchIdx = ChineseCalendar.BRANCH_INDICES[ChineseCalendar.calcFourPillars(date).year.branch];

            // 1. 命宮位置
            const mingIdx = (2 + lunarDate.month - 1 - hourBranch + 12) % 12;
            const bodyIdx = (2 + lunarDate.month - 1 + hourBranch) % 12;

            // 命主・身主
            const lifeMaster = this.LIFE_MASTERS[mingIdx];
            const bodyMaster = this.BODY_MASTERS[yearBranchIdx] || '不明';

            // 2. 命宮の天干（五行局計算用）
            const yinStemBase = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0][yearStemIdx];
            const mingStemIdx = (yinStemBase + (mingIdx - 2 + 12) % 12) % 10;
            const mingStem = ChineseCalendar.STEMS[mingStemIdx];

            // 3. 五行局
            const branchGroup = Math.floor(mingIdx / 2);
            const stemGroup = mingStemIdx % 5;
            const bureau = this.JU_TABLE[branchGroup][stemGroup];
            const bureauName = ['?', '?', '木二局', '火三局', '土五局', '金四局', '水二局'][bureau] || '火三局';

            // 4. 紫微星の位置
            let ziweiIdx = 0;
            const quotient = Math.floor((lunarDate.day - 1) / bureau);
            const remainder = (lunarDate.day - 1) % bureau;
            if (quotient % 2 === 0) {
                ziweiIdx = (2 + quotient + remainder) % 12;
            } else {
                ziweiIdx = (2 + quotient + (bureau - 1 - remainder)) % 12;
            }

            // 5. 天府星の位置
            const tianfuIdx = this.TIANFU_MAP[ziweiIdx];

            // 6. 星を収集
            const starPositions = {
                'major_stars': {},
                'minor_stars': [],
                'bad_stars': []
            };

            // 主星系（紫微・天府）
            const ziOffsets = { '紫微': 0, '天機': -1, '太陽': -3, '武曲': -4, '天同': -5, '廉貞': -8 };
            Object.entries(ziOffsets).forEach(([name, offset]) => {
                const pos = (ziweiIdx + offset + 12) % 12;
                if (!starPositions.major_stars[pos]) starPositions.major_stars[pos] = [];
                starPositions.major_stars[pos].push(name);
            });

            const tianOffsets = { '天府': 0, '太陰': 1, '貪狼': 2, '巨門': 3, '天相': 4, '天梁': 5, '七殺': 6, '破軍': 10 };
            Object.entries(tianOffsets).forEach(([name, offset]) => {
                const pos = (tianfuIdx + offset) % 12;
                if (!starPositions.major_stars[pos]) starPositions.major_stars[pos] = [];
                starPositions.major_stars[pos].push(name);
            });

            // --- 追加：主要な副星・凶星 ---
            // 1. 左輔・右弼（月系）
            const zuofuPos = (4 + lunarDate.month - 1) % 12;
            const youbiPos = (10 - lunarDate.month + 1 + 12) % 12;
            starPositions.minor_stars.push({ name: '左輔', pos: zuofuPos });
            starPositions.minor_stars.push({ name: '右弼', pos: youbiPos });

            // 2. 文昌・文曲（時系）
            const wenchangPos = (10 - hourBranch + 12) % 12;
            const wenquPos = (4 + hourBranch) % 12;
            starPositions.minor_stars.push({ name: '文昌', pos: wenchangPos });
            starPositions.minor_stars.push({ name: '文曲', pos: wenquPos });

            // 3. 天魁・天鉞（年干系 - 簡易版）
            const kuiYueTable = { 0: [1, 7], 1: [0, 8], 2: [11, 9], 3: [11, 9], 4: [1, 7], 5: [1, 7], 6: [0, 8], 7: [1, 7] };
            const ky = kuiYueTable[yearStemIdx % 8] || [1, 7];
            starPositions.minor_stars.push({ name: '天魁', pos: ky[0] });
            starPositions.minor_stars.push({ name: '天鉞', pos: ky[1] });

            // 4. 禄存・擎羊・陀羅（年干系）
            const lucunPosTable = [2, 3, 5, 6, 5, 6, 8, 9, 11, 0];
            const lucunPos = lucunPosTable[yearStemIdx];
            starPositions.minor_stars.push({ name: '禄存', pos: lucunPos });
            starPositions.bad_stars.push({ name: '擎羊', pos: (lucunPos + 1) % 12 });
            starPositions.bad_stars.push({ name: '陀羅', pos: (lucunPos - 1 + 12) % 12 });

            // 十二宮のデータを生成
            const palaces = [];
            for (let i = 0; i < 12; i++) {
                const palaceIdx = (mingIdx - i + 12) % 12;
                const branch = ChineseCalendar.BRANCHES[palaceIdx];

                let combinedStars = [];

                // 主星
                const majors = (starPositions.major_stars[palaceIdx] || []).map(name => ({
                    name, brightness: '廟', type: 'major'
                }));
                combinedStars = combinedStars.concat(majors);

                // 副星
                const minors = starPositions.minor_stars.filter(s => s.pos === palaceIdx).map(s => ({
                    name: s.name, brightness: '', type: 'minor'
                }));
                combinedStars = combinedStars.concat(minors);

                // 凶星
                const bads = starPositions.bad_stars.filter(s => s.pos === palaceIdx).map(s => ({
                    name: s.name, brightness: '', type: 'bad'
                }));
                combinedStars = combinedStars.concat(bads);

                palaces.push({
                    name: this.PALACES[i],
                    branch: branch,
                    stars: combinedStars,
                    is_life_palace: i === 0, // 命宮
                    is_body_palace: this.PALACES[i] === this.PALACES[(mingIdx - bodyIdx + 12) % 12] // 身宮判定
                });
            }

            return {
                type: '紫微斗数',
                lunarDate: `旧暦${lunarDate.year}年${lunarDate.month}月${lunarDate.day}日`,
                bureau: bureauName,
                mingPalace: ChineseCalendar.BRANCHES[mingIdx] + '宮',
                bodyPalace: ChineseCalendar.BRANCHES[bodyIdx] + '宮',
                ziweiPosition: ChineseCalendar.BRANCHES[ziweiIdx] + '宮',
                hourBranch: ChineseCalendar.BRANCHES[hourBranch],
                lifeMaster,
                bodyMaster,
                lifeMaster,
                bodyMaster,
                gender: (yinStemBase % 4 === 2 || yinStemBase % 4 === 6) ? (gender === 'male' ? '陽男' : '陽女') : (gender === 'male' ? '陰男' : '陰女'),
                palaces: palaces
            };
        }
    },

    // ===== 宿曜占星術（高性能版）=====
    Sukuyou: {
        MANSIONS: [
            '昴宿', '畢宿', '觜宿', '参宿', '井宿', '鬼宿', '柳宿', '星宿', '張宿',
            '翼宿', '軫宿', '角宿', '亢宿', '氐宿', '房宿', '心宿', '尾宿', '箕宿',
            '斗宿', '女宿', '虚宿', '危宿', '室宿', '壁宿', '奎宿', '婁宿', '胃宿'
        ],

        MANSIONS_EN: [
            'Mao', 'Bi', 'Zi', 'Shen', 'Jing', 'Gui', 'Liu', 'Xing', 'Zhang',
            'Yi', 'Zhen', 'Jue', 'Kang', 'Di', 'Fang', 'Xin', 'Wei', 'Ji',
            'Dou', 'Nv', 'Xu', 'Wei', 'Shi', 'Bi', 'Kui', 'Lou', 'Wei'
        ],

        // 七曜属性
        SEVEN_DAY_ELEMENT: ['日', '月', '火', '水', '木', '金', '土'],

        // 相性タイプ
        RELATIONSHIP_TYPES: {
            'same': { name: '命', level: 5, description: '同じ宿。運命的な結びつき' },
            'ei': { name: '栄', level: 4, description: '大吉。発展的な関係' },
            'shin': { name: '親', level: 4, description: '大吉。親密な関係' },
            'yu': { name: '友', level: 3, description: '中吉。友好的な関係' },
            'an': { name: '安', level: 3, description: '中吉。安定した関係' },
            'kai': { name: '壊', level: 1, description: '凶。破壊的な関係' },
            'kiki': { name: '危', level: 2, description: '小凶。危険を伴う関係' },
            'sei': { name: '成', level: 3, description: '中吉。成就する関係' },
            'gyou': { name: '業', level: 2, description: '業を背負う関係' },
            'tai': { name: '胎', level: 2, description: '始まりの関係' }
        },

        // 相性マトリクス（距離→相性タイプ）
        COMPATIBILITY_MATRIX: [
            'same', 'ei', 'shin', 'shinYuan', 'yu', 'yuYuan', 'an', 'anYuan', 'kai', 'kaiYuan',
            'kiki', 'kikiYuan', 'sei', 'seiYuan', 'gyou', 'tai', 'taiYuan', 'an', 'anYuan',
            'kai', 'kaiYuan', 'yu', 'yuYuan', 'shin', 'shinYuan', 'ei', 'eiYuan'
        ],

        calculate(date) {
            const jd = AstroCalc.dateToJD(date);
            const moonLon = AstroCalc.getMoonLongitude(jd);

            // 月宿計算
            const mansionSpan = 360 / 27;
            const adjustedLon = (moonLon + 360 - 26) % 360;
            const mansionIndex = Math.floor(adjustedLon / mansionSpan);

            // 七曜属性
            const dayElement = this.SEVEN_DAY_ELEMENT[mansionIndex % 7];

            // 日運サイクル（27日周期）
            const startOfYear = new Date(date.getFullYear(), 0, 1);
            const dayOfYear = Math.floor((date - startOfYear) / (1000 * 60 * 60 * 24));
            const dailyCycle = dayOfYear % 27;

            return {
                type: '宿曜占星術',
                natalMansion: this.MANSIONS[mansionIndex],
                mansionEn: this.MANSIONS_EN[mansionIndex],
                mansionNumber: mansionIndex + 1,
                dayElement,
                element: dayElement,
                moonLongitude: moonLon.toFixed(2),
                dailyCycle: dailyCycle + 1,
                dailyMansion: this.MANSIONS[dailyCycle]
            };
        },

        // 相性計算
        calculateCompatibility(mansion1Index, mansion2Index) {
            const distance = (mansion2Index - mansion1Index + 27) % 27;
            const relType = this.COMPATIBILITY_MATRIX[distance];

            // 安壊の方向性判定
            let direction = null;
            if (relType === 'an' || relType === 'anYuan') {
                direction = 'passive';  // 相手によって安定させられる
            } else if (relType === 'kai' || relType === 'kaiYuan') {
                direction = 'active';   // 相手によって壊される
            }

            const baseType = relType.replace('Yuan', '');
            const info = this.RELATIONSHIP_TYPES[baseType] || { name: relType, level: 3, description: '' };

            return {
                relation: info.name,
                level: info.level,
                description: info.description,
                distance,
                direction,
                isNear: distance <= 3 || distance >= 24,
                isMiddle: distance >= 9 && distance <= 18,
                isFar: distance > 3 && distance < 9 || distance > 18 && distance < 24
            };
        },

        // 二人の相性を計算
        calculateTwoPersons(date1, date2) {
            const person1 = this.calculate(date1);
            const person2 = this.calculate(date2);

            const compatibility = this.calculateCompatibility(
                person1.mansionNumber - 1,
                person2.mansionNumber - 1
            );

            return {
                person1,
                person2,
                compatibility
            };
        }
    },

    // ===== 西洋占星術（高性能版）=====
    Western: {
        // アスペクトタイプ
        ASPECTS: {
            conjunction: { name: 'コンジャンクション', angle: 0, orb: 8, type: 'major' },
            opposition: { name: 'オポジション', angle: 180, orb: 8, type: 'major' },
            trine: { name: 'トライン', angle: 120, orb: 8, type: 'major' },
            square: { name: 'スクエア', angle: 90, orb: 7, type: 'major' },
            sextile: { name: 'セクスタイル', angle: 60, orb: 6, type: 'major' }
        },

        calculate(date, latitude, longitude) {
            const jd = AstroCalc.dateToJD(date);

            // 惑星位置
            const planets = [];
            for (let i = 0; i <= 9; i++) {
                const { longitude: lon, retrograde } = AstroCalc.getPlanetLongitude(jd, i);
                const signInfo = AstroCalc.longitudeToSign(lon);
                planets.push({
                    id: i,
                    name: AstroCalc.PLANET_NAMES[i],
                    longitude: lon,
                    sign: signInfo.sign,
                    signIndex: Math.floor(lon / 30),
                    degree: signInfo.degree,
                    retrograde
                });
            }

            // ASC計算
            const asc = AstroCalc.calcAscendant(jd, latitude, longitude);
            const ascSign = AstroCalc.longitudeToSign(asc);

            // MC計算
            const mc = AstroCalc.normalizeDegrees(asc + 270);
            const mcSign = AstroCalc.longitudeToSign(mc);

            // アスペクト計算
            const aspects = this.calculateAspects(planets);

            // 月のサイン（簡易ボイドタイム判定用）
            const moon = planets.find(p => p.name === '月');
            const moonSign = moon ? moon.signIndex : null;

            return {
                type: '西洋占星術',
                planets,
                ascendant: {
                    longitude: asc,
                    sign: ascSign.sign,
                    signIndex: Math.floor(asc / 30),
                    degree: ascSign.degree
                },
                midheaven: {
                    longitude: mc,
                    sign: mcSign.sign,
                    signIndex: Math.floor(mc / 30),
                    degree: mcSign.degree
                },
                aspects,
                moonSign
            };
        },

        // アスペクト計算
        calculateAspects(planets) {
            const aspects = [];
            for (let i = 0; i < planets.length; i++) {
                for (let j = i + 1; j < planets.length; j++) {
                    const p1 = planets[i];
                    const p2 = planets[j];
                    const diff = Math.abs(p1.longitude - p2.longitude);
                    const angle = diff > 180 ? 360 - diff : diff;

                    for (const [key, aspect] of Object.entries(this.ASPECTS)) {
                        const orb = Math.abs(angle - aspect.angle);
                        if (orb <= aspect.orb) {
                            // Applying/Separating判定
                            const isApplying = this.isApplying(p1, p2, aspect.angle);

                            aspects.push({
                                planet1: p1.name,
                                planet2: p2.name,
                                aspect: aspect.name,
                                aspectType: key,
                                orb: orb.toFixed(2),
                                isApplying,
                                state: isApplying ? 'Applying' : 'Separating'
                            });
                            break;
                        }
                    }
                }
            }
            return aspects;
        },

        // Applying判定（速い惑星が遅い惑星に近づいているか）
        isApplying(p1, p2, targetAngle) {
            // 簡易実装：内惑星が外惑星に近づく方向
            const innerPlanets = [0, 1, 2, 3, 4];  // Sun, Moon, Mercury, Venus, Mars
            const isP1Inner = innerPlanets.includes(p1.id);

            if (isP1Inner) {
                // p1が速い惑星
                const diff = p2.longitude - p1.longitude;
                const normalizedDiff = ((diff % 360) + 360) % 360;
                return normalizedDiff < 180;
            } else {
                const diff = p1.longitude - p2.longitude;
                const normalizedDiff = ((diff % 360) + 360) % 360;
                return normalizedDiff < 180;
            }
        }
    },


    // ===== インド占星術 =====
    Vedic: {
        NAKSHATRAS: [
            'アシュヴィニー', 'バラニー', 'クリッティカー', 'ローヒニー',
            'ムリガシラー', 'アールドラー', 'プナルヴァス', 'プシュヤ',
            'アーシュレーシャー', 'マガー', 'P・パールグニー', 'U・パールグニー',
            'ハスタ', 'チトラー', 'スヴァーティー', 'ヴィシャーカー',
            'アヌラーダー', 'ジェーシュター', 'ムーラ', 'P・アシャーダー',
            'U・アシャーダー', 'シュラヴァナ', 'ダニシュター', 'シャタビシャー',
            'P・バードラパダー', 'U・バードラパダー', 'レーヴァティー'
        ],

        NAKSHATRA_LORDS: ['ケートゥ', '金星', '太陽', '月', '火星', 'ラーフ', '木星',
            '土星', '水星', 'ケートゥ', '金星', '太陽', '月', '火星',
            'ラーフ', '木星', '土星', '水星', 'ケートゥ', '金星', '太陽',
            '月', '火星', 'ラーフ', '木星', '土星', '水星'],

        calculate(date, latitude, longitude) {
            const jd = AstroCalc.dateToJD(date);
            const ayanamsa = AstroCalc.getLahiriAyanamsa(jd);

            // 月のサイデリアル位置
            const moonTropical = AstroCalc.getMoonLongitude(jd);
            const moonSidereal = AstroCalc.getSiderealLongitude(moonTropical, jd);

            // ナクシャトラ
            const nakshatraSpan = 360 / 27;
            const nakshatraIndex = Math.floor(moonSidereal / nakshatraSpan);
            const nakshatra = this.NAKSHATRAS[nakshatraIndex];
            const nakshatraLord = this.NAKSHATRA_LORDS[nakshatraIndex];

            return {
                type: 'インド占星術',
                ayanamsa: ayanamsa.toFixed(2),
                moonNakshatra: nakshatra,
                nakshatraLord,
                moonSign: AstroCalc.longitudeToSign(moonSidereal).sign
            };
        }
    },

    // ===== マヤ暦（高性能版）=====
    Mayan: {
        GMT_CORRELATION: 584283,
        DREAMSPELL_EPOCH: new Date(1987, 6, 26),  // 1987年7月26日

        SOLAR_SEALS: [
            '赤い竜', '白い風', '青い夜', '黄色い種', '赤い蛇',
            '白い世界の橋渡し', '青い手', '黄色い星', '赤い月', '白い犬',
            '青い猿', '黄色い人', '赤い空歩く者', '白い魔法使い', '青い鷲',
            '黄色い戦士', '赤い地球', '白い鏡', '青い嵐', '黄色い太陽'
        ],

        SOLAR_SEALS_EN: [
            'Red Dragon', 'White Wind', 'Blue Night', 'Yellow Seed', 'Red Serpent',
            'White World-Bridger', 'Blue Hand', 'Yellow Star', 'Red Moon', 'White Dog',
            'Blue Monkey', 'Yellow Human', 'Red Skywalker', 'White Wizard', 'Blue Eagle',
            'Yellow Warrior', 'Red Earth', 'White Mirror', 'Blue Storm', 'Yellow Sun'
        ],

        GALACTIC_TONES: {
            1: '磁気の', 2: '月の', 3: '電気の', 4: '自己存在の',
            5: '倍音の', 6: '律動の', 7: '共振の', 8: '銀河の',
            9: '太陽の', 10: '惑星の', 11: 'スペクトルの', 12: '水晶の', 13: '宇宙の'
        },

        GALACTIC_TONE_KEYWORDS: {
            1: '目的・統一', 2: '挑戦・極性', 3: '奉仕・活性化', 4: '形・定義',
            5: '輝き・力', 6: '組織・平等', 7: '調整・チャンネル', 8: '調和・完全性',
            9: '意図・脈動', 10: '顕現・完成', 11: '解放・溶解', 12: '協力・普遍化', 13: '存在・超越'
        },

        // GAPキン（黒キン / Galactic Activation Portal）52日間
        GAP_KINS: new Set([
            1, 20, 22, 39, 43, 50, 51, 58, 64, 69,
            72, 77, 85, 88, 93, 96, 106, 107, 108, 109,
            110, 111, 112, 113, 114, 115, 146, 147, 148, 149,
            150, 151, 152, 153, 154, 155, 165, 168, 173, 176,
            184, 189, 192, 197, 203, 210, 211, 218, 222, 239,
            241, 260
        ]),

        // 閏年チェック
        isLeapYear(year) {
            return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
        },

        // フナブ・クの日（閏年2月29日）チェック
        isHunabKuDay(date) {
            return date.getMonth() === 1 && date.getDate() === 29;
        },

        // 期間内の閏年2月29日をカウント
        countLeapDays(start, end) {
            let count = 0;
            for (let year = start.getFullYear(); year <= end.getFullYear(); year++) {
                if (this.isLeapYear(year)) {
                    const leapDay = new Date(year, 1, 29);
                    if (start <= leapDay && leapDay < end) {
                        count++;
                    }
                }
            }
            return count;
        },

        // 古代マヤ式KIN計算（JDN + GMT相関定数）
        calcKinClassic(date) {
            const jd = AstroCalc.dateToJD(date);
            const jdInt = Math.floor(jd + 0.5);
            return ((jdInt - this.GMT_CORRELATION) % 260 + 260) % 260 + 1;
        },

        // ドリームスペル式KIN計算（閏日スキップ）
        calcKinDreamspell(date) {
            // フナブ・クの日は計算しない
            if (this.isHunabKuDay(date)) {
                return null;
            }

            const daysDiff = Math.floor((date - this.DREAMSPELL_EPOCH) / (1000 * 60 * 60 * 24));
            const leapDays = this.countLeapDays(this.DREAMSPELL_EPOCH, date);
            const adjustedDays = daysDiff - leapDays;

            let kin = (adjustedDays % 260) + 1;
            if (kin <= 0) kin += 260;
            return kin;
        },

        // 高性能計算（モード切替対応）
        calculate(date, mode = 'dreamspell') {
            // フナブ・クの日（ドリームスペルモードのみ）
            if (mode === 'dreamspell' && this.isHunabKuDay(date)) {
                return {
                    type: 'マヤ暦',
                    mode: 'ドリームスペル',
                    isHunabKu: true,
                    kin: null,
                    solarSeal: null,
                    solarSealEn: null,
                    galacticTone: null,
                    galacticToneName: 'フナブ・ク',
                    galacticToneKeyword: '創造主・一なるもの',
                    wavespell: 'フナブ・ク（時間を超えた日）',
                    guide: null,
                    isGapKin: false,
                    note: '2月29日はフナブ・クの日です。KIN番号は付与されず、時間を超えた特別な日として扱われます。'
                };
            }

            // KIN計算
            const kin = mode === 'classic' ? this.calcKinClassic(date) : this.calcKinDreamspell(date);

            const sealIndex = (kin - 1) % 20;
            const tone = ((kin - 1) % 13) + 1;

            // ウェイブスペル
            const wavespellKin = Math.floor((kin - 1) / 13) * 13 + 1;
            const wavespellIndex = (wavespellKin - 1) % 20;

            // ガイドキン
            const guideOffsets = { 1: 0, 6: 0, 11: 0, 2: 12, 7: 12, 12: 12, 3: 4, 8: 4, 13: 4, 4: 16, 9: 16, 5: 8, 10: 8 };
            const guideOffset = guideOffsets[tone] || 0;
            const guideIndex = (sealIndex + guideOffset) % 20;

            // GAPキン判定
            const isGapKin = this.GAP_KINS.has(kin);

            return {
                type: 'マヤ暦',
                mode: mode === 'classic' ? '古代マヤ' : 'ドリームスペル',
                isHunabKu: false,
                kin,
                solarSeal: this.SOLAR_SEALS[sealIndex],
                solarSealEn: this.SOLAR_SEALS_EN[sealIndex],
                galacticTone: tone,
                galacticToneName: this.GALACTIC_TONES[tone],
                galacticToneKeyword: this.GALACTIC_TONE_KEYWORDS[tone],
                wavespell: this.SOLAR_SEALS[wavespellIndex],
                guide: this.SOLAR_SEALS[guideIndex],
                isGapKin,
                note: mode === 'classic'
                    ? `古代マヤ方式で計算。GMT相関定数(${this.GMT_CORRELATION})使用。`
                    : 'ドリームスペル方式で計算。閏年調整あり。'
            };
        },

        // 古代マヤとドリームスペルを比較
        compareModes(date) {
            const classic = this.calculate(date, 'classic');
            const dreamspell = this.calculate(date, 'dreamspell');

            let kinDiff = null;
            if (classic.kin && dreamspell.kin) {
                kinDiff = classic.kin - dreamspell.kin;
                if (kinDiff < -130) kinDiff += 260;
                else if (kinDiff > 130) kinDiff -= 260;
            }

            return {
                date: date.toISOString().split('T')[0],
                classic,
                dreamspell,
                kinDifference: kinDiff,
                note: '古代マヤとドリームスペルでは閏年の扱いが異なるため、KIN番号にズレが生じます。'
            };
        },

        // GAPキン判定
        isGapKin(kin) {
            return this.GAP_KINS.has(kin);
        },

        // 全GAPキンを取得
        getAllGapKins() {
            return Array.from(this.GAP_KINS).sort((a, b) => a - b);
        }
    },


    // ===== 数秘術（高性能版）=====
    Numerology: {
        MEANINGS: {
            1: 'リーダーシップ・独立・開拓',
            2: '協調・調和・パートナーシップ',
            3: '創造性・表現・コミュニケーション',
            4: '安定・実用性・勤勉',
            5: '自由・変化・冒険',
            6: '責任・愛・家庭',
            7: '分析・内省・精神性',
            8: '権力・成功・カルマ',
            9: '人道主義・完成・知恵',
            11: '直感・霊感・啓示',
            22: 'マスタービルダー・大きな夢',
            33: 'マスターティーチャー・癒し'
        },

        // ピタゴラス式テーブル
        PYTHAGOREAN_TABLE: {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
            'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
            'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
        },

        // カルデア式テーブル（9は神聖数として除外）
        CHALDEAN_TABLE: {
            'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
            'B': 2, 'K': 2, 'R': 2,
            'C': 3, 'G': 3, 'L': 3, 'S': 3,
            'D': 4, 'M': 4, 'T': 4,
            'E': 5, 'H': 5, 'N': 5, 'X': 5,
            'U': 6, 'V': 6, 'W': 6,
            'O': 7, 'Z': 7,
            'F': 8, 'P': 8
        },

        // 母音リスト
        VOWELS: new Set(['A', 'E', 'I', 'O', 'U']),

        // 天体対応（数字→支配星）
        PLANET_RULERS: {
            1: '太陽', 2: '月', 3: '木星', 4: '天王星', 5: '水星',
            6: '金星', 7: '海王星', 8: '土星', 9: '火星'
        },

        reduceNumber(num, preserveMaster = true) {
            const masterNumbers = [11, 22, 33];
            while (num > 9) {
                if (preserveMaster && masterNumbers.includes(num)) return num;
                num = num.toString().split('').reduce((a, b) => a + parseInt(b), 0);
            }
            return num;
        },

        // Y母音/子音判定（高精度版）
        isYVowel(word, index) {
            const W = word.toUpperCase();
            if (W[index] !== 'Y') return false;

            // 先頭のYは子音
            if (index === 0) return false;

            const prev = W[index - 1] || '';
            const next = W[index + 1] || '';

            // 母音に挟まれていれば子音
            if (this.VOWELS.has(prev) && this.VOWELS.has(next)) return false;

            // 子音の後で、末尾または次も子音なら母音
            if (!this.VOWELS.has(prev)) {
                if (next === '' || !this.VOWELS.has(next)) return true;
            }

            return false;
        },

        // 名前から数値を計算
        nameToNumbers(name, system = 'pythagorean') {
            const table = system === 'chaldean' ? this.CHALDEAN_TABLE : this.PYTHAGOREAN_TABLE;
            const upper = name.toUpperCase().replace(/[^A-Z]/g, '');

            let total = 0;
            let vowelSum = 0;
            let consonantSum = 0;

            for (let i = 0; i < upper.length; i++) {
                const char = upper[i];
                const value = table[char] || 0;
                total += value;

                // Y判定
                const isVowel = this.VOWELS.has(char) || this.isYVowel(upper, i);

                if (isVowel) {
                    vowelSum += value;
                } else {
                    consonantSum += value;
                }
            }

            return {
                total: this.reduceNumber(total),
                vowelSum: this.reduceNumber(vowelSum),
                consonantSum: this.reduceNumber(consonantSum)
            };
        },

        // 生年月日計算
        calculate(date, name = null, system = 'pythagorean') {
            const year = date.getFullYear();
            const month = date.getMonth() + 1;
            const day = date.getDate();

            // ライフパス数
            const yearReduced = this.reduceNumber(year);
            const monthReduced = this.reduceNumber(month);
            const dayReduced = this.reduceNumber(day);
            const lifePath = this.reduceNumber(yearReduced + monthReduced + dayReduced);

            // バースデー数
            const birthdayNumber = this.reduceNumber(day);

            // パーソナルイヤー（対象年の運勢）
            const currentYear = new Date().getFullYear();
            const personalYear = this.reduceNumber(monthReduced + dayReduced + this.reduceNumber(currentYear));

            // 天体対応
            const lifePathPlanet = this.PLANET_RULERS[lifePath > 9 ? this.reduceNumber(lifePath, false) : lifePath];

            const result = {
                type: '数秘術',
                system: system === 'chaldean' ? 'カルデア式' : 'ピタゴラス式',
                lifePath,
                lifePathMeaning: this.MEANINGS[lifePath] || '',
                lifePathPlanet,
                birthdayNumber,
                birthdayMeaning: this.MEANINGS[birthdayNumber] || '',
                personalYear,
                personalYearMeaning: this.MEANINGS[personalYear] || ''
            };

            // 名前が与えられた場合
            if (name) {
                const nameNumbers = this.nameToNumbers(name, system);
                result.expressionNumber = nameNumbers.total;  // 表現数（人生の目的）
                result.soulNumber = nameNumbers.vowelSum;     // ソウル数（内なる願望）
                result.personalityNumber = nameNumbers.consonantSum; // パーソナリティ数（外見的印象）
                result.expressionMeaning = this.MEANINGS[nameNumbers.total] || '';
                result.soulMeaning = this.MEANINGS[nameNumbers.vowelSum] || '';
                result.personalityMeaning = this.MEANINGS[nameNumbers.consonantSum] || '';
            }

            return result;
        },

        // Y判定テスト
        testYVowel(word) {
            const upper = word.toUpperCase();
            const results = [];
            for (let i = 0; i < upper.length; i++) {
                if (upper[i] === 'Y') {
                    results.push({
                        position: i,
                        isVowel: this.isYVowel(upper, i)
                    });
                }
            }
            return { word, yPositions: results };
        }
    },


    // ===== 姓名判断 =====
    Seimei: {
        // フォールバック用の基本画数データ
        FALLBACK_STROKES: {
            '安': 6, '瀬': 19, '諒': 15, '田': 5, '中': 4, '村': 7, '山': 3, '川': 3,
            '佐': 7, '藤': 18, '井': 4, '高': 10, '橋': 16, '鈴': 13, '木': 4,
            '一': 1, '二': 2, '三': 3, '四': 5, '五': 4, '六': 4, '七': 2, '八': 2,
            '太': 4, '郎': 9, '子': 3, '美': 9, '男': 7, '女': 3, '介': 4,
            '健': 11, '明': 8, '光': 6, '真': 10, '直': 8, '俊': 9, '浩': 10,
            '和': 8, '幸': 8, '彦': 9, '恵': 10, '也': 3, '雄': 12, '大': 3, '小': 3
        },

        getStroke(char) {
            // KanjiStrokesモジュールから取得を試みる
            if (typeof KanjiStrokes !== 'undefined') {
                const stroke = KanjiStrokes.getStroke(char);
                if (stroke !== null) return stroke;
            }
            // フォールバック
            return this.FALLBACK_STROKES[char] || 10;
        },

        calculate(familyName, givenName) {
            const familyStrokes = [...familyName].map(c => this.getStroke(c));
            const givenStrokes = [...givenName].map(c => this.getStroke(c));

            // 霊数処理
            const familyCalc = familyName.length === 1 ? [1, ...familyStrokes] : familyStrokes;
            const givenCalc = givenName.length === 1 ? [...givenStrokes, 1] : givenStrokes;

            const tenkaku = familyCalc.reduce((a, b) => a + b, 0);
            const chikaku = givenCalc.reduce((a, b) => a + b, 0);
            const jinkaku = familyStrokes[familyStrokes.length - 1] + givenStrokes[0];
            const soukaku = familyStrokes.reduce((a, b) => a + b, 0) + givenStrokes.reduce((a, b) => a + b, 0);
            const gaikaku = Math.max(1, soukaku - jinkaku);

            return {
                type: '姓名判断',
                familyName,
                givenName,
                strokes: {
                    family: familyStrokes,
                    given: givenStrokes
                },
                tenkaku,
                jinkaku,
                chikaku,
                gaikaku,
                soukaku
            };
        }
    },




};

// グローバルに公開
window.DivinationModules = DivinationModules;

