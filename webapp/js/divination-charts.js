/**
 * 占術可視化モジュール
 * - 五行バランスのレーダーチャート
 * - 算命学の宇宙盤
 * Canvas APIを使用して描画
 */

const DivinationCharts = {

    // ===== 五行レーダーチャート =====
    GogyoRadar: {
        /**
         * 五行バランスのレーダーチャートを描画
         * @param {string} canvasId - キャンバス要素のID
         * @param {Object} balance - 五行バランス {木: n, 火: n, 土: n, 金: n, 水: n}
         */
        draw(canvasId, balance) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            const width = canvas.width;
            const height = canvas.height;
            const centerX = width / 2;
            const centerY = height / 2;
            const maxRadius = Math.min(width, height) / 2 - 40;

            // クリア
            ctx.clearRect(0, 0, width, height);

            // 背景グラデーション
            const bgGrad = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, maxRadius);
            bgGrad.addColorStop(0, 'rgba(30, 30, 50, 0.9)');
            bgGrad.addColorStop(1, 'rgba(20, 20, 40, 0.95)');
            ctx.fillStyle = bgGrad;
            ctx.fillRect(0, 0, width, height);

            // 五行の定義（五芒星の配置）
            const elements = [
                { name: '木', color: '#4CAF50', angle: -90 },
                { name: '火', color: '#F44336', angle: -18 },
                { name: '土', color: '#FFC107', angle: 54 },
                { name: '金', color: '#9E9E9E', angle: 126 },
                { name: '水', color: '#2196F3', angle: 198 }
            ];

            // 最大値を計算（スケール用）
            const maxValue = Math.max(6, ...Object.values(balance));

            // グリッド線を描画
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
            ctx.lineWidth = 1;

            for (let level = 1; level <= 5; level++) {
                const r = (maxRadius / 5) * level;
                ctx.beginPath();
                for (let i = 0; i <= 5; i++) {
                    const el = elements[i % 5];
                    const angleRad = (el.angle * Math.PI) / 180;
                    const x = centerX + r * Math.cos(angleRad);
                    const y = centerY + r * Math.sin(angleRad);
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.closePath();
                ctx.stroke();
            }

            // 軸線を描画
            elements.forEach(el => {
                const angleRad = (el.angle * Math.PI) / 180;
                ctx.beginPath();
                ctx.moveTo(centerX, centerY);
                ctx.lineTo(
                    centerX + maxRadius * Math.cos(angleRad),
                    centerY + maxRadius * Math.sin(angleRad)
                );
                ctx.stroke();
            });

            // データを描画
            ctx.beginPath();
            elements.forEach((el, i) => {
                const value = balance[el.name] || 0;
                const r = (value / maxValue) * maxRadius;
                const angleRad = (el.angle * Math.PI) / 180;
                const x = centerX + r * Math.cos(angleRad);
                const y = centerY + r * Math.sin(angleRad);

                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.closePath();

            // データエリアの塗りつぶし
            const dataGrad = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, maxRadius);
            dataGrad.addColorStop(0, 'rgba(156, 39, 176, 0.7)');
            dataGrad.addColorStop(1, 'rgba(103, 58, 183, 0.4)');
            ctx.fillStyle = dataGrad;
            ctx.fill();

            // データエリアの枠線
            ctx.strokeStyle = 'rgba(156, 39, 176, 0.9)';
            ctx.lineWidth = 2;
            ctx.stroke();

            // 頂点のドット
            elements.forEach(el => {
                const value = balance[el.name] || 0;
                const r = (value / maxValue) * maxRadius;
                const angleRad = (el.angle * Math.PI) / 180;
                const x = centerX + r * Math.cos(angleRad);
                const y = centerY + r * Math.sin(angleRad);

                ctx.beginPath();
                ctx.arc(x, y, 5, 0, Math.PI * 2);
                ctx.fillStyle = el.color;
                ctx.fill();
                ctx.strokeStyle = 'white';
                ctx.lineWidth = 2;
                ctx.stroke();
            });

            // ラベルを描画
            ctx.font = 'bold 16px "Noto Sans JP", sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            elements.forEach(el => {
                const value = balance[el.name] || 0;
                const labelR = maxRadius + 25;
                const angleRad = (el.angle * Math.PI) / 180;
                const x = centerX + labelR * Math.cos(angleRad);
                const y = centerY + labelR * Math.sin(angleRad);

                ctx.fillStyle = el.color;
                ctx.fillText(`${el.name}`, x, y - 10);
                ctx.fillStyle = 'white';
                ctx.font = '14px "Noto Sans JP", sans-serif';
                ctx.fillText(`${value.toFixed(1)}`, x, y + 10);
                ctx.font = 'bold 16px "Noto Sans JP", sans-serif';
            });

            // タイトル
            ctx.fillStyle = 'white';
            ctx.font = 'bold 18px "Noto Sans JP", sans-serif';
            ctx.fillText('五行バランス', centerX, 20);
        }
    },

    // ===== 宇宙盤（算命学） =====
    Uchuban: {
        // 60干支
        SIXTY_GANZHI: [
            "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
            "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
            "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
            "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
            "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
            "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"
        ],

        /**
         * 干支の角度を取得
         */
        getAngle(ganzhi) {
            const index = this.SIXTY_GANZHI.indexOf(ganzhi);
            if (index === -1) return 0;
            // 甲子を上（90度=北）から開始、時計回り
            return 90 - (index * 6);
        },

        /**
         * 宇宙盤を描画
         * @param {string} canvasId - キャンバス要素のID
         * @param {Object} uchubanData - 宇宙盤データ
         */
        draw(canvasId, uchubanData) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            const width = canvas.width;
            const height = canvas.height;
            const centerX = width / 2;
            const centerY = height / 2;
            const radius = Math.min(width, height) / 2 - 50;

            // クリア
            ctx.clearRect(0, 0, width, height);

            // 背景
            const bgGrad = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius * 1.3);
            bgGrad.addColorStop(0, 'rgba(20, 20, 50, 0.95)');
            bgGrad.addColorStop(1, 'rgba(10, 10, 30, 1)');
            ctx.fillStyle = bgGrad;
            ctx.fillRect(0, 0, width, height);

            // 外円
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(255, 215, 0, 0.6)';
            ctx.lineWidth = 2;
            ctx.stroke();

            // 内円（複数）
            [0.75, 0.5, 0.25].forEach(ratio => {
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius * ratio, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
                ctx.lineWidth = 1;
                ctx.stroke();
            });

            // 60干支を円周上に配置（目盛り）
            ctx.font = '9px "Noto Sans JP", sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            this.SIXTY_GANZHI.forEach((gz, i) => {
                const angle = this.getAngle(gz);
                const angleRad = (angle * Math.PI) / 180;

                // 目盛り線
                const innerR = radius - 5;
                const outerR = radius + 5;
                ctx.beginPath();
                ctx.moveTo(
                    centerX + innerR * Math.cos(angleRad),
                    centerY - innerR * Math.sin(angleRad)
                );
                ctx.lineTo(
                    centerX + outerR * Math.cos(angleRad),
                    centerY - outerR * Math.sin(angleRad)
                );
                ctx.strokeStyle = 'rgba(255, 215, 0, 0.4)';
                ctx.lineWidth = 1;
                ctx.stroke();

                // 10刻みでラベル表示
                if (i % 10 === 0) {
                    const labelR = radius + 20;
                    const x = centerX + labelR * Math.cos(angleRad);
                    const y = centerY - labelR * Math.sin(angleRad);
                    ctx.fillStyle = 'rgba(255, 215, 0, 0.8)';
                    ctx.fillText(gz, x, y);
                }
            });

            // 三角形を描画
            if (uchubanData && uchubanData.points) {
                const points = uchubanData.points;
                const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1'];

                // 三角形の塗りつぶし
                ctx.beginPath();
                points.forEach((point, i) => {
                    const angleRad = (point.angle * Math.PI) / 180;
                    const x = centerX + radius * 0.85 * Math.cos(angleRad);
                    const y = centerY - radius * 0.85 * Math.sin(angleRad);

                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.closePath();

                // グラデーション塗りつぶし
                const triGrad = ctx.createLinearGradient(0, 0, width, height);
                triGrad.addColorStop(0, 'rgba(255, 107, 107, 0.3)');
                triGrad.addColorStop(0.5, 'rgba(78, 205, 196, 0.3)');
                triGrad.addColorStop(1, 'rgba(69, 183, 209, 0.3)');
                ctx.fillStyle = triGrad;
                ctx.fill();

                // 三角形の枠線
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
                ctx.lineWidth = 2;
                ctx.stroke();

                // 頂点を描画
                points.forEach((point, i) => {
                    const angleRad = (point.angle * Math.PI) / 180;
                    const x = centerX + radius * 0.85 * Math.cos(angleRad);
                    const y = centerY - radius * 0.85 * Math.sin(angleRad);

                    // ドット
                    ctx.beginPath();
                    ctx.arc(x, y, 10, 0, Math.PI * 2);
                    ctx.fillStyle = colors[i];
                    ctx.fill();
                    ctx.strokeStyle = 'white';
                    ctx.lineWidth = 2;
                    ctx.stroke();

                    // ラベル
                    const labelR = radius * 0.85 + 25;
                    const lx = centerX + labelR * Math.cos(angleRad);
                    const ly = centerY - labelR * Math.sin(angleRad);

                    ctx.font = 'bold 14px "Noto Sans JP", sans-serif';
                    ctx.fillStyle = colors[i];
                    ctx.fillText(`${point.label}柱`, lx, ly - 10);
                    ctx.fillStyle = 'white';
                    ctx.font = '12px "Noto Sans JP", sans-serif';
                    ctx.fillText(point.ganzhi, lx, ly + 8);
                });

                // 中央に情報表示
                ctx.font = 'bold 16px "Noto Sans JP", sans-serif';
                ctx.fillStyle = 'white';
                ctx.fillText('宇宙盤', centerX, centerY - 30);

                ctx.font = '13px "Noto Sans JP", sans-serif';
                ctx.fillStyle = '#FFD700';
                ctx.fillText(`面積: ${uchubanData.area}`, centerX, centerY);

                ctx.font = '11px "Noto Sans JP", sans-serif';
                ctx.fillStyle = '#4ECDC4';
                ctx.fillText(uchubanData.patternType, centerX, centerY + 25);
            }
        }
    },

    // ===== 九星方位盤 =====
    DirectionBoard: {
        DIRECTIONS: [
            { key: 'N', name: '北', angle: 90 },
            { key: 'NE', name: '北東', angle: 45 },
            { key: 'E', name: '東', angle: 0 },
            { key: 'SE', name: '南東', angle: -45 },
            { key: 'S', name: '南', angle: -90 },
            { key: 'SW', name: '南西', angle: -135 },
            { key: 'W', name: '西', angle: 180 },
            { key: 'NW', name: '北西', angle: 135 }
        ],

        STAR_NAMES: ['', '一白', '二黒', '三碧', '四緑', '五黄', '六白', '七赤', '八白', '九紫'],

        STAR_COLORS: {
            1: '#4FC3F7', // 水 - 青
            2: '#8D6E63', // 土 - 茶
            3: '#66BB6A', // 木 - 緑
            4: '#81C784', // 木 - 薄緑
            5: '#FFEE58', // 土 - 黄
            6: '#E0E0E0', // 金 - 白
            7: '#EF5350', // 金 - 赤
            8: '#BDBDBD', // 土 - 灰白
            9: '#AB47BC'  // 火 - 紫
        },

        /**
         * 方位盤を描画
         * @param {string} canvasId - キャンバス要素のID
         * @param {Object} boardData - 方位盤データ
         * @param {Object} judgment - 吉凶判定
         */
        draw(canvasId, boardData, judgment) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            const width = canvas.width;
            const height = canvas.height;
            const centerX = width / 2;
            const centerY = height / 2;
            const outerRadius = Math.min(width, height) / 2 - 30;
            const innerRadius = outerRadius * 0.3;

            // クリア
            ctx.clearRect(0, 0, width, height);

            // 背景
            ctx.fillStyle = 'rgba(30, 30, 50, 0.95)';
            ctx.fillRect(0, 0, width, height);

            // 方位セクターを描画
            this.DIRECTIONS.forEach((dir, i) => {
                const star = boardData[dir.key] || 5;
                const startAngle = ((dir.angle - 22.5) * Math.PI) / 180;
                const endAngle = ((dir.angle + 22.5) * Math.PI) / 180;

                // 吉凶判定で色を変える
                let fillColor = this.STAR_COLORS[star];
                let alpha = 0.6;

                if (judgment) {
                    if (judgment.gooSatsu && judgment.gooSatsu.includes(dir.key)) {
                        fillColor = '#B71C1C'; // 五黄殺 - 濃い赤
                        alpha = 0.8;
                    } else if (judgment.ankenSatsu && judgment.ankenSatsu.includes(dir.key)) {
                        fillColor = '#880E4F'; // 暗剣殺 - 濃い赤紫
                        alpha = 0.8;
                    } else if (judgment.luckyDirs && judgment.luckyDirs.includes(dir.key)) {
                        fillColor = '#1B5E20'; // 吉方位 - 緑
                        alpha = 0.8;
                    }
                }

                // セクターを描画
                ctx.beginPath();
                ctx.moveTo(centerX, centerY);
                ctx.arc(centerX, centerY, outerRadius, startAngle, endAngle);
                ctx.closePath();

                ctx.fillStyle = fillColor;
                ctx.globalAlpha = alpha;
                ctx.fill();
                ctx.globalAlpha = 1.0;

                ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
                ctx.lineWidth = 1;
                ctx.stroke();

                // 方位名と九星を表示
                const labelAngle = (dir.angle * Math.PI) / 180;
                const labelR = outerRadius * 0.65;
                const lx = centerX + labelR * Math.cos(labelAngle);
                const ly = centerY - labelR * Math.sin(labelAngle);

                ctx.font = 'bold 14px "Noto Sans JP", sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = 'white';
                ctx.fillText(dir.name, lx, ly - 10);

                ctx.font = '12px "Noto Sans JP", sans-serif';
                ctx.fillStyle = '#FFD700';
                ctx.fillText(this.STAR_NAMES[star], lx, ly + 10);
            });

            // 中央円
            ctx.beginPath();
            ctx.arc(centerX, centerY, innerRadius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(50, 50, 80, 0.9)';
            ctx.fill();
            ctx.strokeStyle = '#FFD700';
            ctx.lineWidth = 2;
            ctx.stroke();

            // 中央の九星
            const centerStar = boardData.center || 5;
            ctx.font = 'bold 16px "Noto Sans JP", sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = this.STAR_COLORS[centerStar];
            ctx.fillText(this.STAR_NAMES[centerStar], centerX, centerY - 5);
            ctx.font = '10px "Noto Sans JP", sans-serif';
            ctx.fillStyle = 'white';
            ctx.fillText('中宮', centerX, centerY + 12);

            // 凡例
            ctx.font = '11px "Noto Sans JP", sans-serif';
            ctx.textAlign = 'left';

            const legends = [
                { text: '● 吉方位', color: '#1B5E20' },
                { text: '● 五黄殺', color: '#B71C1C' },
                { text: '● 暗剣殺', color: '#880E4F' }
            ];

            legends.forEach((leg, i) => {
                ctx.fillStyle = leg.color;
                ctx.fillText(leg.text, 10, height - 40 + i * 15);
            });
        }
    },

    /**
     * 全チャートを初期化して描画
     */
    renderAll(baziAdvanced, sanmeiAdvanced, kyuseiAdvanced) {
        // 五行バランス
        if (baziAdvanced && baziAdvanced.gogyoBalance) {
            this.GogyoRadar.draw('gogyo-radar-canvas', baziAdvanced.gogyoBalance);
        }

        // 宇宙盤
        if (sanmeiAdvanced && sanmeiAdvanced.uchuban) {
            this.Uchuban.draw('uchuban-canvas', sanmeiAdvanced.uchuban);
        }

        // 方位盤
        if (kyuseiAdvanced && kyuseiAdvanced.boards && kyuseiAdvanced.boards.day) {
            this.DirectionBoard.draw(
                'direction-board-canvas',
                kyuseiAdvanced.boards.day.directions,
                kyuseiAdvanced.judgment
            );
        }
    }
};

// グローバルに公開
if (typeof window !== 'undefined') {
    window.DivinationCharts = DivinationCharts;
}
