/**
 * 統合占い計算エンジン - マークダウンダウンロード機能
 */

// 既存のapp.jsの末尾に追加するコード

// マークダウンダウンロード機能を追加
document.addEventListener('DOMContentLoaded', () => {
    const btnDownloadMd = document.getElementById('btn-download-md');

    if (btnDownloadMd) {
        btnDownloadMd.addEventListener('click', () => {
            downloadResultsAsMarkdown();
        });
    }
});

/**
 * グローバル変数として結果データを保存
 */
let currentResultsData = null;
let currentUserData = null;

/**
 * 結果データを保存する関数（app.jsのdisplayResults関数内で呼び出す）
 */
function saveResultsData(fullName, birthDate, results) {
    currentUserData = { fullName, birthDate };
    currentResultsData = results;
}

/**
 * ヘルパー関数: オブジェクトから値を安全に取得
 * camelCase, snake_case の両方のキーを試行
 * @param {Object} obj - 対象オブジェクト
 * @param {string[]} keys - キーの配列（優先順）
 * @param {any} defaultVal - デフォルト値
 */
function val(obj, keys, defaultVal = '?') {
    if (!obj) return defaultVal;
    if (typeof keys === 'string') keys = [keys];

    for (const key of keys) {
        if (obj[key] !== undefined && obj[key] !== null) {
            return obj[key];
        }
    }
    return defaultVal;
}

/**
 * 結果をマークダウン形式でダウンロード
 */
function downloadResultsAsMarkdown() {
    if (!currentResultsData || !currentUserData) {
        alert('鑑定結果がありません。先に占いを計算してください。');
        return;
    }

    const markdown = generateMarkdown(currentUserData, currentResultsData);

    // Blobを作成
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });

    // ダウンロードリンクを作成
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;

    // ファイル名を生成（日時付き）
    const now = new Date();
    const timestamp = now.toISOString().split('T')[0].replace(/-/g, '');
    const userName = currentUserData.fullName.replace(/\s/g, '');
    link.download = `鑑定結果_${userName}_${timestamp}.md`;

    // ダウンロードを実行
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * マークダウンを生成
 */
function generateMarkdown(userData, results) {
    const { fullName, birthDate } = userData;

    let md = `# 占い鑑定結果\n\n`;
    md += `## 基本情報\n\n`;
    md += `- **お名前**: ${fullName}\n`;
    md += `- **生年月日**: ${birthDate.getFullYear()}年${birthDate.getMonth() + 1}月${birthDate.getDate()}日\n`;
    md += `- **出生時刻**: ${birthDate.getHours()}時${birthDate.getMinutes()}分\n`;
    md += `- **鑑定日時**: ${new Date().toLocaleString('ja-JP')}\n\n`;

    md += `---\n\n`;

    // 四柱推命
    if (results.bazi) {
        md += generateBaZiMarkdown(results.bazi);
    }

    // 算命学
    if (results.sanmei) {
        md += generateSanmeiMarkdown(results.sanmei);
    }

    // 九星気学
    if (results.kyusei) {
        md += generateKyuseiMarkdown(results.kyusei);
    }

    // 紫微斗数
    if (results.ziwei) {
        md += generateZiWeiMarkdown(results.ziwei);
    }

    // 宿曜
    if (results.sukuyou) {
        md += generateSukuyouMarkdown(results.sukuyou);
    }

    // 西洋占星術
    if (results.western) {
        md += generateWesternMarkdown(results.western);
    }

    // インド占星術
    if (results.vedic) {
        md += generateVedicMarkdown(results.vedic);
    }

    // マヤ暦
    if (results.mayan) {
        md += generateMayanMarkdown(results.mayan);
    }

    // 数秘術
    if (results.numerology) {
        md += generateNumerologyMarkdown(results.numerology);
    }

    // 姓名判断
    if (results.seimei) {
        // 名前データを注入（JS版は内部に持つがAPI版は持たないため）
        if (!results.seimei.familyName) {
            const [fam, given] = fullName.split(' ');
            results.seimei.familyName = fam;
            results.seimei.givenName = given;
        }
        md += generateSeimeiMarkdown(results.seimei);
    }

    md += `---\n\n`;
    md += `*この鑑定結果は統合占い計算エンジンにより生成されました。*\n`;
    md += `*結果は参考情報としてご活用ください。*\n`;

    return md;
}

