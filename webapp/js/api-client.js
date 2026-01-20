/**
 * 占いAPIクライアント
 * Pythonバックエンド（FastAPI）との通信を担当
 */

const APIClient = {
    // APIベースURL（開発環境 / 本番環境で自動切り替え）
    BASE_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000/api'
        : 'https://divination-engine.onrender.com',

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
     * 紫微斗数計算（完全版：十二宮、四化星、大限）
     * @param {Object} data - {birthDateTime, latitude, longitude, gender}
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
                gender: data.gender || 'male'
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Ziwei calculation failed');
        }
        return result.data;
    },

    /**
     * インド占星術計算（完全版：D1/D9、Dasha）
     * @param {Object} data - {birthDateTime, latitude, longitude}
     * @returns {Promise<Object>} - ホロスコープデータ
     */
    async calculateJyotish(data) {
        const response = await fetch(`${this.BASE_URL}/jyotish`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                birth_datetime: data.birthDateTime,
                latitude: data.latitude || 35.68,
                longitude: data.longitude || 139.76
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Jyotish calculation failed');
        }
        return result.data;
    },

    /**
     * 四柱推命計算（高精度版：節入り精密計算）
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
     * 西洋占星術計算（高精度版：Swiss Ephemeris）
     * @param {Object} data - {birthDateTime, latitude, longitude}
     * @returns {Promise<Object>} - ホロスコープデータ
     */
    async calculateWestern(data) {
        const response = await fetch(`${this.BASE_URL}/western`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                birth_datetime: data.birthDateTime,
                latitude: data.latitude || 35.68,
                longitude: data.longitude || 139.76
            })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.detail || 'Western calculation failed');
        }
        return result.data;
    },

    /**
     * 全占術統合計算
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
                gender: data.gender || 'male'
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
