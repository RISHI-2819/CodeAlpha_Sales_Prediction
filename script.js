/* ==========================================================================
   AI Business Intelligence Platform - Core Enterprise JavaScript Engine
   ========================================================================== */

let appState = {
    user: null,
    theme: localStorage.getItem('bi_theme') || 'dark',
    lang: localStorage.getItem('bi_lang') || 'en',
    products: [],
    customers: [],
    orders: [],
    inventory: [],
    advertisingData: [],
    prodPage: 1,
    prodPerPage: 12,
    custPage: 1,
    custPerPage: 15,
    charts: {}
};

// --- i18n Translation Dictionary ---
const i18n = {
    en: {
        nav_brand: "AI Business Intelligence",
        nav_overview: "Overview",
        nav_products: "Product Catalog (100)",
        nav_customers: "Customer Analytics (200)",
        nav_orders: "Orders Management",
        nav_predictor: "AI Sales Predictor",
        nav_advisor: "AI Business Advisor",
        nav_inventory: "Inventory Analytics",
        nav_marketing: "Marketing Analytics",
        nav_finance: "Financial Accounting",
        nav_reports: "Executive Reports"
    },
    ta: {
        nav_brand: "AI வணிக பகுப்பாய்வு",
        nav_overview: "மேலோட்டம்",
        nav_products: "பொருட்கள் பட்டியல் (100)",
        nav_customers: "வாடிக்கையாளர் பகுப்பாய்வு",
        nav_orders: "ஆர்டர்கள் நிர்வாகம்",
        nav_predictor: "AI விற்பனை கணிப்பான்",
        nav_advisor: "AI வணிக ஆலோசகர்",
        nav_inventory: "சரக்கு மேலாண்மை",
        nav_marketing: "விளம்பர பகுப்பாய்வு",
        nav_finance: "நிதி கணக்கியல்",
        nav_reports: "அறிக்கைகள் மையம்"
    }
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    initTheme(appState.theme);
    initLanguage(appState.lang);
    checkAuthSession();
    initClock();
    loadEnterpriseDatasets();
    setupEventListeners();
});

function initTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const icon = document.getElementById('themeIcon');
    if (icon) icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
}

function initLanguage(lang) {
    const dict = i18n[lang] || i18n.en;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) el.innerText = dict[key];
    });
}

function checkAuthSession() {
    const user = localStorage.getItem('bi_session');
    const overlay = document.getElementById('loginOverlay');
    
    if (user) {
        appState.user = user;
        if (overlay) overlay.style.display = 'none';
        document.getElementById('activeUserLabel').innerText = user;
    } else {
        if (overlay) overlay.style.display = 'flex';
    }
}

function initClock() {
    function update() {
        const now = new Date();
        const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
        
        const dEl = document.getElementById('liveDate');
        const tEl = document.getElementById('liveClock');
        if (dEl) dEl.innerText = dateStr;
        if (tEl) tEl.innerText = timeStr;
    }
    update();
    setInterval(update, 1000);
}

// --- Dataset Loader ---
async function loadEnterpriseDatasets() {
    try {
        // Products JSON
        const prodRes = await fetch('dataset/products.json');
        if (prodRes.ok) appState.products = await prodRes.json();
        
        // Customers JSON
        const custRes = await fetch('dataset/customers.json');
        if (custRes.ok) appState.customers = await custRes.json();
        
        // Orders JSON
        const ordRes = await fetch('dataset/orders.json');
        if (ordRes.ok) appState.orders = await ordRes.json();

        // Inventory JSON
        const invRes = await fetch('dataset/inventory.json');
        if (invRes.ok) appState.inventory = await invRes.json();

    } catch (err) {
        console.warn("Using fallback memory datasets", err);
    } finally {
        // Load advertising.csv via PapaParse
        Papa.parse('dataset/advertising.csv', {
            download: true,
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
            complete: function(results) {
                if (results.data) appState.advertisingData = results.data;
                renderAppViews();
            },
            error: function() {
                renderAppViews();
            }
        });
    }
}

