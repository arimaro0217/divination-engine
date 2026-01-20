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
        md += generateSeimeiMarkdown(results.seimei);
    }

    md += `---\n\n`;
    md += `*この鑑定結果は統合占い計算エンジンにより生成されました。*\n`;
    md += `*結果は参考情報としてご活用ください。*\n`;

    return md;
}

// === マークダウン生成関数（各占術） ===

function generateBaZiMarkdown(data) {
    const p = data.pillars;
    let md = `## 四柱推命\n\n`;

    md += `### 四柱\n\n`;
    md += `| 柱 | 天干 | 地支 |\n`;
    md += `|---|---|---|\n`;
    md += `| 年柱 | ${p.year.stem} | ${p.year.branch} |\n`;
    md += `| 月柱 | ${p.month.stem} | ${p.month.branch} |\n`;
    md += `| 日柱 | ${p.day.stem} | ${p.day.branch} |\n`;
    md += `| 時柱 | ${p.hour.stem} | ${p.hour.branch} |\n\n`;

    md += `- **日主（日干）**: ${data.dayMaster}`;
    if (data.dayMasterElement) md += `（${data.dayMasterElement}`;
    if (data.dayMasterYinYang) md += `・${data.dayMasterYinYang}`;
    if (data.dayMasterElement) md += `）`;
    md += `\n`;
    md += `- **空亡**: ${data.voidBranches.join('・')}\n\n`;

    if (data.monthInfo) {
        md += `- **節入り**: ${data.monthInfo.jieName}（節入り後${data.monthInfo.daysFromJieqi}日目）\n\n`;
    }

    // 蔵干
    if (data.hiddenStems) {
        md += `### 蔵干\n\n`;
        md += `| 柱 | 蔵干 | 本気 |\n`;
        md += `|---|---|---|\n`;
        md += `| 年支（${p.year.branch}） | ${data.hiddenStems.year.allStems.join('・')} | ${data.hiddenStems.year.mainStem} |\n`;
        md += `| 月支（${p.month.branch}） | ${data.hiddenStems.month.allStems.join('・')} | ${data.hiddenStems.month.mainStem}（${data.hiddenStems.month.phase}） |\n`;
        md += `| 日支（${p.day.branch}） | ${data.hiddenStems.day.allStems.join('・')} | ${data.hiddenStems.day.mainStem} |\n`;
        md += `| 時支（${p.hour.branch}） | ${data.hiddenStems.hour.allStems.join('・')} | ${data.hiddenStems.hour.mainStem} |\n\n`;
    }

    // 通変星
    md += `### 通変星\n\n`;
    md += `| 位置 | 通変星 |\n`;
    md += `|---|---|\n`;
    for (const [k, v] of Object.entries(data.tenGods)) {
        md += `| ${k} | ${v} |\n`;
    }
    md += `\n`;

    // 十二運
    md += `### 十二運\n\n`;
    md += `| 位置 | 十二運 |\n`;
    md += `|---|---|\n`;
    for (const [k, v] of Object.entries(data.twelveStages)) {
        md += `| ${k} | ${v} |\n`;
    }
    md += `\n`;

    return md;
}

function generateSanmeiMarkdown(data) {
    let md = `## 算命学\n\n`;

    md += `- **天中殺**: ${data.voidGroupName}\n\n`;

    md += `### 十大主星\n\n`;
    md += `| 位置 | 主星 |\n`;
    md += `|---|---|\n`;
    for (const [k, v] of Object.entries(data.mainStars)) {
        md += `| ${k} | ${v} |\n`;
    }
    md += `\n`;

    md += `### 十二大従星\n\n`;
    md += `| 位置 | 従星 |\n`;
    md += `|---|---|\n`;
    for (const [k, v] of Object.entries(data.subStars)) {
        md += `| ${k} | ${v} |\n`;
    }
    md += `\n`;

    return md;
}

function generateKyuseiMarkdown(data) {
    let md = `## 九星気学\n\n`;

    md += `- **本命星**: ${data.yearStar}\n`;
    md += `- **月命星**: ${data.monthStar}\n`;
    md += `- **日命星**: ${data.dayStar}\n`;
    md += `- **傾斜宮**: ${data.inclination}\n\n`;

    return md;
}

function generateZiWeiMarkdown(data) {
    let md = `## 紫微斗数\n\n`;

    md += `- **旧暦生年月日**: ${data.lunarDate}\n`;
    md += `- **命宮**: ${data.mingPalace}宮\n`;
    md += `- **身宮**: ${data.bodyPalace}宮\n\n`;

    return md;
}

function generateSukuyouMarkdown(data) {
    let md = `## 宿曜占星術\n\n`;

    md += `- **本命宿**: ${data.natalMansion}（第${data.mansionNumber}宿）\n`;
    md += `- **属性**: ${data.element}\n\n`;

    return md;
}

