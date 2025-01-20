from sqlalchemy import create_engine, Engine
import pandas as pd
from dotenv import load_dotenv
import os


load_dotenv(override = True)

# Snowflake connection parameters
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
account = os.getenv("SNOWFLAKE_ACCOUNT")
warehouse = os.getenv("WAREHOUSE_NAME")
database = os.getenv("DATABASE_NAME")
schema = os.getenv("TABLE_SCHEMA")

# Create an SQLAlchemy engine
engine = create_engine(
    f'snowflake://{username}:{password}@{account}/{database}/{schema}?warehouse={warehouse}'
)


def get_dataframe_from_query(query: str, engine: Engine = engine):
    try:
        df = pd.read_sql(query, engine)
        print("Data loaded successfully!")
        return df
    except:
        print("Data DID NOT load successfully")
        return pd.DataFrame()
    finally:
        # Close the connection
        engine.dispose()
        
        
        

if __name__ == "__main__":
    # Query the table
    query = "SELECT * FROM MISTRALHEALTHDB.MEDICALRECORDDATAMART.FLATTENED_MEDICAL_RECORDS"
    df = get_dataframe_from_query(query, engine)
    print(df.head())

    
