# callback.py
import pandas as pd
from dash import html
import plotly.express as px
import datetime
import os
# change these imports between render and local
from WebApp.sales import run_sales_forecast
from WebApp.ledger import build_inventory_ledger
from WebApp.purchases import apply_purchase_strategy
from WebApp.data_loader import get_opening_stock, load_inventory_items, load_store_data
from WebApp.path_utils import get_data_path, DATA_DIR, MODELS_DIR

# Orchestrates the backend steps when a form is submitted
# API endpoint to process the selection of store and item
# This function is called when the user selects a store and item from the dropdowns
def process_selection(store_id, item_id):
    # Create directories if they don't exist
    for directory in [DATA_DIR, MODELS_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    # Load item and store details for display purposes
    items_df = load_inventory_items()
    stores_df = load_store_data()
    
    item_desc = items_df[items_df['ItemID'] == item_id]['Description'].iloc[0] if not items_df[items_df['ItemID'] == item_id].empty else f"Item {item_id}"
    store_loc = stores_df[stores_df['StoreID'] == store_id]['Location'].iloc[0] if not stores_df[stores_df['StoreID'] == store_id].empty else f"Store {store_id}"
    
    # Step 1: Get the opening stock and create inventory entry
    opening_stock_data = get_opening_stock(store_id, item_id)
    
    # Step 2: Generate sales forecast
    sales_data = run_sales_forecast(store_id, item_id)
    
    # Step 3: Build inventory ledger with sales data
    inventory_data = build_inventory_ledger(opening_stock_data, sales_data)
    
    # Step 4: Generate purchase orders based on inventory levels
    purchases_data, updated_inventory = apply_purchase_strategy(inventory_data, store_id, item_id)
    
    # Sort inventory data by date
    sorted_inventory = updated_inventory.sort_values(by='Date')
    inventory_path = get_data_path('inventoryLedger.csv')
    sorted_inventory.to_csv(inventory_path, index=False)
    
    # Create the inventory graph
    inventory_fig = px.line(
        sorted_inventory, 
        x='Date', 
        y='StockLevel',
        title=f'Inventory Levels for {store_loc}, Item {item_id} - {item_desc}'
    )
    inventory_fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Stock Level'
    )
    
    # Create the sales graph
    sales_path = get_data_path('sales.csv')
    sales_df = pd.read_csv(sales_path)
    sales_df = sales_df[(sales_df['StoreID'] == store_id) & (sales_df['ItemID'] == item_id)]
    sales_fig = px.bar(
        sales_df, 
        x='SalesDate', 
        y='SalesQuantity',
        title=f'Sales Forecast for {store_loc}, Item {item_id} - {item_desc}'
    )
    sales_fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Sales Quantity'
    )
    
    # Create the purchases graph
    purchases_path = get_data_path('purchases.csv')
    purchases_df = pd.read_csv(purchases_path)
    purchases_df = purchases_df[(purchases_df['StoreID'] == store_id) & (purchases_df['ItemID'] == item_id)]
    purchases_fig = px.scatter(
        purchases_df, 
        x='PODate', 
        y='Quantity',
        size='Quantity',
        title=f'Purchase Orders for {store_loc}, Item {item_id} - {item_desc}'
    )
    purchases_fig.update_layout(
        xaxis_title='Purchase Order Date',
        yaxis_title='Order Quantity'
    )
    
    # Create a text summary
    total_sales = sales_df['SalesQuantity'].sum()
    total_purchases = purchases_df['Quantity'].sum()
    final_stock = sorted_inventory.iloc[-1]['StockLevel'] if not sorted_inventory.empty else 0
    
    results_text = html.Div([
        html.H3(f"Forecast Summary for {store_loc}, {item_desc}"),
        html.P(f"Total sales forecast: {total_sales} units"),
        html.P(f"Total purchases planned: {total_purchases} units"),
        html.P(f"Final stock level: {final_stock} units"),
        html.P(f"Simulation period: Jan 1 - July 31, 2025")
    ])
    
    return inventory_fig, sales_fig, purchases_fig, results_text