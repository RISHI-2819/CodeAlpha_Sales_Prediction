import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
import os

def load_data(filepath='advertising.csv'):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset standard path {filepath} not found.")
    df = pd.read_csv(filepath)
    # Remove unnamed index column if present
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    return df

def clean_data(df):
    report = {}
    
    # 1. Missing Values
    null_counts = df.isnull().sum().to_dict()
    report['null_counts'] = null_counts
    df = df.dropna()
    
    # 2. Duplicates
    dup_count = int(df.duplicated().sum())
    report['duplicates_removed'] = dup_count
    df = df.drop_duplicates()
    
    # 3. Outlier detection (IQR method)
    outliers = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outlier_count = int(((df[col] < lower_bound) | (df[col] > upper_bound)).sum())
        outliers[col] = {
            'q1': float(Q1), 'q3': float(Q3), 'iqr': float(IQR),
            'lower': float(lower_bound), 'upper': float(upper_bound),
            'count': outlier_count
        }
    report['outliers'] = outliers
    
    return df, report

def engineer_features(df):
    df_feat = df.copy()
    
    # Core Spend Metrics
    df_feat['Total_Spend'] = df_feat['TV'] + df_feat['Radio'] + df_feat['Newspaper']
    
    # Channel Budget Distribution Percentages
    eps = 1e-5
    df_feat['TV_Pct'] = (df_feat['TV'] / (df_feat['Total_Spend'] + eps)) * 100
    df_feat['Radio_Pct'] = (df_feat['Radio'] / (df_feat['Total_Spend'] + eps)) * 100
    df_feat['Newspaper_Pct'] = (df_feat['Newspaper'] / (df_feat['Total_Spend'] + eps)) * 100
    
    # Log Transformations
    df_feat['Log_TV'] = np.log1p(df_feat['TV'])
    df_feat['Log_Radio'] = np.log1p(df_feat['Radio'])
    df_feat['Log_Newspaper'] = np.log1p(df_feat['Newspaper'])
    
    # Interaction Features
    df_feat['TV_x_Radio'] = df_feat['TV'] * df_feat['Radio']
    df_feat['TV_x_Newspaper'] = df_feat['TV'] * df_feat['Newspaper']
    df_feat['Radio_x_Newspaper'] = df_feat['Radio'] * df_feat['Newspaper']
    
    # Quadratic / Polynomial Terms
    df_feat['TV_sq'] = df_feat['TV'] ** 2
    df_feat['Radio_sq'] = df_feat['Radio'] ** 2
    
    if 'Sales' in df_feat.columns:
        df_feat['Ad_Efficiency'] = df_feat['Sales'] / (df_feat['Total_Spend'] + eps)
        # Sales in $k units, Spend in $k
        df_feat['ROI_Score'] = ((df_feat['Sales'] * 1000 - df_feat['Total_Spend'] * 1000) / (df_feat['Total_Spend'] * 1000 + eps)) * 100

    return df_feat

def calculate_vif(df_features):
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    numeric_df = df_features.select_dtypes(include=[np.number]).copy()
    if 'Sales' in numeric_df.columns:
        numeric_df = numeric_df.drop(columns=['Sales'])
    
    # Fill any missing values or infinities
    numeric_df = numeric_df.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    vif_data = pd.DataFrame()
    vif_data["Feature"] = numeric_df.columns
    try:
        vif_data["VIF"] = [variance_inflation_factor(numeric_df.values, i) for i in range(numeric_df.shape[1])]
    except Exception:
        vif_data["VIF"] = [1.0 for _ in range(numeric_df.shape[1])]
    return vif_data.to_dict(orient='records')

def get_feature_importance_ranking(X, y):
    # Mutual Info & SelectKBest Scores
    selector = SelectKBest(score_func=f_regression, k='all')
    selector.fit(X, y)
    
    mi = mutual_info_regression(X, y, random_state=42)
    
    rank_df = pd.DataFrame({
        'Feature': X.columns,
        'F_Score': selector.scores_,
        'Mutual_Info': mi
    }).sort_values(by='Mutual_Info', ascending=False)
    
    return rank_df.to_dict(orient='records')
