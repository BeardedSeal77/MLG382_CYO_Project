# data_loader.py
import pandas as pd
import os
from path_utils import get_data_path

def get_opening_stock(store_id, item_id):
    # Load the opening stock data using absolute path
    opening_stock_path = get_data_path('OpeningStock.csv')
    print(f"Loading opening stock from: {opening_stock_path}")
    opening_stock = pd.read_csv(opening_stock_path)
    
    # Filter for the requested store and item
    filtered_data = opening_stock[(opening_stock['StoreID'] == store_id) & 
                                 (opening_stock['ItemID'] == item_id)]
    
    # If no data found, create a default entry
    if filtered_data.empty:
        default_data = {
            'StoreID': store_id,
            'ItemID': item_id,
            'onHand': 100,  # Default starting inventory
            'startDate': '2025-01-01'
        }
        
        # Add to the CSV
        opening_stock = pd.concat([opening_stock, pd.DataFrame([default_data])], ignore_index=True)
        opening_stock.to_csv(opening_stock_path, index=False)
        
        return default_data
    
    # Return the first matching row as a dictionary
    return filtered_data.iloc[0].to_dict()

def load_store_data():
    # Load the store data using absolute path
    store_path = get_data_path('Stores.csv')
    print(f"Loading store data from: {store_path}")
    return pd.read_csv(store_path)

def load_inventory_items():
    # Load the inventory data using absolute path
    inventory_path = get_data_path('Inventory.csv')
    print(f"Loading inventory data from: {inventory_path}")
    df = pd.read_csv(inventory_path)
    print(f"Loaded inventory columns: {df.columns.tolist()}")
    return df