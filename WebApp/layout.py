# layout.py
from dash import html, dcc
import pandas as pd
import os
# change these imports between render and local
from WebApp.data_loader import load_store_data, load_inventory_items

def create_layout():
    # Load store and item data for dropdowns
    stores_df = load_store_data()
    items_df = load_inventory_items()
    
    # Create dropdown options with descriptions
    store_options = [
        {'label': f"{row['StoreID']} - {row['Location']}", 'value': row['StoreID']} 
        for _, row in stores_df.iterrows()
    ]
    
    # Create dropdown options for items (there could be hundreds)
    item_options = [
        {'label': f"{row['ItemID']} - {row['Description']}", 'value': row['ItemID']} 
        for _, row in items_df.iterrows()
    ]
    
    return html.Div([
        html.H1("Inventory Management System", className="app-header"),
        
        html.Div([
            html.Div([
                html.Label("Select Store:"),
                dcc.Dropdown(
                    id='store-dropdown',
                    options=store_options,
                    placeholder="Select a Store"
                ),
            ], className="dropdown-container"),
            
            html.Div([
                html.Label("Select Item:"),
                dcc.Dropdown(
                    id='item-dropdown',
                    options=item_options,
                    placeholder="Select an Item",
                    style={'maxHeight': '200px'}
                ),
            ], className="dropdown-container"),
            
            html.Button('Run Forecast', id='submit-button', className="submit-button"),
            
            dcc.Loading(
                id="loading",
                type="circle",
                children=html.Div(id="loading-output")
            ),
        ], className="controls-container"),
        
        html.Div(id='results-container', className="results-text"),
        
        html.Div([
            html.H3("Inventory Levels Over Time"),
            dcc.Graph(id='inventory-graph')
        ], className="graph-container"),
        
        html.Div([
            html.H3("Sales Forecast"),
            dcc.Graph(id='sales-graph')
        ], className="graph-container"),
        
        html.Div([
            html.H3("Purchase Orders"),
            dcc.Graph(id='purchases-graph')
        ], className="graph-container"),
        
        html.Link(
            rel='stylesheet',
            href='/assets/styles.css'
        )
    ], className="app-container")