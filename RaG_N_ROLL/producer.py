import asyncio
import os
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

from dotenv import load_dotenv
from faker import Faker
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize Faker
fake = Faker()

def create_snowflake_connection():
    """
    Creates and returns a connection to Snowflake using environment variables.
    
    Returns:
        snowflake.connector.connection: Snowflake connection object
    
    Raises:
        Exception: If connection fails
    """
    try:
        return snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        raise

def create_medical_table(conn):
    """
    Creates the medical records table in Snowflake if it doesn't exist.
    
    Args:
        conn: Snowflake connection object
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS MEDICAL_RECORDS (
                    record_id VARCHAR(36) PRIMARY KEY,
                    created_at TIMESTAMP_NTZ,
                    patient_id VARCHAR(36),
                    patient_name VARCHAR(100),
                    date_of_birth DATE,
                    age INTEGER,
                    gender VARCHAR(20),
                    blood_type VARCHAR(5),
                    diagnosis VARCHAR(200),
                    treatment_plan TEXT,
                    medication VARCHAR(500),
                    allergies VARCHAR(500),
                    vital_signs VARIANT,
                    insurance_provider VARCHAR(100),
                    insurance_id VARCHAR(50),
                    attending_physician VARCHAR(100),
                    department VARCHAR(50),
                    admission_date TIMESTAMP_NTZ,
                    discharge_date TIMESTAMP_NTZ,
                    last_updated_at TIMESTAMP_NTZ
                )
            """)
    except Exception as e:
        print(f"Error creating table: {e}")
        raise

def generate_medical_record() -> Dict[str, Any]:
    """
    Generates comprehensive fake medical record data.
    
    Returns:
        Dict[str, Any]: Generated medical record data
    """
    # Lists for realistic medical data generation
    departments = ['Cardiology', 'Neurology', 'Oncology', 'Pediatrics', 
                  'Emergency', 'Orthopedics', 'Internal Medicine']
    
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    common_diagnoses = [
        'Hypertension', 'Type 2 Diabetes', 'Acute Bronchitis',
        'Major Depressive Disorder', 'Osteoarthritis', 'Migraine',
        'Upper Respiratory Infection', 'Lower Back Pain'
    ]
    
    medications = [
        'Lisinopril', 'Metformin', 'Amlodipine', 'Omeprazole',
        'Sertraline', 'Amoxicillin', 'Ibuprofen', 'Levothyroxine'
    ]
    
    insurance_providers = [
        'Blue Cross Blue Shield', 'UnitedHealth Group', 'Aetna',
        'Cigna', 'Humana', 'Kaiser Permanente', 'Medicare', 'Medicaid'
    ]

    # Generate admission and discharge dates
    current_time = datetime.now()
    admission_date = fake.date_time_between(start_date='-30d', end_date='now')
    discharge_date = fake.date_time_between(
        start_date=admission_date,
        end_date=admission_date + timedelta(days=14)
    )
    
    # Generate date of birth and calculate age
    date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=90)
    age = (datetime.now().date() - date_of_birth).days // 365

    return {
        'record_id': fake.uuid4(),
        'created_at': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'patient_id': fake.uuid4(),
        'patient_name': fake.name(),
        'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),
        'age': age,
        'gender': fake.random_element(elements=('Male', 'Female', 'Other')),
        'blood_type': fake.random_element(elements=blood_types),
        'diagnosis': fake.random_element(elements=common_diagnoses),
        'treatment_plan': fake.paragraph(nb_sentences=3),
        'medication': ', '.join(fake.random_elements(elements=medications, length=fake.random_int(1, 3))),
        'allergies': ', '.join(fake.random_elements(elements=['Penicillin', 'Pollen', 'Latex', 'Peanuts', 'None'], length=fake.random_int(0, 2))),
        'vital_signs': {
            'blood_pressure': f"{fake.random_int(90, 140)}/{fake.random_int(60, 90)}",
            'heart_rate': fake.random_int(60, 100),
            'temperature': round(fake.random.uniform(36.1, 37.5), 1),
            'respiratory_rate': fake.random_int(12, 20),
            'oxygen_saturation': fake.random_int(95, 100)
        },
        'insurance_provider': fake.random_element(elements=insurance_providers),
        'insurance_id': fake.bothify(text='???-########'),
        'attending_physician': fake.name() + ", " + fake.random_element(elements=['MD', 'DO']),
        'department': fake.random_element(elements=departments),
        'admission_date': admission_date.strftime('%Y-%m-%d %H:%M:%S'),
        'discharge_date': discharge_date.strftime('%Y-%m-%d %H:%M:%S'),
        'last_updated_at': current_time.strftime('%Y-%m-%d %H:%M:%S')
    }

async def insert_medical_record(conn, record: Dict[str, Any]):
    """
    Inserts a single medical record into Snowflake.
    
    Args:
        conn: Snowflake connection object
        record (Dict[str, Any]): Medical record to insert
    """
    try:
        # Convert record to DataFrame for efficient loading
        df = pd.DataFrame([record])
        
        # Convert vital_signs dictionary to JSON string
        df['vital_signs'] = df['vital_signs'].apply(lambda x: str(x))
        
        # Write to Snowflake
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name='MEDICAL_RECORDS',
            quote_identifiers=False
        )
        
        if success:
            print(f"Successfully inserted record {record['record_id']}")
        else:
            print(f"Failed to insert record {record['record_id']}")
            
    except Exception as e:
        print(f"Error inserting record: {e}")

async def continuous_data_generation(conn, generation_interval: int = 10, pause_interval: int = 60):
    """
    Continuously generates and inserts medical records with specified intervals.
    
    Args:
        conn: Snowflake connection object
        generation_interval (int): Seconds between each record generation
        pause_interval (int): Seconds to pause after each minute of generation
    """
    try:
        while True:
            print("\nStarting medical record generation cycle...")
            cycle_start = time.time()
            
            # Generate records for one minute
            while time.time() - cycle_start < 60:
                record = generate_medical_record()
                await insert_medical_record(conn, record)
                await asyncio.sleep(generation_interval)
            
            print(f"\nPausing for {pause_interval} seconds...")
            await asyncio.sleep(pause_interval)
            
    except asyncio.CancelledError:
        print("\nData generation stopped.")
    except Exception as e:
        print(f"\nAn error occurred during data generation: {e}")

def handle_termination(conn):
    """
    Handles graceful termination of the Snowflake connection.
    
    Args:
        conn: Snowflake connection to close
    """
    print("\nTermination signal received. Closing Snowflake connection...")
    conn.close()
    print("Connection closed. Exiting.")
    sys.exit(0)

async def main():
    """
    Main async function to set up and run medical record generation.
    """
    try:
        # Create Snowflake connection
        conn = create_snowflake_connection()
        print("Connected to Snowflake successfully")
        
        # Create table if it doesn't exist
        create_medical_table(conn)
        print("Medical records table ready")
        
        # Set up termination handling
        def sigint_handler(signum, frame):
            handle_termination(conn)
        
        signal.signal(signal.SIGINT, sigint_handler)
        
        print("\nMedical Records Generation Started. Press Ctrl+C to stop.")
        
        # Start continuous generation
        await continuous_data_generation(conn)
        
    except Exception as e:
        print(f"An error occurred in main: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    asyncio.run(main())