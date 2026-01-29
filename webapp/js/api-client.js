/**
 * 占いAPIクライアント（高性能版）
 * Pythonバックエンド（FastAPI）との通信を担当
 * 
 * 全占術を高性能なPython版計算で実行
 */

const APIClient = {
    // APIベースURL（開発環境 / 本番環境で自動切り替え）
    BASE_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000/api'
        : 'https://divination-engine.onrender.com',

    // API利用可能フラグ
    _apiAvailable: null,

    /**
     * APIサーバーが利用可能かチェック
     */
    async isApiAvailable() {
        if (this._apiAvailable !== null) return this._apiAvailable;
        this._apiAvailable = await this.healthCheck();
        return this._apiAvailable;
    },

    /**
     * 数秘術計算（高度版：Y判定、Chaldean、天体連携）
     * @param {Object} data - {name, birthDate, system, targetYear}
     * @returns {Promise<Object>} - 計算結果
     */
    async calculateNumerology(data) {
        const response = await fetch(`${this.BASE_URL}/numerology`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: data.name,
                birth_date: data.birthDate,
                system: data.system || 'pythagorean',
                target_year: data.targetYear || null
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Numerology calculation failed');
        }
        return result.data;
    },

    /**
     * 紫微斗数計算（高性能版：輝度、乙級星、四化星、グリッド座標）
     * @param {Object} data - {birthDateTime, latitude, longitude, gender, leapMonthMode}
     * @returns {Promise<Object>} - 命盤データ
     */
    async calculateZiwei(data) {
        const response = await fetch(`${this.BASE_URL}/ziwei`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                birth_datetime: data.birthDateTime,
                latitude: data.latitude || 35.68,
                longitude: data.longitude || 139.76,
                gender: data.gender || 'male',
                leap_month_mode: data.leapMonthMode || 'previous'  // 閏月モード
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Ziwei calculation failed');
        }
        return result.data;
    },

    /**
     * インド占星術計算（高性能版：D1/D9/D10、Dasha、ナクシャトラ）
     * @param {Object} data - {birthDateTime, latitude, longitude, ayanamsa}
     * @returns {Promise<Object>} - ホロスコープデータ
     */
    async calculateJyotish(data) {
        const response = await fetch(`${this.BASE_URL}/jyotish`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                birth_datetime: data.birthDateTime,
                latitude: data.latitude || 35.68,
                longitude: data.longitude || 139.76,
                ayanamsa: data.ayanamsa || 'LAHIRI'  // アヤナムサ選択
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Jyotish calculation failed');
        }
        return result.data;
    },

    /**
     * 四柱推命計算（高精度版：節入り精密計算、蔵干）
     * @param {Object} data - {year, month, day, hour, minute, latitude, longitude}
     * @returns {Promise<Object>} - 四柱データ
     */
    async calculateBazi(data) {
        const response = await fetch(`${this.BASE_URL}/bazi`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                year: data.year,
                month: data.month,
                day: data.day,
                hour: data.hour,
                minute: data.minute,
                latitude: data.latitude || 35.68,
                longitude: data.longitude || 139.76
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'BaZi calculation failed');
        }
        return result.data;
    },

    /**
     * 西洋占星術計算（高精度版：Swiss Ephemeris、Applying/Separating）
     * @param {Object} data - {birthDateTime, latitude, longitude, altitude, houseSystem}
     * @returns {Promise<Object>} - ホロスコープデータ
     */
    async calculateWestern(data) {
        const response = await fetch(`${this.BASE_URL}/western`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                birth_datetime: data.birthDateTime,
                latitude: data.latitude || 35.68,
                longitude: data.longitude || 139.76,
                altitude: data.altitude || 0,  // 標高
                house_system: data.houseSystem || 'placidus'  // ハウスシステム
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Western calculation failed');
        }
        return result.data;
    },

    /**
     * 西洋占星術ボイドタイム計算
     * @param {Object} data - {datetime, latitude, longitude}
     * @returns {Promise<Object>} - ボイドタイム情報
     */
    async calculateVoidOfCourse(data) {
        const response = await fetch(`${this.BASE_URL}/western/void-of-course`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                datetime: data.datetime,
                latitude: data.latitude || 35.68,
                longitude: data.longitude || 139.76
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Void of Course calculation failed');
        }
        return result.data;
    },

    /**
     * 宿曜占星術計算（高性能版：凌犯期間、相性方向性）
     * @param {Object} data - {birthDate, targetDate, checkRyohan}
     * @returns {Promise<Object>} - 宿曜データ
     */
    async calculateSukuyo(data) {
        const response = await fetch(`${this.BASE_URL}/sukuyo`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                birth_date: data.birthDate,
                target_date: data.targetDate || null,
                check_ryohan: data.checkRyohan !== false  // 凌犯期間チェック
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Sukuyo calculation failed');
        }
        return result.data;
    },

    /**
     * 宿曜占星術相性計算
     * @param {Object} data - {person1BirthDate, person2BirthDate}
     * @returns {Promise<Object>} - 相性データ
     */
    async calculateSukuyoCompatibility(data) {
        const response = await fetch(`${this.BASE_URL}/sukuyo/compatibility`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                person1_birth_date: data.person1BirthDate,
                person2_birth_date: data.person2BirthDate
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Sukuyo compatibility calculation failed');
        }
        return result.data;
    },

    /**
     * マヤ暦計算（高性能版：古代/ドリームスペル、GAPキン、フナブ・クの日）
     * @param {Object} data - {birthDate, mode, sunriseHour}
     * @returns {Promise<Object>} - マヤ暦データ
     */
    async calculateMayan(data) {
        const response = await fetch(`${this.BASE_URL}/mayan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                birth_date: data.birthDate,
                mode: data.mode || 'dreamspell',  // 'dreamspell' or 'classic'
                sunrise_hour: data.sunriseHour || 6.0  // 日の出時刻
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Mayan calculation failed');
        }
        return result.data;
    },

    /**
     * マヤ暦モード比較（古代 vs ドリームスペル）
     * @param {Object} data - {date}
     * @returns {Promise<Object>} - 比較データ
     */
    async compareMayanModes(data) {
        const response = await fetch(`${this.BASE_URL}/mayan/compare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                date: data.date
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Mayan comparison failed');
        }
        return result.data;
    },

    /**
     * 九星気学計算（高精度版：陽遁/陰遁、動的節入り）
     * @param {Object} data - {birthDate, gender}
     * @returns {Promise<Object>} - 九星データ
     */
    async calculateKyusei(data) {
        const response = await fetch(`${this.BASE_URL}/kyusei`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                birth_date: data.birthDate,
                gender: data.gender || 'male'
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Kyusei calculation failed');
        }
        return result.data;
    },

    /**
     * 算命学計算
     * @param {Object} data - {birthDate}
     * @returns {Promise<Object>} - 算命学データ
     */
    async calculateSanmei(data) {
        const response = await fetch(`${this.BASE_URL}/sanmei`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                birth_date: data.birthDate
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Sanmei calculation failed');
        }
        return result.data;
    },

    /**
     * 姓名判断計算
     * @param {Object} data - {familyName, givenName}
     * @returns {Promise<Object>} - 姓名判断データ
     */
    async calculateSeimei(data) {
        const response = await fetch(`${this.BASE_URL}/seimei`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                family_name: data.familyName,
                given_name: data.givenName
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Seimei calculation failed');
        }
        return result.data;
    },

    /**
     * 全占術統合計算（高性能版）
     * @param {Object} data - {nameKanji, nameKana, birthDateTime, latitude, longitude, gender}
     * @returns {Promise<Object>} - 全占術結果
     */
    async calculateAll(data) {
        const response = await fetch(`${this.BASE_URL}/calculate-all`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name_kanji: data.nameKanji,
                name_kana: data.nameKana || data.nameKanji,
                birth_datetime: data.birthDateTime,
                birth_place: data.birthPlace || '',
                latitude: data.latitude || 35.68,
                longitude: data.longitude || 139.76,
                gender: data.gender || 'male',
                // 高性能オプション
                options: {
                    mayan_mode: data.mayanMode || 'dreamspell',
                    numerology_system: data.numerologySystem || 'pythagorean',
                    house_system: data.houseSystem || 'placidus',
                    ayanamsa: data.ayanamsa || 'LAHIRI',
                    check_void_of_course: true,
                    check_ryohan: true,
                    include_gap_kin: true
                }
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Calculation failed');
        }
        return result.data;
    },

    /**
     * ヘルスチェック（APIサーバーが起動しているか確認）
     * @returns {Promise<boolean>}
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.BASE_URL.replace('/api', '')}/health`);
            const result = await response.json();
            return result.status === 'ok';
        } catch (e) {
            return false;
        }
    }
};

// グローバルに公開
window.APIClient = APIClient;

