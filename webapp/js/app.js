/**
 * 統合占い計算エンジン - メインアプリケーション
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('divination-form');
    const resultsSection = document.getElementById('results-section');
    const resultsContainer = document.getElementById('results-container');
    const userSummary = document.getElementById('user-summary');
    const birthPlaceSelect = document.getElementById('birth-place');
    const customCoords = document.getElementById('custom-coords');
    const btnSample = document.getElementById('btn-sample');
    const btnPrint = document.getElementById('btn-print');
    const btnNew = document.getElementById('btn-new');

    // 出生地選択の処理
    birthPlaceSelect.addEventListener('change', () => {
        if (birthPlaceSelect.value === 'custom') {
            customCoords.classList.remove('hidden');
        } else {
            customCoords.classList.add('hidden');
        }
    });

    // サンプルデータ入力
    btnSample.addEventListener('click', () => {
        document.getElementById('family-name').value = '安瀬';
        document.getElementById('given-name').value = '諒';
        document.getElementById('birth-year').value = '1992';
        document.getElementById('birth-month').value = '2';
        document.getElementById('birth-day').value = '17';
        document.getElementById('birth-hour').value = '17';
        document.getElementById('birth-minute').value = '18';
        birthPlaceSelect.value = '35.6762,139.6503'; // 東京
    });

    // フォーム送信
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        calculateDivinations();
    });

    // 印刷ボタン
    btnPrint.addEventListener('click', () => {
        window.print();
    });

    // 新しい鑑定ボタン
    btnNew.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        form.reset();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    /**
     * 占術計算を実行
     */
    async function calculateDivinations() {
        // 入力値を取得
        const familyName = document.getElementById('family-name').value.trim();
        const givenName = document.getElementById('given-name').value.trim();
        const fullName = familyName + ' ' + givenName;
        const year = parseInt(document.getElementById('birth-year').value);
        const month = parseInt(document.getElementById('birth-month').value);
        const day = parseInt(document.getElementById('birth-day').value);
        const hour = parseInt(document.getElementById('birth-hour').value);
        const minute = parseInt(document.getElementById('birth-minute').value);

        // 緯度経度
        let latitude = 35.6762;
        let longitude = 139.6503;
        const placeValue = birthPlaceSelect.value;
        if (placeValue && placeValue !== 'custom') {
            const [lat, lon] = placeValue.split(',').map(parseFloat);
            latitude = lat;
            longitude = lon;
        } else if (placeValue === 'custom') {
            latitude = parseFloat(document.getElementById('latitude').value) || 35.6762;
            longitude = parseFloat(document.getElementById('longitude').value) || 139.6503;
        }

        // 日時オブジェクト
        const birthDate = new Date(year, month - 1, day, hour, minute);
        const birthDateISO = birthDate.toISOString();

        // 性別を取得
        const genderInput = document.querySelector('input[name="gender"]:checked');
        const gender = genderInput ? genderInput.value : 'male';

        // 選択された占術
        const selectedDivinations = Array.from(
            document.querySelectorAll('input[name="divination"]:checked')
        ).map(cb => cb.value);

        // ローディング表示
        // ローディング表示
        resultsSection.classList.remove('hidden');
        resultsContainer.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">サーバーを起動しています...</div>
                <div class="loading-subtext">※バックエンドの起動に最大1分ほどかかる場合があります</div>
            </div>
        `;
        userSummary.innerHTML = '';

        // 結果を計算
        const results = {};

        // APIが利用可能かチェック
        let apiAvailable = false;
        if (window.APIClient) {
            try {
                apiAvailable = await APIClient.healthCheck();
            } catch (e) {
                console.log('API not available, using JS fallback');
            }
        }

        // ===== 四柱推命 =====
        if (selectedDivinations.includes('bazi')) {
            if (apiAvailable) {
                try {
                    const apiResult = await APIClient.calculateBazi({
                        year, month, day, hour, minute, latitude, longitude
                    });
                    results.bazi = {
                        pillars: apiResult.four_pillars,
                        dayMaster: apiResult.day_master,
                        voidBranches: apiResult.void_branches,
                        fromAPI: true
                    };
                } catch (e) {
                    console.error('BaZi API error:', e);
                    results.bazi = DivinationModules.BaZi.calculate(birthDate);
                }
            } else {
                results.bazi = DivinationModules.BaZi.calculate(birthDate);
            }
            // 高度機能を追加
            if (window.AdvancedDivinationModules && results.bazi && results.bazi.pillars) {
                const advBazi = AdvancedDivinationModules.BaziAdvanced.calculate(
                    results.bazi.pillars, 0.5
                );
                results.bazi.advanced = advBazi;
            }
        }

        // ===== 算命学 =====
        if (selectedDivinations.includes('sanmei')) {
            results.sanmei = DivinationModules.Sanmei.calculate(birthDate);
            if (window.AdvancedDivinationModules && results.sanmei) {
                const baziData = DivinationModules.BaZi.calculate(birthDate);
                if (baziData && baziData.pillars) {
                    const advSanmei = AdvancedDivinationModules.SanmeiAdvanced.calculate(
                        baziData.pillars, baziData.tenGods
                    );
                    results.sanmei.advanced = advSanmei;
                }
            }
        }

        // ===== 九星気学 =====
        if (selectedDivinations.includes('kyusei')) {
            results.kyusei = DivinationModules.Kyusei.calculate(birthDate, gender);
            if (window.AdvancedDivinationModules && results.kyusei) {
                const yearStarNum = results.kyusei.yearStarNum;
                const monthStarNum = results.kyusei.monthStarNum;
                const dayStarNum = results.kyusei.dayStarNum;
                const advKyusei = AdvancedDivinationModules.KyuseiAdvanced.calculate(
                    yearStarNum, monthStarNum, dayStarNum,
                    yearStarNum, latitude, longitude
                );
                results.kyusei.advanced = advKyusei;
            }
        }

        // ===== 紫微斗数（高度版API使用） =====
        if (selectedDivinations.includes('ziwei')) {
            if (apiAvailable) {
                try {
                    results.ziwei = await APIClient.calculateZiwei({
                        birthDateTime: birthDateISO,
                        latitude, longitude, gender
                    });
                    results.ziwei.fromAPI = true;
                } catch (e) {
                    console.error('Ziwei API error:', e);
                    try {
                        results.ziwei = DivinationModules.ZiWei.calculate(birthDate);
                    } catch (e2) { console.error('ZiWei JS error:', e2); }
                }
            } else {
                try {
                    results.ziwei = DivinationModules.ZiWei.calculate(birthDate);
                } catch (e) { console.error('ZiWei error:', e); }
            }
        }

        // ===== 宿曜 =====
        if (selectedDivinations.includes('sukuyou')) {
            try {
                results.sukuyou = DivinationModules.Sukuyou.calculate(birthDate);
            } catch (e) { console.error('Sukuyou error:', e); }
        }

        // ===== 西洋占星術（高度版API使用） =====
        if (selectedDivinations.includes('western')) {
            if (apiAvailable) {
                try {
                    results.western = await APIClient.calculateWestern({
                        birthDateTime: birthDateISO,
                        latitude, longitude
                    });
                    results.western.fromAPI = true;
                } catch (e) {
                    console.error('Western API error:', e);
                    try {
                        results.western = DivinationModules.Western.calculate(birthDate, latitude, longitude);
                    } catch (e2) { console.error('Western JS error:', e2); }
                }
            } else {
                try {
                    results.western = DivinationModules.Western.calculate(birthDate, latitude, longitude);
                } catch (e) { console.error('Western error:', e); }
            }
        }

        // ===== インド占星術（高度版API使用） =====
        if (selectedDivinations.includes('vedic')) {
            if (apiAvailable) {
                try {
                    results.vedic = await APIClient.calculateJyotish({
                        birthDateTime: birthDateISO,
                        latitude, longitude
                    });
                    results.vedic.fromAPI = true;
                } catch (e) {
                    console.error('Jyotish API error:', e);
                    try {
                        results.vedic = DivinationModules.Vedic.calculate(birthDate, latitude, longitude);
                    } catch (e2) { console.error('Vedic JS error:', e2); }
                }
            } else {
                try {
                    results.vedic = DivinationModules.Vedic.calculate(birthDate, latitude, longitude);
                } catch (e) { console.error('Vedic error:', e); }
            }
        }

        // ===== マヤ暦 =====
        if (selectedDivinations.includes('mayan')) {
            results.mayan = DivinationModules.Mayan.calculate(birthDate);
        }

        // ===== 数秘術（高度版API使用） =====
        if (selectedDivinations.includes('numerology')) {
            if (apiAvailable) {
                try {
                    results.numerology = await APIClient.calculateNumerology({
                        name: fullName,
                        birthDate: birthDateISO,
                        system: 'pythagorean'
                    });
                    results.numerology.fromAPI = true;
                } catch (e) {
                    console.error('Numerology API error:', e);
                    results.numerology = DivinationModules.Numerology.calculate(birthDate);
                }
            } else {
                results.numerology = DivinationModules.Numerology.calculate(birthDate);
            }
        }

        // ===== 姓名判断 =====
        if (selectedDivinations.includes('seimei')) {
            results.seimei = DivinationModules.Seimei.calculate(familyName, givenName);
        }

        // 結果を表示
        displayResults(fullName, birthDate, results, latitude, longitude);
    }

    /**
     * 結果を表示
     */
    function displayResults(fullName, birthDate, results, latitude, longitude) {
        // マークダウンダウンロード用にデータを保存
        if (typeof saveResultsData === 'function') {
            saveResultsData(fullName, birthDate, results);
        }

        // ユーザーサマリー
        userSummary.innerHTML = `
            <h3>${fullName} 様</h3>
            <p>${birthDate.getFullYear()}年${birthDate.getMonth() + 1}月${birthDate.getDate()}日 
               ${birthDate.getHours()}時${birthDate.getMinutes()}分生まれ</p>
        `;

        // 結果カードを生成
        let html = '';

        // 四柱推命
        if (results.bazi) {
            html += generateBaZiCard(results.bazi);
        }

        // 算命学
        if (results.sanmei) {
            html += generateSanmeiCard(results.sanmei);
        }

        // 九星気学
        if (results.kyusei) {
            html += generateKyuseiCard(results.kyusei);
        }

        // 紫微斗数
        if (results.ziwei) {
            html += generateZiWeiCard(results.ziwei);
        }

        // 宿曜
        if (results.sukuyou) {
            html += generateSukuyouCard(results.sukuyou);
        }

        // 西洋占星術
        if (results.western) {
            html += generateWesternCard(results.western);
        }

        // インド占星術
        if (results.vedic) {
            html += generateVedicCard(results.vedic);
        }

        // マヤ暦
        if (results.mayan) {
            html += generateMayanCard(results.mayan);
        }

        // 数秘術
        if (results.numerology) {
            html += generateNumerologyCard(results.numerology);
        }

        // 姓名判断
        if (results.seimei) {
            html += generateSeimeiCard(results.seimei);
        }

        resultsContainer.innerHTML = html;
        resultsSection.classList.remove('hidden');

        // 結果データを保存（マークダウンダウンロード用）
        if (typeof saveResultsData === 'function') {
            saveResultsData(fullName, birthDate, results);
        }

        // 結果セクションへスクロール
        resultsSection.scrollIntoView({ behavior: 'smooth' });

        // チャートを描画（Canvas要素がDOMに追加された後に実行）
        setTimeout(() => {
            if (typeof DivinationCharts !== 'undefined') {
                const baziAdvanced = results.bazi?.advanced;
                const sanmeiAdvanced = results.sanmei?.advanced;
                const kyuseiAdvanced = results.kyusei?.advanced;

                DivinationCharts.renderAll(baziAdvanced, sanmeiAdvanced, kyuseiAdvanced);
            }
        }, 100);
    }

    // ===== 結果カード生成関数 =====

    function generateBaZiCard(data) {
        const p = data.pillars;

        // 蔵干表示用
        let hiddenStemsHtml = '';
        if (data.hiddenStems) {
            hiddenStemsHtml = `
                <h4 class="subheading">蔵干</h4>
                <table class="result-table">
                    <tr><th>柱</th><th>蔵干</th><th>本気</th></tr>
                    <tr><td>年支（${p.year.branch}）</td><td>${data.hiddenStems.year.allStems.join('・')}</td><td>${data.hiddenStems.year.mainStem}</td></tr>
                    <tr><td>月支（${p.month.branch}）</td><td>${data.hiddenStems.month.allStems.join('・')}</td><td>${data.hiddenStems.month.mainStem}（${data.hiddenStems.month.phase}）</td></tr>
                    <tr><td>日支（${p.day.branch}）</td><td>${data.hiddenStems.day.allStems.join('・')}</td><td>${data.hiddenStems.day.mainStem}</td></tr>
                    <tr><td>時支（${p.hour.branch}）</td><td>${data.hiddenStems.hour.allStems.join('・')}</td><td>${data.hiddenStems.hour.mainStem}</td></tr>
                </table>
            `;
        }

        // 月情報表示用
        let monthInfoHtml = '';
        if (data.monthInfo) {
            monthInfoHtml = `
                <p><span class="highlight">★ 節入り</span>：${data.monthInfo.jieName}（節入り後${data.monthInfo.daysFromJieqi}日目）</p>
            `;
        }

        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">四柱推命</h3>
                </div>
                <div class="result-card-body">
                    <div class="pillars-display">
                        <div class="pillar">
                            <div class="pillar-label">年柱</div>
                            <div class="pillar-value">
                                <span class="pillar-stem">${p.year.stem}</span><span class="pillar-branch">${p.year.branch}</span>
                            </div>
                        </div>
                        <div class="pillar">
                            <div class="pillar-label">月柱</div>
                            <div class="pillar-value">
                                <span class="pillar-stem">${p.month.stem}</span><span class="pillar-branch">${p.month.branch}</span>
                            </div>
                        </div>
                        <div class="pillar">
                            <div class="pillar-label">日柱</div>
                            <div class="pillar-value">
                                <span class="pillar-stem">${p.day.stem}</span><span class="pillar-branch">${p.day.branch}</span>
                            </div>
                        </div>
                        <div class="pillar">
                            <div class="pillar-label">時柱</div>
                            <div class="pillar-value">
                                <span class="pillar-stem">${p.hour.stem}</span><span class="pillar-branch">${p.hour.branch}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="important-box">
                        <p><span class="highlight">★ 日主（日干）</span>：${data.dayMaster}（${data.dayMasterElement || ''}・${data.dayMasterYinYang || ''}）</p>
                        <p><span class="highlight">★ 空亡</span>：${data.voidBranches.join('・')}</p>
                        ${monthInfoHtml}
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
                    
                    ${data.advanced ? `
                    <h4 class="subheading">刑冲会合</h4>
                    <div class="interaction-list">
                        ${data.advanced.interactions.kango.length > 0 ? `<p>★ 干合：${data.advanced.interactions.kango.join('、')}</p>` : ''}
                        ${data.advanced.interactions.sango.length > 0 ? `<p>★ 三合会局：${data.advanced.interactions.sango.join('、')}</p>` : ''}
                        ${data.advanced.interactions.chu.length > 0 ? `<p>★ 対冲：${data.advanced.interactions.chu.join('、')}</p>` : ''}
                        ${data.advanced.interactions.zhihe.length > 0 ? `<p>★ 六合：${data.advanced.interactions.zhihe.join('、')}</p>` : ''}
                        ${data.advanced.interactions.kei.length > 0 ? `<p>★ 刑：${data.advanced.interactions.kei.join('、')}</p>` : ''}
                    </div>
                    
                    <h4 class="subheading">神殺（特殊星）</h4>
                    <table class="result-table">
                        <tr><th>神殺</th><th>成立地支</th></tr>
                        ${Object.entries(data.advanced.specialStars || {}).map(([k, v]) => v.length > 0 ? `<tr><td>${k}</td><td>${v.join('・')}</td></tr>` : '').join('')}
                    </table>
                    
                    <h4 class="subheading">五行バランス</h4>
                    <div class="gogyo-balance">
                        ${Object.entries(data.advanced.gogyoBalance || {}).map(([k, v]) => `<span class="gogyo-item">${k}:${v.toFixed(1)}</span>`).join(' ')}
                    </div>
                    <div class="chart-container">
                        <canvas id="gogyo-radar-canvas" width="320" height="320"></canvas>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    function generateSanmeiCard(data) {
        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">算命学</h3>
                </div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ 天中殺</span>：${data.voidGroupName}</p>
                        ${data.advanced && data.advanced.abnormalGanzhi.length > 0 ?
                `<p><span class="highlight">★ 異常干支</span>：${data.advanced.abnormalGanzhi.join('・')}</p>` : ''}
                    </div>
                    
                    <h4 class="subheading">十大主星</h4>
                    <table class="result-table">
                        <tr><th>位置</th><th>主星</th></tr>
                        ${Object.entries(data.mainStars).map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('')}
                    </table>
                    
                    <h4 class="subheading">十二大従星</h4>
                    <table class="result-table">
                        <tr><th>位置</th><th>従星</th></tr>
                        ${Object.entries(data.subStars).map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('')}
                    </table>
                    
                    ${data.advanced && data.advanced.uchuban ? `
                    <h4 class="subheading">宇宙盤</h4>
                    <div class="uchuban-info">
                        <p>★ 三角形面積：${data.advanced.uchuban.area}</p>
                        <p>★ パターン：${data.advanced.uchuban.patternType}</p>
                        <table class="result-table">
                            <tr><th>柱</th><th>干支</th><th>角度</th></tr>
                            ${data.advanced.uchuban.points.map(p => `<tr><td>${p.label}</td><td>${p.ganzhi}</td><td>${p.angle.toFixed(0)}°</td></tr>`).join('')}
                        </table>
                    </div>
                    <div class="chart-container">
                        <canvas id="uchuban-canvas" width="360" height="360"></canvas>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    function generateKyuseiCard(data) {
        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">九星気学</h3>
                </div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ 本命星</span>：${data.yearStar}</p>
                    </div>
                    
                    <table class="result-table">
                        <tr><th>項目</th><th>結果</th></tr>
                        <tr><td>本命星（年）</td><td>${data.yearStar}</td></tr>
                        <tr><td>月命星</td><td>${data.monthStar}</td></tr>
                        <tr><td>日命星</td><td>${data.dayStar}</td></tr>
                        <tr><td>傾斜宮</td><td>${data.inclination}</td></tr>
                    </table>
                    
                    ${data.advanced ? `
                    <h4 class="subheading">方位盤（日盤）</h4>
                    <div class="direction-board">
                        <table class="result-table">
                            <tr><th>方位</th><th>九星</th></tr>
                            ${Object.entries(data.advanced.boards.day.directions || {}).map(([dir, star]) => {
            const dirNames = { N: '北', NE: '北東', E: '東', SE: '南東', S: '南', SW: '南西', W: '西', NW: '北西' };
            const starNames = ['', '一白水星', '二黒土星', '三碧木星', '四緑木星', '五黄土星', '六白金星', '七赤金星', '八白土星', '九紫火星'];
            return `<tr><td>${dirNames[dir] || dir}</td><td>${starNames[star] || star}</td></tr>`;
        }).join('')}
                        </table>
                    </div>
                    
                    <h4 class="subheading">吉凶方位</h4>
                    <div class="direction-judgment">
                        ${data.advanced.judgment.gooSatsu.length > 0 ? `<p class="bad-direction">★ 五黄殺：${data.advanced.judgment.gooSatsu.map(d => ({ N: '北', NE: '北東', E: '東', SE: '南東', S: '南', SW: '南西', W: '西', NW: '北西' }[d])).join('・')}</p>` : ''}
                        ${data.advanced.judgment.ankenSatsu.length > 0 ? `<p class="bad-direction">★ 暗剣殺：${data.advanced.judgment.ankenSatsu.map(d => ({ N: '北', NE: '北東', E: '東', SE: '南東', S: '南', SW: '南西', W: '西', NW: '北西' }[d])).join('・')}</p>` : ''}
                        ${data.advanced.judgment.luckyDirs.length > 0 ? `<p class="good-direction">★ 吉方位：${data.advanced.judgment.luckyDirs.map(d => ({ N: '北', NE: '北東', E: '東', SE: '南東', S: '南', SW: '南西', W: '西', NW: '北西' }[d])).join('・')}</p>` : ''}
                    </div>
                    
                    <h4 class="subheading">地図連携情報</h4>
                    <div class="map-info">
                        <p>★ 磁気偏角：${data.advanced.mapOverlay.magneticDeclination}°（${data.advanced.mapOverlay.magneticDeclination < 0 ? '西偏' : '東偏'}）</p>
                    </div>
                    <div class="chart-container">
                        <canvas id="direction-board-canvas" width="360" height="360"></canvas>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    function generateZiWeiCard(data) {
        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">紫微斗数</h3>
                </div>
                <div class="result-card-body">
                    <p>旧暦生年月日：${data.lunarDate}</p>
                    
                    <div class="important-box">
                        <p><span class="highlight">★ 命宮</span>：${data.mingPalace}宮</p>
                        <p><span class="highlight">★ 身宮</span>：${data.bodyPalace}宮</p>
                    </div>
                </div>
            </div>
        `;
    }

    function generateSukuyouCard(data) {
        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">宿曜占星術</h3>
                </div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ 本命宿</span>：${data.natalMansion}（第${data.mansionNumber}宿）</p>
                        <p><span class="highlight">★ 属性</span>：${data.element}</p>
                    </div>
                </div>
            </div>
        `;
    }

    function generateWesternCard(data) {
        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">西洋占星術</h3>
                </div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ 太陽星座</span>：${data.sunSign || ''}</p>
                        <p><span class="highlight">★ 月星座</span>：${data.moonSign || ''}</p>
                        <p><span class="highlight">★ ASC（上昇宮）</span>：${data.ascendant || ''}</p>
                    </div>
                    
                    <h4 class="subheading">惑星位置</h4>
                    <table class="result-table">
                        <tr><th>惑星</th><th>星座</th></tr>
                        ${(data.planets || []).map(p => `
                            <tr>
                                <td>${p.name}${p.retrograde ? ' ℞' : ''}</td>
                                <td>${p.sign || p.signEn || ''}</td>
                            </tr>
                        `).join('')}
                    </table>
                    
                    ${data.houses ? `
                    <h4 class="subheading">ハウス</h4>
                    <table class="result-table">
                        <tr><th>ハウス</th><th>星座</th></tr>
                        ${data.houses.slice(0, 6).map(h => `
                            <tr><td>第${h.house}ハウス</td><td>${h.sign}</td></tr>
                        `).join('')}
                    </table>
                    ` : ''}
                    
                    ${data.aspects && data.aspects.length > 0 ? `
                    <h4 class="subheading">アスペクト</h4>
                    <table class="result-table">
                        <tr><th>天体組み合わせ</th><th>角度</th><th>オーブ</th><th>状態</th></tr>
                        ${data.aspects.map(a => `
                            <tr>
                                <td>${a.planet1} - ${a.planet2}</td>
                                <td>${a.aspect_type}</td>
                                <td>${a.orb.toFixed(2)}°</td>
                                <td>${a.applying ? '接近(A)' : '分離(S)'}</td>
                            </tr>
                        `).join('')}
                    </table>
                    ` : ''}
                </div>
            </div>
        `;
    }

    function generateZiWeiCard(data) {
        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">紫微斗数</h3>
                </div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ 旧暦</span>：${data.lunarDate || ''}</p>
                        <p><span class="highlight">★ 時辰</span>：${data.hourBranch || ''}の刻</p>
                        <p><span class="highlight">★ 命宮</span>：${data.lifePalace || ''}</p>
                        <p><span class="highlight">★ 五行局</span>：${data.bureau || ''}</p>
                        <p><span class="highlight">★ 紫微星</span>：${data.ziweiPosition || ''}宮</p>
                    </div>
                    
                    <h4 class="subheading">十二宮配置</h4>
                    <div class="palace-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; font-size: 0.75rem;">
                        ${(data.palaces || []).slice(0, 12).map(p => `
                            <div style="border: 1px solid #ddd; padding: 4px; text-align: center;">
                                <div style="font-weight: bold;">${p.name}</div>
                                <div>${p.branch}</div>
                                <div style="color: #e74c3c;">${(p.stars || []).join(' ')}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    function generateSukuyouCard(data) {
        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">宿曜占星術</h3>
                </div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ 本命宿</span>：${data.mansion || ''}</p>
                        <p><span class="highlight">★ 七曜</span>：${data.weekday || ''}</p>
                        <p><span class="highlight">★ 性格グループ</span>：${data.group || ''}</p>
                        ${data.lunarDate ? `<p><span class="highlight">★ 旧暦日</span>：${data.lunarDate}</p>` : ''}
                    </div>
                    
                    <h4 class="subheading">相性マンダラ（抜粋）</h4>
                    <table class="result-table">
                        <tr><th>宿</th><th>相性</th></tr>
                        ${(data.mandala || []).slice(0, 8).map(m => `
                            <tr><td>${m.shuku}</td><td>${m.relation}</td></tr>
                        `).join('')}
                    </table>
                </div>
            </div>
        `;
    }

    function generateVedicCard(data) {
        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">インド占星術（ジョーティシュ）</h3>
                </div>
                <div class="result-card-body">
                    <p>アヤナムサ：${data.ayanamsa || 'Lahiri'}</p>
                    
                    <div class="important-box">
                        <p><span class="highlight">★ 太陽星座（ラシ）</span>：${data.sunSign || ''}</p>
                        <p><span class="highlight">★ ラグナ</span>：${data.lagna || ''}</p>
                        <p><span class="highlight">★ 月のナクシャトラ</span>：${data.moonNakshatra || ''}</p>
                        <p><span class="highlight">★ パダ</span>：${data.nakshatraPada || ''}</p>
                    </div>
                    
                    ${data.dashas && data.dashas.length > 0 ? `
                    <h4 class="subheading">ヴィムショッタリ・ダシャー</h4>
                    <table class="result-table">
                        <tr><th>支配星</th><th>期間</th></tr>
                        ${data.dashas.map(d => `
                            <tr><td>${d.lord}</td><td>${d.start}〜${d.end}年（${d.years}年間）</td></tr>
                        `).join('')}
                    </table>
                    ` : ''}
                </div>
            </div>
        `;
    }


    function generateMayanCard(data) {
        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">マヤ暦</h3>
                </div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ KIN</span>：${data.kin}</p>
                        <p><span class="highlight">★ 太陽の紋章</span>：${data.solarSeal}</p>
                        <p><span class="highlight">★ 銀河の音</span>：${data.galacticTone}（${data.galacticToneName}）</p>
                    </div>
                    
                    <table class="result-table">
                        <tr><th>項目</th><th>結果</th></tr>
                        <tr><td>ウェイブスペル</td><td>${data.wavespell}</td></tr>
                        <tr><td>ガイドキン</td><td>${data.guide}</td></tr>
                    </table>
                </div>
            </div>
        `;
    }

    function generateNumerologyCard(data) {
        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">数秘術</h3>
                </div>
                <div class="result-card-body">
                    <div class="important-box">
                        <p><span class="highlight">★ ライフパス数</span>：${data.lifePath}</p>
                        <p>意味：${data.lifePathMeaning}</p>
                    </div>
                    
                    <table class="result-table">
                        <tr><th>項目</th><th>数</th><th>意味</th></tr>
                        <tr><td>ライフパス数</td><td>${data.lifePath}</td><td>${data.lifePathMeaning}</td></tr>
                        <tr><td>バースデー数</td><td>${data.birthdayNumber}</td><td>${data.birthdayMeaning}</td></tr>
                    </table>
                </div>
            </div>
        `;
    }

    function generateSeimeiCard(data) {
        return `
            <div class="result-card">
                <div class="result-card-header">
                    <h3 class="result-card-title">姓名判断</h3>
                </div>
                <div class="result-card-body">
                    <p>姓：${data.familyName}（画数：${data.strokes.family.join(', ')}）</p>
                    <p>名：${data.givenName}（画数：${data.strokes.given.join(', ')}）</p>
                    
                    <table class="result-table">
                        <tr><th>格</th><th>画数</th><th>意味</th></tr>
                        <tr><td>天格（祖運）</td><td>${data.tenkaku}</td><td>先祖代々の運勢</td></tr>
                        <tr><td>人格（主運）</td><td>${data.jinkaku}</td><td>性格・才能の中心</td></tr>
                        <tr><td>地格（初運）</td><td>${data.chikaku}</td><td>幼少期〜青年期</td></tr>
                        <tr><td>外格（副運）</td><td>${data.gaikaku}</td><td>対人関係・社会運</td></tr>
                        <tr><td>総格（総運）</td><td>${data.soukaku}</td><td>人生全体の運勢</td></tr>
                    </table>
                </div>
            </div>
        `;
    }
});
