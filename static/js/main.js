/* ==========================================================================
   AI Sales Prediction Platform - Main Controller & i18n Dictionary
   ========================================================================== */

const i18n = {
    en: {
        nav_brand: "📈 SalesAI Analytics",
        nav_overview: "Overview",
        nav_predictor: "AI Predictor",
        nav_whatif: "What-If Analysis",
        nav_optimizer: "Budget Optimizer",
        nav_eda: "EDA & Charts",
        nav_models: "Model Leaderboard",
        nav_forecast: "Sales Forecast",
        nav_history: "Prediction Logs",
        nav_export: "Export Reports",
        
        kpi_total_spend: "Total Media Budget",
        kpi_pred_sales: "Predicted Sales",
        kpi_roi: "Estimated ROI",
        kpi_best_channel: "Top Performer",
        
        btn_predict: "Generate Prediction",
        btn_optimize: "Optimize Budget",
        btn_retrain: "Retrain Models",
        btn_export_pdf: "Export PDF Report",
        btn_export_excel: "Export Excel Data",
        
        title_prediction_form: "AI Sales Predictor",
        lbl_tv: "TV Advertising Spend ($k)",
        lbl_radio: "Radio Advertising Spend ($k)",
        lbl_newspaper: "Newspaper Advertising Spend ($k)",
        
        title_advisor: "AI Business Advisor",
        title_leaderboard: "Model Performance Leaderboard",
        title_forecast: "Time Series Sales Projection"
    },
    ta: {
        nav_brand: "📈 விற்பனை AI பகுப்பாய்வு",
        nav_overview: "மேலோட்டம்",
        nav_predictor: "AI கணிப்பான்",
        nav_whatif: "சூழல் ஆய்வு",
        nav_optimizer: "பட்ஜெட் உகப்பாக்கம்",
        nav_eda: "தரவு வரைபடங்கள்",
        nav_models: "மாதிரி பட்டியல்",
        nav_forecast: "விற்பனை கணிப்பு",
        nav_history: "முந்தைய கணிப்புகள்",
        nav_export: "அறிக்கைகள் பதிவிறக்கம்",
        
        kpi_total_spend: "மொத்த விளம்பர பட்ஜெட்",
        kpi_pred_sales: "கணிக்கப்பட்ட விற்பனை",
        kpi_roi: "எதிர்பார்க்கப்படும் ROI",
        kpi_best_channel: "சிறந்த ஊடகம்",
        
        btn_predict: "விற்பனையை கணிக்குக",
        btn_optimize: "பட்ஜெட்டை மேம்படுத்துக",
        btn_retrain: "மாதிரியை மீண்டும் பயிற்றுவி",
        btn_export_pdf: "PDF அறிக்கை பெறுக",
        btn_export_excel: "Excel தரவு பெறுக",
        
        title_prediction_form: "AI விற்பனை கணிப்பான்",
        lbl_tv: "டிவி விளம்பர செலவு ($k)",
        lbl_radio: "ரேடியோ விளம்பர செலவு ($k)",
        lbl_newspaper: "செய்தித்தாள் விளம்பர செலவு ($k)",
        
        title_advisor: "AI வணிக ஆலோசகர்",
        title_leaderboard: "மாதிரி செயல்திறன் பட்டியல்",
        title_forecast: "எதிர்கால விற்பனை கணிப்பு"
    }
};

let currentLang = localStorage.getItem('app_lang') || 'en';
let currentTheme = localStorage.getItem('app_theme') || 'dark';

document.addEventListener('DOMContentLoaded', () => {
    applyTheme(currentTheme);
    applyLanguage(currentLang);
    
    // Theme Switcher Event Listener
    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('app_theme', currentTheme);
            applyTheme(currentTheme);
        });
    }
    
    // Language Switcher Event Listener
    const langSelect = document.getElementById('langSelect');
    if (langSelect) {
        langSelect.value = currentLang;
        langSelect.addEventListener('change', (e) => {
            currentLang = e.target.value;
            localStorage.setItem('app_lang', currentLang);
            applyLanguage(currentLang);
        });
    }
});

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    }
}

function applyLanguage(lang) {
    const dict = i18n[lang] || i18n.en;
    document.querySelectorAll('[data-i18n]').forEach(elem => {
        const key = elem.getAttribute('data-i18n');
        if (dict[key]) {
            elem.innerText = dict[key];
        }
    });
}

function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0 show`;
    toast.role = 'alert';
    toast.style.marginBottom = '10px';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-${type === 'success' ? 'check-circle-fill' : 'exclamation-triangle-fill'} me-2"></i> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}
