import os
import io
import json
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flasgger import Swagger

from utils.data_preprocessing import load_data, clean_data, engineer_features
from utils.business_insights import analyze_business_performance, optimize_budget_allocation, simulate_sales_forecast
from utils.db_helper import init_db, save_prediction, get_all_predictions, clear_prediction_history
from utils.model_trainer import train_and_evaluate_all
from utils.eda_generator import generate_eda_summary

app = Flask(__name__)
app.config['SECRET_KEY'] = 'enterprise-sales-ai-secret-key'

# Initialize Swagger
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "📈 AI Sales Prediction & Advertising Analytics API",
        "description": "Production REST API endpoints for predicting sales, optimizing advertising budgets, retrieving model benchmarks, and forecasting growth.",
        "version": "1.0.0"
    }
}
swagger = Swagger(app, template=swagger_template)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Global Model Loaded State
MODEL = None
SCALER = None
FEATURE_COLS = None

def load_artifacts():
    global MODEL, SCALER, FEATURE_COLS
    model_path = os.path.join(PROJECT_ROOT, 'model.pkl')
    scaler_path = os.path.join(PROJECT_ROOT, 'scaler.pkl')
    cols_path = os.path.join(PROJECT_ROOT, 'feature_columns.pkl')

    if not (os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(cols_path)):
        print("Model artifacts missing. Triggering automated model training...")
        train_and_evaluate_all()

    MODEL = joblib.load(model_path)
    SCALER = joblib.load(scaler_path)
    FEATURE_COLS = joblib.load(cols_path)
    print("Artifacts loaded successfully!")

# Initialize DB and Artifacts
init_db()
load_artifacts()

# Helper for feature dictionary creation
def build_feature_dataframe(tv, radio, newspaper):
    total_spend = tv + radio + newspaper
    eps = 1e-5
    
    tv_pct = (tv / (total_spend + eps)) * 100
    radio_pct = (radio / (total_spend + eps)) * 100
    newspaper_pct = (newspaper / (total_spend + eps)) * 100
    
    log_tv = np.log1p(tv)
    log_radio = np.log1p(radio)
    log_newspaper = np.log1p(newspaper)
    
    tv_x_radio = tv * radio
    tv_x_newspaper = tv * newspaper
    radio_x_newspaper = radio * newspaper
    
    tv_sq = tv ** 2
    radio_sq = radio ** 2
    
    feat_dict = {
        'TV': tv, 'Radio': radio, 'Newspaper': newspaper,
        'Total_Spend': total_spend,
        'TV_Pct': tv_pct, 'Radio_Pct': radio_pct, 'Newspaper_Pct': newspaper_pct,
        'Log_TV': log_tv, 'Log_Radio': log_radio, 'Log_Newspaper': log_newspaper,
        'TV_x_Radio': tv_x_radio, 'TV_x_Newspaper': tv_x_newspaper, 'Radio_x_Newspaper': radio_x_newspaper,
        'TV_sq': tv_sq, 'Radio_sq': radio_sq
    }
    
    df_feat = pd.DataFrame([feat_dict])
    df_feat = df_feat.reindex(columns=FEATURE_COLS, fill_value=0)
    return df_feat

