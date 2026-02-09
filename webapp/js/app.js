/**
 * 統合占い計算エンジン - メインアプリケーション
 * Refactored for High Reliability and Performance
 * Phase 5: Chart Rendering & Advanced Features Integration
 */

document.addEventListener('DOMContentLoaded', () => {
    // UI要素の取得
    const elements = {
        form: document.getElementById('divination-form'),
        resultsSection: document.getElementById('results-section'),
        resultsContainer: document.getElementById('results-container'),
        userSummary: document.getElementById('user-summary'),
        birthPlaceSelect: document.getElementById('birth-place'),
        customCoords: document.getElementById('custom-coords'),
        btnSample: document.getElementById('btn-sample'),
        btnPrint: document.getElementById('btn-print'),
        btnNew: document.getElementById('btn-new'),
        inputs: {
            familyName: document.getElementById('family-name'),
            givenName: document.getElementById('given-name'),
            year: document.getElementById('birth-year'),
            month: document.getElementById('birth-month'),
            day: document.getElementById('birth-day'),
            hour: document.getElementById('birth-hour'),
            minute: document.getElementById('birth-minute'),
            lat: document.getElementById('latitude'),
            lon: document.getElementById('longitude'),
        }
    };

    // 初期化処理
    initEventListeners();

    // ==========================================
    // Event Listeners
    // ==========================================
    function initEventListeners() {
        // 出生地選択
        elements.birthPlaceSelect.addEventListener('change', () => {
            if (elements.birthPlaceSelect.value === 'custom') {
                elements.customCoords.classList.remove('hidden');
            } else {
                elements.customCoords.classList.add('hidden');
            }
        });

        // サンプルデータ
        elements.btnSample.addEventListener('click', fillSampleData);

        // フォーム送信
        elements.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleCalculation();
        });

        // 印刷
        elements.btnPrint.addEventListener('click', () => window.print());

        // 新規作成
        elements.btnNew.addEventListener('click', resetForm);
    }

    function fillSampleData() {
        elements.inputs.familyName.value = '安瀬';
        elements.inputs.givenName.value = '諒';
        elements.inputs.year.value = '1992';
        elements.inputs.month.value = '2';
        elements.inputs.day.value = '17';
        elements.inputs.hour.value = '17';
        elements.inputs.minute.value = '18';
        elements.birthPlaceSelect.value = '35.6762,139.6503'; // 東京
    }

    function resetForm() {
        elements.resultsSection.classList.add('hidden');
        elements.form.reset();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // ==========================================
    // Calculation Logic
    // ==========================================
    async function handleCalculation() {
        // 入力値取得
        const params = getCalculationParams();

        // ローディング表示
        showLoading();

        // 計算実行
        const results = await executeCalculations(params);

        // 結果の正規化（Adapter）
        const normalizedResults = DivinationAdapter.normalizeAll(results, params.fullName);

        // 高度計算データ（チャート用）の補完
        augmentWithAdvancedData(normalizedResults, params);

        // 結果の表示（Renderer）
        renderResults(params, normalizedResults);
    }

    function getCalculationParams() {
        const familyName = elements.inputs.familyName.value.trim();
        const givenName = elements.inputs.givenName.value.trim();
        const fullName = familyName + ' ' + givenName;

        const year = parseInt(elements.inputs.year.value);
        const month = parseInt(elements.inputs.month.value);
        const day = parseInt(elements.inputs.day.value);
        const hour = parseInt(elements.inputs.hour.value);
        const minute = parseInt(elements.inputs.minute.value);

        let latitude = 35.6762;
        let longitude = 139.6503;
        const placeValue = elements.birthPlaceSelect.value;
        if (placeValue && placeValue !== 'custom') {
            const [lat, lon] = placeValue.split(',').map(parseFloat);
            latitude = lat;
            longitude = lon;
        } else if (placeValue === 'custom') {
            latitude = parseFloat(elements.inputs.lat.value) || 35.6762;
            longitude = parseFloat(elements.inputs.lon.value) || 139.6503;
        }

        const birthDate = new Date(year, month - 1, day, hour, minute);

        const genderInput = document.querySelector('input[name="gender"]:checked');
        const gender = genderInput ? genderInput.value : 'male';

        const selectedDivinations = Array.from(
            document.querySelectorAll('input[name="divination"]:checked')
        ).map(cb => cb.value);

        return {
            familyName, givenName, fullName,
            birthDate, latitude, longitude, gender,
            selectedDivinations
        };
    }

    function showLoading() {
        elements.resultsSection.classList.remove('hidden');
        elements.resultsContainer.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">サーバーと通信中...</div>
                <div class="loading-subtext">高度な天文計算を実行しています。これには最大1分ほどかかる場合があります。</div>
            </div>
        `;
        elements.userSummary.innerHTML = '';
    }

    async function executeCalculations(params) {
        const results = {};
        const { birthDate, latitude, longitude, gender, fullName, familyName, givenName, selectedDivinations } = params;
        const birthDateISO = birthDate.toISOString();

        // API可用性チェック
        let apiAvailable = false;
        if (window.APIClient) {
            try {
                apiAvailable = await APIClient.healthCheck();
            } catch (e) {
                console.warn('API connection failed, falling back to local calculation.', e);
            }
        }

        const calcConfig = [
            { id: 'bazi', apiFunc: 'calculateBazi', params: { year: birthDate.getFullYear(), month: birthDate.getMonth() + 1, day: birthDate.getDate(), hour: birthDate.getHours(), minute: birthDate.getMinutes(), latitude, longitude }, jsFunc: () => DivinationModules.BaZi.calculate(birthDate) },
            { id: 'sanmei', apiFunc: 'calculateSanmei', params: { birthDate: birthDateISO }, jsFunc: () => DivinationModules.Sanmei.calculate(birthDate) },
            { id: 'kyusei', apiFunc: 'calculateKyusei', params: { birthDate: birthDateISO, gender }, jsFunc: () => DivinationModules.Kyusei.calculate(birthDate, gender) },
            { id: 'ziwei', apiFunc: 'calculateZiwei', params: { birthDateTime: birthDateISO, latitude, longitude, gender }, jsFunc: () => DivinationModules.ZiWei.calculate(birthDate) },
            { id: 'sukuyou', apiFunc: 'calculateSukuyo', params: { birthDate: birthDateISO }, jsFunc: () => DivinationModules.Sukuyou.calculate(birthDate) },
            { id: 'western', apiFunc: 'calculateWestern', params: { birthDateTime: birthDateISO, latitude, longitude }, jsFunc: () => DivinationModules.Western.calculate(birthDate, latitude, longitude) },
            { id: 'vedic', apiFunc: 'calculateJyotish', params: { birthDateTime: birthDateISO, latitude, longitude }, jsFunc: () => DivinationModules.Vedic.calculate(birthDate, latitude, longitude) },
            { id: 'mayan', apiFunc: 'calculateMayan', params: { birthDate: birthDateISO }, jsFunc: () => DivinationModules.Mayan.calculate(birthDate) },
            { id: 'numerology', apiFunc: 'calculateNumerology', params: { name: fullName, birthDate: birthDateISO, system: 'pythagorean' }, jsFunc: () => DivinationModules.Numerology.calculate(birthDate) },
            { id: 'seimei', apiFunc: 'calculateSeimei', params: { familyName, givenName }, jsFunc: () => DivinationModules.Seimei.calculate(params.familyName, params.givenName) }
        ];

        // 並列実行ではなく順次または個別実行（依存関係やエラーハンドリングのため）
        for (const config of calcConfig) {
            if (!selectedDivinations.includes(config.id)) continue;

            let result = null;

            if (apiAvailable && config.apiFunc && APIClient[config.apiFunc]) {
                try {
                    result = await APIClient[config.apiFunc](config.params);
                    result.source = 'API';
                } catch (e) {
                    console.error(`${config.id} API Error:`, e);
                }
            }

            if (!result && config.jsFunc) {
                try {
                    result = config.jsFunc();
                    result.source = 'JS';
                } catch (e) {
                    console.error(`${config.id} JS Error:`, e);
                }
            }

            if (result) results[config.id] = result;
        }

        return results;
    }

    /**
     * 高度な計算データを補完する（チャート描画用など）
     * API/JSどちらの結果であっても、AdvancedModulesを用いて正規化後のデータから計算・統合する
     */
    function augmentWithAdvancedData(results, params) {
        if (!window.AdvancedDivinationModules) return;
        const Adv = window.AdvancedDivinationModules;

        // 四柱推命（五行バランス）
        if (results.bazi && results.bazi.pillars) {
            try {
                // pillarsはnormalize済みなのでJS版構造に近い
                const adv = Adv.BaziAdvanced.calculate(results.bazi.pillars, 0.5);
                results.bazi.advanced = { ...(results.bazi.advanced || {}), ...adv };
            } catch (e) { console.error('Bazi Advanced Error', e); }
        }

        // 算命学（宇宙盤）
        if (results.sanmei && results.bazi && results.bazi.pillars) {
            try {
                // tenGodsが必要（baziから取得）
                const adv = Adv.SanmeiAdvanced.calculate(results.bazi.pillars, results.bazi.tenGods);
                results.sanmei.advanced = { ...(results.sanmei.advanced || {}), ...adv };
            } catch (e) { console.error('Sanmei Advanced Error', e); }
        }

        // 九星気学（方位盤）
        if (results.kyusei) {
            try {
                // 文字列から数値へ変換
                const starToNum = (s) => (Adv.KyuseiAdvanced.NINE_STARS.indexOf(s) + 1) || 5;
                const yearStarNum = starToNum(results.kyusei.yearStar);
                const monthStarNum = starToNum(results.kyusei.monthStar);
                const dayStarNum = starToNum(results.kyusei.dayStar);

                // 本命星を使用（ユーザーの方位判断用）
                const userStar = yearStarNum;

                const adv = Adv.KyuseiAdvanced.calculate(
                    yearStarNum, monthStarNum, dayStarNum, userStar,
                    params.latitude, params.longitude
                );
                results.kyusei.advanced = { ...(results.kyusei.advanced || {}), ...adv };
            } catch (e) { console.error('Kyusei Advanced Error', e); }
        }
    }

    function renderResults(params, results) {
        // 結果データの保存（ダウンロード用）
        if (typeof saveResultsData === 'function') {
            saveResultsData(params.fullName, params.birthDate, results);
        }

        // ユーザーサマリー表示
        elements.userSummary.innerHTML = `
            <h3>${params.fullName} 様</h3>
            <p>${params.birthDate.getFullYear()}年${params.birthDate.getMonth() + 1}月${params.birthDate.getDate()}日 
               ${params.birthDate.getHours()}時${params.birthDate.getMinutes()}分生まれ</p>
            <p style="font-size: 0.9em; color: #666;">緯度: ${params.latitude.toFixed(4)}, 経度: ${params.longitude.toFixed(4)}</p>
        `;

        // HTML生成
        let html = '';
        if (results.bazi) html += DivinationRenderer.renderBaZi(results.bazi);
        if (results.sanmei) html += DivinationRenderer.renderSanmei(results.sanmei);
        if (results.kyusei) html += DivinationRenderer.renderKyusei(results.kyusei);
        if (results.ziwei) html += DivinationRenderer.renderZiWei(results.ziwei);
        if (results.sukuyou) html += DivinationRenderer.renderSukuyou(results.sukuyou);
        if (results.western) html += DivinationRenderer.renderWestern(results.western);
        if (results.vedic) html += DivinationRenderer.renderVedic(results.vedic);
        if (results.mayan) html += DivinationRenderer.renderMayan(results.mayan);
        if (results.numerology) html += DivinationRenderer.renderNumerology(results.numerology);
        if (results.seimei) html += DivinationRenderer.renderSeimei(results.seimei);

        if (html === '') {
            html = '<div class="error-message">結果を計算できませんでした。入力値を確認してください。</div>';
        }

        elements.resultsContainer.innerHTML = html;
        elements.resultsSection.scrollIntoView({ behavior: 'smooth' });

        // チャート描画（Canvas）
        // DOMが描画された後に実行
        setTimeout(() => {
            if (typeof DivinationCharts !== 'undefined') {
                try {
                    DivinationCharts.renderAll(
                        results.bazi ? results.bazi.advanced : null,
                        results.sanmei ? results.sanmei.advanced : null,
                        results.kyusei ? results.kyusei.advanced : null
                    );
                } catch (e) {
                    console.error("Chart Rendering Error:", e);
                }
            }
        }, 100);
    }
});

/**
 * ==========================================
 * DivinationAdapter
 * API(snake_case)とJS(camelCase)の差異を吸収し
 * 統一されたデータ構造(camelCase)に変換する
 * ==========================================
 */
class DivinationAdapter {
    static normalizeAll(results, fullName) {
        const normalized = {};
        if (results.bazi) normalized.bazi = this.normalizeBazi(results.bazi);
        if (results.sanmei) normalized.sanmei = this.normalizeSanmei(results.sanmei);
        if (results.kyusei) normalized.kyusei = this.normalizeKyusei(results.kyusei);
        if (results.ziwei) normalized.ziwei = this.normalizeZiWei(results.ziwei);
        if (results.sukuyou) normalized.sukuyou = this.normalizeSukuyou(results.sukuyou);
        if (results.western) normalized.western = this.normalizeWestern(results.western);
        if (results.vedic) normalized.vedic = this.normalizeVedic(results.vedic);
        if (results.mayan) normalized.mayan = this.normalizeMayan(results.mayan);
        if (results.numerology) normalized.numerology = this.normalizeNumerology(results.numerology);
        if (results.seimei) normalized.seimei = this.normalizeSeimei(results.seimei, fullName);
        return normalized;
    }

    static val(obj, keys, defaultVal = undefined) {
        if (!obj) return defaultVal;
        for (const k of keys) {
            if (obj[k] !== undefined && obj[k] !== null) return obj[k];
        }
        return defaultVal;
    }

    static normalizeBazi(data) {
        const srcPillars = this.val(data, ['four_pillars', 'pillars']);
        const pillars = {
            year: this._normalizePillar(srcPillars?.year),
            month: this._normalizePillar(srcPillars?.month),
            day: this._normalizePillar(srcPillars?.day),
            hour: this._normalizePillar(srcPillars?.hour)
        };

        const hiddenStems = this.val(data, ['hidden_stems', 'hiddenStems']);

        return {
            pillars,
            dayMaster: this.val(data, ['day_master', 'dayMaster']),
            voidBranches: this.val(data, ['void_branches', 'voidBranches'], []),
            tenGods: this.val(data, ['ten_gods', 'tenGods'], {}),
            twelveStages: this.val(data, ['twelve_stages', 'twelveStages'], {}),
            hiddenStems,
            monthInfo: this.val(data, ['monthInfo']),
            advanced: data.advanced || {}
        };
    }

    static _normalizePillar(p) {
        if (!p) return { stem: '?', branch: '?' };
        return {
            stem: this.val(p, ['heavenly_stem', 'stem'], '?'),
            branch: this.val(p, ['earthly_branch', 'branch'], '?')
        };
    }

    static normalizeSanmei(data) {
        return {
            voidGroupName: this.val(data, ['void_group_name', 'voidGroupName']),
            mainStars: this.val(data, ['main_stars', 'mainStars'], {}),
            subStars: this.val(data, ['sub_stars', 'subStars'], {}),
            advanced: data.advanced || {}
        };
    }

    static normalizeKyusei(data) {
        return {
            yearStar: this.val(data, ['year_star', 'yearStar']),
            monthStar: this.val(data, ['month_star', 'monthStar']),
            dayStar: this.val(data, ['day_star', 'dayStar']),
            inclination: this.val(data, ['inclination']),
            advanced: data.advanced || {}
        };
    }

    static normalizeZiWei(data) {
        let palaces = [];
        const srcPalaces = this.val(data, ['palaces']);
        const srcMainStars = this.val(data, ['main_stars']);

        if (srcPalaces && Array.isArray(srcPalaces)) {
            palaces = srcPalaces.map(p => {
                let allStars = [];

                // 主星
                const rawStars = p.stars || p.major_stars || [];
                allStars = allStars.concat(rawStars.map(s => {
                    if (typeof s === 'string') return { name: s, brightness: '', type: 'major' };
                    return {
                        name: s.name,
                        brightness: s.brightness || '',
                        type: 'major'
                    };
                }));

                // 副星
                const minor = p.minor_stars || [];
                allStars = allStars.concat(minor.map(s => {
                    if (typeof s === 'string') return { name: s, brightness: '', type: 'minor' };
                    return { name: s.name, brightness: s.brightness || '', type: 'minor' };
                }));

                // 凶星
                const bad = p.bad_stars || [];
                allStars = allStars.concat(bad.map(s => {
                    if (typeof s === 'string') return { name: s, brightness: '', type: 'bad' };
                    return { name: s.name, brightness: s.brightness || '', type: 'bad' };
                }));

                return {
                    name: p.name || p.palace_type || '?',
                    branch: p.branch || '',
                    stars: (p.stars && p.stars[0] && p.stars[0].type) ? p.stars : allStars
                };
            });
        } else if (srcMainStars) {
            // 後方互換性（古い形式の場合）
            const ORDER = ['命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮', '遷移宮', '奴僕宮', '官禄宮', '田宅宮', '福徳宮', '父母宮'];
            palaces = ORDER.map((name, i) => {
                const starsRaw = srcMainStars[name] || [];
                const starNames = Array.isArray(starsRaw) ? starsRaw : [starsRaw];
                return {
                    name,
                    branch: '', // 不明
                    stars: starNames.map(s => ({ name: s, brightness: '' }))
                };
            });
        }

        return {
            lunarDate: this.val(data, ['lunar_date', 'lunarDate']),
            mingPalace: this.val(data, ['ming_palace', 'mingPalace', 'life_palace', 'lifePalace']),
            bodyPalace: this.val(data, ['body_palace', 'bodyPalace']),
            ziweiPosition: this.val(data, ['ziwei_position', 'ziweiPosition']),
            bureau: this.val(data, ['bureau']),
            hourBranch: this.val(data, ['hour_branch', 'hourBranch']),
            palaces
        };
    }

    static normalizeSukuyou(data) {
        return {
            mansion: this.val(data, ['natal_mansion', 'natalMansion', 'mansion']),
            mansionNumber: this.val(data, ['mansion_number', 'mansionNumber', 'mansionIndex'], 0),
            element: this.val(data, ['element']),
            weekday: this.val(data, ['weekday', 'day_element', 'dayElement']),
            group: this.val(data, ['group']),
            lunarDate: this.val(data, ['lunar_date', 'lunarDate']),
            dailyMansion: data.dailyMansion,
            dailyCycle: data.dailyCycle,
            mandala: data.mandala
        };
    }

    static normalizeWestern(data) {
        const srcPlanets = this.val(data, ['planets'], []);
        const planets = srcPlanets.map(p => ({
            name: this.val(p, ['planet', 'name']),
            sign: this.val(p, ['sign', 'signEn']),
            degree: this.val(p, ['degree', 'degree_in_sign', 'longitude']),
            retrograde: this.val(p, ['retrograde'], false)
        }));

        const srcHouses = this.val(data, ['houses'], {});
        let houses = [];
        if (Array.isArray(srcHouses)) {
            houses = srcHouses;
        } else {
            houses = Object.entries(srcHouses).map(([k, v]) => ({
                house: parseInt(k),
                sign: '',
                degree: v
            }));
        }

        const srcAspects = this.val(data, ['aspects'], []);
        const aspects = srcAspects.map(a => ({
            planet1: this.val(a, ['planet1']),
            planet2: this.val(a, ['planet2']),
            type: this.val(a, ['aspect_type', 'aspect']),
            orb: this.val(a, ['orb']),
            applying: this.val(a, ['applying'])
        }));

        let asc = this.val(data, ['ascendant']);
        if (typeof asc === 'object') asc = asc.sign;

        return {
            sunSign: this.val(data, ['sunSign']),
            moonSign: this.val(data, ['moonSign']),
            ascendant: asc,
            planets,
            houses,
            aspects,
            voidInfo: this.val(data, ['void_of_course', 'voidInfo'], {})
        };
    }

    static normalizeVedic(data) {
        return {
            ayanamsa: this.val(data, ['ayanamsa']),
            nakshatra: this.val(data, ['nakshatra', 'moon_nakshatra', 'moonNakshatra']),
            nakshatraLord: this.val(data, ['nakshatra_lord', 'nakshatraLord']),
            lagna: this.val(data, ['lagna']),
            sunSign: this.val(data, ['sunSign']),
            dashas: this.val(data, ['dashas', 'dasha', 'sequence'], [])
        };
    }

    static normalizeMayan(data) {
        return {
            kin: this.val(data, ['kin_number', 'kin']),
            solarSeal: this.val(data, ['solar_seal', 'solarSeal']),
            galacticTone: this.val(data, ['galactic_tone', 'galacticTone']),
            galacticToneName: this.val(data, ['galacticToneName']),
            wavespell: this.val(data, ['wavespell']),
            guide: this.val(data, ['guide']),
            isGapKin: this.val(data, ['isGapKin'])
        };
    }

    static normalizeNumerology(data) {
        return {
            lifePath: this.val(data, ['life_path', 'lifePath', 'life_path_number']),
            lifePathMeaning: this.val(data, ['lifePathMeaning']),
            birthdayNumber: this.val(data, ['birthday_number', 'birthdayNumber']),
            expressionNumber: this.val(data, ['expression_number', 'expressionNumber']),
            soulNumber: this.val(data, ['soul_urge', 'soulNumber'])
        };
    }

    static normalizeSeimei(data, fullName) {
        const result = {
            familyName: this.val(data, ['family_name', 'familyName']),
            givenName: this.val(data, ['given_name', 'givenName']),
            strokes: this.val(data, ['strokes']),
            tenkaku: this.val(data, ['tenkaku']),
            jinkaku: this.val(data, ['jinkaku']),
            chikaku: this.val(data, ['chikaku']),
            gaikaku: this.val(data, ['gaikaku']),
            soukaku: this.val(data, ['soukaku'])
        };

        if (!result.familyName && fullName) {
            const parts = fullName.split(' ');
            if (parts.length >= 2) {
                result.familyName = parts[0];
                result.givenName = parts[1];
            }
        }
        return result;
    }
}

/**
 * ==========================================
 * DivinationRenderer
 * 正規化されたデータを受け取り
 * 高性能なUIコンポーネント(HTML)を生成する
 * ==========================================
 */
class DivinationRenderer {
    static renderBaZi(data) {
        const p = data.pillars;

        let hiddenStemsHtml = '';
        if (data.hiddenStems) {
            const row = (label, hs) => `<tr><td>${label}</td><td>${(hs.allStems || []).join('・')}</td><td>${hs.mainStem || ''}</td></tr>`;
            hiddenStemsHtml = `
                <h4 class="subheading">蔵干</h4>
                <table class="result-table">
                    <tr><th>柱</th><th>蔵干</th><th>本気</th></tr>
                    ${row(`年支（${p.year.branch}）`, data.hiddenStems.year)}
                    ${row(`月支（${p.month.branch}）`, data.hiddenStems.month)}
                    ${row(`日支（${p.day.branch}）`, data.hiddenStems.day)}
                    ${row(`時支（${p.hour.branch}）`, data.hiddenStems.hour)}
                </table>`;
        }

        let advancedHtml = '';
        if (data.advanced) {
            const adv = data.advanced;

            // 神殺
            if (adv.specialStars && Object.keys(adv.specialStars).length > 0) {
                const rows = Object.entries(adv.specialStars).map(([k, v]) => `<tr><td>${k}</td><td>${v.join('・')}</td></tr>`).join('');
                advancedHtml += `
                    <h4 class="subheading">神殺・特殊星</h4>
                    <table class="result-table">
                        <tr><th>星名</th><th>地支</th></tr>
                        ${rows}
                    </table>`;
            }

            // 位相法
            let interactions = [];
            if (adv.interactions) {
                const i = adv.interactions;
                interactions = [
                    ...(i.kango || []), ...(i.zhihe || []), ...(i.sango || []),
                    ...(i.chu || []), ...(i.kei || []), ...(i.gai || []), ...(i.ha || [])
                ];
            }

            if (interactions.length > 0) {
                advancedHtml += `
                    <h4 class="subheading">位相法（刑冲会合）</h4>
                    <ul style="list-style-type: disc; padding-left: 20px; font-size: 0.9em; margin-bottom: 20px;">
                        ${interactions.map(s => `<li>${s}</li>`).join('')}
                    </ul>`;
            }
        }

        return `
            <div class="result-card">
                <div class="result-card-header"><h3 class="result-card-title">四柱推命</h3></div>
                <div class="result-card-body">
                    <div class="pillars-display">
                        ${this._renderPillar('年柱', p.year)}
                        ${this._renderPillar('月柱', p.month)}
                        ${this._renderPillar('日柱', p.day)}
                        ${this._renderPillar('時柱', p.hour)}
                    </div>
                    
                    <div class="important-box">
                        <p><span class="highlight">★ 日主</span>：${data.dayMaster}</p>
                        <p><span class="highlight">★ 空亡</span>：${data.voidBranches.join('・')}</p>
                        ${data.monthInfo ? `<p><span class="highlight">★ 節入り</span>：${data.monthInfo.jieName}（${data.monthInfo.daysFromJieqi}日目）</p>` : ''}
                    </div>
                    
                    ${hiddenStemsHtml}
                    
                    <h4 class="subheading">通変星</h4>
                    <table class="result-table">
                        <tr><th>位置</th><th>通変星</th></tr>
                        ${Object.entries(data.tenGods).map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('')}
                    </table>
                    
                    <h4 class="subheading">十二運</h4>
                    <table class="result-table">
                        <tr><th>位置</th><th>十二運</th></tr>
                        ${Object.entries(data.twelveStages).map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('')}
                    </table>
                    
                    ${advancedHtml}

                    <div class="chart-section" style="margin-top:20px; text-align:center;">
                        <h4 class="subheading">五行バランス</h4>
                        <canvas id="gogyo-radar-canvas" width="300" height="300" style="max-width:100%;"></canvas>
                    </div>
                </div>
            </div>
        `;
    }

    static _renderPillar(label, p) {
        return `
            <div class="pillar">
                <div class="pillar-label">${label}</div>
                <div class="pillar-value">
                    <span class="pillar-stem">${p.stem}</span><span class="pillar-branch">${p.branch}</span>
                </div>
            </div>`;
    }

    static renderSanmei(data) {
        return `
            <div class="result-card">
                <div class="result-card-header"><h3 class="result-card-title">算命学</h3></div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ 天中殺</span>：${data.voidGroupName}</p>
                    </div>
                    <h4 class="subheading">十大主星</h4>
                    <table class="result-table">
                        ${Object.entries(data.mainStars).map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('')}
                    </table>
                    <h4 class="subheading">十二大従星</h4>
                    <table class="result-table">
                        ${Object.entries(data.subStars).map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('')}
                    </table>
                    
                    <div class="chart-section" style="margin-top:20px; text-align:center;">
                        <h4 class="subheading">宇宙盤</h4>
                        <canvas id="uchuban-canvas" width="300" height="300" style="max-width:100%;"></canvas>
                    </div>
                </div>
            </div>`;
    }

    static renderKyusei(data) {
        return `
            <div class="result-card">
                <div class="result-card-header"><h3 class="result-card-title">九星気学</h3></div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ 本命星</span>：${data.yearStar}</p>
                        <p><span class="highlight">★ 月命星</span>：${data.monthStar}</p>
                        <p><span class="highlight">★ 日命星</span>：${data.dayStar}</p>
                        <p><span class="highlight">★ 傾斜宮</span>：${data.inclination}</p>
                    </div>
                    
                    <div class="chart-section" style="margin-top:20px; text-align:center;">
                        <h4 class="subheading">本日の吉凶方位</h4>
                        <canvas id="direction-board-canvas" width="300" height="300" style="max-width:100%;"></canvas>
                    </div>
                </div>
            </div>`;
    }

    static renderZiWei(data) {
        const palacesHtml = data.palaces.map(p => {
            const starHtml = p.stars.map(s => {
                let style = '';
                if (s.type === 'major') style = 'color:#e74c3c; font-weight:bold;'; // 赤
                else if (s.type === 'minor') style = 'color:#27ae60; font-size:0.9em;'; // 緑
                else if (s.type === 'bad') style = 'color:#7f8c8d; font-size:0.85em;'; // グレー

                const b = s.brightness ? `<span style="font-size:0.8em; color:#888;">${s.brightness}</span>` : '';
                return `<div style="${style}">${s.name}${b}</div>`;
            }).join('');

            return `
            <div style="border:1px solid #ddd; padding:4px; text-align:center;">
                <div style="font-weight:bold;">${p.name}</div>
                <div>${p.branch}</div>
                <div style="margin-top:4px;">${starHtml}</div>
            </div>`;
        }).join('');

        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">紫微斗数</h3>
                    <span class="source-tag">${data.source === 'API' ? '✨ 高性能API版' : '⚡ 予備JS版'}</span>
                </div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ 命宮</span>：${data.mingPalace}宮</p>
                        <p><span class="highlight">★ 身宮</span>：${data.bodyPalace}宮</p>
                        <p><span class="highlight">★ 紫微星</span>：${data.ziweiPosition}宮</p>
                    </div>
                    <h4 class="subheading">十二宮配置</h4>
                    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:4px; font-size:0.75rem;">
                        ${palacesHtml}
                    </div>
                </div>
            </div>`;
    }

    static renderSukuyou(data) {
        return `
            <div class="result-card">
                <div class="result-card-header"><h3 class="result-card-title">宿曜占星術</h3></div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ 本命宿</span>：${data.mansion}（第${data.mansionNumber}宿）</p>
                        <p><span class="highlight">★ 属性</span>：${data.element}</p>
                        <p><span class="highlight">★ 七曜</span>：${data.weekday}</p>
                        ${data.group ? `<p><span class="highlight">★ 性格</span>：${data.group}</p>` : ''}
                    </div>
                    ${data.dailyMansion ? `<div class="warning-box" style="background:#f9f9f9; color:#333;">今日の運勢：${data.dailyMansion}（サイクル${data.dailyCycle}日目）</div>` : ''}
                </div>
            </div>`;
    }

    static renderWestern(data) {
        const warning = data.voidInfo?.is_void
            ? `<div class="warning-box" style="background:#fff3cd; color:#856404; border:1px solid #ffeeba;"><strong>⚠ ボイドタイム警告</strong><br>現在ボイドタイム中です。</div>`
            : '';

        return `
            <div class="result-card">
                <div class="result-card-header"><h3 class="result-card-title">西洋占星術</h3></div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ 太陽</span>：${this._findPlanetSign(data.planets, 'Sun', '太陽')}</p>
                        <p><span class="highlight">★ 月</span>：${this._findPlanetSign(data.planets, 'Moon', '月')}</p>
                        <p><span class="highlight">★ ASC</span>：${data.ascendant}</p>
                    </div>
                    ${warning}
                    <h4 class="subheading">惑星位置</h4>
                    <table class="result-table">
                        <tr><th>惑星</th><th>星座</th><th>度数</th></tr>
                        ${data.planets.map(p => `<tr><td>${p.name}${p.retrograde ? ' <span style="color:red">℞</span>' : ''}</td><td>${p.sign}</td><td>${typeof p.degree === 'number' ? p.degree.toFixed(2) : p.degree}°</td></tr>`).join('')}
                    </table>
                    <h4 class="subheading">アスペクト</h4>
                    <table class="result-table">
                        <tr><th>天体</th><th>角度</th><th>オーブ</th><th>状態</th></tr>
                        ${data.aspects.map(a => `<tr><td>${a.planet1}-${a.planet2}</td><td>${a.type}</td><td>${typeof a.orb === 'number' ? a.orb.toFixed(2) : a.orb}°</td><td>${a.applying ? 'A' : 'S'}</td></tr>`).join('')}
                    </table>
                </div>
            </div>`;
    }

    static _findPlanetSign(planets, enName, jpName) {
        const p = planets.find(x => x.name === enName || x.name === jpName);
        return p ? p.sign : '?';
    }

    static renderVedic(data) {
        let dashasHtml = '';
        if (data.dashas && data.dashas.length > 0) {
            const rows = data.dashas.map(d => `<tr><td>${d.lord}</td><td>${d.start}〜${d.end} (${d.years}年)</td></tr>`).join('');
            dashasHtml = `
                <h4 class="subheading">ヴィムショッタリ・ダシャー</h4>
                <div style="max-height:200px; overflow-y:auto;">
                    <table class="result-table">
                        <tr><th>支配星</th><th>期間（開始年〜終了年）</th></tr>
                        ${rows}
                    </table>
                </div>`;
        }

        return `
            <div class="result-card">
                <div class="result-card-header"><h3 class="result-card-title">インド占星術</h3></div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ ラグナ</span>：${data.lagna}</p>
                        <p><span class="highlight">★ 月ナクシャトラ</span>：${data.nakshatra}</p>
                        <p><span class="highlight">★ 支配星</span>：${data.nakshatraLord}</p>
                    </div>
                    ${dashasHtml}
                </div>
            </div>`;
    }

    static renderMayan(data) {
        const gap = data.isGapKin ? `<div class="warning-box" style="background:#333; color:#fff;"><strong>★ GAPキン（黒キン）</strong><br>強力なエネルギーの日です。</div>` : '';
        return `
            <div class="result-card">
                <div class="result-card-header"><h3 class="result-card-title">マヤ暦</h3></div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ KIN</span>：${data.kin}</p>
                        <p><span class="highlight">★ 紋章</span>：${data.solarSeal}</p>
                        <p><span class="highlight">★ 音</span>：${data.galacticTone}</p>
                    </div>
                    ${gap}
                </div>
            </div>`;
    }

    static renderNumerology(data) {
        const rows = [
            `<tr><td>ライフパス</td><td>${data.lifePath}</td><td>${data.lifePathMeaning || ''}</td></tr>`,
            `<tr><td>バースデー</td><td>${data.birthdayNumber}</td><td></td></tr>`
        ];
        if (data.expressionNumber) rows.push(`<tr><td>ディスティニー</td><td>${data.expressionNumber}</td><td>運命数</td></tr>`);
        if (data.soulNumber) rows.push(`<tr><td>ソウル</td><td>${data.soulNumber}</td><td>魂の欲求</td></tr>`);

        return `
            <div class="result-card">
                <div class="result-card-header"><h3 class="result-card-title">数秘術</h3></div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ ライフパス</span>：${data.lifePath}</p>
                    </div>
                    <table class="result-table">
                        <tr><th>項目</th><th>数</th><th>意味</th></tr>
                        ${rows.join('')}
                    </table>
                </div>
            </div>`;
    }

    static renderSeimei(data) {
        return `
            <div class="result-card">
                <div class="result-card-header"><h3 class="result-card-title">姓名判断</h3></div>
                <div class="result-card-body">
                    <p>姓：${data.familyName}　名：${data.givenName}</p>
                    <table class="result-table">
                        <tr><th>格</th><th>画数</th></tr>
                        <tr><td>天格</td><td>${data.tenkaku}</td></tr>
                        <tr><td>人格</td><td>${data.jinkaku}</td></tr>
                        <tr><td>地格</td><td>${data.chikaku}</td></tr>
                        <tr><td>外格</td><td>${data.gaikaku}</td></tr>
                        <tr><td>総格</td><td>${data.soukaku}</td></tr>
                    </table>
                </div>
            </div>`;
    }
}
