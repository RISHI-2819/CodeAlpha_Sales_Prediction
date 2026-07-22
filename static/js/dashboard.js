/* ==========================================================================
   AI Sales Prediction & Analytics Dashboard JavaScript Controller
   Chart.js & Plotly Integration | Real-time Predictor & Optimizer APIs
   ========================================================================== */

let actualVsPredChart = null;
let residualChart = null;
let budgetPieChart = null;
let leaderboardChart = null;
let forecastChart = null;

document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardData();
    setupEventListeners();
});

function setupEventListeners() {
    // Prediction Form Submission
    const predForm = document.getElementById('predictionForm');
    if (predForm) {
        predForm.addEventListener('submit', handlePrediction);
    }
    
    // What-If Sliders Sync & Real-time Update
    ['whatif_tv', 'whatif_radio', 'whatif_newspaper'].forEach(id => {
        const slider = document.getElementById(id);
        if (slider) {
            slider.addEventListener('input', debounce(handleWhatIfChange, 150));
        }
    });

    // Budget Optimizer Form
    const optForm = document.getElementById('budgetOptimizerForm');
    if (optForm) {
        optForm.addEventListener('submit', handleBudgetOptimization);
    }

    // Retrain Model Button
    const retrainBtn = document.getElementById('retrainBtn');
    if (retrainBtn) {
        retrainBtn.addEventListener('click', handleRetrainModel);
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

async function fetchDashboardData() {
    showLoading(true);
    try {
        // 1. Fetch EDA & Dataset summary
        const edaRes = await fetch('/api/eda-data');
        const edaData = await edaRes.json();
        
        // 2. Fetch Model Leaderboard
        const lbRes = await fetch('/api/model-leaderboard');
        const lbData = await lbRes.json();
        
        // 3. Fetch Prediction History
        const histRes = await fetch('/api/history');
        const histData = await histRes.json();

        // Render Dashboard UI Elements
        renderLeaderboard(lbData.leaderboard);
        renderLeaderboardChart(lbData.leaderboard);
        renderFeatureImportance(lbData.feature_importances);
        renderActualVsPredictedChart(lbData.actual_vs_pred);
        renderResidualChart(lbData.actual_vs_pred.residuals);
        renderHistoryTable(histData.history);
        renderEdaCharts(edaData);
        
        // Initial forecast rendering (using average sales 15.0)
        fetchForecast(15.0);

    } catch (err) {
        console.error("Error loading dashboard data:", err);
        showToast("Failed to load analytics dashboard data.", "danger");
    } finally {
        showLoading(false);
    }
}

async function handlePrediction(e) {
    e.preventDefault();
    const tv = parseFloat(document.getElementById('tv_spend').value) || 0;
    const radio = parseFloat(document.getElementById('radio_spend').value) || 0;
    const newspaper = parseFloat(document.getElementById('newspaper_spend').value) || 0;

    showLoading(true);
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tv, radio, newspaper })
        });
        const data = await response.json();

        if (response.ok) {
            // Update Prediction KPI Display
            document.getElementById('res_pred_sales').innerText = `$${data.predicted_sales}k`;
            document.getElementById('res_roi').innerText = `${data.business_insights.roi_percentage}%`;
            document.getElementById('res_confidence').innerText = `${data.business_insights.confidence_level}%`;
            document.getElementById('res_total_spend').innerText = `$${data.business_insights.total_spend}k`;
            
            // Render Advice Box
            const adviceBox = document.getElementById('aiAdviceBox');
            adviceBox.innerHTML = `
                <div class="alert alert-info border-0 shadow-sm" style="background: rgba(59, 130, 246, 0.15); color: var(--text-primary);">
                    <h6 class="fw-bold mb-2"><i class="bi bi-lightbulb-fill text-warning me-2"></i> Strategic AI Recommendations</h6>
                    <ul class="mb-0 ps-3">
                        ${data.business_insights.recommendations.map(r => `<li class="mb-1">${r}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            // Sync What-If Sliders with prediction input
            document.getElementById('whatif_tv').value = tv;
            document.getElementById('whatif_radio').value = radio;
            document.getElementById('whatif_newspaper').value = newspaper;
            document.getElementById('val_whatif_tv').innerText = tv;
            document.getElementById('val_whatif_radio').innerText = radio;
            document.getElementById('val_whatif_newspaper').innerText = newspaper;
            
            // Update time-series forecast with predicted sales base
            fetchForecast(data.predicted_sales);
            
            // Refresh history table
            const histRes = await fetch('/api/history');
            const histData = await histRes.json();
            renderHistoryTable(histData.history);

            showToast("Sales prediction generated successfully!", "success");
        } else {
            showToast(data.error || "Prediction request failed.", "danger");
        }
    } catch (err) {
        showToast("Server network error occurred.", "danger");
    } finally {
        showLoading(false);
    }
}

