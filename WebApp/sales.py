# sales.py
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
import random
from path_utils import get_model_path, get_data_path

# Generate sales forecast for the given store and item
def run_sales_forecast(store_id, item_id):
    # Path to the sales model
    sales_model_path = get_model_path('sales_model.pkl')
    sales_model = None
    
    # Try to load the model
    if os.path.exists(sales_model_path):
        try:
            with open(sales_model_path, 'rb') as f:
                sales_model = pickle.load(f)
        except Exception as e:
            print(f"Error loading sales model: {e}. Using fallback approach.")
    else:
        print(f"Sales model not found at {sales_model_path}. Using fallback approach.")
    
    # Generate dates from January 1 to July 31
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 7, 31)
    date_range = pd.date_range(start=start_date, end=end_date)
    
    # Build feature set
    features = []
    for date in date_range:
        features.append({
            'Date': date,
            'Month': date.month,
            'Day': date.day,
            'DayOfWeek': date.dayofweek,
            'StoreID': store_id,
            'ItemID': item_id,
            'IsWeekend': 1 if date.dayofweek >= 5 else 0,
            'IsHoliday': 0  # Simplified
        })
    
    feature_df = pd.DataFrame(features)
    
    # Make predictions using model or fallback
    if sales_model and hasattr(sales_model, 'predict'):
        try:
            # Prepare features for the model
            X = feature_df[['Month', 'Day', 'DayOfWeek', 'IsWeekend', 'IsHoliday']].copy()
            
            # Add extra features that might be needed by the model
            X['StoreID'] = pd.to_numeric(store_id, errors='coerce')
            X['ItemID'] = pd.to_numeric(item_id, errors='coerce')
            
            # Try to predict using the model
            predictions = sales_model.predict(X)
            
            # Ensure predictions are positive integers
            predictions = np.maximum(1, np.round(predictions).astype(int))
        except Exception as e:
            print(f"Prediction error: {e}")
            # Fallback
            predictions = generate_fallback_predictions(feature_df)
    else:
        # Fallback to rule-based approach
        predictions = generate_fallback_predictions(feature_df)
    
    # Create the sales dataframe
    sales_data = pd.DataFrame({
        'StoreID': store_id,
        'ItemID': item_id,
        'SalesDate': feature_df['Date'].dt.strftime('%Y-%m-%d'),
        'SalesQuantity': predictions
    })
    
    # Save to CSV using absolute path
    sales_path = get_data_path('sales.csv')
    sales_data.to_csv(sales_path, index=False)
    
    return sales_data

def generate_fallback_predictions(df):
    """Generate fallback predictions using a rule-based approach"""
    predictions = []
    for i, row in df.iterrows():
        base_sales = random.randint(5, 15)
        
        # Weekend effect
        if 'IsWeekend' in row and row['IsWeekend'] == 1:
            base_sales = int(base_sales * 1.5)
        elif 'DayOfWeek' in row and row['DayOfWeek'] >= 5:
            base_sales = int(base_sales * 1.5)
            
        # Seasonal variation
        if 'Month' in row:
            month_factor = 1.0 + 0.1 * np.sin((row['Month'] - 1) * np.pi / 6)
            base_sales = int(base_sales * month_factor)
        
        predictions.append(max(1, base_sales))
    
    return np.array(predictions)