# --------------------------------------------------------------------------
# ROUTES
# --------------------------------------------------------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# --------------------------------------------------------------------------
# API ENDPOINTS
# --------------------------------------------------------------------------

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Generate Sales Prediction
    ---
    tags:
      - Predictions
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            tv:
              type: number
              example: 150.0
            radio:
              type: number
              example: 25.0
            newspaper:
              type: number
              example: 15.0
    responses:
      200:
        description: Returns predicted sales, confidence level, and ROI analysis.
    """
    try:
        data = request.get_json() or {}
        tv = float(data.get('tv', 0))
        radio = float(data.get('radio', 0))
        newspaper = float(data.get('newspaper', 0))

        if tv < 0 or radio < 0 or newspaper < 0:
            return jsonify({'error': 'Advertising budgets cannot be negative.'}), 400

        df_feats = build_feature_dataframe(tv, radio, newspaper)
        scaled_feats = SCALER.transform(df_feats)
        predicted_sales = float(MODEL.predict(scaled_feats)[0])
        predicted_sales = max(0.0, round(predicted_sales, 2))

        # Insights
        insights = analyze_business_performance(tv, radio, newspaper, predicted_sales, MODEL, SCALER, FEATURE_COLS)
        
        # Save to SQLite Database
        confidence_str = f"[{round(predicted_sales*0.93, 2)}, {round(predicted_sales*1.07, 2)}]"
        rec_summary = "; ".join(insights['recommendations']) if insights['recommendations'] else "Balanced spend."
        save_prediction(tv, radio, newspaper, insights['total_spend'], predicted_sales, confidence_str, insights['roi_percentage'], rec_summary)

        return jsonify({
            'success': True,
            'predicted_sales': predicted_sales,
            'business_insights': insights
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/whatif', methods=['POST'])
def whatif():
    """
    Interactive What-If Scenario Prediction
    ---
    tags:
      - Predictions
    """
    try:
        data = request.get_json() or {}
        tv = float(data.get('tv', 0))
        radio = float(data.get('radio', 0))
        newspaper = float(data.get('newspaper', 0))

        df_feats = build_feature_dataframe(tv, radio, newspaper)
        scaled_feats = SCALER.transform(df_feats)
        predicted_sales = float(MODEL.predict(scaled_feats)[0])
        predicted_sales = max(0.0, round(predicted_sales, 2))

        total_spend = tv + radio + newspaper
        revenue_est = predicted_sales * 1000.0
        cost_est = total_spend * 1000.0
        roi_pct = round(((revenue_est - cost_est) / (cost_est + 1e-5)) * 100.0, 1)

        return jsonify({
            'predicted_sales': predicted_sales,
            'total_spend': round(total_spend, 2),
            'roi_percentage': roi_pct
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/optimize-budget', methods=['POST'])
def optimize_budget():
    """
    Calculate Optimal Budget Allocation
    ---
    tags:
      - Budget Optimizer
    """
    try:
        data = request.get_json() or {}
        target_budget = float(data.get('budget', 100.0))
        
        if target_budget <= 0:
            return jsonify({'error': 'Target budget must be greater than zero.'}), 400

        result = optimize_budget_allocation(target_budget, MODEL, SCALER, FEATURE_COLS)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/model-leaderboard', methods=['GET'])
def model_leaderboard():
    """
    Get Model Benchmarks & Comparison Leaderboard
    ---
    tags:
      - Models
    """
    comp_file = os.path.join(PROJECT_ROOT, 'outputs', 'model_comparison.json')
    if not os.path.exists(comp_file):
        train_and_evaluate_all()

    with open(comp_file, 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/api/eda-data', methods=['GET'])
def eda_data():
    """
    Get Preprocessed Dataset Summary & Correlations
    ---
    tags:
      - EDA
    """
    df = load_data('advertising.csv')
    df_clean, report = clean_data(df)
    summary = generate_eda_summary(df_clean)
    return jsonify(summary)

@app.route('/api/history', methods=['GET'])
def history():
    """
    Get SQLite Stored Prediction Logs
    ---
    tags:
      - Database History
    """
    logs = get_all_predictions(limit=50)
    return jsonify({'history': logs})

@app.route('/api/forecast', methods=['GET'])
def forecast():
    """
    Simulate Sales Growth Forecast Timeline
    ---
    tags:
      - Forecasting
    """
    base_sales = float(request.args.get('base_sales', 15.0))
    days = int(request.args.get('days', 180))
    result = simulate_sales_forecast(base_sales, days)
    return jsonify(result)

@app.route('/api/retrain', methods=['POST'])
def retrain():
    """
    Trigger Online Model Retraining
    ---
    tags:
      - Models
    """
    try:
        summary = train_and_evaluate_all()
        load_artifacts()
        return jsonify({
            'success': True,
            'message': 'All 9 ML models retrained successfully!',
            'champion_model': summary['best_model']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --------------------------------------------------------------------------
# EXPORT ENDPOINTS
# --------------------------------------------------------------------------

@app.route('/export/excel')
def export_excel():
    logs = get_all_predictions(limit=500)
    df_history = pd.DataFrame(logs)
    
    comp_file = os.path.join(PROJECT_ROOT, 'outputs', 'model_comparison.json')
    if os.path.exists(comp_file):
        with open(comp_file, 'r') as f:
            comp_data = json.load(f)
        df_models = pd.DataFrame(comp_data.get('leaderboard', []))
    else:
        df_models = pd.DataFrame()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_history.to_excel(writer, sheet_name='Prediction History', index=False)
        if not df_models.empty:
            df_models.to_excel(writer, sheet_name='Model Leaderboard', index=False)

    output.seek(0)
    return send_file(output, download_name='SalesAI_Analytics_Report.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/export/pdf')
def export_pdf():
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#3b82f6'), spaceAfter=12)
    story.append(Paragraph("📈 AI Sales Prediction & Analytics - Executive Report", title_style))
    story.append(Spacer(1, 10))

    comp_file = os.path.join(PROJECT_ROOT, 'outputs', 'model_comparison.json')
    if os.path.exists(comp_file):
        with open(comp_file, 'r') as f:
            comp_data = json.load(f)
        
        best_m = comp_data.get('best_model', 'N/A')
        story.append(Paragraph(f"<b>Champion Model Selected:</b> {best_m}", styles['Normal']))
        story.append(Spacer(1, 10))

        leaderboard = comp_data.get('leaderboard', [])
        if leaderboard:
            table_data = [['Model', 'Test R²', 'RMSE', 'MAE', 'Accuracy %']]
            for row in leaderboard:
                table_data.append([
                    row['model_name'],
                    str(row['test_r2']),
                    f"${row['rmse']}k",
                    f"${row['mae']}k",
                    f"{row['accuracy_percentage']}%"
                ])
            
            t = Table(table_data, colWidths=[160, 80, 80, 80, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
                ('ALIGN', (1,0), (-1,-1), 'CENTER')
            ]))
            story.append(t)

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, download_name='SalesAI_Executive_Report.pdf', as_attachment=True, mimetype='application/pdf')

if __name__ == '__main__':
    print("Launching AI Sales Prediction & Advertising Analytics Server on http://127.0.0.1:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
