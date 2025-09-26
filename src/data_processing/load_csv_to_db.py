import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import postgresql, load_dotenv

load_dotenv()


# Define PostgreSQL connection parameters
user = 'postgres'
password = os.getenv("POSTGRESQL_PW")
host = 'localhost'
port = '5432'
db = 'yelp_project_db'

# Define file path
file_path = '/Users/isaac/Documents/Python/Restaurant Recommendation Project/Data/yelp_master_original.csv'

# Create SQLAlchemy engine
engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

# Load your csv into a pandas DataFrame
df = pd.read_csv(file_path)

# Send data to PostgreSQL
df.to_sql('yelp_master_original', engine, schema='project_schema',if_exists='fail',index=False)

print("Data imported successfully.")