// === マークダウン生成関数（各占術） ===

function generateBaZiMarkdown(data) {
    // API版: four_pillars, JS版: pillars
    const p = val(data, ['pillars', 'four_pillars'], null);
    if (!p) return `## 四柱推命\n\nデータがありません\n\n`;

    let md = `## 四柱推命\n\n`;

    // 柱データの正規化
    // JS版: { year: { stem: '甲', branch: '子' } }
    // API版: { year: { heavenly_stem: '甲', earthly_branch: '子' } }
    const getPillar = (pillarName) => {
        const pillar = p[pillarName];
        if (!pillar) return { stem: '?', branch: '?' };
        const stem = val(pillar, ['stem', 'heavenly_stem']);
        const branch = val(pillar, ['branch', 'earthly_branch']);
        return { stem, branch };
    };

    const yearP = getPillar('year');
    const monthP = getPillar('month');
    const dayP = getPillar('day');
    const hourP = getPillar('hour');

    md += `### 四柱\n\n`;
    md += `| 柱 | 天干 | 地支 |\n`;
    md += `|---|---|---|\n`;
    md += `| 年柱 | ${yearP.stem} | ${yearP.branch} |\n`;
    md += `| 月柱 | ${monthP.stem} | ${monthP.branch} |\n`;
    md += `| 日柱 | ${dayP.stem} | ${dayP.branch} |\n`;
    md += `| 時柱 | ${hourP.stem} | ${hourP.branch} |\n\n`;

    const dayMaster = val(data, ['dayMaster', 'day_master']);
    const dayMasterElement = val(data, ['dayMasterElement']); // API版にはないかも
    const dayMasterYinYang = val(data, ['dayMasterYinYang']); // API版にはないかも

    md += `- **日主（日干）**: ${dayMaster}`;
    if (dayMasterElement && dayMasterElement !== '?') md += `（${dayMasterElement}`;
    if (dayMasterYinYang && dayMasterYinYang !== '?') md += `・${dayMasterYinYang}`;
    if (dayMasterElement && dayMasterElement !== '?') md += `）`;
    md += `\n`;

    // 空亡
    // API: void_branches (List[str]), JS: voidBranches (Array)
    const voidBranches = val(data, ['voidBranches', 'void_branches'], []);
    if (Array.isArray(voidBranches) && voidBranches.length > 0) {
        md += `- **空亡**: ${voidBranches.join('・')}\n\n`;
    }

    const monthInfo = val(data, ['monthInfo', 'month_info']);
    if (monthInfo) {
        const jieName = val(monthInfo, ['jieName', 'jie_name']);
        const daysFromJieqi = val(monthInfo, ['daysFromJieqi', 'days_from_jie']);
        if (jieName && jieName !== '?') {
            md += `- **節入り**: ${jieName}${daysFromJieqi !== '?' ? `（節入り後${typeof daysFromJieqi === 'number' ? daysFromJieqi.toFixed(1) : daysFromJieqi}日目）` : ''}\n\n`;
        }
    }

    // 蔵干
    // API: hidden_stems (ないかも?), JS: hiddenStems
    const hiddenStems = val(data, ['hiddenStems', 'hidden_stems']);
    if (hiddenStems) {
        md += `### 蔵干\n\n`;
        md += `| 柱 | 蔵干 | 本気 |\n`;
        md += `|---|---|---|\n`;

        const formatHS = (hsData, branch) => {
            if (!hsData) return `| ? | ? | ? |`;
            // JS: allStems, mainStem
            // API版に合わせるなら調整必要だが現状JS版のみ対応
            const all = val(hsData, ['allStems', 'all_stems'], []).join('・');
            const main = val(hsData, ['mainStem', 'main_stem']);
            const phase = val(hsData, ['phase'], '');
            return `| ${branch} | ${all} | ${main}${phase ? `（${phase}）` : ''} |`;
        };

        if (hiddenStems.year) md += formatHS(hiddenStems.year, `年支（${yearP.branch}）`) + '\n';
        if (hiddenStems.month) md += formatHS(hiddenStems.month, `月支（${monthP.branch}）`) + '\n';
        if (hiddenStems.day) md += formatHS(hiddenStems.day, `日支（${dayP.branch}）`) + '\n';
        if (hiddenStems.hour) md += formatHS(hiddenStems.hour, `時支（${hourP.branch}）`) + '\n';
        md += `\n`;
    }

    // 通変星
    const tenGods = val(data, ['tenGods', 'ten_gods']);
    if (tenGods && Object.keys(tenGods).length > 0) {
        md += `### 通変星\n\n`;
        md += `| 位置 | 通変星 |\n`;
        md += `|---|---|\n`;
        for (const [k, v] of Object.entries(tenGods)) {
            md += `| ${k} | ${v} |\n`;
        }
        md += `\n`;
    }

    // 十二運
    const twelveStages = val(data, ['twelveStages', 'twelve_stages']);
    if (twelveStages && Object.keys(twelveStages).length > 0) {
        md += `### 十二運\n\n`;
        md += `| 位置 | 十二運 |\n`;
        md += `|---|---|\n`;
        for (const [k, v] of Object.entries(twelveStages)) {
            md += `| ${k} | ${v} |\n`;
        }
        md += `\n`;
    }

    // パフォーマンス（五行バランス）
    if (data.advanced) {
        if (data.advanced.gogyoBalance) {
            md += `### 五行バランス（数値）\n\n`;
            md += `| 五行 | 木 | 火 | 土 | 金 | 水 |\n`;
            md += `|---|---|---|---|---|---|\n`;
            const b = data.advanced.gogyoBalance;
            const fmt = (n) => (typeof n === 'number') ? n.toFixed(1) : n;
            md += `| 数値 | ${fmt(b['木'] || 0)} | ${fmt(b['火'] || 0)} | ${fmt(b['土'] || 0)} | ${fmt(b['金'] || 0)} | ${fmt(b['水'] || 0)} |\n\n`;
        }

        // 神殺
        if (data.advanced.specialStars && Object.keys(data.advanced.specialStars).length > 0) {
            md += `### 神殺・特殊星\n\n`;
            md += `| 星名 | 地支 |\n`;
            md += `|---|---|\n`;
            for (const [k, v] of Object.entries(data.advanced.specialStars)) {
                md += `| ${k} | ${v.join('・')} |\n`;
            }
            md += `\n`;
        }

        // 位相法
        let interactions = [];
        if (data.advanced.interactions) {
            const i = data.advanced.interactions;
            interactions = [
                ...(i.kango || []), ...(i.zhihe || []), ...(i.sango || []),
                ...(i.chu || []), ...(i.kei || []), ...(i.gai || []), ...(i.ha || [])
            ];
        }

        if (interactions.length > 0) {
            md += `### 位相法（刑冲会合）\n\n`;
            for (const s of interactions) {
                md += `- ${s}\n`;
            }
            md += `\n`;
        }
    }

    return md;
}

