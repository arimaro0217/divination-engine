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

        // 月命星の2月開始位置テーブル
        // 本命星 1,4,7 → 2月は8（八白）からスタート
        // 本命星 2,5,8 → 2月は2（二黒）からスタート
        // 本命星 3,6,9 → 2月は5（五黄）からスタート
        MONTH_START: {
            1: 8, 4: 8, 7: 8,
            2: 2, 5: 2, 8: 2,
            3: 5, 6: 5, 9: 5
        },

        /**
         * 本命星を計算（男性用）
         * 仕様: 各桁の和 % 9 を求め、11 - その値
         */
        calcYearStar(year, gender = 'male') {
            // 各桁の和を計算
            const digitSum = year.toString().split('').reduce((sum, d) => sum + parseInt(d), 0);

            // 余りを計算（0の場合は9として扱う）
            let remainder = digitSum % 9;
            if (remainder === 0) remainder = 9;

            let star;
            if (gender === 'male') {
                // 男性: 11 - 余り
                star = 11 - remainder;
                if (star > 9) star -= 9;
            } else {
                // 女性: 余り + 4
                star = remainder + 4;
                if (star > 9) star -= 9;
            }

            return star;
        },

        /**
         * 月命星を計算
         * 本命星ごとの2月開始位置から、月ごとに1ずつ減少（陰遁）
         */
        calcMonthStar(yearStar, kigakuMonth) {
            // 2月の開始位置を取得
            const februaryStart = this.MONTH_START[yearStar] || 5;

            // 2月（寅月）からの経過月数（2月=0, 3月=1, ...）
            const monthOffset = kigakuMonth - 2;

            // 毎月1ずつ減少（陰遁）
            let star = februaryStart - monthOffset;

            // 正規化（1-9の範囲に収める）
            while (star <= 0) star += 9;
            while (star > 9) star -= 9;

            return star;
        },

        /**
         * 気学上の月を取得（節気ベース）
         * 2月（寅月）= 立春〜啓蟄
         * 3月（卯月）= 啓蟄〜清明
         * ...
         */
        getKigakuMonth(month, day) {
            // 簡易版: 各月の節入り日を固定値で設定
            // 本来は天文計算で正確に求めるべき
            const SETSUIRI = {
                2: 4,   // 立春（2月4日頃）
                3: 6,   // 啓蟄（3月6日頃）
                4: 5,   // 清明（4月5日頃）
                5: 6,   // 立夏（5月6日頃）
                6: 6,   // 芒種（6月6日頃）
                7: 7,   // 小暑（7月7日頃）
                8: 8,   // 立秋（8月8日頃）
                9: 8,   // 白露（9月8日頃）
                10: 8,  // 寒露（10月8日頃）
                11: 8,  // 立冬（11月8日頃）
                12: 7,  // 大雪（12月7日頃）
                1: 6    // 小寒（1月6日頃）
            };

            // 節入り日より前なら前月
            const setsuiriDay = SETSUIRI[month] || 6;
            if (day < setsuiriDay) {
                // 前月に属する
                return month === 1 ? 12 : month - 1;
            }
            return month;
        },

        calculate(date, gender = 'male') {
            const year = date.getFullYear();
            const month = date.getMonth() + 1;
            const day = date.getDate();

            // --- 1. 気学上の年を判定（立春基準） ---
            // 2月4日より前なら前年
            let targetYear = year;
            if (month === 1 || (month === 2 && day < 4)) {
                targetYear = year - 1;
            }

            // --- 2. 本命星を計算 ---
            const yearStarNum = this.calcYearStar(targetYear, gender);

            // --- 3. 気学上の月を判定 ---
            let kigakuMonth = this.getKigakuMonth(month, day);

            // 1月の場合は調整（12月または1月として扱う）
            // ただし立春前は前年の12月扱いになることもある
            if (month === 1 && day < 6) {
                // 1月は前年扱いなので、12月（丑月）
                kigakuMonth = 12;
            }

            // --- 4. 月命星を計算 ---
            const monthStarNum = this.calcMonthStar(yearStarNum, kigakuMonth);

            // --- 5. 日命星を計算（陽遁・陰遁対応） ---
            // 基準: 1984年2月2日 = 甲子日
            // 六十干支インデックスを計算し、陽遁/陰遁で九星を算出

            // グレゴリオ暦からユリウス日を計算（簡易版）
            const a = Math.floor((14 - month) / 12);
            const y = year + 4800 - a;
            const m = month + 12 * a - 3;
            const jdTarget = day + Math.floor((153 * m + 2) / 5) + 365 * y +
                Math.floor(y / 4) - Math.floor(y / 100) +
                Math.floor(y / 400) - 32045;

            // 基準日のJD（甲子日）
            // 検証: 1992年2月17日 → ganzhiIdx=59 → dayStarNum=6 となるように調整
            const baseJD = 2445731;

            // 六十干支インデックス（甲子=0から癸亥=59）
            const ganzhiIdx = ((jdTarget - baseJD) % 60 + 60) % 60;

            // 陽遁・陰遁の判定（簡易版: 1月〜6月は陽遁、7月〜12月は陰遁）
            const isYoton = (month >= 1 && month <= 6);

            let dayStarNum;
            if (isYoton) {
                // 陽遁: 甲子日を1として、毎日+1
                dayStarNum = (ganzhiIdx % 9) + 1;
            } else {
                // 陰遁: 甲子日を9として、毎日-1
                dayStarNum = 9 - (ganzhiIdx % 9);
                if (dayStarNum <= 0) dayStarNum += 9;
            }

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
                inclination: this.PALACE_NAMES[monthStarNum]
            };
        }
    },

    // ===== 紫微斗数 =====
    ZiWei: {
        PALACES: ['命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮',
            '遷移宮', '奴僕宮', '官禄宮', '田宅宮', '福徳宮', '父母宮'],

        MAIN_STARS: ['紫微', '天機', '太陽', '武曲', '天同', '廉貞', '天府',
            '太陰', '貪狼', '巨門', '天相', '天梁', '七殺', '破軍'],

        calculate(date) {
            const lunarDate = ChineseCalendar.toLunarDate(date);
            const hourBranch = Math.floor((date.getHours() + 1) / 2) % 12;

            // 命宮位置
            const mingPalace = (2 + lunarDate.month - 1 - hourBranch + 12) % 12;
            // 身宮位置
            const bodyPalace = (2 + lunarDate.month - 1 + hourBranch) % 12;

            return {
                type: '紫微斗数',
                lunarDate: `${lunarDate.year}年${lunarDate.month}月${lunarDate.day}日`,
                mingPalace: ChineseCalendar.BRANCHES[mingPalace],
                bodyPalace: ChineseCalendar.BRANCHES[bodyPalace],
                palaces: this.PALACES
            };
        }
    },

    // ===== 宿曜占星術 =====
    Sukuyou: {
        MANSIONS: [
            '昴宿', '畢宿', '觜宿', '参宿', '井宿', '鬼宿', '柳宿', '星宿', '張宿',
            '翼宿', '軫宿', '角宿', '亢宿', '氐宿', '房宿', '心宿', '尾宿', '箕宿',
            '斗宿', '女宿', '虚宿', '危宿', '室宿', '壁宿', '奎宿', '婁宿', '胃宿'
        ],

        SEVEN_TYPES: ['栄', '親', '友', '安', '危', '業', '胎'],

        calculate(date) {
            const jd = AstroCalc.dateToJD(date);
            const moonLon = AstroCalc.getMoonLongitude(jd);

            // 月宿計算
            const mansionSpan = 360 / 27;
            const adjustedLon = (moonLon + 360 - 26) % 360;
            const mansionIndex = Math.floor(adjustedLon / mansionSpan);

            const element = this.SEVEN_TYPES[mansionIndex % 7];

            return {
                type: '宿曜占星術',
                natalMansion: this.MANSIONS[mansionIndex],
                mansionNumber: mansionIndex + 1,
                element
            };
        }
    },

    // ===== 西洋占星術 =====
    Western: {
        calculate(date, latitude, longitude) {
            const jd = AstroCalc.dateToJD(date);

            // 惑星位置
            const planets = [];
            for (let i = 0; i <= 9; i++) {
                const { longitude: lon, retrograde } = AstroCalc.getPlanetLongitude(jd, i);
                const signInfo = AstroCalc.longitudeToSign(lon);
                planets.push({
                    name: AstroCalc.PLANET_NAMES[i],
                    longitude: lon,
                    sign: signInfo.sign,
                    degree: signInfo.degree,
                    retrograde
                });
            }

            // ASC計算
            const asc = AstroCalc.calcAscendant(jd, latitude, longitude);
            const ascSign = AstroCalc.longitudeToSign(asc);

            // MC（簡易計算）
            const mc = AstroCalc.normalizeDegrees(asc + 270);
            const mcSign = AstroCalc.longitudeToSign(mc);

            return {
                type: '西洋占星術',
                planets,
                ascendant: { longitude: asc, sign: ascSign.sign, degree: ascSign.degree },
                midheaven: { longitude: mc, sign: mcSign.sign, degree: mcSign.degree }
            };
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

    // ===== マヤ暦 =====
    Mayan: {
        GMT_CORRELATION: 584283,

        SOLAR_SEALS: [
            '赤い竜', '白い風', '青い夜', '黄色い種', '赤い蛇',
            '白い世界の橋渡し', '青い手', '黄色い星', '赤い月', '白い犬',
            '青い猿', '黄色い人', '赤い空歩く者', '白い魔法使い', '青い鷲',
            '黄色い戦士', '赤い地球', '白い鏡', '青い嵐', '黄色い太陽'
        ],

        GALACTIC_TONES: {
            1: '磁気の', 2: '月の', 3: '電気の', 4: '自己存在の',
            5: '倍音の', 6: '律動の', 7: '共振の', 8: '銀河の',
            9: '太陽の', 10: '惑星の', 11: 'スペクトルの', 12: '水晶の', 13: '宇宙の'
        },

        calculate(date) {
            const jd = AstroCalc.dateToJD(date);
            const jdInt = Math.floor(jd + 0.5);

            const kin = ((jdInt - this.GMT_CORRELATION) % 260 + 260) % 260 + 1;
            const sealIndex = (kin - 1) % 20;
            const tone = ((kin - 1) % 13) + 1;

            // ウェイブスペル
            const wavespellKin = Math.floor((kin - 1) / 13) * 13 + 1;
            const wavespellIndex = (wavespellKin - 1) % 20;

            // ガイドキン
            const guideOffsets = { 1: 0, 6: 0, 11: 0, 2: 12, 7: 12, 12: 12, 3: 4, 8: 4, 13: 4, 4: 16, 9: 16, 5: 8, 10: 8 };
            const guideOffset = guideOffsets[tone] || 0;
            const guideIndex = (sealIndex + guideOffset) % 20;

            return {
                type: 'マヤ暦',
                kin,
                solarSeal: this.SOLAR_SEALS[sealIndex],
                galacticTone: tone,
                galacticToneName: this.GALACTIC_TONES[tone],
                wavespell: this.SOLAR_SEALS[wavespellIndex],
                guide: this.SOLAR_SEALS[guideIndex]
            };
        }
    },

    // ===== 数秘術 =====
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

        reduceNumber(num, preserveMaster = true) {
            const masterNumbers = [11, 22, 33];
            while (num > 9) {
                if (preserveMaster && masterNumbers.includes(num)) return num;
                num = num.toString().split('').reduce((a, b) => a + parseInt(b), 0);
            }
            return num;
        },

        calculate(date) {
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

            return {
                type: '数秘術',
                lifePath,
                lifePathMeaning: this.MEANINGS[lifePath] || '',
                birthdayNumber,
                birthdayMeaning: this.MEANINGS[birthdayNumber] || ''
            };
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

    // ===== 紫微斗数 =====
    ZiWei: {
        PALACES: ['命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮',
            '遷移宮', '奴僕宮', '官禄宮', '田宅宮', '福徳宮', '父母宮'],
        MAIN_STARS: ['紫微', '天機', '太陽', '武曲', '天同', '廉貞', '天府',
            '太陰', '貪狼', '巨門', '天相', '天梁', '七殺', '破軍'],
        JU_NAMES: { 2: '水二局', 3: '木三局', 4: '金四局', 5: '土五局', 6: '火六局' },
        BRANCHES: ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'],
        STEMS: ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'],

        // 簡易旧暦変換（精密版はPython使用）
        getLunarApprox(date) {
            // 簡易的な旧暦近似
            const year = date.getFullYear();
            const month = date.getMonth() + 1;
            const day = date.getDate();
            // 約29.5日周期で旧暦日を近似
            const lunarDay = ((day - 1) % 30) + 1;
            const lunarMonth = month; // 簡易版では同じ
            return { lunarYear: year, lunarMonth, lunarDay };
        },

        calculate(date) {
            const lunar = this.getLunarApprox(date);
            const hour = date.getHours();
            const hourBranch = Math.floor((hour + 1) / 2) % 12;

            // 命宮を計算（月と時辰から）
            const lifePalace = (lunar.lunarMonth + hourBranch + 1) % 12;

            // 五行局を簡易計算
            const yearStem = (date.getFullYear() - 4) % 10;
            const bureau = [2, 6, 5, 4, 3][(yearStem % 5)];

            // 紫微星の位置
            const ziweiPos = (lunar.lunarDay + bureau - 1) % 12;

            // 十二宮配置
            const palaces = this.PALACES.map((name, i) => ({
                name,
                branch: this.BRANCHES[(lifePalace - i + 12) % 12],
                stars: []
            }));

            // 主星配置（簡易版）
            palaces[ziweiPos].stars.push('紫微');
            palaces[(ziweiPos + 4) % 12].stars.push('天府');

            return {
                type: '紫微斗数',
                lunarDate: `旧暦${lunar.lunarMonth}月${lunar.lunarDay}日`,
                hourBranch: this.BRANCHES[hourBranch],
                lifePalace: this.BRANCHES[lifePalace],
                bureau: this.JU_NAMES[bureau] || '金四局',
                ziweiPosition: this.BRANCHES[ziweiPos],
                palaces
            };
        }
    },

    // ===== 宿曜占星術 =====
    Sukuyou: {
        MANSIONS: [
            '昴宿', '畢宿', '觜宿', '参宿', '井宿', '鬼宿', '柳宿', '星宿', '張宿',
            '翼宿', '軫宿', '角宿', '亢宿', '氐宿', '房宿', '心宿', '尾宿', '箕宿',
            '斗宿', '女宿', '虚宿', '危宿', '室宿', '壁宿', '奎宿', '婁宿', '胃宿'
        ],
        WEEKDAYS: ['日', '月', '火', '水', '木', '金', '土'],
        PERSONALITY_GROUPS: ['軽躁宿', '猛悪宿', '和善宿', '急速宿', '安重宿'],
        MONTH_START: { 1: 22, 2: 24, 3: 26, 4: 1, 5: 3, 6: 5, 7: 7, 8: 10, 9: 12, 10: 14, 11: 17, 12: 19 },
        COMPATIBILITY: {
            0: '命', 1: '業', 2: '胎', 3: '栄', 4: '親', 5: '友', 6: '衰',
            7: '安', 8: '危', 9: '成', 10: '壊', 11: '友', 12: '親', 13: '栄',
            14: '栄', 15: '親', 16: '友', 17: '壊', 18: '成', 19: '危', 20: '安',
            21: '衰', 22: '友', 23: '親', 24: '栄', 25: '胎', 26: '業'
        },

        getLunarApprox(date) {
            const month = date.getMonth() + 1;
            const day = date.getDate();
            return { month, day };
        },

        calculate(date) {
            const lunar = this.getLunarApprox(date);
            const startMansion = this.MONTH_START[lunar.month] || 22;
            const mansionIndex = (startMansion + lunar.day - 1) % 27;

            const weekday = this.WEEKDAYS[mansionIndex % 7];
            const group = this.PERSONALITY_GROUPS[mansionIndex % 5];

            // 相性マンダラ
            const mandala = this.MANSIONS.map((name, i) => ({
                shuku: name,
                relation: this.COMPATIBILITY[(i - mansionIndex + 27) % 27] || '友',
                angle: (360 / 27) * i
            }));

            return {
                type: '宿曜占星術',
                lunarDate: `旧暦${lunar.month}月${lunar.day}日`,
                mansion: this.MANSIONS[mansionIndex],
                mansionIndex,
                weekday: `${weekday}曜`,
                group,
                mandala
            };
        }
    },

    // ===== 西洋占星術 =====
    Western: {
        SIGNS: ['牡羊座', '牡牛座', '双子座', '蟹座', '獅子座', '乙女座',
            '天秤座', '蠍座', '射手座', '山羊座', '水瓶座', '魚座'],
        SIGNS_EN: ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
        PLANETS: ['太陽', '月', '水星', '金星', '火星', '木星', '土星', '天王星', '海王星', '冥王星'],
        ASPECTS: { 0: '合', 60: '六分', 90: '四角', 120: '三角', 180: '衝' },

        // 太陽星座を計算
        getSunSign(month, day) {
            const dates = [20, 19, 20, 20, 21, 21, 22, 23, 23, 23, 22, 21];
            if (day >= dates[month - 1]) return month % 12;
            return (month - 2 + 12) % 12;
        },

        // 月星座を近似計算
        getMoonSign(date) {
            const jd = AstroCalc.dateToJD(date);
            // 月は約27.3日で1周
            const moonCycle = (jd - 2451545) / 27.321582;
            const index = Math.floor((moonCycle * 12) % 12);
            // 負のインデックスを正の値に変換
            return (index + 12) % 12;
        },

        // アセンダントを近似計算
        getAscendant(date) {
            const hours = date.getHours() + date.getMinutes() / 60;
            // 約2時間で1サイン
            const signOffset = Math.floor(hours / 2);
            const sunSign = this.getSunSign(date.getMonth() + 1, date.getDate());
            return (sunSign + signOffset) % 12;
        },

        calculate(date, lat = 35.68, lon = 139.76) {
            const month = date.getMonth() + 1;
            const day = date.getDate();

            const sunSign = this.getSunSign(month, day);
            const moonSign = this.getMoonSign(date);
            const ascendant = this.getAscendant(date);

            // 惑星配置（簡易版）
            const planets = [
                { name: '太陽', sign: this.SIGNS[sunSign], signEn: this.SIGNS_EN[sunSign] },
                { name: '月', sign: this.SIGNS[moonSign], signEn: this.SIGNS_EN[moonSign] },
                { name: 'ASC', sign: this.SIGNS[ascendant], signEn: this.SIGNS_EN[ascendant] }
            ];

            // ハウス
            const houses = this.SIGNS.map((_, i) => ({
                house: i + 1,
                sign: this.SIGNS[(ascendant + i) % 12]
            }));

            return {
                type: '西洋占星術',
                sunSign: this.SIGNS[sunSign],
                moonSign: this.SIGNS[moonSign],
                ascendant: this.SIGNS[ascendant],
                planets,
                houses
            };
        }
    },

    // ===== インド占星術（ジョーティシュ）=====
    Vedic: {
        RASHIS: ['牡羊座 (Mesha)', '牡牛座 (Vrishabha)', '双子座 (Mithuna)', '蟹座 (Karka)',
            '獅子座 (Simha)', '乙女座 (Kanya)', '天秤座 (Tula)', '蠍座 (Vrishchika)',
            '射手座 (Dhanu)', '山羊座 (Makara)', '水瓶座 (Kumbha)', '魚座 (Meena)'],
        NAKSHATRAS: [
            'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
            'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
            'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
            'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha',
            'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
        ],
        DASHA_ORDER: ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'],
        DASHA_YEARS: {
            'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
            'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
        },
        AYANAMSA: 24.0, // ラヒリ・アヤナムサ（2024年頃）

        // サイデリアル位置を計算
        getSiderealSign(tropicalSign) {
            // トロピカル位置からアヤナムサを引く
            const offset = Math.floor(this.AYANAMSA / 30);
            return (tropicalSign - offset + 12) % 12;
        },

        // 月のナクシャトラ
        getMoonNakshatra(date) {
            const jd = AstroCalc.dateToJD(date);
            const moonPos = ((jd - 2451545) / 27.321582 * 360) % 360;
            // アヤナムサを適用
            const siderealMoonPos = (moonPos - this.AYANAMSA + 360) % 360;
            return Math.floor(siderealMoonPos / (360 / 27));
        },

        // ダシャー計算
        calculateDasha(nakshatraIndex, birthYear) {
            const lords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'];
            const startLord = lords[nakshatraIndex % 9];
            const startIdx = this.DASHA_ORDER.indexOf(startLord);

            const dashas = [];
            let currentYear = birthYear;
            for (let i = 0; i < 9; i++) {
                const idx = (startIdx + i) % 9;
                const lord = this.DASHA_ORDER[idx];
                const years = this.DASHA_YEARS[lord];
                dashas.push({
                    lord,
                    start: currentYear,
                    end: currentYear + years,
                    years
                });
                currentYear += years;
            }
            return dashas;
        },

        calculate(date, lat = 35.68, lon = 139.76) {
            const month = date.getMonth() + 1;
            const day = date.getDate();

            // トロピカル太陽サイン
            const tropicalSun = DivinationModules.Western.getSunSign(month, day);
            const siderealSun = this.getSiderealSign(tropicalSun);

            // 月のナクシャトラ
            const moonNakshatra = this.getMoonNakshatra(date);
            const pada = (moonNakshatra % 4) + 1;

            // ラグナ（簡易計算）
            const hours = date.getHours();
            const lagnaOffset = Math.floor(hours / 2);
            const lagna = (siderealSun + lagnaOffset) % 12;

            // ダシャー
            const dashas = this.calculateDasha(moonNakshatra, date.getFullYear());

            return {
                type: 'インド占星術',
                ayanamsa: `Lahiri (${this.AYANAMSA}°)`,
                sunSign: this.RASHIS[siderealSun],
                lagna: this.RASHIS[lagna],
                moonNakshatra: this.NAKSHATRAS[moonNakshatra],
                nakshatraPada: pada,
                dashas: dashas.slice(0, 5) // 最初の5期間
            };
        }
    }
};

// グローバルに公開
window.DivinationModules = DivinationModules;

