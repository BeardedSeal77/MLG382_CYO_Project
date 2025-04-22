# app.py
import os
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as fig
from layout import create_layout
from callback import process_selection
from path_utils import BASE_DIR

app = dash.Dash(__name__, assets_folder=os.path.join(BASE_DIR, "assets"), suppress_callback_exceptions=True)
server = app.server
app.title = "DL Model Dashboard"
app.layout = create_layout()

# Register callbacks
@app.callback(
    [Output('inventory-graph', 'figure'),
     Output('sales-graph', 'figure'),
     Output('purchases-graph', 'figure'),
     Output('results-container', 'children'),
     Output('loading-output', 'children')],
    [Input('submit-button', 'n_clicks')],
    [State('store-dropdown', 'value'),
     State('item-dropdown', 'value')]
)
def update_graphs(n_clicks, store_id, item_id):
    if n_clicks is None or store_id is None or item_id is None:
        # Return empty figures for initial load
        empty_fig = fig.Figure().update_layout(
            title="No data to display",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Value")
        )
        return empty_fig, empty_fig, empty_fig, html.Div("Select store and item, then click Submit"), ""
    
    # Process the selection and generate the data
    inventory_fig, sales_fig, purchases_fig, results_text = process_selection(store_id, item_id)
    
    return inventory_fig, sales_fig, purchases_fig, results_text, ""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True, host='0.0.0.0', port=port)