function renderAppViews() {
    renderOverviewDashboard();
    renderProductCatalog();
    renderCustomerTable();
    renderOrdersTable();
    renderInventoryTable();
    renderAnalyticsCharts();
    
    const loader = document.getElementById('appLoading');
    if (loader) loader.style.display = 'none';
}

// --- UI Navigation Router ---
function setupEventListeners() {
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSec = link.getAttribute('data-section');
            
            document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            document.querySelectorAll('.app-section').forEach(sec => sec.classList.add('d-none'));
            const showEl = document.getElementById(targetSec);
            if (showEl) showEl.classList.remove('d-none');
        });
    });

    // Theme Toggle Button
    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            appState.theme = appState.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('bi_theme', appState.theme);
            initTheme(appState.theme);
        });
    }

    // Language Toggle
    const langSelect = document.getElementById('langSelect');
    if (langSelect) {
        langSelect.value = appState.lang;
        langSelect.addEventListener('change', (e) => {
            appState.lang = e.target.value;
            localStorage.setItem('bi_lang', appState.lang);
            initLanguage(appState.lang);
        });
    }

    // Login Form Submit
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const u = document.getElementById('loginUser').value.trim();
            if (u) {
                appState.user = u;
                localStorage.setItem('bi_session', u);
                checkAuthSession();
                showToast(`Welcome to Enterprise Analytics, ${u}!`, 'success');
            }
        });
    }

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('bi_session');
            appState.user = null;
            checkAuthSession();
            showToast('Logged out successfully.', 'info');
        });
    }

    // AI Predictor Form Submit
    const predForm = document.getElementById('aiPredictorForm');
    if (predForm) {
        predForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const tv = parseFloat(document.getElementById('pred_tv').value) || 0;
            const radio = parseFloat(document.getElementById('pred_radio').value) || 0;
            const news = parseFloat(document.getElementById('pred_newspaper').value) || 0;

            const predUnits = 2.92 + (0.0458 * tv) + (0.1880 * radio) + (0.0010 * news) + (0.0009 * tv * radio);
            const predRevenue = Math.round(predUnits * 1000);
            const totalSpend = tv + radio + news;
            const estProfit = Math.round(predRevenue * 0.42);
            const roiPct = Math.round(((predRevenue - (totalSpend * 1000)) / (totalSpend * 1000 + 1e-5)) * 100);
            const confidence = Math.min(98.5, Math.max(85.0, 96.8 - (totalSpend / 400.0)));

            document.getElementById('out_pred_sales').innerText = `$${(predRevenue / 1000).toFixed(1)}k`;
            document.getElementById('out_confidence').innerText = `${confidence.toFixed(1)}%`;
            document.getElementById('out_profit').innerText = `$${(estProfit / 1000).toFixed(1)}k`;
            document.getElementById('out_roi').innerText = `${roiPct}%`;

            showToast("AI Sales prediction updated!", "success");
        });
    }

    // Search & Filter listeners
    ['prodSearchInput', 'prodCategoryFilter', 'prodSortFilter'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('change', () => { appState.prodPage = 1; renderProductCatalog(); });
    });

    const searchInput = document.getElementById('prodSearchInput');
    if (searchInput) searchInput.addEventListener('keyup', () => { appState.prodPage = 1; renderProductCatalog(); });

    const custSearch = document.getElementById('custSearchInput');
    if (custSearch) custSearch.addEventListener('keyup', () => { appState.custPage = 1; renderCustomerTable(); });

    // Export & Print Buttons
    const exportBtn = document.getElementById('exportCsvBtn');
    if (exportBtn) exportBtn.addEventListener('click', exportProductsToCsv);

    const printBtn = document.getElementById('printBtn');
    if (printBtn) printBtn.addEventListener('click', () => window.print());
}

// --- Render Overview Dashboard ---
function renderOverviewDashboard() {
    let totalRevenue = appState.products.reduce((acc, p) => acc + (p.selling_price * p.units_sold), 0);
    let totalProfit = appState.products.reduce((acc, p) => acc + (p.profit * p.units_sold), 0);

    const revEl = document.getElementById('kpi_revenue');
    const profEl = document.getElementById('kpi_profit');
    if (revEl) revEl.innerText = `$${(totalRevenue / 1000000).toFixed(2)}M`;
    if (profEl) profEl.innerText = `$${(totalProfit / 1000000).toFixed(2)}M (${((totalProfit/totalRevenue)*100).toFixed(1)}%)`;
}