function generateSanmeiMarkdown(data) {
    let md = `## 算命学\n\n`;

    const voidGroupName = val(data, ['voidGroupName', 'void_group_name'], '不明');
    md += `- **天中殺**: ${voidGroupName}\n`;

    const voidBranches = val(data, ['voidBranches', 'void_branches'], []);
    if (Array.isArray(voidBranches) && voidBranches.length > 0) {
        md += `- **天中殺支**: ${voidBranches.join('・')}\n`;
    }
    md += `\n`;

    const mainStars = val(data, ['mainStars', 'main_stars']);
    if (mainStars && Object.keys(mainStars).length > 0) {
        md += `### 十大主星\n\n`;
        md += `| 位置 | 主星 |\n`;
        md += `|---|---|\n`;
        for (const [k, v] of Object.entries(mainStars)) {
            md += `| ${k} | ${v} |\n`;
        }
        md += `\n`;
    }

    const subStars = val(data, ['subStars', 'sub_stars']);
    if (subStars && Object.keys(subStars).length > 0) {
        md += `### 十二大従星\n\n`;
        md += `| 位置 | 従星 |\n`;
        md += `|---|---|\n`;
        for (const [k, v] of Object.entries(subStars)) {
            md += `| ${k} | ${v} |\n`;
        }
        md += `\n`;
    }

    // 宇宙盤（行動領域）
    if (data.advanced && data.advanced.area !== undefined) {
        md += `### 宇宙盤（行動領域）\n\n`;
        md += `- **面積**: ${data.advanced.area.toFixed(2)}\n`;
        md += `- **領域**: ${data.advanced.patternName || '不明'}\n`;
        md += `\n`;
    }

    return md;
}

