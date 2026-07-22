import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

def ensure_output_dir():
    if not os.path.exists(OUTPUTS_DIR):
        os.makedirs(OUTPUTS_DIR)

def generate_eda_summary(df):
    ensure_output_dir()
    
    summary = {
        'num_samples': int(len(df)),
        'num_columns': int(len(df.columns)),
        'stats': df.describe().to_dict(),
        'correlations': df.corr().to_dict()
    }
    
    # Save correlation heatmap image
    plt.figure(figsize=(8, 6))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Advertising vs Sales Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS_DIR, 'correlation_heatmap.png'), dpi=300)
    plt.close()

    # Save Scatter Plot matrix / channel vs sales
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    channels = ['TV', 'Radio', 'Newspaper']
    colors = ['#4f46e5', '#10b981', '#f59e0b']
    
    for i, ch in enumerate(channels):
        if ch in df.columns:
            sns.regplot(x=ch, y='Sales', data=df, ax=axes[i], color=colors[i], scatter_kws={'alpha':0.6})
            axes[i].set_title(f'{ch} Spend vs Sales')
            axes[i].set_xlabel(f'{ch} Budget ($k)')
            axes[i].set_ylabel('Sales ($k units)')
            axes[i].grid(True, linestyle='--', alpha=0.5)
            
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS_DIR, 'channels_vs_sales.png'), dpi=300)
    plt.close()
    
    # Distributions plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    cols = ['TV', 'Radio', 'Newspaper', 'Sales']
    for i, col in enumerate(cols):
        r, c = i // 2, i % 2
        sns.histplot(df[col], kde=True, ax=axes[r, c], color='#3b82f6', bins=15)
        axes[r, c].set_title(f'Distribution of {col}')
        axes[r, c].grid(True, linestyle='--', alpha=0.5)
        
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS_DIR, 'distributions.png'), dpi=300)
    plt.close()

    return summary
