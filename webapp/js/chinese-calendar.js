/**
 * 東洋暦計算エンジン（JavaScript版）
 * 二十四節気、干支、旧暦変換
 */

const ChineseCalendar = {
    // 天干（十干）
    STEMS: ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'],

    // 地支（十二支）
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

    // 地支の五行
    BRANCH_ELEMENTS: {
        '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
        '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
    },

    // 蔵干
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

    // 二十四節気（名前と太陽黄経）
    SOLAR_TERMS: [
        { name: '小寒', longitude: 285 },
        { name: '大寒', longitude: 300 },
        { name: '立春', longitude: 315 },
        { name: '雨水', longitude: 330 },
        { name: '啓蟄', longitude: 345 },
        { name: '春分', longitude: 0 },
        { name: '清明', longitude: 15 },
        { name: '穀雨', longitude: 30 },
        { name: '立夏', longitude: 45 },
        { name: '小満', longitude: 60 },
        { name: '芒種', longitude: 75 },
        { name: '夏至', longitude: 90 },
        { name: '小暑', longitude: 105 },
        { name: '大暑', longitude: 120 },
        { name: '立秋', longitude: 135 },
        { name: '処暑', longitude: 150 },
        { name: '白露', longitude: 165 },
        { name: '秋分', longitude: 180 },
        { name: '寒露', longitude: 195 },
        { name: '霜降', longitude: 210 },
        { name: '立冬', longitude: 225 },
        { name: '小雪', longitude: 240 },
        { name: '大雪', longitude: 255 },
        { name: '冬至', longitude: 270 }
    ],

    // 節気（月の境界となる12節気）
    JIEQI_NAMES: ['立春', '啓蟄', '清明', '立夏', '芒種', '小暑',
        '立秋', '白露', '寒露', '立冬', '大雪', '小寒'],

    // 月干起算（年干から寅月の天干を求める）
    MONTH_STEM_START: { 0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0 },

    // 時干起算（日干から子刻の天干を求める）
    HOUR_STEM_START: { 0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8 },

    // 空亡（天中殺）対応表
    VOID_BRANCHES: [
        ['戌', '亥'], ['申', '酉'], ['午', '未'],
        ['辰', '巳'], ['寅', '卯'], ['子', '丑']
    ],

    /**
     * 立春のJDを取得
     * @param {number} year - 西暦年
     * @returns {number} 立春のJD
     */
    getLichunJD(year) {
        const approxJD = AstroCalc.dateToJD(new Date(Date.UTC(year, 1, 4)));
        return AstroCalc.findSolarTermTime(315, approxJD);
    },

    /**
     * 直前の節気を取得
     * @param {number} jd - ユリウス日
     * @returns {object} {monthNum, name, jd}
     */
    getPreviousJieqi(jd) {
        const date = AstroCalc.jdToDate(jd);
        const year = date.getUTCFullYear();

        // 現在の太陽黄経
        const sunLon = AstroCalc.getSunLongitude(jd);

        // 直前の節気を検索
        for (let i = 0; i < this.JIEQI_NAMES.length; i++) {
            const jieqiName = this.JIEQI_NAMES[i];
            const term = this.SOLAR_TERMS.find(t => t.name === jieqiName);
            if (!term) continue;

            // 節気のJDを計算
            let approxMonth = Math.floor(i / 2) + 1;
            if (i >= 11) approxMonth = 0; // 小寒は前年12月
            const approxJD = AstroCalc.dateToJD(new Date(Date.UTC(year, approxMonth, 5)));
            const jieqiJD = AstroCalc.findSolarTermTime(term.longitude, approxJD);

            if (jieqiJD <= jd) {
                // この節気より後かチェック
                const nextIdx = (i + 1) % 12;
                const nextTerm = this.SOLAR_TERMS.find(t => t.name === this.JIEQI_NAMES[nextIdx]);
                if (nextTerm) {
                    let nextApproxMonth = Math.floor(nextIdx / 2) + 1;
                    const nextYear = nextIdx === 0 ? year + 1 : year;
                    const nextApproxJD = AstroCalc.dateToJD(new Date(Date.UTC(nextYear, nextApproxMonth, 5)));
                    const nextJieqiJD = AstroCalc.findSolarTermTime(nextTerm.longitude, nextApproxJD);

                    if (jd < nextJieqiJD) {
                        return { monthNum: i + 1, name: jieqiName, jd: jieqiJD };
                    }
                }
            }
        }

        // デフォルト：現在の太陽黄経から推定
        const termIndex = Math.floor(((sunLon - 315 + 360) % 360) / 30);
        return {
            monthNum: termIndex + 1,
            name: this.JIEQI_NAMES[termIndex % 12],
            jd: jd
        };
    },

    /**
     * 日干支を計算（23時切り替え対応）
     * @param {number} jd - ユリウス日
     * @param {Date} date - 日時（JST、23時切り替え用）
     * @returns {object} {stem, branch, stemIndex, branchIndex, full}
     */
    calcDayPillar(jd, date) {
        // JSTの日時を取得
        let calcDate = new Date(date);

        // 23時以降は翌日の干支を使用（晩子時方式）
        if (calcDate.getHours() >= 23) {
            calcDate = new Date(calcDate.getTime() + 24 * 60 * 60 * 1000);
        }

        // 基準日: 1992年2月17日 JST = 癸亥
        const baseDate = new Date(1992, 1, 17); // 月は0始まりなので2月=1

        // 日数差を計算（日付のみで比較）
        const baseDateOnly = new Date(baseDate.getFullYear(), baseDate.getMonth(), baseDate.getDate());
        const calcDateOnly = new Date(calcDate.getFullYear(), calcDate.getMonth(), calcDate.getDate());
        const daysDiff = Math.floor((calcDateOnly - baseDateOnly) / (24 * 60 * 60 * 1000));

        // 癸亥のインデックス: 59
        const kuikaiIndex = 59;

        // 60干支のインデックスを計算
        const index = ((kuikaiIndex + daysDiff) % 60 + 60) % 60;

        const stemIndex = index % 10;
        const branchIndex = index % 12;

        return {
            stem: this.STEMS[stemIndex],
            branch: this.BRANCHES[branchIndex],
            stemIndex,
            branchIndex,
            full: this.STEMS[stemIndex] + this.BRANCHES[branchIndex]
        };
    },

    /**
     * 年干支を計算（立春基準）
     * @param {number} jd - ユリウス日
     * @returns {object} {stem, branch, stemIndex, branchIndex, full}
     */
    calcYearPillar(jd) {
        const date = AstroCalc.jdToDate(jd);
        let year = date.getUTCFullYear();

        // 立春のJDを取得
        const lichunJD = this.getLichunJD(year);

        // 立春前なら前年
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
            full: this.STEMS[stemIndex] + this.BRANCHES[branchIndex]
        };
    },

    /**
     * 月干支を計算（節気基準）
     * @param {number} jd - ユリウス日
     * @param {number} yearStemIndex - 年干インデックス
     * @returns {object} {stem, branch, stemIndex, branchIndex, full}
     */
    calcMonthPillar(jd, yearStemIndex) {
        const jieqi = this.getPreviousJieqi(jd);
        const monthNum = jieqi.monthNum;

        // 寅月(1月) = 地支インデックス2
        const branchIndex = (monthNum + 1) % 12;

        // 年干から月干を計算
        const baseStem = this.MONTH_STEM_START[yearStemIndex];
        const stemIndex = (baseStem + monthNum - 1) % 10;

        return {
            stem: this.STEMS[stemIndex],
            branch: this.BRANCHES[branchIndex],
            stemIndex,
            branchIndex,
            full: this.STEMS[stemIndex] + this.BRANCHES[branchIndex]
        };
    },

    /**
     * 時干支を計算
     * @param {Date} date - 日時
     * @param {number} dayStemIndex - 日干インデックス
     * @returns {object} {stem, branch, stemIndex, branchIndex, full}
     */
    calcHourPillar(date, dayStemIndex) {
        const hour = date.getHours();

        // 時支（00:00-01:00が子の刻）
        const branchIndex = Math.floor((hour + 1) / 2) % 12;

        // 日干から子刻の天干を決定
        const baseStem = this.HOUR_STEM_START[dayStemIndex];
        const stemIndex = (baseStem + branchIndex) % 10;

        return {
            stem: this.STEMS[stemIndex],
            branch: this.BRANCHES[branchIndex],
            stemIndex,
            branchIndex,
            full: this.STEMS[stemIndex] + this.BRANCHES[branchIndex]
        };
    },

    /**
     * 四柱を計算
     * @param {Date} date - 生年月日時（ローカル時間）
     * @returns {object} {year, month, day, hour}
     */
    calcFourPillars(date) {
        // JSTとして扱う
        const jstOffset = 9 * 60 * 60 * 1000;
        const utcDate = new Date(date.getTime() - jstOffset);
        const jd = AstroCalc.dateToJD(utcDate);

        const year = this.calcYearPillar(jd);
        const month = this.calcMonthPillar(jd, year.stemIndex);
        const day = this.calcDayPillar(jd, date);  // dateパラメータを追加
        const hour = this.calcHourPillar(date, day.stemIndex);

        return { year, month, day, hour };
    },

    /**
     * 空亡（天中殺）を計算
     * @param {object} dayPillar - 日柱
     * @returns {string[]} 空亡の地支
     */
    calcVoidBranches(dayPillar) {
        // 六十干支のインデックス
        const sexagenaryIndex = (dayPillar.stemIndex + dayPillar.branchIndex * 10) % 60;

        // より正確な計算
        const group = Math.floor(sexagenaryIndex / 10);
        return this.VOID_BRANCHES[group];
    },

    /**
     * 旧暦に変換（簡易版）
     * @param {Date} date - 太陽暦日付
     * @returns {object} {year, month, day, isLeap}
     */
    toLunarDate(date) {
        // 簡易版：2000年1月6日を旧暦1999年12月1日として概算
        // 実用には外部ライブラリが必要
        const baseDate = new Date(2000, 0, 6);
        const diffDays = Math.floor((date - baseDate) / (24 * 60 * 60 * 1000));

        // 約29.5日周期
        const lunarMonthDays = 29.530588;
        const totalMonths = Math.floor(diffDays / lunarMonthDays) + 11; // 1999年12月から開始

        const year = 2000 + Math.floor(totalMonths / 12);
        const month = (totalMonths % 12) + 1;
        const day = Math.floor(diffDays % lunarMonthDays) + 1;

        return { year, month: Math.min(month, 12), day: Math.min(day, 30), isLeap: false };
    }
};

// グローバルに公開
window.ChineseCalendar = ChineseCalendar;
