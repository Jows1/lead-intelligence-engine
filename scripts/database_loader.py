import pandas as pd
from sqlalchemy import create_engine
from config import DB_SETTINGS, CLEAN_DATA_PATH

class DatabaseLoader:
    def __init__(self, data_path, db_config):
        self.data_path = data_path
        self.db_config = db_config
        # Create the connection string format: postgresql+psycopg2://user:password@host:port/dbname
        self.db_url = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        self.engine = create_engine(self.db_url)

    def load_data(self):
        print(f"Reading cleaned data from {self.data_path}...")
        df = pd.read_csv(self.data_path)
        
        table_name = 'leads'
        print(f"Pushing {len(df)} rows to the '{table_name}' table in PostgreSQL...")
        
        # This one line creates the table and inserts the data!
        # if_exists='replace' means if you run it twice, it resets the table clean.
        df.to_sql(table_name, con=self.engine, if_exists='replace', index=False)
        
        print("✅ Data successfully loaded into the database!")

if __name__ == "__main__":
    loader = DatabaseLoader(CLEAN_DATA_PATH, DB_SETTINGS)
    loader.load_data()