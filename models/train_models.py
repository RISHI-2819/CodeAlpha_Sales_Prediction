import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.model_trainer import train_and_evaluate_all
from utils.eda_generator import generate_eda_summary
from utils.data_preprocessing import load_data, clean_data

if __name__ == '__main__':
    print("=" * 60)
    print("Starting AI Sales Prediction & Analytics Model Training")
    print("=" * 60)
    
    # 1. Run EDA
    df = load_data('advertising.csv')
    df_clean, report = clean_data(df)
    eda_summary = generate_eda_summary(df_clean)
    print("EDA Summary Generated Successfully.")
    
    # 2. Run Model Training Pipeline
    summary = train_and_evaluate_all()
    print("All models trained and serialized cleanly!")