async function handleWhatIfChange() {
    const tv = parseFloat(document.getElementById('whatif_tv').value) || 0;
    const radio = parseFloat(document.getElementById('whatif_radio').value) || 0;
    const newspaper = parseFloat(document.getElementById('whatif_newspaper').value) || 0;

    document.getElementById('val_whatif_tv').innerText = tv;
    document.getElementById('val_whatif_radio').innerText = radio;
    document.getElementById('val_whatif_newspaper').innerText = newspaper;

    try {
        const response = await fetch('/api/whatif', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tv, radio, newspaper })
        });
        const data = await response.json();
        if (response.ok) {
            document.getElementById('whatif_pred_sales').innerText = `$${data.predicted_sales}k`;
            document.getElementById('whatif_roi').innerText = `${data.roi_percentage}%`;
        }
    } catch (err) {
        console.error("What-If simulation error:", err);
    }
}

async function handleBudgetOptimization(e) {
    e.preventDefault();
    const budget = parseFloat(document.getElementById('targetBudget').value) || 100;

    showLoading(true);
    try {
        const response = await fetch('/api/optimize-budget', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ budget })
        });
        const data = await response.json();

        if (response.ok) {
            document.getElementById('opt_tv').innerText = `$${data.optimal_tv}k (${data.optimal_tv_pct}%)`;
            document.getElementById('opt_radio').innerText = `$${data.optimal_radio}k (${data.optimal_radio_pct}%)`;
            document.getElementById('opt_newspaper').innerText = `$${data.optimal_newspaper}k (${data.optimal_newspaper_pct}%)`;
            document.getElementById('opt_max_sales').innerText = `$${data.maximized_sales}k`;

            renderBudgetPieChart(data.optimal_tv, data.optimal_radio, data.optimal_newspaper);
            showToast("Optimal budget allocation calculated!", "success");
        }
    } catch (err) {
        showToast("Error optimizing budget.", "danger");
    } finally {
        showLoading(false);
    }
}

async function handleRetrainModel() {
    showLoading(true);
    try {
        const response = await fetch('/api/retrain', { method: 'POST' });
        const data = await response.json();
        if (response.ok) {
            showToast(`Models retrained cleanly! New Champion: ${data.champion_model}`, "success");
            fetchDashboardData();
        } else {
            showToast(data.error || "Retraining failed.", "danger");
        }
    } catch (err) {
        showToast("Network error during model retraining.", "danger");
    } finally {
        showLoading(false);
    }
}

async function fetchForecast(baseSales) {
    try {
        const res = await fetch(`/api/forecast?base_sales=${baseSales}&days=180`);
        const forecastData = await res.json();
        renderForecastChart(forecastData);
    } catch (err) {
        console.error("Error fetching forecast:", err);
    }
}

function renderLeaderboard(leaderboard) {
    const tbody = document.getElementById('leaderboardBody');
    if (!tbody) return;

    tbody.innerHTML = leaderboard.map((row, idx) => `
        <tr>
            <td>
                <span class="badge ${idx === 0 ? 'bg-success' : 'bg-secondary'} me-2">#${idx + 1}</span>
                <strong>${row.model_name}</strong>
            </td>
            <td><span class="badge bg-primary">${row.test_r2}</span></td>
            <td>${row.adjusted_r2}</td>
            <td>${row.cv_r2_score}</td>
            <td>$${row.rmse}k</td>
            <td>$${row.mae}k</td>
            <td>${row.mape}%</td>
            <td><span class="text-success fw-bold">${row.accuracy_percentage}%</span></td>
        </tr>
    `).join('');
}

