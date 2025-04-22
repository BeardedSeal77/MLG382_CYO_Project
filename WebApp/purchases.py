# purchases.py
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
import random
from path_utils import get_model_path, get_data_path

# Generate purchase orders based on inventory levels
def apply_purchase_strategy(inventory_df, store_id, item_id):
    # Path to the leadtime model
    leadtime_model_path = get_model_path('leadtime_model.pkl')
    
    # Create a dummy leadtime model if the file doesn't exist
    if not os.path.exists(leadtime_model_path):
        # Create a dummy model that outputs random values
        class DummyLeadTimeModel:
            def predict(self, X):
                return np.random.randint(3, 10, size=len(X))
        
        dummy_model = DummyLeadTimeModel()
        with open(leadtime_model_path, 'wb') as f:
            pickle.dump(dummy_model, f)
    
    # Load the leadtime model
    try:
        with open(leadtime_model_path, 'rb') as f:
            leadtime_model = pickle.load(f)
    except Exception as e:
        print(f"Error loading leadtime model: {e}. Using fallback approach.")
        leadtime_model = None
    
    # Initialize purchases dataframe
    purchases_data = []
    
    # Set bottom line (reorder point) and standard order quantity
    bottomline = 20  # Reorder point
    standard_order_quantity = 50  # Always order 50 items as specified
    
    # Sort inventory by date
    inventory_df = inventory_df.sort_values(by='Date')
    
    if inventory_df.empty:
        return pd.DataFrame(), inventory_df
    
    # Convert dates to datetime for easier manipulation
    inventory_df['DateObj'] = pd.to_datetime(inventory_df['Date'])
    
    # Find dates when stock goes below bottomline
    below_bottomline = inventory_df[inventory_df['StockLevel'] < bottomline]
    
    # Track days we've already placed orders
    order_dates = set()
    
    if not below_bottomline.empty:
        # Get the earliest date when stock goes below bottomline
        for _, row in below_bottomline.iterrows():
            issue_date = row['DateObj']
            
            # Use a consistent lead time for this store-item combination
            lead_time_days = predict_lead_time(leadtime_model, store_id, item_id, standard_order_quantity)
            
            # Calculate when we need to place the order
            order_date = issue_date - timedelta(days=lead_time_days)
            
            # Skip if we've already placed an order within 7 days of this order date
            if any(abs((order_date - pd.to_datetime(od)).days) < 7 for od in order_dates):
                continue
            
            # Format dates as strings
            order_date_str = order_date.strftime('%Y-%m-%d')
            receive_date_str = (order_date + timedelta(days=lead_time_days)).strftime('%Y-%m-%d')
            
            # Add to order dates set
            order_dates.add(order_date_str)
            
            # Create purchase order entry
            purchases_data.append({
                'StoreID': store_id,
                'ItemID': item_id,
                'PODate': order_date_str,
                'ReceivingDate': receive_date_str,
                'Quantity': standard_order_quantity
            })
            
            # Add purchase order to inventory ledger on order date (not affecting stock)
            inventory_df = pd.concat([inventory_df, pd.DataFrame([{
                'Date': order_date_str,
                'DateObj': order_date,
                'StoreID': store_id,
                'ItemID': item_id,
                'TranType': 'PurchaseOrder',
                'Quantity': 0,  # Order doesn't affect stock immediately
                'StockLevel': 0  # Will be recalculated
            }])], ignore_index=True)
            
            # Add stock receipt to inventory ledger on receiving date
            inventory_df = pd.concat([inventory_df, pd.DataFrame([{
                'Date': receive_date_str,
                'DateObj': order_date + timedelta(days=lead_time_days),
                'StoreID': store_id,
                'ItemID': item_id,
                'TranType': 'Purchase',
                'Quantity': standard_order_quantity,  # Stock increases on receiving date
                'StockLevel': 0  # Will be recalculated
            }])], ignore_index=True)
    
    # Convert to DataFrame
    purchases_df = pd.DataFrame(purchases_data) if purchases_data else pd.DataFrame(columns=['StoreID', 'ItemID', 'PODate', 'ReceivingDate', 'Quantity'])
    
    # Save to CSV using absolute path
    purchases_path = get_data_path('purchases.csv')
    purchases_df.to_csv(purchases_path, index=False)
    
    # Resort inventory by date (after adding purchases)
    inventory_df = inventory_df.sort_values(by='DateObj')
    
    # Remove temporary DateObj column
    original_columns = [col for col in inventory_df.columns if col != 'DateObj']
    inventory_df = inventory_df[original_columns]
    
    # Recalculate stock levels
    if not inventory_df.empty:
        current_stock = inventory_df.iloc[0]['StockLevel']
        for i, row in inventory_df.iloc[1:].iterrows():
            current_stock += row['Quantity']
            inventory_df.at[i, 'StockLevel'] = current_stock
    
    return purchases_df, inventory_df

def predict_lead_time(model, store_id, item_id, quantity):
    """Predict lead time using the model with direct features (no one-hot encoding)"""
    if model is None:
        return random.randint(3, 10)
    
    try:
        # Current date for feature extraction
        current_date = datetime.now()
        
        # Create DataFrame with the correct features that match the model training
        features_df = pd.DataFrame(columns=[
            'ItemID', 'StoreID', 'Quantity', 'Week', 'Month', 'Day'
        ])
        
        # Add a row with the actual values
        features_df.loc[0] = [
            int(item_id) if str(item_id).isdigit() else 0,
            int(store_id) if str(store_id).isdigit() else 0,
            quantity,
            current_date.isocalendar()[1],  # ISO week number
            current_date.month,
            current_date.weekday()  # Day of the week (0-6)
        ]
        
        # Predict lead time using the model
        lead_time_days = int(model.predict(features_df)[0])
        
        # Ensure lead time is reasonable (between 3 and 14 days)
        lead_time_days = max(3, min(lead_time_days, 14))
        
        return lead_time_days
    
    except Exception as e:
        print(f"Lead time prediction error: {e}. Using fallback approach.")
        return random.randint(3, 10)