import pandas as pd
import pickle
import os
from datetime import datetime
from path_utils import get_model_path, get_data_path

# Generate sales forecast for the given store and item
def run_sales_forecast(store_id, item_id):
    # Path to the sales model
    sales_model_path = get_model_path('sales_model.pkl')
    sales_model = None
    
    # Try to load the model
    if os.path.exists(sales_model_path):
        with open(sales_model_path, 'rb') as f:
            sales_model = pickle.load(f)
    else:
        print(f"Sales model not found at {sales_model_path}. Using fallback approach.")
    
    # Generate dates from January 1 to July 31, 2025
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 7, 31)
    date_range = pd.date_range(start=start_date, end=end_date)
    
    # Build feature set with initial features that match the model training
    features = []
    for date in date_range:
        features.append({
            'SalesDate': date,
            'Month': date.month,
            'DayOfWeek': date.dayofweek,
            'DayOfMonth': date.day,
            'IsWeekend': 1 if date.dayofweek >= 5 else 0,
            'StoreID': store_id,
            'ItemID': item_id
        })
    
    feature_df = pd.DataFrame(features)
    
    # Make predictions using model
    if sales_model and hasattr(sales_model, 'predict'):
        predictions = []
        initial_sales = 10
        
        for i in range(len(feature_df)):
            lag_1 = predictions[i-1] if i > 0 else initial_sales
            lag_7 = predictions[i-7] if i >= 7 else initial_sales
            if i >= 7:
                rolling_avg_7 = sum(predictions[i-7:i]) / 7
            elif i > 0:
                rolling_avg_7 = sum(predictions[:i]) / i
            else:
                rolling_avg_7 = initial_sales
            
            row = feature_df.iloc[i]
            features = {
                'Lag_1': lag_1,
                'Lag_7': lag_7,
                'RollingAvg_7': rolling_avg_7,
                'Month': row['Month'],
                'DayOfWeek': row['DayOfWeek'],
                'DayOfMonth': row['DayOfMonth'],
                'IsWeekend': row['IsWeekend']
            }
            X_row = pd.DataFrame([features])
            
            pred = sales_model.predict(X_row)[0] #predict using the loaded model
            pred = max(1, int(round(pred)))
            predictions.append(pred)

        feature_df['SalesQuantity'] = predictions
 
    # Create the sales dataframe
    sales_data = pd.DataFrame({
        'StoreID': store_id,
        'ItemID': item_id,
        'SalesDate': feature_df['SalesDate'].dt.strftime('%Y-%m-%d'),
        'SalesQuantity': feature_df['SalesQuantity']
    })
    
    # Save to CSV using absolute path
    sales_path = get_data_path('sales.csv')
    sales_data.to_csv(sales_path, index=False)
    
    return sales_data