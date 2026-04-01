import pandas as pd
import numpy as np
from config import DB_SETTINGS, RAW_DATA_PATH

class LeadCleaner:
    def __init__(self, path):
        self.df = pd.read_csv(path)
        # 1. AUTOMATIC SNAKE_CASE: This fixes ALL underscores at once (including Discount_Applied)
        self.df.columns = [c.replace(' ', '_').strip() for c in self.df.columns]
        
        # 2. RENAME: Map the long names to short ones for SQL
        rename_map = {
            'Transaction_Date': 'Date',
            'Transaction_ID': 'ID',
        }
        self.df.rename(columns=rename_map, inplace=True)
        print(f"Headers standardized: {self.df.columns.tolist()}")

    def clean_dates(self):
        print(f"Sample before cleaning: {self.df['Date'].head(3).tolist()}")
        
        # 'dayfirst=False' handles MM/DD/YYYY (Standard US/Kaggle format)
        self.df['Date'] = pd.to_datetime(self.df['Date'], dayfirst=False, errors='coerce')
        
        # Check how many rows became 'NaT' (Not a Time)
        invalid_dates = self.df['Date'].isna().sum()
        if invalid_dates > 0:
            print(f"⚠️ Warning: {invalid_dates} rows had invalid dates and were removed.")
            
        self.df.dropna(subset=['Date'], inplace=True)
        return self

    def impute_financials(self):
        # We use the clean names with underscores here
        mask = self.df['Price_Per_Unit'].isnull() & self.df['Total_Spent'].notnull() & self.df['Quantity'].notnull()
        self.df.loc[mask, 'Price_Per_Unit'] = self.df['Total_Spent'] / self.df['Quantity']
        
        mask_total = self.df['Total_Spent'].isnull() & self.df['Price_Per_Unit'].notnull() & self.df['Quantity'].notnull()
        self.df.loc[mask_total, 'Total_Spent'] = self.df['Price_Per_Unit'] * self.df['Quantity']
        return self

    def handle_missing_values(self):
        # 3. DROP NOISE: If a lead has no ID or hasn't spent anything, we can't use it.
        self.df.dropna(subset=['ID', 'Customer_ID', 'Total_Spent'], inplace=True)
        
        # 4. IMPUTE MISSING: Replace 'NaN' in Discount_Applied with False
        if 'Discount_Applied' in self.df.columns:
            self.df['Discount_Applied'] = self.df['Discount_Applied'].fillna(False)
            
        # 5. FILL NAMES: Replace empty Items or Categories
        self.df['Item'] = self.df['Item'].fillna("Unknown")
        self.df['Category'] = self.df['Category'].fillna("General")
        return self

    def save_data(self, output_path):
        self.df.to_csv(output_path, index=False)
        print(f"Cleaning complete. Final row count: {len(self.df)}")
        print(f"Saved to {output_path}")

if __name__ == "__main__":
    cleaner = LeadCleaner(RAW_DATA_PATH)
    # The Chain: We added .handle_missing_values() to the workflow
    cleaner.clean_dates() \
           .impute_financials() \
           .handle_missing_values() \
           .save_data("data/cleaned_leads.csv")