function renderLeaderboardChart(leaderboard) {
    const ctx = document.getElementById('leaderboardChart');
    if (!ctx) return;

    if (leaderboardChart) leaderboardChart.destroy();

    const labels = leaderboard.map(m => m.model_name);
    const scores = leaderboard.map(m => m.test_r2);

    leaderboardChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Test R² Score',
                data: scores,
                backgroundColor: scores.map((s, i) => i === 0 ? '#10b981' : '#3b82f6'),
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0.8, max: 1.0, grid: { color: 'rgba(255,255,255,0.08)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function renderFeatureImportance(importances) {
    const container = document.getElementById('featureImportanceBars');
    if (!container) return;

    const entries = Object.entries(importances).slice(0, 8); // Top 8 features
    container.innerHTML = entries.map(([feat, val]) => `
        <div class="mb-3">
            <div class="d-flex justify-content-between mb-1 fs-7">
                <span class="fw-semibold">${feat}</span>
                <span class="text-primary font-monospace">${val}%</span>
            </div>
            <div class="progress" style="height: 8px; background: rgba(255,255,255,0.1);">
                <div class="progress-bar bg-gradient-primary" style="width: ${val}%"></div>
            </div>
        </div>
    `).join('');
}

function renderActualVsPredictedChart(data) {
    const ctx = document.getElementById('actualVsPredChart');
    if (!ctx) return;

    if (actualVsPredChart) actualVsPredChart.destroy();

    actualVsPredChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Actual vs Predicted Sales ($k)',
                    data: data.actual.map((act, i) => ({ x: act, y: data.predicted[i] })),
                    backgroundColor: '#6366f1',
                    pointRadius: 5
                },
                {
                    label: 'Ideal 1:1 Reference Line',
                    data: [{ x: 0, y: 0 }, { x: 35, y: 35 }],
                    type: 'line',
                    borderColor: '#ef4444',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Actual Sales ($k)' }, grid: { color: 'rgba(255,255,255,0.08)' } },
                y: { title: { display: true, text: 'Predicted Sales ($k)' }, grid: { color: 'rgba(255,255,255,0.08)' } }
            }
        }
    });
}

function renderResidualChart(residuals) {
    const ctx = document.getElementById('residualChart');
    if (!ctx) return;

    if (residualChart) residualChart.destroy();

    residualChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: residuals.map((_, i) => `#${i + 1}`),
            datasets: [{
                label: 'Residual Error (Actual - Predicted)',
                data: residuals,
                backgroundColor: residuals.map(r => r >= 0 ? '#10b981' : '#f43f5e'),
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.08)' } },
                x: { display: false }
            }
        }
    });
}

function renderBudgetPieChart(tv, radio, newspaper) {
    const ctx = document.getElementById('budgetPieChart');
    if (!ctx) return;

    if (budgetPieChart) budgetPieChart.destroy();

    budgetPieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['TV Spend', 'Radio Spend', 'Newspaper Spend'],
            datasets: [{
                data: [tv, radio, newspaper],
                backgroundColor: ['#4f46e5', '#10b981', '#f59e0b'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } }
        }
    });
}

function renderForecastChart(forecastData) {
    const ctx = document.getElementById('forecastChart');
    if (!ctx) return;

    if (forecastChart) forecastChart.destroy();

    forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: forecastData.days.map(d => `Day ${d}`),
            datasets: [{
                label: 'Projected Daily Sales ($k units)',
                data: forecastData.sales_forecast,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { grid: { display: false } },
                y: { grid: { color: 'rgba(255,255,255,0.08)' } }
            }
        }
    });

    document.getElementById('forecast_30').innerText = `$${forecastData.day_30}k`;
    document.getElementById('forecast_90').innerText = `$${forecastData.day_90}k`;
    document.getElementById('forecast_180').innerText = `$${forecastData.day_180}k`;
}

function renderHistoryTable(history) {
    const tbody = document.getElementById('historyTableBody');
    if (!tbody) return;

    if (!history || history.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted py-4">No prediction logs stored yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = history.map(row => `
        <tr>
            <td class="font-monospace fs-7 text-muted">${row.timestamp}</td>
            <td>$${row.tv_spend}k</td>
            <td>$${row.radio_spend}k</td>
            <td>$${row.newspaper_spend}k</td>
            <td class="fw-bold">$${row.total_spend}k</td>
            <td><span class="badge bg-primary font-monospace fs-6">$${row.predicted_sales}k</span></td>
            <td><span class="badge bg-success">${row.roi_score}%</span></td>
            <td class="fs-7 text-truncate" style="max-width: 200px;">${row.recommendation}</td>
        </tr>
    `).join('');
}

function renderEdaCharts(edaData) {
    // Heatmap / Correlation Plotly render
    const heatmapDiv = document.getElementById('plotlyHeatmap');
    if (heatmapDiv && edaData.correlations) {
        const cols = Object.keys(edaData.correlations);
        const zValues = cols.map(c1 => cols.map(c2 => edaData.correlations[c1][c2]));

        Plotly.newPlot(heatmapDiv, [{
            z: zValues,
            x: cols,
            y: cols,
            type: 'heatmap',
            colorscale: 'Viridis',
            showscale: true
        }], {
            margin: { t: 30, b: 30, l: 40, r: 40 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#94a3b8' }
        }, { responsive: true, displayModeBar: false });
    }
}

function showLoading(show) {
    const loader = document.getElementById('loadingOverlay');
    if (loader) {
        loader.style.display = show ? 'flex' : 'none';
    }
}
