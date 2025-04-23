# data_loader.py
import pandas as pd
import os
# change these imports between render and local
from WebApp.path_utils import get_data_path

# Load the opening stock data using store_id and item_id
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
            'startDate': '2024-12-31'
        }
        
        # Add to the CSV
        opening_stock = pd.concat([opening_stock, pd.DataFrame([default_data])], ignore_index=True)
        opening_stock.to_csv(opening_stock_path, index=False)
        
        return default_data
    
    # Return the first matching row as a dictionary
    return filtered_data.iloc[0].to_dict()

# Load the store data using absolute path
def load_store_data():
    store_path = get_data_path('Stores.csv')
    print(f"Loading store data from: {store_path}")
    return pd.read_csv(store_path)

# Load the inventory data using absolute path
def load_inventory_items():
    inventory_path = get_data_path('Inventory.csv')
    print(f"Loading inventory data from: {inventory_path}")
    df = pd.read_csv(inventory_path)
    print(f"Loaded inventory columns: {df.columns.tolist()}")
    return df

# Copy the PKL model files from model training directory to the website directory
def copy_model_files(model_name):
    # Model Names: sales_model.pkl, leadtime_model.pkl

    # copy the model_name from "../Artifacts/Models/"
    # to "../WebApp/Models/"
    model_path = os.path.join('..', 'Artifacts', 'Models', model_name)
    dest_path = os.path.join('..', 'WebApp', 'Models', model_name)
    print(f"Copying model from {model_path} to {dest_path}")
    if os.path.exists(model_path):
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(model_path, 'rb') as fsrc:
            with open(dest_path, 'wb') as fdst:
                fdst.write(fsrc.read())
    else:
        print(f"Model file {model_path} does not exist.")