function generateWesternMarkdown(data) {
    let md = `## 西洋占星術\n\n`;

    // アセンダント（度数なしの文字列の場合はそのまま表示）
    if (data.ascendant) {
        if (typeof data.ascendant === 'object' && data.ascendant.sign) {
            // オブジェクト形式
            if (data.ascendant.degree != null) {
                md += `- **ASC（上昇宮）**: ${data.ascendant.sign} ${data.ascendant.degree.toFixed(1)}°\n`;
            } else {
                md += `- **ASC（上昇宮）**: ${data.ascendant.sign}\n`;
            }
        } else if (typeof data.ascendant === 'number') {
            // 度数のみ
            md += `- **ASC（上昇宮）**: ${data.ascendant.toFixed(1)}°\n`;
        } else {
            // 文字列（星座名のみ）
            md += `- **ASC（上昇宮）**: ${data.ascendant}\n`;
        }
    }

    // MC（天頂）
    if (data.midheaven) {
        if (typeof data.midheaven === 'object' && data.midheaven.sign) {
            if (data.midheaven.degree != null) {
                md += `- **MC（天頂）**: ${data.midheaven.sign} ${data.midheaven.degree.toFixed(1)}°\n\n`;
            } else {
                md += `- **MC（天頂）**: ${data.midheaven.sign}\n\n`;
            }
        } else if (typeof data.midheaven === 'number') {
            md += `- **MC（天頂）**: ${data.midheaven.toFixed(1)}°\n\n`;
        } else {
            md += `- **MC（天頂）**: ${data.midheaven}\n\n`;
        }
    }

    // 惑星位置
    if (data.planets && Array.isArray(data.planets) && data.planets.length > 0) {
        // 度数を持つデータかどうかチェック
        const hasDegree = data.planets.some(p =>
            typeof p.degree === 'number' || typeof p.degree_in_sign === 'number' || typeof p.longitude === 'number'
        );

        md += `### 惑星位置\n\n`;

        if (hasDegree) {
            // 度数あり：3列テーブル
            md += `| 惑星 | 星座 | 度数 |\n`;
            md += `|---|---|---|\n`;
            for (const p of data.planets) {
                const name = p.name || p.planet || '?';
                const sign = p.sign || '?';
                let degree = '-';
                if (typeof p.degree === 'number') {
                    degree = p.degree.toFixed(1) + '°';
                } else if (typeof p.degree_in_sign === 'number') {
                    degree = p.degree_in_sign.toFixed(1) + '°';
                } else if (typeof p.longitude === 'number') {
                    degree = (p.longitude % 30).toFixed(1) + '°';
                }
                const retro = p.retrograde ? ' ℞' : '';
                md += `| ${name}${retro} | ${sign} | ${degree} |\n`;
            }
        } else {
            // 度数なし：2列テーブル（JS簡易版）
            md += `| 惑星 | 星座 |\n`;
            md += `|---|---|\n`;
            for (const p of data.planets) {
                const name = p.name || p.planet || '?';
                const sign = p.sign || '?';
                md += `| ${name} | ${sign} |\n`;
            }
        }
        md += `\n`;
    }

    // 太陽星座・月星座（JS版フォーマット）
    if (data.sunSign) {
        md += `- **太陽星座**: ${data.sunSign}\n`;
    }
    if (data.moonSign) {
        md += `- **月星座**: ${data.moonSign}\n`;
    }
    if (data.sunSign || data.moonSign) {
        md += `\n`;
    }

    return md;
}

function generateVedicMarkdown(data) {
    let md = `## インド占星術（ヴェーダ）\n\n`;

    md += `- **アヤナムサ**: ${data.ayanamsa}°（ラヒリ）\n`;
    md += `- **月のナクシャトラ**: ${data.moonNakshatra}\n`;
    md += `- **ナクシャトラ支配星**: ${data.nakshatraLord}\n`;
    md += `- **月星座**: ${data.moonSign}\n\n`;

    return md;
}

function generateMayanMarkdown(data) {
    let md = `## マヤ暦\n\n`;

    md += `- **KIN**: ${data.kin}\n`;
    md += `- **太陽の紋章**: ${data.solarSeal}\n`;
    md += `- **銀河の音**: ${data.galacticTone}（${data.galacticToneName}）\n`;
    md += `- **ウェイブスペル**: ${data.wavespell}\n`;
    md += `- **ガイドキン**: ${data.guide}\n\n`;

    return md;
}

function generateNumerologyMarkdown(data) {
    let md = `## 数秘術\n\n`;

    md += `- **ライフパス数**: ${data.lifePath}\n`;
    md += `  - 意味: ${data.lifePathMeaning}\n`;
    md += `- **バースデー数**: ${data.birthdayNumber}\n`;
    md += `  - 意味: ${data.birthdayMeaning}\n\n`;

    return md;
}

function generateSeimeiMarkdown(data) {
    let md = `## 姓名判断\n\n`;

    md += `- **姓**: ${data.familyName}（画数: ${data.strokes.family.join(', ')}）\n`;
    md += `- **名**: ${data.givenName}（画数: ${data.strokes.given.join(', ')}）\n\n`;

    md += `### 五格\n\n`;
    md += `| 格 | 画数 | 意味 |\n`;
    md += `|---|---|---|\n`;
    md += `| 天格（祖運） | ${data.tenkaku} | 先祖代々の運勢 |\n`;
    md += `| 人格（主運） | ${data.jinkaku} | 性格・才能の中心 |\n`;
    md += `| 地格（初運） | ${data.chikaku} | 幼少期〜青年期 |\n`;
    md += `| 外格（副運） | ${data.gaikaku} | 対人関係・社会運 |\n`;
    md += `| 総格（総運） | ${data.soukaku} | 人生全体の運勢 |\n\n`;

    return md;
}
