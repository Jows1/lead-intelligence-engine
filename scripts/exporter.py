import pandas as pd
from sqlalchemy import create_engine
from config import DB_SETTINGS

class LeadExporter:
    def __init__(self, db_config):
        # Using the "Side Door" Port 5433 we set up
        self.db_url = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        self.engine = create_engine(self.db_url)

    def extract_high_value_leads(self):
        print("📤 Connecting to database to extract Gold Tier leads...")
        
        # We use double quotes here to match the case-sensitive columns in Postgres
        query = 'SELECT * FROM enriched_leads'
        
        df = pd.read_sql(query, self.engine)
        return df

    def save_to_csv(self, df, output_path):
        if df.empty:
            print("⚠️ No Gold leads found to export.")
            return
        
        # Exporting without the index for a cleaner look in Excel/Sheets
        df.to_csv(output_path, index=False)
        print(f"✅ Export Success! {len(df)} High-Value leads saved to: {output_path}")

if __name__ == "__main__":
    exporter = LeadExporter(DB_SETTINGS)
    gold_df = exporter.extract_high_value_leads()
    exporter.save_to_csv(gold_df, "data/final_gold_leads.csv")