function generateKyuseiMarkdown(data) {
    let md = `## 九星気学\n\n`;

    md += `- **本命星**: ${val(data, ['yearStar', 'year_star'])}\n`;
    md += `- **月命星**: ${val(data, ['monthStar', 'month_star'])}\n`;
    md += `- **日命星**: ${val(data, ['dayStar', 'day_star'])}\n`;
    const inclination = val(data, ['inclination']);
    if (inclination && inclination !== '?') {
        md += `- **傾斜宮**: ${inclination}\n`;
    }
    md += `\n`;

    return md;
}

function generateZiWeiMarkdown(data) {
    let md = `## 紫微斗数\n\n`;

    // 基本情報（DivinationAdapterで正規化されたキーを使用）
    const bureau = val(data, ['bureau', 'bureau_name']) || '不明';
    const mingPalace = val(data, ['mingPalace', 'life_palace', 'ming_palace', 'lifePalace']) || '?';
    const bodyPalace = val(data, ['bodyPalace', 'body_palace', 'bodyPalace']) || '?';
    const ziweiPos = val(data, ['ziweiPosition', 'ziwei_position']) || '?';
    const lunarDate = val(data, ['lunarDate', 'lunar_date']) || '?';
    const hourBranch = val(data, ['hourBranch', 'hour_branch']) || '?';

    md += `- **五行局**: ${bureau}\n`;
    md += `- **命宮**: ${mingPalace}\n`;
    md += `- **身宮**: ${bodyPalace}\n`;
    md += `- **紫微星**: ${ziweiPos}宮\n`;
    md += `- **旧暦**: ${lunarDate}\n`;
    md += `- **時辰**: ${hourBranch}\n\n`;

    md += `### 十二宮\n\n`;

    // 宮データの処理
    const palaces = val(data, ['palaces'], []);

    if (palaces.length > 0) {
        // マークダウンのリスト形式で出力
        palaces.forEach(p => {
            const name = p.name || p.palace_type || '?';
            const branch = p.branch || '';

            let stars = [];
            if (p.stars) {
                stars = p.stars;
            } else if (p.major_stars) {
                // API生データの場合のフォールバック
                stars = p.major_stars.map(s => typeof s === 'string' ? { name: s, type: 'major' } : { ...s, type: 'major' });
                if (p.minor_stars) stars = stars.concat(p.minor_stars.map(s => typeof s === 'string' ? { name: s, type: 'minor' } : { ...s, type: 'minor' }));
                if (p.bad_stars) stars = stars.concat(p.bad_stars.map(s => typeof s === 'string' ? { name: s, type: 'bad' } : { ...s, type: 'bad' }));
            }

            // 星の文字列生成
            const starStrs = stars.map(s => {
                const sName = s.name || s;
                const brightness = s.brightness ? `(${s.brightness})` : '';
                return `${sName}${brightness}`;
            }).join(', ');

            md += `- **${name}** (${branch}): ${starStrs}\n`;
        });
    } else {
        md += `データなし\n`;
    }

    md += `\n`;
    return md;
}