// --- Render Product Catalog with Pagination ---
function renderProductCatalog() {
    const container = document.getElementById('productsGridContainer');
    if (!container) return;

    let search = (document.getElementById('prodSearchInput')?.value || '').toLowerCase();
    let cat = document.getElementById('prodCategoryFilter')?.value || 'all';
    let sort = document.getElementById('prodSortFilter')?.value || 'bestseller';

    let filtered = appState.products.filter(p => {
        let matchName = p.name.toLowerCase().includes(search) || p.id.toLowerCase().includes(search) || p.brand.toLowerCase().includes(search);
        let matchCat = (cat === 'all') || (p.category === cat);
        return matchName && matchCat;
    });

    // Sorting
    if (sort === 'price_high') filtered.sort((a, b) => b.selling_price - a.selling_price);
    else if (sort === 'price_low') filtered.sort((a, b) => a.selling_price - b.selling_price);
    else if (sort === 'most_sold') filtered.sort((a, b) => b.units_sold - a.units_sold);
    else filtered.sort((a, b) => (b.bestseller ? 1 : 0) - (a.bestseller ? 1 : 0));

    // Pagination slice
    let totalPages = Math.ceil(filtered.length / appState.prodPerPage) || 1;
    appState.prodPage = Math.min(appState.prodPage, totalPages);
    let startIdx = (appState.prodPage - 1) * appState.prodPerPage;
    let paginated = filtered.slice(startIdx, startIdx + appState.prodPerPage);

    container.innerHTML = paginated.map(p => `
        <div class="col-xl-4 col-md-6">
            <div class="product-card glass-card h-100 d-flex flex-column justify-content-between">
                <div>
                    <div class="product-img-wrapper mb-3 rounded-3 position-relative">
                        <img src="${p.img}" alt="${p.name}" class="img-fluid" onerror="this.src='https://via.placeholder.com/200x140?text=Product'">
                        <div class="position-absolute top-0 start-0 p-2 d-flex gap-1">
                            ${p.bestseller ? '<span class="badge badge-bestseller">Best Seller</span>' : ''}
                            <span class="badge badge-discount">${p.discount}</span>
                        </div>
                    </div>
                    <div class="d-flex justify-content-between align-items-start mb-1">
                        <span class="badge bg-primary bg-opacity-20 text-primary fs-8">${p.category}</span>
                        <span class="fs-8 text-secondary font-monospace">${p.id}</span>
                    </div>
                    <h6 class="fw-bold mb-1">${p.name}</h6>
                    <span class="fs-8 text-muted d-block mb-2">Brand: ${p.brand} | Supplier: ${p.supplier}</span>
                    <div class="d-flex align-items-center gap-2 mb-3 fs-7">
                        <span class="text-warning fw-bold">⭐ ${p.rating}</span>
                        <span class="text-muted">(${p.reviews} reviews)</span>
                    </div>
                </div>
                <div class="pt-3 border-top border-secondary border-opacity-25 d-flex justify-content-between align-items-center">
                    <div>
                        <span class="fs-8 text-secondary d-block">Price</span>
                        <h5 class="fw-bold text-success mb-0">$${p.selling_price.toFixed(2)}</h5>
                    </div>
                    <span class="badge ${p.stock < 15 ? 'bg-danger' : 'bg-success'} fs-8">${p.stock} in stock</span>
                </div>
            </div>
        </div>
    `).join('');

    renderPagination('productsPagination', totalPages, appState.prodPage, (page) => {
        appState.prodPage = page;
        renderProductCatalog();
    });
}

