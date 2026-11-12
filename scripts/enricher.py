import pandas as pd
from sqlalchemy import create_engine
from config import DB_SETTINGS

class LeadEnricher:
    def __init__(self, db_config):
        self.db_url = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        self.engine = create_engine(self.db_url)

    def get_data(self):
        # Pull the cleaned data back out of the database
        query = "SELECT * FROM leads"
        return pd.read_sql(query, self.engine)

    def score_leads(self, df):
        print("Running rule-based scoring...")
        
        # Rule-based score out of 100. A transaction earns points for:
        # 1. Spending more than the average transaction (+50)
        # 2. Buying more than 5 items (+30)
        # 3. Paying full price, i.e. no discount applied (+20)
        avg_spend = df['Total_Spent'].mean()
        
        def calculate_priority(row):
            score = 0
            if row['Total_Spent'] > avg_spend: score += 50
            if row['Quantity'] > 5: score += 30
            if row['Discount_Applied'] == False: score += 20 # Full price payers are gold
            return score

        df['Priority_Score'] = df.apply(calculate_priority, axis=1)
        
        # Categorize them
        df['Lead_Tier'] = pd.cut(df['Priority_Score'], 
                                bins=[0, 30, 70, 100], 
                                labels=['Bronze', 'Silver', 'Gold'],
                                include_lowest=True)  # score 0 counts as Bronze (it was dropped before)
        return df

    def update_database(self, df):
        # Save the enriched data back to a NEW table called 'enriched_leads'
        df.to_sql('enriched_leads', con=self.engine, if_exists='replace', index=False)
        print(f"✅ Scoring complete: {len(df)} transactions tiered into Gold / Silver / Bronze.")

if __name__ == "__main__":
    enricher = LeadEnricher(DB_SETTINGS)
    raw_df = enricher.get_data()
    enriched_df = enricher.score_leads(raw_df)
    enricher.update_database(enriched_df)