function generateSukuyouMarkdown(data) {
    let md = `## 宿曜占星術\n\n`;

    const mansion = val(data, ['mansion', 'natalMansion', 'natal_mansion']);

    let mansionNum = '?';
    const idx = val(data, ['mansionIndex', 'mansion_index'], null);
    const num = val(data, ['mansionNumber', 'mansion_number'], null);

    if (idx !== null) {
        mansionNum = parseInt(idx) + 1;
    } else if (num !== null) {
        mansionNum = parseInt(num);
    }

    md += `- **本命宿**: ${mansion}（第${mansionNum}宿）\n`;

    // 七曜/属性
    const weekday = val(data, ['weekday']); // JS版
    const dayElement = val(data, ['dayElement', 'day_element']); // API版
    if (weekday && weekday !== '?') {
        md += `- **七曜**: ${weekday}\n`;
    } else if (dayElement && dayElement !== '?') {
        md += `- **七曜属性**: ${dayElement}\n`;
    }

    const group = val(data, ['group']);
    if (group && group !== '?') {
        md += `- **性格グループ**: ${group}\n`;
    }

    const element = val(data, ['element']);
    if (element && element !== '?') {
        md += `- **属性**: ${element}\n`;
    }

    const lunarDate = val(data, ['lunarDate', 'lunar_date']);
    if (lunarDate && lunarDate !== '?') {
        md += `- **旧暦日**: ${lunarDate}\n`;
    }
    md += `\n`;

    // 相性マンダラ（JS版のみ）
    const mandala = val(data, ['mandala']);
    if (mandala && Array.isArray(mandala) && mandala.length > 0) {
        md += `### 相性マンダラ（抜粋）\n\n`;
        md += `| 宿 | 相性 |\n`;
        md += `|---|---|\n`;
        for (const m of mandala.slice(0, 8)) {
            md += `| ${m.shuku} | ${m.relation} |\n`;
        }
        md += `\n`;
    }

    return md;
}