// --- Render Customers Table ---
function renderCustomerTable() {
    const tbody = document.getElementById('customerTableBody');
    if (!tbody) return;

    let search = (document.getElementById('custSearchInput')?.value || '').toLowerCase();
    let filtered = appState.customers.filter(c => c.name.toLowerCase().includes(search) || c.email.toLowerCase().includes(search) || c.location.toLowerCase().includes(search));

    let totalPages = Math.ceil(filtered.length / appState.custPerPage) || 1;
    appState.custPage = Math.min(appState.custPage, totalPages);
    let startIdx = (appState.custPage - 1) * appState.custPerPage;
    let paginated = filtered.slice(startIdx, startIdx + appState.custPerPage);

    tbody.innerHTML = paginated.map(c => `
        <tr>
            <td class="font-monospace fs-7 text-muted">${c.id}</td>
            <td class="fw-bold">${c.name}</td>
            <td class="fs-7">${c.location}</td>
            <td class="fs-7">${c.gender}, ${c.age} yrs</td>
            <td><span class="badge bg-secondary">${c.purchases_count} orders</span></td>
            <td class="fw-bold text-success">$${c.total_spending.toFixed(2)}</td>
            <td class="fw-bold text-info">$${c.clv.toFixed(2)}</td>
            <td><span class="badge ${c.loyalty_tier === 'VIP Gold' ? 'badge-bestseller' : 'bg-primary'}">${c.loyalty_tier}</span></td>
        </tr>
    `).join('');

    renderPagination('customerPagination', totalPages, appState.custPage, (page) => {
        appState.custPage = page;
        renderCustomerTable();
    });
}

// --- Render Orders & Inventory Tables ---
function renderOrdersTable() {
    const tbody = document.getElementById('ordersTableBody');
    if (!tbody) return;

    tbody.innerHTML = appState.orders.slice(0, 20).map(o => `
        <tr>
            <td class="font-monospace fs-7 text-muted">${o.id}</td>
            <td class="fw-bold">${o.product_name}</td>
            <td class="fs-7">${o.customer_name}</td>
            <td class="fs-7 text-muted">${o.order_date}</td>
            <td>${o.quantity}</td>
            <td class="fw-bold text-success">$${o.revenue.toFixed(2)}</td>
            <td><span class="badge ${o.status === 'Delivered' ? 'bg-success' : 'bg-warning'}">${o.status}</span></td>
            <td class="fs-7 text-secondary">${o.payment_method}</td>
        </tr>
    `).join('');
}

function renderInventoryTable() {
    const tbody = document.getElementById('inventoryTableBody');
    if (!tbody) return;

    tbody.innerHTML = appState.inventory.slice(0, 20).map(inv => `
        <tr>
            <td class="font-monospace fs-7 text-muted">${inv.product_id}</td>
            <td class="fw-bold">${inv.product_name}</td>
            <td><span class="badge bg-secondary">${inv.category}</span></td>
            <td class="fs-7">${inv.warehouse}</td>
            <td><span class="badge ${inv.stock_qty < 15 ? 'bg-danger' : 'bg-success'}">${inv.stock_qty} units</span></td>
            <td class="fw-bold text-primary">$${inv.inventory_value.toFixed(2)}</td>
            <td><span class="badge ${inv.velocity === 'Fast Moving' ? 'badge-bestseller' : 'bg-info'}">${inv.velocity}</span></td>
        </tr>
    `).join('');
}

// --- Generic Pagination Renderer ---
function renderPagination(elemId, totalPages, currentPage, onPageClick) {
    const ul = document.getElementById(elemId);
    if (!ul) return;

    let items = [];
    for (let i = 1; i <= Math.min(totalPages, 8); i++) {
        items.push(`
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="event.preventDefault(); window.paginationCallbacks['${elemId}'](${i})">${i}</a>
            </li>
        `);
    }

    if (!window.paginationCallbacks) window.paginationCallbacks = {};
    window.paginationCallbacks[elemId] = onPageClick;

    ul.innerHTML = items.join('');
}

