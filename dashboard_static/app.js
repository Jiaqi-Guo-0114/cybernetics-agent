/**
 * Cybernetics Agent Dashboard 前端逻辑。
 *
 * 独立前端，通过轮询 API 获取数据。
 * 支持自动检测 API 端点，如果本地打开，提示启动 agent。
 */

const API_BASE = ''; // 同源

const MODULE_CONFIG = [
    { name: "反馈闭环", key: "feedback_loop" },
    { name: "稳定性引擎", key: "stability" },
    { name: "系统辨识", key: "system_id" },
    { name: "最优控制", key: "optimal_control" },
    { name: "信息流", key: "info_flow" },
    { name: "自适应调谐", key: "adaptive" },
    { name: "分层控制", key: "hierarchy" },
];

let apiAvailable = false;

async function fetchJSON(path) {
    try {
        const res = await fetch(API_BASE + path);
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        return null;
    }
}

function renderModules(status) {
    const grid = document.getElementById('modules-grid');
    const modules = status.modules || {};
    grid.innerHTML = MODULE_CONFIG.map(m => {
        const cfg = modules[m.key] || {};
        const enabled = cfg.enabled || false;
        const statusText = enabled ? "✅ 已启用" : "⚠️ 未启用";
        return `
            <div class="module-card">
                <h3>${m.name}</h3>
                <span class="status-badge ${enabled ? 'enabled' : 'disabled'}">${statusText}</span>
                <p>模块 ID: <code>${m.key}</code></p>
            </div>
        `;
    }).join('');
}

async function refreshMetrics() {
    const data = await fetchJSON('/api/metrics');
    if (!data) return;

    const tc = data.counters?.tool_calls_total || {};
    const toolCalls = Object.values(tc).reduce((a, b) => a + b, 0);
    document.getElementById('tool-calls').textContent = toolCalls;

    const te = data.counters?.tool_errors_total || {};
    const toolErrors = Object.values(te).reduce((a, b) => a + b, 0);
    const tsr = toolCalls > 0 ? ((toolCalls - toolErrors) / toolCalls * 100).toFixed(1) + '%' : 'N/A';
    document.getElementById('tool-success').textContent = tsr;

    const lc = data.counters?.llm_calls_total || {};
    const llmCalls = Object.values(lc).reduce((a, b) => a + b, 0);
    document.getElementById('llm-calls').textContent = llmCalls;

    const le = data.counters?.llm_errors_total || {};
    const llmErrors = Object.values(le).reduce((a, b) => a + b, 0);
    const lsr = llmCalls > 0 ? ((llmCalls - llmErrors) / llmCalls * 100).toFixed(1) + '%' : 'N/A';
    document.getElementById('llm-success').textContent = lsr;

    const err = data.counters?.errors_total || {};
    const errTotal = Object.values(err).reduce((a, b) => a + b, 0);
    document.getElementById('errors').textContent = errTotal;
}

async function refreshStatus() {
    const data = await fetchJSON('/api/status');
    if (!data) return;
    document.getElementById('session-id').textContent = data.session_id || '-';
    document.getElementById('project-name').textContent =
        (data.project_name || 'Cybernetics Agent') + ' - 系统状态仪表盘';
    renderModules(data);
}

async function refreshAlerts() {
    const data = await fetchJSON('/alert/status');
    const panel = document.getElementById('alert-panel');
    if (!data) {
        panel.innerHTML = '<p style="color:#888">未启用告警系统</p>';
        return;
    }
    let html = '<div style="margin-bottom:12px;">';
    html += '<strong>规则 (' + data.rules.length + '):</strong> ';
    html += data.rules.map(r => r.name).join(', ') || '无';
    html += '</div>';
    html += '<div style="margin-bottom:12px;">';
    html += '<strong>渠道:</strong> ';
    html += data.channels.map(c => c.name + (c.healthy ? '(✓)' : '(✗)')).join(', ') || '无';
    html += '</div>';
    if (data.aggregator) {
        html += '<div style="margin-bottom:12px; color:#6c7ae0;">';
        html += '<strong>聚合器:</strong> ';
        html += data.aggregator.strategy + ' / ' + data.aggregator.active_groups + ' 组';
        html += '</div>';
    }
    if (data.history.length > 0) {
        html += '<div><strong>最近告警:</strong></div>';
        html += '<div class="event-log" style="margin-top:8px;">';
        data.history.slice(-10).reverse().forEach(h => {
            const t = new Date(h.timestamp * 1000).toLocaleTimeString();
            const sev = h.severity || 'warning';
            const color = sev === 'critical' ? '#ff4444' : sev === 'error' ? '#ff8800' : '#aaa';
            html += '<div class="event-line" style="color:' + color + '">[' + t + '] ' + h.rule_name + ' | ' + h.message + '</div>';
        });
        html += '</div>';
    }
    panel.innerHTML = html;
}

async function refreshEvents() {
    // 尝试获取最新事件
    const data = await fetchJSON('/api/events?limit=20');
    const panel = document.getElementById('events-panel');
    if (!data || !Array.isArray(data)) {
        panel.innerHTML = '<p style="color:#888">暂无事件</p>';
        return;
    }
    let html = '<div class="event-log">';
    data.forEach(evt => {
        const t = new Date((evt.timestamp || Date.now()/1000) * 1000).toLocaleTimeString();
        const type = evt.event_type || 'unknown';
        const msg = evt.payload ? JSON.stringify(evt.payload).slice(0, 80) : '';
        html += '<div class="event-line">[' + t + '] <strong>' + type + '</strong> ' + msg + '</div>';
    });
    html += '</div>';
    panel.innerHTML = html;
}

async function checkAPI() {
    const health = await fetchJSON('/health');
    if (health && health.status === 'healthy') {
        apiAvailable = true;
        document.getElementById('version').textContent = 'v' + (health.version || '0.6.3');
    } else {
        apiAvailable = false;
        document.getElementById('version').textContent = 'API 未连接 - 请启动 agent';
    }
}

async function init() {
    await checkAPI();
    if (apiAvailable) {
        await refreshStatus();
        await refreshMetrics();
        await refreshAlerts();
        await refreshEvents();

        setInterval(refreshMetrics, 3000);
        setInterval(refreshStatus, 10000);
        setInterval(refreshAlerts, 5000);
        setInterval(refreshEvents, 5000);
    } else {
        document.getElementById('modules-grid').innerHTML =
            '<p style="color:#888; grid-column: 1 / -1; text-align: center;">' +
            '未检测到运行中的 Cybernetics Agent。<br>' +
            '请运行 <code>python -m cybernetics_agent dashboard</code> 后刷新本页面。' +
            '</p>';
    }
}

init();