function generateWesternMarkdown(data) {
    let md = `## 西洋占星術\n\n`;

    // アセンダント
    const asc = val(data, ['ascendant']);
    if (asc !== '?') {
        if (typeof asc === 'number') {
            md += `- **ASC（上昇宮）**: ${asc.toFixed(2)}°\n`;
        } else if (typeof asc === 'object') {
            const sign = val(asc, 'sign');
            const degree = val(asc, 'degree');
            md += `- **ASC（上昇宮）**: ${sign} ${typeof degree === 'number' ? degree.toFixed(1) + '°' : ''}\n`;
        } else {
            md += `- **ASC（上昇宮）**: ${asc}\n`;
        }
    }

    // MC
    const mc = val(data, ['midheaven']);
    if (mc !== '?') {
        if (typeof mc === 'number') {
            md += `- **MC（天頂）**: ${mc.toFixed(2)}°\n\n`;
        } else if (typeof mc === 'object') {
            const sign = val(mc, 'sign');
            const degree = val(mc, 'degree');
            md += `- **MC（天頂）**: ${sign} ${typeof degree === 'number' ? degree.toFixed(1) + '°' : ''}\n\n`;
        } else {
            md += `- **MC（天頂）**: ${mc}\n\n`;
        }
    } else {
        md += `\n`;
    }

    // 惑星位置
    const planets = val(data, ['planets'], []);

    if (Array.isArray(planets) && planets.length > 0) {
        md += `### 惑星位置\n\n`;
        md += `| 惑星 | 星座 | 度数 | 逆行 |\n`;
        md += `|---|---|---|---|\n`;

        for (const p of planets) {
            // API: {planet: 'Sun', longitude: ..., sign: 'Leo', ...}
            // JS: {name: '太陽', sign: ..., degree: ...}
            const name = val(p, ['name', 'planet']);
            const sign = val(p, ['sign', 'signEn']);
            let degree = '-';

            // 度数計算
            const deg = val(p, ['degree', 'degree_in_sign']);
            const lon = val(p, ['longitude']);

            if (deg !== '?') degree = deg.toFixed(2) + '°';
            else if (lon !== '?') degree = (lon % 30).toFixed(2) + '°';

            const retro = val(p, ['retrograde']) ? 'Yes' : '-';

            md += `| ${name} | ${sign} | ${degree} | ${retro} |\n`;
        }
        md += `\n`;
    }

    // アスペクト
    const aspects = val(data, ['aspects'], []);
    if (Array.isArray(aspects) && aspects.length > 0) {
        md += `### アスペクト\n\n`;
        md += `| 組み合わせ | 角度 | オーブ | 状態 |\n`;
        md += `|---|---|---|---|\n`;

        for (const a of aspects) {
            const p1 = val(a, ['planet1']);
            const p2 = val(a, ['planet2']);
            const type = val(a, ['aspect', 'aspect_type']);
            const orb = val(a, ['orb']);
            const applying = val(a, ['applying']);

            const state = applying === true ? '接近(A)' : (applying === false ? '分離(S)' : '-');
            const orbStr = (typeof orb === 'number') ? orb.toFixed(2) + '°' : orb;

            md += `| ${p1} - ${p2} | ${type} | ${orbStr} | ${state} |\n`;
        }
        md += `\n`;
    }

    return md;
}

function generateVedicMarkdown(data) {
    let md = `## インド占星術（ヴェーダ）\n\n`;

    const ayanamsa = val(data, ['ayanamsa']);
    md += `- **アヤナムサ**: ${ayanamsa}\n`;

    // API: nakshatra, JS: moonNakshatra
    const nakshatra = val(data, ['nakshatra', 'moonNakshatra', 'moon_nakshatra']);
    md += `- **月のナクシャトラ**: ${nakshatra}\n`;

    // API: nakshatra_lord, JS: nakshatraLord
    const lord = val(data, ['nakshatraLord', 'nakshatra_lord']);
    md += `- **ナクシャトラ支配星**: ${lord}\n`;

    // JS: sunSign, APIには単純なフィールドがないため省略、またはplanetsから探す
    const sunSign = val(data, ['sunSign']);
    if (sunSign && sunSign !== '?') {
        md += `- **太陽星座**: ${sunSign}\n`;
    }

    const lagna = val(data, ['lagna']);
    if (lagna && lagna !== '?') {
        md += `- **ラグナ**: ${lagna}\n`;
    }

    md += `\n`;

    // ダシャー
    const dashas = val(data, ['dashas', 'dasha']);
    // API: { Vimshottari: { current: {...}, sequence: [...] } } or JS: [{lord:..., start:..., ...}]

    if (Array.isArray(dashas) && dashas.length > 0) {
        md += `### ヴィムショッタリ・ダシャー\n\n`;
        md += `| 支配星 | 期間 |\n`;
        md += `|---|---|\n`;
        for (const d of dashas) {
            md += `| ${d.lord} | ${d.start}〜${d.end}年（${d.years}年間） |\n`;
        }
        md += `\n`;
    } else if (dashas && typeof dashas === 'object') {
        // API版など
        md += `### ダシャー情報\n\n`;
        // API構造に合わせて展開（ここでは簡易表示）
        md += `詳細データあり（構造化未対応）\n\n`;
    }

    return md;
}

