#import packages
import pandas as pd


# Load the csv files
"""
Inventory.csv:
-   ItemID - Gives the ItemID
-   Description - Gives the Item Description

OpeningStock.csv:
-   StoreID - StoreID
-   onHand - How Much Stock is on hand
-   startDate - 2015-12-31 stock taken for the start of 2016
-   ItemID - Gives the ItemID

Purchases.csv
-   StoreID - StoreID
-   PODate - Purchase Order Date
-   ReceivingDate - Order Revieved Date
-   Quantity - Quantity Recieved in Order
-   ItemID - Gives the ItemID 

Sales.csv
-   StoreID - StoreID
-   SalesQuantity - Quantity of item sold
-   SalesDate - Date that the sale took place
-   ItemID - Gives the ItemID 

Stores.csv
-   StoreID - StoreID
-   Location - Location of the store
"""

# load the data
inventory_df = pd.read_csv('../../Data/Processed/Inventory.csv')
opening_stock_df = pd.read_csv('../../Data/Processed/OpeningStock.csv')
purchases_df = pd.read_csv('../../Data/Processed/Purchases.csv')
sales_df = pd.read_csv('../../Data/Processed/Sales.csv')
stores_df = pd.read_csv('../../Data/Processed/Stores.csv')

# convert the date columns to datetime format
purchases_df['PODate'] = pd.to_datetime(purchases_df['PODate'])
purchases_df['ReceivingDate'] = pd.to_datetime(purchases_df['ReceivingDate'])
sales_df['SalesDate'] = pd.to_datetime(sales_df['SalesDate'])
opening_stock_df['startDate'] = pd.to_datetime(opening_stock_df['startDate'])



# ==================================================================================
# Create a lead_time_data.csv file
# This will be used to train a lead time model
def create_lead_time_data():
    """
    Lead_time_data.csv:
    Column Name     | Description
    PODate          | Date the item was ordered (purchases_df) (yyyy-mm-dd)
    ReceivingDate   | Date the item was received (purchases_df) (yyyy-mm-dd)
    LeadTimeDays    | Target = ReceivingDate - PODate (in days)
    ItemID          | Item identifier (purchases_df)
    Description     | Item description (inventory_df)
    StoreID         | Store identifier (purchases_df)
    Location        | Store location (stores_df)
    Quantity        | Quantity ordered (purchases_df)
    Week            | Week number of the PODate     (optional feature)
    Month           | Month of PODate               (optional feature)
    Day             | Day of week PODate was placed (optional feature)
"""
    # Create a new dataframe for lead time data
    lead_time_df = purchases_df.copy()

    # add the description and store location to the lead time data
    lead_time_df = lead_time_df.merge(inventory_df[['ItemID', 'Description']], on='ItemID', how='left')
    lead_time_df = lead_time_df.merge(stores_df[['StoreID', 'Location']], on='StoreID', how='left')

    # -----------------------------------------------------------------------------------
    # Feature Engineering

    # Calculate lead time in days
    lead_time_df['LeadTimeDays'] = (lead_time_df['ReceivingDate'] - lead_time_df['PODate']).dt.days

    # Add Week, Month, Day features
    lead_time_df['Week'] = lead_time_df['PODate'].dt.isocalendar().week
    lead_time_df['Month'] = lead_time_df['PODate'].dt.month
    lead_time_df['Day'] = lead_time_df['PODate'].dt.dayofweek

    # Rearrange the columns accoring to required csv file format
    lead_time_df = lead_time_df[[
        'PODate', 
        'ReceivingDate', 
        'LeadTimeDays', 
        'ItemID', 
        'Description', 
        'StoreID', 
        'Location', 
        'Quantity', 
        'Week', 
        'Month', 
        'Day'
        ]]

    # Save lead_time_csv to prepped data folder
    lead_time_df.to_csv('../../Data/Prepped/lead_time_data.csv', index=False)

    # return lead_time_df for notebook to use
    return lead_time_df


# ==================================================================================
# Create a sales_forecast.csv file
# This will be used to train a lead time model
def create_sales_forecast_data():
    """
    Sales_forecast.csv:
    Column Name     | Description
    SalesDate       | Date of sale (daily or weekly aggregated)
    ItemID          | Item identifier
    StoreID         | Store identifier
    SalesQuantity   | Target: quantity sold
    Lag_1           | Sales one day/week before (optional)
    Lag_7           | Sales one week before (optional)
    RollingAvg_7    | 7-day rolling average (optional)
    Month           | Month of sale
    DayOfWeek       | Day of week of sale
    """

    # Create a new dataframe for sales forecast data
    sales_forecast_df = sales_df.copy()

    # add the description and store location to the sales forecast data
    sales_forecast_df = sales_forecast_df.merge(inventory_df[['ItemID', 'Description']], on='ItemID', how='left')
    sales_forecast_df = sales_forecast_df.merge(stores_df[['StoreID', 'Location']], on='StoreID', how='left')

    # -----------------------------------------------------------------------------------
    # Feature Engineering

    # Add Month, DayOfWeek features
    sales_forecast_df['Month'] = sales_forecast_df['SalesDate'].dt.month
    sales_forecast_df['DayOfWeek'] = sales_forecast_df['SalesDate'].dt.dayofweek

    # Lag features (1 day/week), temporal / short term trends
    # Lag features are used to capture the temporal dependencies in the data, they are the values of the target variable (SalesQuantity) from previous time steps.
    # 1 day before:
    sales_forecast_df['Lag_1'] = sales_forecast_df.groupby(['StoreID', 'ItemID'])['SalesQuantity'].shift(1)
    # 7 days before:
    sales_forecast_df['Lag_7'] = sales_forecast_df.groupby(['StoreID', 'ItemID'])['SalesQuantity'].shift(7)

    # Rolling average feature (7-day rolling average)
    # Smooths out short-term fluctuations and highlights longer-term trends or cycles.
    # Gives the model trend signal and helps to reduce noise in the data.
    sales_forecast_df['RollingAvg_7'] = sales_forecast_df.groupby(['StoreID', 'ItemID'])['SalesQuantity'].transform(
        lambda x: x.rolling(window=7).mean())

    # fill missing values with 0
    sales_forecast_df[['Lag_1', 'Lag_7', 'RollingAvg_7']] = sales_forecast_df[['Lag_1', 'Lag_7', 'RollingAvg_7']].fillna(0)

    # Rearrange the columns according to required csv file format
    sales_forecast_df = sales_forecast_df[[
        'SalesDate',
        'ItemID',
        'StoreID',
        'SalesQuantity',
        'Lag_1',
        'Lag_7',
        'RollingAvg_7',
        'Month',
        'DayOfWeek'
        ]]

    # Save lead_time_csv to prepped data folder
    sales_forecast_df.to_csv('../../Data/Prepped/sales_forecast_data.csv', index=False)

    # return lead_time_df for notebook to use
    return sales_forecast_df