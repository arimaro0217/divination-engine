/**
 * 天体計算エンジン（JavaScript版）
 * Meeus "Astronomical Algorithms" に基づく計算
 */

const AstroCalc = {
    // 定数
    DEG_TO_RAD: Math.PI / 180,
    RAD_TO_DEG: 180 / Math.PI,

    // 惑星ID
    PLANETS: {
        SUN: 0,
        MOON: 1,
        MERCURY: 2,
        VENUS: 3,
        MARS: 4,
        JUPITER: 5,
        SATURN: 6,
        URANUS: 7,
        NEPTUNE: 8,
        PLUTO: 9
    },

    // 惑星名
    PLANET_NAMES: {
        0: '太陽', 1: '月', 2: '水星', 3: '金星', 4: '火星',
        5: '木星', 6: '土星', 7: '天王星', 8: '海王星', 9: '冥王星'
    },

    // 12星座
    ZODIAC_SIGNS: [
        '牡羊座', '牡牛座', '双子座', '蟹座', '獅子座', '乙女座',
        '天秤座', '蠍座', '射手座', '山羊座', '水瓶座', '魚座'
    ],

    /**
     * 日時からユリウス日を計算
     * @param {Date} date - JavaScriptのDateオブジェクト
     * @returns {number} ユリウス日
     */
    dateToJD(date) {
        let year = date.getUTCFullYear();
        let month = date.getUTCMonth() + 1;
        let day = date.getUTCDate();
        let hour = date.getUTCHours() + date.getUTCMinutes() / 60 + date.getUTCSeconds() / 3600;

        if (month <= 2) {
            year -= 1;
            month += 12;
        }

        const A = Math.floor(year / 100);
        const B = 2 - A + Math.floor(A / 4);

        const JD = Math.floor(365.25 * (year + 4716)) +
            Math.floor(30.6001 * (month + 1)) +
            day + hour / 24 + B - 1524.5;

        return JD;
    },

    /**
     * ユリウス日から日時を計算
     * @param {number} jd - ユリウス日
     * @returns {Date} JavaScriptのDateオブジェクト
     */
    jdToDate(jd) {
        const Z = Math.floor(jd + 0.5);
        const F = jd + 0.5 - Z;

        let A;
        if (Z < 2299161) {
            A = Z;
        } else {
            const alpha = Math.floor((Z - 1867216.25) / 36524.25);
            A = Z + 1 + alpha - Math.floor(alpha / 4);
        }

        const B = A + 1524;
        const C = Math.floor((B - 122.1) / 365.25);
        const D = Math.floor(365.25 * C);
        const E = Math.floor((B - D) / 30.6001);

        const day = B - D - Math.floor(30.6001 * E) + F;
        const month = E < 14 ? E - 1 : E - 13;
        const year = month > 2 ? C - 4716 : C - 4715;

        const dayInt = Math.floor(day);
        const dayFrac = day - dayInt;
        const hours = dayFrac * 24;
        const hour = Math.floor(hours);
        const minutes = (hours - hour) * 60;
        const minute = Math.floor(minutes);
        const second = Math.floor((minutes - minute) * 60);

        return new Date(Date.UTC(year, month - 1, dayInt, hour, minute, second));
    },

    /**
     * ユリウス世紀を計算（J2000.0基準）
     * @param {number} jd - ユリウス日
     * @returns {number} ユリウス世紀
     */
    julianCentury(jd) {
        return (jd - 2451545.0) / 36525.0;
    },

    /**
     * 角度を0-360度に正規化
     * @param {number} deg - 角度（度）
     * @returns {number} 正規化された角度
     */
    normalizeDegrees(deg) {
        let result = deg % 360;
        if (result < 0) result += 360;
        return result;
    },

    /**
     * 太陽の黄経を計算（低精度版、約0.01度精度）
     * @param {number} jd - ユリウス日
     * @returns {number} 太陽黄経（度）
     */
    getSunLongitude(jd) {
        const T = this.julianCentury(jd);

        // 太陽の平均黄経
        let L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T;
        L0 = this.normalizeDegrees(L0);

        // 太陽の平均近点角
        let M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T;
        M = this.normalizeDegrees(M);
        const Mrad = M * this.DEG_TO_RAD;

        // 太陽の中心差
        const C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * Math.sin(Mrad) +
            (0.019993 - 0.000101 * T) * Math.sin(2 * Mrad) +
            0.000289 * Math.sin(3 * Mrad);

        // 太陽の真黄経
        let sunLongitude = L0 + C;

        return this.normalizeDegrees(sunLongitude);
    },

    /**
     * 月の黄経を計算（低精度版）
     * @param {number} jd - ユリウス日
     * @returns {number} 月黄経（度）
     */
    getMoonLongitude(jd) {
        const T = this.julianCentury(jd);

        // 月の平均黄経
        let Lp = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T;
        Lp = this.normalizeDegrees(Lp);

        // 月の平均近点角
        let M = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T;
        M = this.normalizeDegrees(M);
        const Mrad = M * this.DEG_TO_RAD;

        // 太陽の平均近点角
        let Ms = 357.5291092 + 35999.0502909 * T;
        Ms = this.normalizeDegrees(Ms);
        const Msrad = Ms * this.DEG_TO_RAD;

        // 月の平均引数
        let F = 93.2720950 + 483202.0175233 * T;
        F = this.normalizeDegrees(F);
        const Frad = F * this.DEG_TO_RAD;

        // 月の平均離角
        let D = 297.8501921 + 445267.1114034 * T;
        D = this.normalizeDegrees(D);
        const Drad = D * this.DEG_TO_RAD;

        // 主要項のみの簡易計算
        let moonLongitude = Lp +
            6.289 * Math.sin(Mrad) +
            1.274 * Math.sin(2 * Drad - Mrad) +
            0.658 * Math.sin(2 * Drad) +
            0.214 * Math.sin(2 * Mrad) -
            0.186 * Math.sin(Msrad) -
            0.114 * Math.sin(2 * Frad);

        return this.normalizeDegrees(moonLongitude);
    },

    /**
     * 惑星の黄経を計算（超簡易版）
     * @param {number} jd - ユリウス日
     * @param {number} planetId - 惑星ID
     * @returns {object} {longitude, retrograde}
     */
    getPlanetLongitude(jd, planetId) {
        const T = this.julianCentury(jd);

        // 各惑星の軌道要素（平均値）
        const orbitalElements = {
            2: { L: 252.25084, n: 4.09233445 },    // Mercury
            3: { L: 181.97973, n: 1.60213034 },    // Venus
            4: { L: 355.45332, n: 0.52402068 },    // Mars
            5: { L: 34.40438, n: 0.08308676 },     // Jupiter
            6: { L: 49.94432, n: 0.03344414 },     // Saturn
            7: { L: 313.23218, n: 0.01172834 },    // Uranus
            8: { L: 304.87997, n: 0.00601190 },    // Neptune
            9: { L: 238.92881, n: 0.00397557 }     // Pluto（簡易）
        };

        if (planetId === 0) {
            return { longitude: this.getSunLongitude(jd), retrograde: false };
        }
        if (planetId === 1) {
            return { longitude: this.getMoonLongitude(jd), retrograde: false };
        }

        const elem = orbitalElements[planetId];
        if (!elem) return { longitude: 0, retrograde: false };

        // 平均黄経
        let L = elem.L + elem.n * T * 36525;
        L = this.normalizeDegrees(L);

        // 逆行判定（簡易版：太陽との位置関係）
        const sunLon = this.getSunLongitude(jd);
        const elongation = Math.abs(L - sunLon);
        // 内惑星は太陽に近いとき、外惑星は衝近くで逆行
        const retrograde = planetId <= 3 ? elongation < 20 : elongation > 160;

        return { longitude: L, retrograde };
    },

    /**
     * 黄経からサインを取得
     * @param {number} longitude - 黄経（度）
     * @returns {object} {signIndex, sign, degree}
     */
    longitudeToSign(longitude) {
        const signIndex = Math.floor(longitude / 30);
        const degree = longitude % 30;
        return {
            signIndex,
            sign: this.ZODIAC_SIGNS[signIndex],
            degree: degree
        };
    },

    /**
     * 太陽が特定の黄経に達する日時を検索
     * @param {number} targetLongitude - 目標黄経（度）
     * @param {number} startJD - 検索開始JD
     * @returns {number} 目標黄経に達するJD
     */
    findSolarTermTime(targetLongitude, startJD) {
        let jd = startJD;

        // 初期推定
        const currentLon = this.getSunLongitude(jd);
        let diff = targetLongitude - currentLon;
        if (diff > 180) diff -= 360;
        if (diff < -180) diff += 360;
        jd += diff; // 太陽は約1度/日

        // ニュートン法で収束
        for (let i = 0; i < 20; i++) {
            const lon = this.getSunLongitude(jd);
            diff = targetLongitude - lon;
            if (diff > 180) diff -= 360;
            if (diff < -180) diff += 360;

            if (Math.abs(diff) < 0.0001) break;
            jd += diff;
        }

        return jd;
    },

    /**
     * アヤナムサ値を計算（ラヒリ）
     * @param {number} jd - ユリウス日
     * @returns {number} アヤナムサ値（度）
     */
    getLahiriAyanamsa(jd) {
        const T = this.julianCentury(jd);
        // Lahiri Ayanamsa（歳差値）
        const ayanamsa = 23.85 + 0.0137 * (jd - 2451545.0) / 365.25;
        return ayanamsa;
    },

    /**
     * サイデリアル黄経を計算
     * @param {number} tropicalLongitude - トロピカル黄経
     * @param {number} jd - ユリウス日
     * @returns {number} サイデリアル黄経
     */
    getSiderealLongitude(tropicalLongitude, jd) {
        const ayanamsa = this.getLahiriAyanamsa(jd);
        return this.normalizeDegrees(tropicalLongitude - ayanamsa);
    },

    /**
     * ハウスカスプを計算（イコールハウス方式）
     * @param {number} ascendant - ASC度数
     * @returns {number[]} 12ハウスのカスプ
     */
    calcHouses(ascendant) {
        const cusps = [];
        for (let i = 0; i < 12; i++) {
            cusps.push(this.normalizeDegrees(ascendant + i * 30));
        }
        return cusps;
    },

    /**
     * ASC（アセンダント）を計算
     * @param {number} jd - ユリウス日
     * @param {number} latitude - 緯度
     * @param {number} longitude - 経度
     * @returns {number} ASC度数
     */
    calcAscendant(jd, latitude, longitude) {
        const T = this.julianCentury(jd);

        // 恒星時
        let GMST = 280.46061837 + 360.98564736629 * (jd - 2451545.0);
        GMST = this.normalizeDegrees(GMST);

        // 地方恒星時
        const LST = this.normalizeDegrees(GMST + longitude);
        const LSTrad = LST * this.DEG_TO_RAD;

        // 黄道傾斜角
        const eps = 23.439291 - 0.0130042 * T;
        const epsRad = eps * this.DEG_TO_RAD;

        // 緯度
        const latRad = latitude * this.DEG_TO_RAD;

        // ASC計算
        const y = -Math.cos(LSTrad);
        const x = Math.sin(epsRad) * Math.tan(latRad) + Math.cos(epsRad) * Math.sin(LSTrad);

        let asc = Math.atan2(y, x) * this.RAD_TO_DEG;
        asc = this.normalizeDegrees(asc);

        return asc;
    }
};

// グローバルに公開
window.AstroCalc = AstroCalc;