function generateMayanMarkdown(data) {
    let md = `## マヤ暦\n\n`;

    md += `- **KIN**: ${val(data, ['kin', 'kin_number'])}\n`;
    md += `- **太陽の紋章**: ${val(data, ['solarSeal', 'solar_seal'])}\n`;

    const tone = val(data, ['galacticTone', 'galactic_tone']);
    const toneName = val(data, ['galacticToneName', 'galactic_tone_name']);
    md += `- **銀河の音**: ${tone}${toneName !== '?' ? `（${toneName}）` : ''}\n`;

    const wave = val(data, ['wavespell']);
    if (wave && wave !== '?') {
        md += `- **ウェイブスペル**: ${wave}\n`;
    }

    const guide = val(data, ['guide']);
    if (guide && guide !== '?') {
        md += `- **ガイドキン**: ${guide}\n`;
    }
    md += `\n`;

    return md;
}

function generateNumerologyMarkdown(data) {
    let md = `## 数秘術\n\n`;

    md += `- **ライフパス数**: ${val(data, ['lifePath', 'life_path', 'life_path_number'])}\n`;

    const lpMeaning = val(data, ['lifePathMeaning', 'life_path_meaning']);
    if (lpMeaning && lpMeaning !== '?') {
        md += `  - 意味: ${lpMeaning}\n`;
    }

    md += `- **バースデー数**: ${val(data, ['birthdayNumber', 'birthday_number'])}\n`;

    const bdMeaning = val(data, ['birthdayMeaning', 'birthday_meaning']);
    if (bdMeaning && bdMeaning !== '?') {
        md += `  - 意味: ${bdMeaning}\n`;
    }

    // API版独自フィールド：expression_numberなど
    const expNum = val(data, ['expressionNumber', 'expression_number']);
    if (expNum && expNum !== '?') {
        md += `- **ディスティニー（運命数）**: ${expNum}\n`;
    }

    const soulNum = val(data, ['soulNumber', 'soul_urge']);
    if (soulNum && soulNum !== '?') {
        md += `- **ソウルナンバー**: ${soulNum}\n`;
    }

    md += `\n`;

    return md;
}

function generateSeimeiMarkdown(data) {
    let md = `## 姓名判断\n\n`;

    const familyName = val(data, ['familyName', 'family_name']);
    const givenName = val(data, ['givenName', 'given_name']);

    // strokes: { family: [x, y], given: [z, w] } (JS) vs strokes: { '安': 6, ... } (API)
    const strokes = val(data, ['strokes']);
    let familyStrokesStr = '?';
    let givenStrokesStr = '?';

    if (strokes && strokes.family && Array.isArray(strokes.family)) {
        familyStrokesStr = strokes.family.join(', ');
    }
    if (strokes && strokes.given && Array.isArray(strokes.given)) {
        givenStrokesStr = strokes.given.join(', ');
    }
    // API版の場合、文字ごとの画数は辞書で返ってくるため、名前から逆引きする必要があるが
    // ここでは簡略化

    md += `- **姓**: ${familyName}（画数: ${familyStrokesStr}）\n`;
    md += `- **名**: ${givenName}（画数: ${givenStrokesStr}）\n\n`;

    md += `### 五格\n\n`;
    md += `| 格 | 画数 | 意味 |\n`;
    md += `|---|---|---|\n`;
    md += `| 天格（祖運） | ${val(data, ['tenkaku'])} | 先祖代々の運勢 |\n`;
    md += `| 人格（主運） | ${val(data, ['jinkaku'])} | 性格・才能の中心 |\n`;
    md += `| 地格（初運） | ${val(data, ['chikaku'])} | 幼少期〜青年期 |\n`;
    md += `| 外格（副運） | ${val(data, ['gaikaku'])} | 対人関係・社会運 |\n`;
    md += `| 総格（総運） | ${val(data, ['soukaku'])} | 人生全体の運勢 |\n\n`;

    return md;
}