// --- Render Chart.js & Plotly Visualizations ---
function renderAnalyticsCharts() {
    // 1. Sales Trend Line Chart
    const ctxTrend = document.getElementById('salesTrendChart');
    if (ctxTrend) {
        if (appState.charts.trend) appState.charts.trend.destroy();
        appState.charts.trend = new Chart(ctxTrend, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'Sales Revenue ($k)',
                        data: [210, 245, 230, 285, 310, 345, 330, 385, 410, 395, 440, 485],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.12)',
                        fill: true,
                        tension: 0.35
                    },
                    {
                        label: 'Net Profit ($k)',
                        data: [82, 95, 88, 112, 125, 138, 130, 152, 165, 154, 178, 195],
                        borderColor: '#10b981',
                        backgroundColor: 'transparent',
                        borderDash: [5, 5],
                        tension: 0.35
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { color: 'rgba(255,255,255,0.08)' } }
                }
            }
        });
    }

    // 2. Category Pie Chart
    const ctxPie = document.getElementById('categoryPieChart');
    if (ctxPie) {
        if (appState.charts.pie) appState.charts.pie.destroy();
        appState.charts.pie = new Chart(ctxPie, {
            type: 'doughnut',
            data: {
                labels: ['Electronics', 'Audio & Sound', 'Wearables', 'Accessories', 'Smart Home'],
                datasets: [{
                    data: [30, 25, 20, 15, 10],
                    backgroundColor: ['#6366f1', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } }
            }
        });
    }

    // 3. Marketing ROI Chart
    const ctxMktRoi = document.getElementById('marketingRoiChart');
    if (ctxMktRoi) {
        if (appState.charts.mktRoi) appState.charts.mktRoi.destroy();
        appState.charts.mktRoi = new Chart(ctxMktRoi, {
            type: 'bar',
            data: {
                labels: ['Digital Ads', 'Social Media', 'TV Ads', 'Radio Ads', 'Email Mktg', 'Newspaper'],
                datasets: [{
                    label: 'ROI Multiplier (x)',
                    data: [4.2, 3.8, 3.5, 3.2, 2.9, 1.4],
                    backgroundColor: ['#10b981', '#3b82f6', '#6366f1', '#8b5cf6', '#f59e0b', '#f43f5e'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { y: { grid: { color: 'rgba(255,255,255,0.08)' } }, x: { grid: { display: false } } }
            }
        });
    }

    // 4. Marketing Channel Distribution Chart
    const ctxMktChan = document.getElementById('marketingChannelChart');
    if (ctxMktChan) {
        if (appState.charts.mktChan) appState.charts.mktChan.destroy();
        appState.charts.mktChan = new Chart(ctxMktChan, {
            type: 'doughnut',
            data: {
                labels: ['Digital Ads', 'TV Ads', 'Radio Ads', 'Social Media', 'Newspaper'],
                datasets: [{
                    data: [35, 30, 18, 12, 5],
                    backgroundColor: ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#f43f5e'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } }
            }
        });
    }

    // 5. Plotly Heatmap
    const heatmapDiv = document.getElementById('plotlyHeatmap');
    if (heatmapDiv && appState.advertisingData.length > 0) {
        Plotly.newPlot(heatmapDiv, [{
            z: [
                [1.00, 0.05, 0.78],
                [0.05, 1.00, 0.58],
                [0.78, 0.58, 1.00]
            ],
            x: ['TV Spend', 'Radio Spend', 'Sales'],
            y: ['TV Spend', 'Radio Spend', 'Sales'],
            type: 'heatmap',
            colorscale: 'Viridis'
        }], {
            margin: { t: 20, b: 30, l: 60, r: 20 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#94a3b8' }
        }, { responsive: true, displayModeBar: false });
    }
}

// --- Export CSV Helpers ---
function exportProductsToCsv() {
    if (!appState.products || appState.products.length === 0) return;
    const csv = Papa.unparse(appState.products);
    downloadBlob(csv, 'Enterprise_Products_Report.csv');
    showToast('Exported 100 Products CSV!', 'success');
}

function exportCustomersToCsv() {
    if (!appState.customers || appState.customers.length === 0) return;
    const csv = Papa.unparse(appState.customers);
    downloadBlob(csv, 'Enterprise_Customers_Report.csv');
    showToast('Exported 200 Customers CSV!', 'success');
}

function downloadBlob(content, filename) {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// --- Toast Notification Helper ---
function showToast(msg, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'primary'} border-0 show`;
    toast.role = 'alert';
    toast.style.marginBottom = '10px';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body fs-7">
                <i class="bi bi-info-circle-fill me-2"></i> ${msg}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}
