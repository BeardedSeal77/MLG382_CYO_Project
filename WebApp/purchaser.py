# purchaser.py
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
import random
from path_utils import get_model_path, get_data_path

def apply_purchase_strategy(inventory_df, store_id, item_id):
    """Generate purchase orders based on inventory levels"""
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
    
    # Set reorder point and order quantity
    reorder_point = 10
    standard_order_quantity = 50
    
    # Sort inventory by date
    inventory_df = inventory_df.sort_values(by='Date')
    
    # Track if we already have a pending order
    pending_order = False
    next_delivery_date = None
    
    # Loop through inventory entries
    for i, row in inventory_df.iterrows():
        current_date = datetime.strptime(row['Date'], '%Y-%m-%d')
        
        # Check if we have a pending delivery on this date
        if next_delivery_date and current_date.strftime('%Y-%m-%d') == next_delivery_date:
            pending_order = False
        
        # If stock level is below reorder point and no pending order
        if row['StockLevel'] < reorder_point and not pending_order:
            # Predict lead time
            if leadtime_model:
                # In a real scenario, we would prepare proper features for the model
                lead_time_days = int(leadtime_model.predict([[
                    int(store_id) if str(store_id).isdigit() else 1,
                    int(item_id) if str(item_id).isdigit() else 1,
                    current_date.month,
                    current_date.day
                ]])[0])
            else:
                # Fallback to random lead time between 3-10 days
                lead_time_days = random.randint(3, 10)
            
            # Calculate receiving date
            receiving_date = current_date + timedelta(days=lead_time_days)
            receiving_date_str = receiving_date.strftime('%Y-%m-%d')
            po_date_str = current_date.strftime('%Y-%m-%d')
            
            # Create purchase order
            purchases_data.append({
                'StoreID': store_id,
                'ItemID': item_id,
                'PODate': po_date_str,
                'ReceivingDate': receiving_date_str,
                'Quantity': standard_order_quantity
            })
            
            # Add to inventory ledger
            inventory_df = pd.concat([inventory_df, pd.DataFrame([{
                'Date': receiving_date_str,
                'StoreID': store_id,
                'ItemID': item_id,
                'TranType': 'Purchase',
                'Quantity': standard_order_quantity,
                'StockLevel': row['StockLevel'] + standard_order_quantity  # This is approximate
            }])], ignore_index=True)
            
            # Set pending order flag and next delivery date
            pending_order = True
            next_delivery_date = receiving_date_str
    
    # Convert to DataFrame
    purchases_df = pd.DataFrame(purchases_data)
    
    # Save to CSV using absolute path
    purchases_path = get_data_path('purchases.csv')
    purchases_df.to_csv(purchases_path, index=False)
    
    # Resort inventory by date (after adding purchases)
    inventory_df = inventory_df.sort_values(by='Date')
    
    # Recalculate stock levels
    current_stock = inventory_df.iloc[0]['StockLevel']
    for i, row in inventory_df.iloc[1:].iterrows():
        current_stock += row['Quantity']
        inventory_df.at[i, 'StockLevel'] = current_stock
    
    return purchases_df, inventory_df