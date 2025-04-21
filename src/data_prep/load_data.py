# ==================================================================================

## Step 1) Import Libraries
#Libraries
import os
import shutil
import pandas as pd
import kagglehub



# ==================================================================================
# Method that allows the user to choose to download the dataset and/or process the data
# The function will download the dataset if the download parameter is set to True
# The function will process the data if the process parameter is set to True
# The function will return a dictionary containing all processed DataFrames
def run_inventory_analysis(download=False, process=True):
    raw_path = '../../Data/Raw/'
    processed_path = '../../Data/Processed/'
    
    if download:
        download_dataset(raw_path)
    
    if process:
        return process_all_data(raw_path, processed_path, download=False)
    
    return {}

# ==================================================================================
# Process Dataset
# main function to process all data files
# returns tuple containing all processed DataFrames
def process_all_data(raw_path='../../Data/Raw/', processed_path='../../Data/Processed/', download=False):
    # Step 1: Download dataset if required
    if download:
        raw_path = download_dataset(raw_path)
    
    # Step 2: Create processed directory if it doesn't exist
    os.makedirs(processed_path, exist_ok=True)
    
    # Load original DataFrames for later use in creating the inventory master
    sales_file = os.path.join(raw_path, 'SalesFINAL12312016.csv')
    sales_df_orig = pd.read_csv(sales_file)
    
    purchases_file = os.path.join(raw_path, 'PurchasesFINAL12312016.csv')
    purchases_df_orig = pd.read_csv(purchases_file)
    
    opening_stock_file = os.path.join(raw_path, 'BegInvFINAL12312016.csv')
    opening_stock_df_orig = pd.read_csv(opening_stock_file)
    
    # Step 3: Process each dataset
    print("Processing sales data...")
    sales_cleaned = process_sales_data(raw_path, processed_path)
    
    print("Processing purchases data...")
    purchases_cleaned = process_purchases_data(raw_path, processed_path)
    
    print("Processing opening stock data...")
    opening_stock_cleaned = process_opening_stock_data(raw_path, processed_path)
    
    print("Creating inventory master...")
    inventory_df = create_inventory_master(sales_df_orig, purchases_df_orig, opening_stock_df_orig, processed_path)
    
    print("Creating stores file...")
    stores_df = create_stores_file(raw_path, processed_path)
    
    print("All processing complete!")
    
    return {
        'sales': sales_cleaned,
        'purchases': purchases_cleaned,
        'opening_stock': opening_stock_cleaned,
        'inventory': inventory_df,
        'stores': stores_df
    }


# ==================================================================================
# Download Dataset

# Download dataset from Kaggle and move it to the target directory
def download_dataset(target_dir="../../Data/Raw"):
    # Download the dataset
    print("Downloading dataset...")
    download_path = kagglehub.dataset_download("bhanupratapbiswas/inventory-analysis-case-study")
    
    # Make sure the target directory exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Move all files (not folders) from download_path to target_dir
    for filename in os.listdir(download_path):
        src = os.path.join(download_path, filename)
        dst = os.path.join(target_dir, filename)
        
        if os.path.isfile(src):
            shutil.move(src, dst)
    
    print(f"Files moved to: {target_dir}")
    return target_dir


# ==================================================================================
# Create Clean CSV files

# Splits the composite InventoryId column into Store, Location, and ItemId columns.
# Returns a DataFrame with split columns.
def split_inventory_id(df):
    df_copy = df.copy()
    split_cols = df_copy['InventoryId'].str.split('_', expand=True)
    df_copy['Store'] = split_cols[0]
    df_copy['Location'] = split_cols[1]
    df_copy['ItemId'] = split_cols[2]
    df_copy.drop(columns=['InventoryId'], inplace=True)
    return df_copy

# ----------------------------------------------------------------------------------
# Create Sales.csv (StoreID, ItemId, SalesQuantity, SalesDate)
# ingests and cleans the sales data
# returns a DataFrame with cleaned sales data and saves it to a CSV file
def process_sales_data(raw_path, processed_path):
    # Load the Sales.csv file
    sales_file = os.path.join(raw_path, 'SalesFINAL12312016.csv')
    sales_df = pd.read_csv(sales_file)
    
    # Clean Sales.csv
    sales_cleaned = sales_df[['InventoryId', 'Store', 'SalesQuantity', 'SalesDate']]
    
    # Strip whitespace and filter for stores "1" and "2"
    sales_cleaned['Store'] = sales_cleaned['Store'].astype(str).str.strip()
    sales_cleaned = sales_cleaned[sales_cleaned['Store'].isin(['1', '2'])]
    
    # Apply split function to separate the composite InventoryId
    sales_cleaned = split_inventory_id(sales_cleaned)
    
    # Drop the Location column after splitting the InventoryId
    sales_cleaned.drop(columns=['Location'], inplace=True)
    
    # Rename 'Store' column to 'StoreID'
    sales_cleaned.rename(columns={'Store': 'StoreID'}, inplace=True)
    
    # Save the cleaned Sales.csv
    sales_cleaned.to_csv(os.path.join(processed_path, 'Sales.csv'), index=False)
    
    return sales_cleaned

