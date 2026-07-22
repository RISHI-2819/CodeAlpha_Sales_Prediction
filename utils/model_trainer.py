import os
import joblib
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor

try:
    from xgboost import XGBRegressor
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from utils.data_preprocessing import load_data, clean_data, engineer_features

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

def calculate_adjusted_r2(r2, n, p):
    if n - p - 1 <= 0:
        return r2
    return 1 - (1 - r2) * (n - 1) / (n - p - 1)

def train_and_evaluate_all():
    # 1. Load & Preprocess Data
    raw_df = load_data(os.path.join(PROJECT_ROOT, 'advertising.csv'))
    df, clean_report = clean_data(raw_df)
    df_engineered = engineer_features(df)
    
    # Drop target and non-predictor metrics from features
    target_col = 'Sales'
    drop_cols = ['Sales', 'Ad_Efficiency', 'ROI_Score']
    feature_cols = [c for c in df_engineered.columns if c not in drop_cols]
    
    X = df_engineered[feature_cols]
    y = df_engineered[target_col]
    
    # 2. Train Test Split & Scaling
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 3. Model Dictionary
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=1.0),
        'Lasso Regression': Lasso(alpha=0.1),
        'ElasticNet': ElasticNet(alpha=0.1, l1_ratio=0.5),
        'Decision Tree': DecisionTreeRegressor(max_depth=6, random_state=42),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42),
        'Extra Trees': ExtraTreesRegressor(n_estimators=100, max_depth=8, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    }
    
    if HAS_XGBOOST:
        models['XGBoost'] = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
        
    results = []
    trained_model_objects = {}
    
    n_test = len(y_test)
    p_feats = len(feature_cols)
    
    for name, model in models.items():
        # Fit
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_train_pred = model.predict(X_train_scaled)
        y_test_pred = model.predict(X_test_scaled)
        
        # Metrics
        train_r2 = float(r2_score(y_train, y_train_pred))
        test_r2 = float(r2_score(y_test, y_test_pred))
        adj_r2 = float(calculate_adjusted_r2(test_r2, n_test, p_feats))
        
        mae = float(mean_absolute_error(y_test, y_test_pred))
        mse = float(mean_squared_error(y_test, y_test_pred))
        rmse = float(np.sqrt(mse))
        mape = float(mean_absolute_percentage_error(y_test, y_test_pred)) * 100.0
        
        cv_scores = cross_val_score(model, scaler.transform(X), y, cv=5, scoring='r2')
        cv_mean = float(np.mean(cv_scores))
        
        accuracy_pct = float(max(0.0, min(100.0, (1 - (mae / (y_test.mean() + 1e-5))) * 100)))
        
        res_entry = {
            'model_name': name,
            'train_r2': round(train_r2, 4),
            'test_r2': round(test_r2, 4),
            'adjusted_r2': round(adj_r2, 4),
            'cv_r2_score': round(cv_mean, 4),
            'mae': round(mae, 4),
            'mse': round(mse, 4),
            'rmse': round(rmse, 4),
            'mape': round(mape, 2),
            'accuracy_percentage': round(accuracy_pct, 2)
        }
        results.append(res_entry)
        trained_model_objects[name] = model

    # Sort results by test_r2 descending
    results = sorted(results, key=lambda x: x['test_r2'], reverse=True)
    best_model_name = results[0]['model_name']
    best_model_obj = trained_model_objects[best_model_name]
    
    # Save artifacts to root and models directory
    joblib.dump(best_model_obj, os.path.join(PROJECT_ROOT, 'model.pkl'))
    joblib.dump(scaler, os.path.join(PROJECT_ROOT, 'scaler.pkl'))
    joblib.dump(feature_cols, os.path.join(PROJECT_ROOT, 'feature_columns.pkl'))

    # Save to models/ folder as well
    models_dir = os.path.join(PROJECT_ROOT, 'models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    joblib.dump(best_model_obj, os.path.join(models_dir, 'best_model.pkl'))
    joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))
    joblib.dump(feature_cols, os.path.join(models_dir, 'feature_columns.pkl'))

    # Feature Importance of best model
    feature_importances = {}
    if hasattr(best_model_obj, 'feature_importances_'):
        importances = best_model_obj.feature_importances_
        for col, val in zip(feature_cols, importances):
            feature_importances[col] = float(val)
    elif hasattr(best_model_obj, 'coef_'):
        coefs = np.abs(best_model_obj.coef_)
        for col, val in zip(feature_cols, coefs):
            feature_importances[col] = float(val)
    else:
        for col in feature_cols:
            feature_importances[col] = 1.0 / len(feature_cols)
            
    # Normalize importances
    tot_imp = sum(feature_importances.values()) + 1e-5
    feature_importances = {k: round((v / tot_imp) * 100, 2) for k, v in feature_importances.items()}
    feature_importances = dict(sorted(feature_importances.items(), key=lambda x: x[1], reverse=True))

    # Actual vs Predicted data for best model
    best_y_pred = best_model_obj.predict(X_test_scaled)
    residuals = y_test - best_y_pred
    
    act_vs_pred = {
        'actual': [round(float(a), 2) for a in y_test.values],
        'predicted': [round(float(p), 2) for p in best_y_pred],
        'residuals': [round(float(r), 2) for r in residuals.values]
    }

    # Save model comparison summary JSON
    outputs_dir = os.path.join(PROJECT_ROOT, 'outputs')
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
        
    summary_data = {
        'best_model': best_model_name,
        'leaderboard': results,
        'feature_importances': feature_importances,
        'actual_vs_pred': act_vs_pred
    }
    
    with open(os.path.join(outputs_dir, 'model_comparison.json'), 'w') as f:
        json.dump(summary_data, f, indent=2)
        
    # Save leaderboard CSV
    pd.DataFrame(results).to_csv(os.path.join(outputs_dir, 'model_leaderboard.csv'), index=False)
    
    print(f"Model Training Complete! Best Model: {best_model_name} (Test R2: {results[0]['test_r2']})")
    return summary_data
