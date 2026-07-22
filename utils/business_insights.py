import numpy as np
import pandas as pd
from scipy.optimize import minimize

def analyze_business_performance(tv, radio, newspaper, predicted_sales, model, scaler, feature_cols):
    total_spend = tv + radio + newspaper
    eps = 1e-5
    
    tv_pct = (tv / (total_spend + eps)) * 100
    radio_pct = (radio / (total_spend + eps)) * 100
    newspaper_pct = (newspaper / (total_spend + eps)) * 100
    
    # Calculate Marginal ROI per channel (+ $10k spend test)
    delta = 10.0
    
    # Base features construction helper
    def get_features(t, r, n):
        tot = t + r + n
        t_p = (t / (tot + eps)) * 100
        r_p = (r / (tot + eps)) * 100
        n_p = (n / (tot + eps)) * 100
        l_t = np.log1p(t)
        l_r = np.log1p(r)
        l_n = np.log1p(n)
        tr = t * r
        tn = t * n
        rn = r * n
        t2 = t ** 2
        r2 = r ** 2
        
        feat_dict = {
            'TV': t, 'Radio': r, 'Newspaper': n,
            'Total_Spend': tot, 'TV_Pct': t_p, 'Radio_Pct': r_p, 'Newspaper_Pct': n_p,
            'Log_TV': l_t, 'Log_Radio': l_r, 'Log_Newspaper': l_n,
            'TV_x_Radio': tr, 'TV_x_Newspaper': tn, 'Radio_x_Newspaper': rn,
            'TV_sq': t2, 'Radio_sq': r2
        }
        df_f = pd.DataFrame([feat_dict])
        df_f = df_f.reindex(columns=feature_cols, fill_value=0)
        return df_f

    # Base prediction
    base_feats = get_features(tv, radio, newspaper)
    base_scaled = scaler.transform(base_feats)
    base_pred = float(model.predict(base_scaled)[0])
    
    # TV marginal gain
    tv_feats = get_features(tv + delta, radio, newspaper)
    tv_pred = float(model.predict(scaler.transform(tv_feats))[0])
    tv_marginal = (tv_pred - base_pred) / delta
    
    # Radio marginal gain
    r_feats = get_features(tv, radio + delta, newspaper)
    r_pred = float(model.predict(scaler.transform(r_feats))[0])
    radio_marginal = (r_pred - base_pred) / delta
    
    # Newspaper marginal gain
    n_feats = get_features(tv, radio, newspaper + delta)
    n_pred = float(model.predict(scaler.transform(n_feats))[0])
    np_marginal = (n_pred - base_pred) / delta
    
    marginals = {
        'TV': tv_marginal,
        'Radio': radio_marginal,
        'Newspaper': np_marginal
    }
    
    best_channel = max(marginals, key=marginals.get)
    worst_channel = min(marginals, key=marginals.get)
    
    # ROI Score
    # Sales in thousands, spend in thousands -> Revenue = Sales * $1000
    revenue_est = base_pred * 1000.0
    cost_est = total_spend * 1000.0
    roi_pct = ((revenue_est - cost_est) / (cost_est + eps)) * 100.0
    
    # Smart Recommendations
    recommendations = []
    if radio_marginal > tv_marginal and radio_marginal > np_marginal:
        recommendations.append("Radio advertising shows the highest marginal return per dollar. Consider increasing Radio allocation.")
    elif tv_marginal >= radio_marginal and tv_marginal >= np_marginal:
        recommendations.append("TV advertising provides strong baseline reach with solid marginal ROI. Maintain robust TV presence.")
    
    if np_marginal <= 0.05:
        recommendations.append("Newspaper returns are saturating. Reducing Newspaper budget and reallocating to Radio/TV is recommended.")
    
    if total_spend < 50:
        recommendations.append("Overall marketing budget is under-leveraged. Increasing total spend could yield exponential sales expansion.")
    
    confidence = min(98.5, max(82.0, 95.0 - (total_spend / 500.0)))
    
    return {
        'total_spend': round(total_spend, 2),
        'predicted_sales': round(base_pred, 2),
        'revenue_estimation': round(revenue_est, 2),
        'roi_percentage': round(roi_pct, 2),
        'marginal_returns': {k: round(v, 4) for k, v in marginals.items()},
        'best_channel': best_channel,
        'worst_channel': worst_channel,
        'confidence_level': round(confidence, 1),
        'recommendations': recommendations
    }