# ----------------------------------------------------------------------------------
# Create Purchases.csv (StoreID, ItemId, Quantity, PODate, ReceivingDate)
# ingests and cleans the purchases data
# returns a DataFrame with cleaned purchases data and saves it to a CSV file
def process_purchases_data(raw_path, processed_path):
    # Load the Purchases.csv file
    purchases_file = os.path.join(raw_path, 'PurchasesFINAL12312016.csv')
    purchases_df = pd.read_csv(purchases_file)
    
    # Clean Purchases.csv
    purchases_cleaned = purchases_df[['InventoryId', 'Store', 'PODate', 'ReceivingDate', 'Quantity']]
    
    # Strip whitespace and filter for stores "1" and "2"
    purchases_cleaned['Store'] = purchases_cleaned['Store'].astype(str).str.strip()
    purchases_cleaned = purchases_cleaned[purchases_cleaned['Store'].isin(['1', '2'])]
    
    # Apply split function
    purchases_cleaned = split_inventory_id(purchases_cleaned)
    
    # Drop the Location column after splitting the InventoryId
    purchases_cleaned.drop(columns=['Location'], inplace=True)
    
    # Rename 'Store' column to 'StoreID'
    purchases_cleaned.rename(columns={'Store': 'StoreID'}, inplace=True)
    
    # Save the cleaned Purchases.csv
    purchases_cleaned.to_csv(os.path.join(processed_path, 'Purchases.csv'), index=False)
    
    return purchases_cleaned

# ----------------------------------------------------------------------------------
# Create OpeningStock.csv (StoreID, ItemId, onHand, startDate)
# ingests and cleans the opening stock data
# returns a DataFrame with cleaned opening stock data and saves it to a CSV file
def process_opening_stock_data(raw_path, processed_path):
    # Load the beginning inventory file
    opening_stock_file = os.path.join(raw_path, 'BegInvFINAL12312016.csv')
    opening_stock_df = pd.read_csv(opening_stock_file)
    
    # Clean BegInvFINAL12312016.csv
    opening_stock_cleaned = opening_stock_df[['InventoryId', 'Store', 'onHand', 'startDate']]
    
    # Strip whitespace from Store and keep only store "1" and "2"
    opening_stock_cleaned['Store'] = opening_stock_cleaned['Store'].astype(str).str.strip()
    opening_stock_cleaned = opening_stock_cleaned[opening_stock_cleaned['Store'].isin(['1', '2'])]
    
    # Replace the startDate with 2015-12-31
    opening_stock_cleaned['startDate'] = '2015-12-31'
    
    # Apply split function
    opening_stock_cleaned = split_inventory_id(opening_stock_cleaned)
    
    # Drop the Location column after splitting the InventoryId
    opening_stock_cleaned.drop(columns=['Location'], inplace=True)
    
    # Rename 'Store' column to 'StoreID'
    opening_stock_cleaned.rename(columns={'Store': 'StoreID'}, inplace=True)
    
    # Save the cleaned beginning inventory
    opening_stock_cleaned.to_csv(os.path.join(processed_path, 'OpeningStock.csv'), index=False)
    
    return opening_stock_cleaned

# ----------------------------------------------------------------------------------
# Create Inventory.csv (ItemID, Description)
# ingests and cleans the inventory data from multiple sources
# returns a DataFrame with cleaned inventory data and saves it to a CSV file
def create_inventory_master(sales_df, purchases_df, opening_stock_df, processed_path):
    # Pull ItemID and Description from original CSVs
    sales_info = sales_df[['Brand', 'Description']].rename(columns={'Brand': 'ItemID'})
    purchases_info = purchases_df[['Brand', 'Description']].rename(columns={'Brand': 'ItemID'})
    opening_info = opening_stock_df[['Brand', 'Description']].rename(columns={'Brand': 'ItemID'})
    
    # Combine and deduplicate
    inventory_df = pd.concat([sales_info, purchases_info, opening_info])
    inventory_df.drop_duplicates(subset=['ItemID', 'Description'], keep='first', inplace=True)
    
    # Save Inventory Master file
    inventory_df.to_csv(os.path.join(processed_path, 'Inventory.csv'), index=False)
    
    return inventory_df

# ----------------------------------------------------------------------------------
# Create Stores.csv (StoreID, Location)
# ingests and cleans the store data
# returns a DataFrame with cleaned store data and saves it to a CSV file
def create_stores_file(raw_path, processed_path):
    # Extract InventoryID from BeginInv file only
    beg_inv_file = os.path.join(raw_path, 'BegInvFINAL12312016.csv')
    beg_inv_df = pd.read_csv(beg_inv_file)
    
    # Extract inventory IDs and filter for valid format
    inventory_ids = pd.Series(beg_inv_df['InventoryId'].dropna().unique())
    valid_ids = inventory_ids[inventory_ids.str.count('_') == 2]
    
    # Split InventoryID into StoreID, Location, and ItemID
    split_data = valid_ids.str.split('_', expand=True)
    split_data.columns = ['StoreID', 'Location', 'ItemID']
    
    # Keep only stores 1 and 2
    split_data = split_data[split_data['StoreID'].isin(['1', '2'])]
    
    # Create Stores DataFrame with just StoreID and Location
    stores_df = split_data[['StoreID', 'Location']].drop_duplicates()
    
    # Save to CSV
    stores_df.to_csv(os.path.join(processed_path, 'Stores.csv'), index=False)
    
    return stores_df