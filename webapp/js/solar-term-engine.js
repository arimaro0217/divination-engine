/**
 * 精密節入り計算・干支算出エンジン
 * 四柱推命・算命学・九星気学の基礎計算を提供
 */

const SolarTermEngine = {
    // ===== 二十四節気定義 =====
    // 太陽黄経と月番号・節気種別（節：月の始まり、中：月の中間）
    SOLAR_TERMS_FULL: [
        { name: '小寒', longitude: 285, monthNum: 12, isJie: true },
        { name: '大寒', longitude: 300, monthNum: 12, isJie: false },
        { name: '立春', longitude: 315, monthNum: 1, isJie: true, isLichun: true },
        { name: '雨水', longitude: 330, monthNum: 1, isJie: false },
        { name: '啓蟄', longitude: 345, monthNum: 2, isJie: true },
        { name: '春分', longitude: 0, monthNum: 2, isJie: false },
        { name: '清明', longitude: 15, monthNum: 3, isJie: true },
        { name: '穀雨', longitude: 30, monthNum: 3, isJie: false },
        { name: '立夏', longitude: 45, monthNum: 4, isJie: true },
        { name: '小満', longitude: 60, monthNum: 4, isJie: false },
        { name: '芒種', longitude: 75, monthNum: 5, isJie: true },
        { name: '夏至', longitude: 90, monthNum: 5, isJie: false },
        { name: '小暑', longitude: 105, monthNum: 6, isJie: true },
        { name: '大暑', longitude: 120, monthNum: 6, isJie: false },
        { name: '立秋', longitude: 135, monthNum: 7, isJie: true },
        { name: '処暑', longitude: 150, monthNum: 7, isJie: false },
        { name: '白露', longitude: 165, monthNum: 8, isJie: true },
        { name: '秋分', longitude: 180, monthNum: 8, isJie: false },
        { name: '寒露', longitude: 195, monthNum: 9, isJie: true },
        { name: '霜降', longitude: 210, monthNum: 9, isJie: false },
        { name: '立冬', longitude: 225, monthNum: 10, isJie: true },
        { name: '小雪', longitude: 240, monthNum: 10, isJie: false },
        { name: '大雪', longitude: 255, monthNum: 11, isJie: true },
        { name: '冬至', longitude: 270, monthNum: 11, isJie: false }
    ],

    // 節気のみ（月の境界、12個）
    JIE_TERMS: [
        { name: '立春', longitude: 315, monthNum: 1, branchIndex: 2 },  // 寅月
        { name: '啓蟄', longitude: 345, monthNum: 2, branchIndex: 3 },  // 卯月
        { name: '清明', longitude: 15, monthNum: 3, branchIndex: 4 },  // 辰月
        { name: '立夏', longitude: 45, monthNum: 4, branchIndex: 5 },  // 巳月
        { name: '芒種', longitude: 75, monthNum: 5, branchIndex: 6 },  // 午月
        { name: '小暑', longitude: 105, monthNum: 6, branchIndex: 7 },  // 未月
        { name: '立秋', longitude: 135, monthNum: 7, branchIndex: 8 },  // 申月
        { name: '白露', longitude: 165, monthNum: 8, branchIndex: 9 },  // 酉月
        { name: '寒露', longitude: 195, monthNum: 9, branchIndex: 10 }, // 戌月
        { name: '立冬', longitude: 225, monthNum: 10, branchIndex: 11 }, // 亥月
        { name: '大雪', longitude: 255, monthNum: 11, branchIndex: 0 },  // 子月
        { name: '小寒', longitude: 285, monthNum: 12, branchIndex: 1 }   // 丑月
    ],

    // 天干
    STEMS: ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'],

    // 地支
    BRANCHES: ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'],

    // 天干の五行
    STEM_ELEMENTS: {
        '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
        '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
    },

    // 天干の陰陽
    STEM_YIN_YANG: {
        '甲': '陽', '乙': '陰', '丙': '陽', '丁': '陰', '戊': '陽',
        '己': '陰', '庚': '陽', '辛': '陰', '壬': '陽', '癸': '陰'
    },

    // 蔵干の配分（余気・中気・正気）と日数
    // 四柱推命では節入り後の経過日数により蔵干が変化
    HIDDEN_STEMS_DETAIL: {
        '子': { stems: ['壬', '癸'], days: [10, 20] },          // 壬10日、癸20日
        '丑': { stems: ['癸', '辛', '己'], days: [9, 3, 18] },  // 癸9日、辛3日、己18日
        '寅': { stems: ['戊', '丙', '甲'], days: [7, 7, 16] },  // 戊7日、丙7日、甲16日
        '卯': { stems: ['甲', '乙'], days: [10, 20] },          // 甲10日、乙20日
        '辰': { stems: ['乙', '癸', '戊'], days: [9, 3, 18] },  // 乙9日、癸3日、戊18日
        '巳': { stems: ['戊', '庚', '丙'], days: [7, 7, 16] },  // 戊7日、庚7日、丙16日
        '午': { stems: ['丙', '己', '丁'], days: [10, 9, 11] }, // 丙10日、己9日、丁11日
        '未': { stems: ['丁', '乙', '己'], days: [9, 3, 18] },  // 丁9日、乙3日、己18日
        '申': { stems: ['己', '壬', '庚'], days: [7, 7, 16] },  // 己7日、壬7日、庚16日
        '酉': { stems: ['庚', '辛'], days: [10, 20] },          // 庚10日、辛20日
        '戌': { stems: ['辛', '丁', '戊'], days: [9, 3, 18] },  // 辛9日、丁3日、戊18日
        '亥': { stems: ['戊', '甲', '壬'], days: [7, 7, 16] }   // 戊7日、甲7日、壬16日
    },

    // 簡易蔵干（余気・中気・正気のリスト形式）
    HIDDEN_STEMS: {
        '子': ['癸'],
        '丑': ['己', '癸', '辛'],
        '寅': ['甲', '丙', '戊'],
        '卯': ['乙'],
        '辰': ['戊', '乙', '癸'],
        '巳': ['丙', '庚', '戊'],
        '午': ['丁', '己'],
        '未': ['己', '丁', '乙'],
        '申': ['庚', '壬', '戊'],
        '酉': ['辛'],
        '戌': ['戊', '辛', '丁'],
        '亥': ['壬', '甲']
    },

    // 年干から寅月の月干を求める対応表
    MONTH_STEM_START: { 0: 2, 1: 4, 2: 6, 3: 8, 4: 0, 5: 2, 6: 4, 7: 6, 8: 8, 9: 0 },

    // 日干から子刻の時干を求める対応表
    HOUR_STEM_START: { 0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 0, 6: 2, 7: 4, 8: 6, 9: 8 },

    // 空亡（天中殺）
    VOID_BRANCHES_TABLE: [
        ['戌', '亥'], // 甲子～癸酉旬
        ['申', '酉'], // 甲戌～癸未旬
        ['午', '未'], // 甲申～癸巳旬
        ['辰', '巳'], // 甲午～癸卯旬
        ['寅', '卯'], // 甲辰～癸丑旬
        ['子', '丑']  // 甲寅～癸亥旬
    ],

    // ===== 節気計算 =====

    /**
     * 太陽が特定の黄経に達する精密な日時を計算
     * @param {number} targetLongitude - 目標黄経（度）
     * @param {number} startJD - 検索開始のユリウス日
     * @returns {number} 目標黄経に達するJD
     */
    findSolarTermJD(targetLongitude, startJD) {
        let jd = startJD;

        // 初期推定：太陽は約1度/日移動
        const currentLon = AstroCalc.getSunLongitude(jd);
        let diff = targetLongitude - currentLon;
        if (diff > 180) diff -= 360;
        if (diff < -180) diff += 360;
        jd += diff;

        // ニュートン法で高精度収束（約0.0001度 ≈ 約8秒）
        for (let i = 0; i < 30; i++) {
            const lon = AstroCalc.getSunLongitude(jd);
            diff = targetLongitude - lon;
            if (diff > 180) diff -= 360;
            if (diff < -180) diff += 360;

            if (Math.abs(diff) < 0.00001) break; // 約0.9秒精度
            jd += diff;
        }

        return jd;
    },

    /**
     * 指定年の特定の節気の正確なJDを計算
     * @param {number} year - 西暦年
     * @param {string} termName - 節気名
     * @returns {number|null} JD or null
     */
    getSolarTermJD(year, termName) {
        const term = this.SOLAR_TERMS_FULL.find(t => t.name === termName);
        if (!term) return null;

        // 概算開始日
        let approxMonth;
        const termIndex = this.SOLAR_TERMS_FULL.indexOf(term);
        approxMonth = Math.floor(termIndex / 2);

        // 小寒・大寒は1月
        if (termIndex <= 1) {
            approxMonth = 0;
        }

        const approxDate = new Date(Date.UTC(year, approxMonth, 1 + (termIndex % 2) * 15));
        const approxJD = AstroCalc.dateToJD(approxDate);

        return this.findSolarTermJD(term.longitude, approxJD);
    },

    /**
     * 立春のJDを取得
     * @param {number} year - 西暦年
     * @returns {number} 立春のJD
     */
    getLichunJD(year) {
        return this.getSolarTermJD(year, '立春');
    },

    /**
     * 指定年の全節気（24個）の日時を計算
     * @param {number} year - 西暦年
     * @returns {Array} [{name, longitude, jd, utc, jst}]
     */
    getYearSolarTerms(year) {
        const results = [];

        for (const term of this.SOLAR_TERMS_FULL) {
            // 黄経から概算日を推定
            let approxYear = year;
            if (term.longitude >= 285 && term.longitude <= 300) {
                // 小寒・大寒はその年の1月
            }

            const jd = this.getSolarTermJD(year, term.name);
            if (jd) {
                const utcDate = AstroCalc.jdToDate(jd);
                const jstDate = new Date(utcDate.getTime() + 9 * 60 * 60 * 1000);

                results.push({
                    name: term.name,
                    longitude: term.longitude,
                    monthNum: term.monthNum,
                    isJie: term.isJie,
                    jd: jd,
                    utc: utcDate,
                    jst: jstDate
                });
            }
        }

        return results;
    },

    /**
     * 直前の節気（月の境界となる「節」のみ）を取得
     * @param {number} jd - ユリウス日
     * @returns {object} {name, jd, monthNum, branchIndex, daysFromJieqi}
     */
    getPreviousJie(jd) {
        const date = AstroCalc.jdToDate(jd);
        const year = date.getUTCFullYear();

        // 前後2年分の節気を計算して最も近い「節」を見つける
        let prevJie = null;
        let prevJieJD = 0;

        for (let y = year - 1; y <= year + 1; y++) {
            for (const jie of this.JIE_TERMS) {
                const jieJD = this.getSolarTermJD(y, jie.name);
                if (jieJD && jieJD <= jd && jieJD > prevJieJD) {
                    prevJieJD = jieJD;
                    prevJie = { ...jie, jd: jieJD, year: y };
                }
            }
        }

        if (!prevJie) {
            // フォールバック
            return {
                name: '立春',
                jd: jd,
                monthNum: 1,
                branchIndex: 2,
                daysFromJieqi: 0
            };
        }

        // 節入りからの経過日数
        const daysFromJieqi = jd - prevJie.jd;

        return {
            name: prevJie.name,
            jd: prevJie.jd,
            monthNum: prevJie.monthNum,
            branchIndex: prevJie.branchIndex,
            daysFromJieqi: daysFromJieqi,
            year: prevJie.year
        };
    },

    // ===== 干支算出 =====

    /**
     * 日干支を計算（1992年2月17日=癸亥基準）
     * @param {number} jd - ユリウス日
     * @returns {object} 日柱データ
     */
    calcDayPillar(jd) {
        // 基準日: 1992年2月17日 JST = 癸亥
        // JDをUTCのDateに変換してからJST日付で計算
        const utcDate = AstroCalc.jdToDate(jd);
        const jstDate = new Date(utcDate.getTime() + 9 * 60 * 60 * 1000);

        // 基準日（1992年2月17日 JST）
        const baseDate = new Date(1992, 1, 17); // 月は0始まり

        // 日数差を計算（日付のみ）
        const baseDateOnly = new Date(baseDate.getFullYear(), baseDate.getMonth(), baseDate.getDate());
        const jstDateOnly = new Date(jstDate.getUTCFullYear(), jstDate.getUTCMonth(), jstDate.getUTCDate());
        const daysDiff = Math.floor((jstDateOnly - baseDateOnly) / (24 * 60 * 60 * 1000));

        // 癸亥のインデックス: 59
        const kuikaiIndex = 59;
        const sexagenaryIndex = ((kuikaiIndex + daysDiff) % 60 + 60) % 60;

        const stemIndex = sexagenaryIndex % 10;
        const branchIndex = sexagenaryIndex % 12;

        return {
            stem: this.STEMS[stemIndex],
            branch: this.BRANCHES[branchIndex],
            stemIndex,
            branchIndex,
            sexagenaryIndex,
            full: this.STEMS[stemIndex] + this.BRANCHES[branchIndex]
        };
    },

    /**
     * 年干支を計算（立春基準）
     * @param {number} jd - ユリウス日
     * @returns {object} 年柱データ
     */
    calcYearPillar(jd) {
        const date = AstroCalc.jdToDate(jd);
        let year = date.getUTCFullYear();

        // 立春のJDを取得
        const lichunJD = this.getLichunJD(year);

        // 立春前なら前年とする
        if (jd < lichunJD) {
            year -= 1;
        }

        // 1984年が甲子年
        const offset = ((year - 1984) % 60 + 60) % 60;
        const stemIndex = offset % 10;
        const branchIndex = offset % 12;

        return {
            stem: this.STEMS[stemIndex],
            branch: this.BRANCHES[branchIndex],
            stemIndex,
            branchIndex,
            year: year,
            full: this.STEMS[stemIndex] + this.BRANCHES[branchIndex]
        };
    },

    /**
     * 月干支を計算（節入り基準）
     * @param {number} jd - ユリウス日
     * @param {number} yearStemIndex - 年干インデックス
     * @returns {object} 月柱データ
     */
    calcMonthPillar(jd, yearStemIndex) {
        const jie = this.getPreviousJie(jd);

        const branchIndex = jie.branchIndex;

        // 年干から寅月の天干を決定し、月を進める
        // 寅月 = monthNum 1
        const baseStem = this.MONTH_STEM_START[yearStemIndex];
        // monthNum 1が寅月なので、そこからの差分
        const monthOffset = jie.monthNum - 1;
        const stemIndex = (baseStem + monthOffset) % 10;

        return {
            stem: this.STEMS[stemIndex],
            branch: this.BRANCHES[branchIndex],
            stemIndex,
            branchIndex,
            monthNum: jie.monthNum,
            jieName: jie.name,
            jieJD: jie.jd,
            daysFromJieqi: jie.daysFromJieqi,
            full: this.STEMS[stemIndex] + this.BRANCHES[branchIndex]
        };
    },

    /**
     * 時干支を計算（23時切り替え方式）
     * @param {Date} localDate - ローカル日時
     * @param {number} dayStemIndex - 日干インデックス
     * @param {boolean} use23Switch - 23時切り替えを使用するか（true: 23時説、false: 0時説）
     * @returns {object} 時柱データ
     */
    calcHourPillar(localDate, dayStemIndex, use23Switch = true) {
        const hour = localDate.getHours();
        const minute = localDate.getMinutes();

        let branchIndex;
        let adjustDay = false;

        if (use23Switch) {
            // 23時切り替え方式
            // 23:00-00:59 = 子の刻（翌日の干支を使用）
            // 01:00-02:59 = 丑の刻
            // ...
            if (hour >= 23) {
                branchIndex = 0; // 子
                adjustDay = true; // 翌日の日干を使用
            } else if (hour < 1) {
                branchIndex = 0; // 子（早子時）
                // adjustDay = false; // 当日扱い
            } else {
                branchIndex = Math.floor((hour + 1) / 2);
            }
        } else {
            // 0時切り替え方式
            // 00:00-01:59 = 子の刻
            // 02:00-03:59 = 丑の刻
            // ...
            branchIndex = Math.floor((hour + 1) / 2) % 12;
        }

        // 時干を計算
        // 日干から子刻の天干を決定し、時支分進める
        let effectiveDayStemIndex = dayStemIndex;
        if (adjustDay) {
            effectiveDayStemIndex = (dayStemIndex + 1) % 10;
        }

        const baseStem = this.HOUR_STEM_START[effectiveDayStemIndex];
        const stemIndex = (baseStem + branchIndex) % 10;

        return {
            stem: this.STEMS[stemIndex],
            branch: this.BRANCHES[branchIndex],
            stemIndex,
            branchIndex,
            hour: hour,
            minute: minute,
            use23Switch: use23Switch,
            dayAdjusted: adjustDay,
            full: this.STEMS[stemIndex] + this.BRANCHES[branchIndex]
        };
    },

    /**
     * 四柱を一括計算
     * @param {Date} localDate - ローカル日時（JST想定）
     * @param {boolean} use23Switch - 23時切り替え方式を使用
     * @returns {object} 四柱データ
     */
    calcFourPillars(localDate, use23Switch = true) {
        // ローカル時間をUTCに変換（JST = UTC + 9h）
        const jstOffset = 9 * 60 * 60 * 1000;
        const utcTime = localDate.getTime() - jstOffset;
        const utcDate = new Date(utcTime);
        const jd = AstroCalc.dateToJD(utcDate);

        // 23時以降の場合、日柱は翌日を使用（23時切り替え方式）
        let dayJD = jd;
        if (use23Switch && localDate.getHours() >= 23) {
            dayJD = jd + 1;
        }

        const yearPillar = this.calcYearPillar(jd);
        const monthPillar = this.calcMonthPillar(jd, yearPillar.stemIndex);
        const dayPillar = this.calcDayPillar(dayJD);
        const hourPillar = this.calcHourPillar(localDate, dayPillar.stemIndex, use23Switch);

        return {
            year: yearPillar,
            month: monthPillar,
            day: dayPillar,
            hour: hourPillar,
            jd: jd,
            use23Switch: use23Switch
        };
    },

    // ===== 蔵干計算 =====

    /**
     * 蔵干を取得（節入りからの経過日数に基づく）
     * @param {string} branch - 地支
     * @param {number} daysFromJieqi - 節入りからの経過日数
     * @returns {object} {mainStem, allStems, phase}
     */
    getHiddenStems(branch, daysFromJieqi = 15) {
        const detail = this.HIDDEN_STEMS_DETAIL[branch];
        if (!detail) {
            return {
                mainStem: null,
                allStems: [],
                phase: null
            };
        }

        const { stems, days } = detail;
        let cumulative = 0;
        let mainStem = stems[stems.length - 1]; // デフォルトは正気
        let phase = '正気';

        for (let i = 0; i < days.length; i++) {
            cumulative += days[i];
            if (daysFromJieqi < cumulative) {
                mainStem = stems[i];
                if (i === 0) phase = '余気';
                else if (i === stems.length - 1) phase = '正気';
                else phase = '中気';
                break;
            }
        }

        return {
            mainStem,
            allStems: stems,
            days: days,
            phase,
            daysFromJieqi
        };
    },

    /**
     * 四柱すべての蔵干を計算
     * @param {object} fourPillars - calcFourPillarsの結果
     * @returns {object} 各柱の蔵干
     */
    getAllHiddenStems(fourPillars) {
        const monthDays = fourPillars.month.daysFromJieqi || 15;

        return {
            year: this.getHiddenStems(fourPillars.year.branch, 15),
            month: this.getHiddenStems(fourPillars.month.branch, monthDays),
            day: this.getHiddenStems(fourPillars.day.branch, 15),
            hour: this.getHiddenStems(fourPillars.hour.branch, 15)
        };
    },

    // ===== 空亡（天中殺）計算 =====

    /**
     * 空亡を計算
     * @param {object} dayPillar - 日柱
     * @returns {object} {branches, name}
     */
    calcVoidBranches(dayPillar) {
        // 六十干支を10個ずつの旬に分ける
        const sexagenaryIndex = dayPillar.sexagenaryIndex;
        const groupIndex = Math.floor(sexagenaryIndex / 10);
        const branches = this.VOID_BRANCHES_TABLE[groupIndex];

        // 旬の名前
        const groupNames = ['甲子', '甲戌', '甲申', '甲午', '甲辰', '甲寅'];

        return {
            branches,
            groupName: groupNames[groupIndex] + '旬',
            voidName: branches.join('・') + '空亡'
        };
    },

    // ===== ユーティリティ =====

    /**
     * JDをJST日時文字列に変換
     * @param {number} jd - ユリウス日
     * @returns {string} JST日時文字列
     */
    jdToJSTString(jd) {
        const utcDate = AstroCalc.jdToDate(jd);
        const jstDate = new Date(utcDate.getTime() + 9 * 60 * 60 * 1000);

        const year = jstDate.getUTCFullYear();
        const month = String(jstDate.getUTCMonth() + 1).padStart(2, '0');
        const day = String(jstDate.getUTCDate()).padStart(2, '0');
        const hour = String(jstDate.getUTCHours()).padStart(2, '0');
        const minute = String(jstDate.getUTCMinutes()).padStart(2, '0');
        const second = String(jstDate.getUTCSeconds()).padStart(2, '0');

        return `${year}/${month}/${day} ${hour}:${minute}:${second} JST`;
    },

    /**
     * 完全な鑑定データを生成
     * @param {Date} birthDate - 生年月日時（ローカル時間）
     * @param {boolean} use23Switch - 23時切り替え方式
     * @returns {object} 完全な鑑定データ
     */
    generateFullReading(birthDate, use23Switch = true) {
        const pillars = this.calcFourPillars(birthDate, use23Switch);
        const hiddenStems = this.getAllHiddenStems(pillars);
        const voidBranches = this.calcVoidBranches(pillars.day);

        // 日主（日干）
        const dayMaster = pillars.day.stem;
        const dayMasterElement = this.STEM_ELEMENTS[dayMaster];
        const dayMasterYinYang = this.STEM_YIN_YANG[dayMaster];

        return {
            input: {
                birthDate: birthDate,
                use23Switch: use23Switch
            },
            pillars: pillars,
            hiddenStems: hiddenStems,
            voidBranches: voidBranches,
            dayMaster: {
                stem: dayMaster,
                element: dayMasterElement,
                yinYang: dayMasterYinYang
            },
            monthInfo: {
                jieName: pillars.month.jieName,
                daysFromJieqi: Math.floor(pillars.month.daysFromJieqi),
                mainHiddenStem: hiddenStems.month.mainStem,
                phase: hiddenStems.month.phase
            }
        };
    }
};

// グローバルに公開
window.SolarTermEngine = SolarTermEngine;