def optimize_budget_allocation(target_budget, model, scaler, feature_cols):
    eps = 1e-5
    
    def get_features(t, r, n):
        tot = t + r + n
        t_p = (t / (tot + eps)) * 100
        r_p = (r / (tot + eps)) * 100
        n_p = (n / (tot + eps)) * 100
        l_t = np.log1p(t)
        l_r = np.log1p(r)
        l_n = np.log1p(n)
        tr = t * r
        tn = t * n
        rn = r * n
        t2 = t ** 2
        r2 = r ** 2
        
        feat_dict = {
            'TV': t, 'Radio': r, 'Newspaper': n,
            'Total_Spend': tot, 'TV_Pct': t_p, 'Radio_Pct': r_p, 'Newspaper_Pct': n_p,
            'Log_TV': l_t, 'Log_Radio': l_r, 'Log_Newspaper': l_n,
            'TV_x_Radio': tr, 'TV_x_Newspaper': tn, 'Radio_x_Newspaper': rn,
            'TV_sq': t2, 'Radio_sq': r2
        }
        df_f = pd.DataFrame([feat_dict])
        df_f = df_f.reindex(columns=feature_cols, fill_value=0)
        return df_f

    # Objective: Minimize negative sales prediction
    def objective(x):
        t, r, n = x[0], x[1], x[2]
        df_f = get_features(t, r, n)
        scaled = scaler.transform(df_f)
        pred = model.predict(scaled)[0]
        return -pred

    # Constraint: sum of spend <= target_budget
    constraints = ({'type': 'eq', 'fun': lambda x: target_budget - (x[0] + x[1] + x[2])})
    bounds = [(0, target_budget), (0, target_budget), (0, target_budget)]
    
    # Initial guess: split budget 60% TV, 30% Radio, 10% Newspaper
    x0 = [target_budget * 0.6, target_budget * 0.3, target_budget * 0.1]
    
    res = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
    
    opt_tv, opt_radio, opt_news = max(0.0, res.x[0]), max(0.0, res.x[1]), max(0.0, res.x[2])
    opt_pred = -res.fun
    
    return {
        'target_budget': round(target_budget, 2),
        'optimal_tv': round(opt_tv, 2),
        'optimal_radio': round(opt_radio, 2),
        'optimal_newspaper': round(opt_news, 2),
        'optimal_tv_pct': round((opt_tv / target_budget) * 100, 1) if target_budget > 0 else 0,
        'optimal_radio_pct': round((opt_radio / target_budget) * 100, 1) if target_budget > 0 else 0,
        'optimal_newspaper_pct': round((opt_news / target_budget) * 100, 1) if target_budget > 0 else 0,
        'maximized_sales': round(float(opt_pred), 2)
    }

def simulate_sales_forecast(base_sales, days=180):
    # Generates projected sales curve over time with organic growth trend and seasonality
    time_steps = list(range(1, days + 1))
    daily_sales = []
    
    for d in time_steps:
        # Weekly seasonality + gradual growth curve
        seasonality = 1.0 + 0.05 * np.sin(2 * np.pi * d / 7.0)
        growth = 1.0 + (0.15 * (d / days))
        noise = np.random.normal(0, 0.02)
        val = base_sales * seasonality * growth * (1 + noise)
        daily_sales.append(round(val, 2))
        
    return {
        'days': time_steps,
        'sales_forecast': daily_sales,
        'day_30': daily_sales[29] if len(daily_sales) >= 30 else daily_sales[-1],
        'day_90': daily_sales[89] if len(daily_sales) >= 90 else daily_sales[-1],
        'day_180': daily_sales[179] if len(daily_sales) >= 180 else daily_sales[-1]
    }
