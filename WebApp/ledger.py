# ledger.py
import pandas as pd
import os
# change these imports between render and local
from path_utils import get_data_path

def build_inventory_ledger(opening_stock_data, sales_data):
    """Build the inventory ledger with opening stock and sales transactions"""
    # Initialize inventory ledger
    inventory_data = []
    
    # Add opening stock entry
    start_date = opening_stock_data['startDate']
    on_hand = opening_stock_data['onHand']
    store_id = opening_stock_data['StoreID']
    item_id = opening_stock_data['ItemID']
    
    inventory_data.append({
        'Date': start_date,
        'StoreID': store_id,
        'ItemID': item_id,
        'TranType': 'Opening',
        'Quantity': on_hand,
        'StockLevel': on_hand
    })
    
    # Current stock level
    current_stock = on_hand
    
    # Add sales transactions
    for _, sale in sales_data.iterrows():
        sale_quantity = sale['SalesQuantity']
        sale_date = sale['SalesDate']
        
        # Subtract from stock level
        current_stock -= sale_quantity
        
        # Add to inventory ledger
        inventory_data.append({
            'Date': sale_date,
            'StoreID': store_id,
            'ItemID': item_id,
            'TranType': 'Sale',
            'Quantity': -sale_quantity,  # Negative because it's a reduction
            'StockLevel': current_stock
        })
    
    # Convert to DataFrame
    inventory_df = pd.DataFrame(inventory_data)
    
    # Save to CSV using absolute path
    inventory_path = get_data_path('inventoryLedger.csv')
    inventory_df.to_csv(inventory_path, index=False)
    
    return inventory_df