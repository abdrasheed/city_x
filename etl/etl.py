import json
import sys
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
import re
from sqlalchemy import create_engine, text
import os

# SQLAlchemy engine for PostgreSQL connection

db_user = os.getenv("POSTGRES_USER")
db_pass = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")
db_host = os.getenv("DB_HOST", "localhost")

# Create the Engine
engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:5432/{db_name}")


def get_db_connection():
    try:
        # Test the connection by acquiring one from the engine
        with engine.connect() as conn:
            print('\n\n\n')
            print("✅ Database connection successful")
            print("-"*80)
        return engine
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        sys.exit(1)

# This function will extract the data from the json file and insert into staging database.
def extract_json(engine, file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        dd = ()

        with engine.connect() as conn:
            for record in data:
                conn.execute(
                    text("""
                        INSERT INTO staging.raw_crime_data 
                        (district_id, timestamp, crime_type, nearest_police_patrol)
                        VALUES (:district_id, :timestamp, :crime_type, :nearest_police_patrol)
                    """),
                    {
                        "district_id": record['district_id'],
                        "timestamp": record['timestamp'],
                        "crime_type": record['crime_type'],
                        "nearest_police_patrol": record['nearest_police_patrol']
                    }
                )
            conn.commit()
        print("✅ Crime data extracted into STAGING Crime table successfully")
        print("-"*80)
    except Exception as e:
        print(f"JSON extraction failed: {str(e)}")
        sys.exit(1)


# This function will extract the data from the PDF file using OCR and insert into staging database.
def extract_pdf(engine, file_path):
    try:

        # Local tool paths (hardcoded inside function)
        pytesseract.pytesseract.tesseract_cmd = "tesseract"

        # Convert PDF to image
        images = convert_from_path(file_path)

        if not images:
            print("No pages found in PDF.")
            return
        
        # OCR to extract text
        ocr_text = pytesseract.image_to_string(images[0])
        ocr_text = ocr_text.replace('|', ' ').replace('\n', ' ')
        ocr_text = re.sub(r'\s+', ' ', ocr_text)
        
        # Regex to parse structured data
        pattern = re.compile(r'(\d+)\s+([A-Za-z\/\- ]+?)\s+([\d,]+)\s+([A-Za-z\- ]{3,})')
        rows = []
        for match in pattern.finditer(ocr_text):
            district_id = int(match.group(1))
            district = match.group(2).strip()
            population = int(match.group(3).replace(',', ''))
            governor = match.group(4).strip()
            rows.append((district_id, district, population, governor))

        if not rows:
            print("No valid data found in PDF.")
            return

        # Insert into existing staging table using SQLAlchemy
        with engine.connect() as conn:
            
            conn.execute(
                text("""
                    INSERT INTO staging.raw_district_data (district_id, district, population, governor)
                    VALUES (:district_id, :district, :population, :governor)
                """),
                [{"district_id": row[0], "district": row[1], "population": row[2], "governor": row[3]} for row in rows]
            )

            conn.commit()
        print("✅ District data extracted into STAGING Ditrict table successfully")
        print("-"*80)
    except Exception as e:
        print(f"PDF extraction failed: {str(e)}")
        sys.exit(1)

# This function will transform and merge the data and insert into core database.
def transform_and_load_core_data(engine):
    try:
        # Step 1: Load staging tables
        with engine.connect() as conn:
            crime_df = pd.read_sql("SELECT * FROM staging.raw_crime_data", conn)
            district_df = pd.read_sql("SELECT * FROM staging.raw_district_data", conn)

        # Step 2: Clean and Transform Crime Records Table

        # Remove invalid records (missing or empty crime_type)
        crime_df = crime_df[crime_df['crime_type'].notnull() & (crime_df['crime_type'].str.strip() != '')]

        # Correct spelling mistakes in crime_type
        correct_crimes = {
            "Assult": "assault",
            "Frued": "fraud",
            "cybercrime":"cyber crime"
        }
        crime_df['crime_type'] = crime_df['crime_type'].replace(correct_crimes)
        crime_df['crime_type'] = crime_df['crime_type'].str.capitalize()

        # Standardize nearest_police_patrol to kilometers
        crime_df['nearest_police_patrol'] = crime_df['nearest_police_patrol'].apply(
            lambda x: float(x.split()[0]) * 1.60934 if 'mile' in x.lower() else float(x.split()[0])
        )

        # Split timestamp into day_of_week, date, and time
        crime_df['timestamp'] = pd.to_datetime(crime_df['timestamp'])
        crime_df['day_of_week'] = crime_df['timestamp'].dt.day_name()
        crime_df['date'] = crime_df['timestamp'].dt.date
        crime_df['time'] = crime_df['timestamp'].dt.time

        # Drop unnecessary columns
        crime_df.drop(columns=['timestamp', 'id'], inplace=True)

        # Step 2: Clean and Transform District Information Table
        district_df['district'] = district_df['district'].replace("District", "")
        district_df = district_df.rename(columns={'district': 'district_name'}) 
        district_df['governor'] = district_df['governor'].replace("District", "")

        # Drop unnecessary columns
        district_df.drop(columns=['id'], inplace=True)

        # Step 3: Merge tables on district_id
        merged_df = pd.merge(crime_df, district_df, on='district_id', how='inner')

        # Step 4: Ensure final table has required fields (implicitly handled by merge)
        # Step 5: Insert into core table
        with engine.connect() as conn:
            
            # Re-create ID from scratch
            conn.execute(text("ALTER SEQUENCE core.transformed_crime_data_id_seq RESTART WITH 1"))

            # Truncate core table first
            conn.execute(text("TRUNCATE TABLE core.transformed_crime_data"))

            # Insert merged data
            merged_df.to_sql('transformed_crime_data', schema='core', con=conn, if_exists='append', index=False)
            conn.commit()

        print("✅ Data transformed and loaded into CORE Crime full data table successfully.")
        print("-"*80)
    except Exception as e:
        print(f"❌ ETL failed: {str(e)}")
        sys.exit(1)

# This function will truncate the staging database
def truncate_staging_tables(engine):
    try:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE staging.raw_crime_data RESTART IDENTITY"))
            conn.execute(text("TRUNCATE TABLE staging.raw_district_data RESTART IDENTITY"))
            conn.commit()

        print("✅ Staging tables truncated successfully.")
        print("-"*80)
    except Exception as e:
        print(f"❌ Failed to truncate staging tables: {e}")
        sys.exit(1)


def main():
    # Test connection
    get_db_connection()
    
    # Extract data
    extract_json(engine, 'data/crime_records.json')
    extract_pdf(engine, 'data/district_info.pdf')

    # Transform and load into core database
    transform_and_load_core_data(engine)

    # Truncate the staging tables
    truncate_staging_tables(engine)

    # SUCCESS
    print("✅ ETL Data Pipeline has been executed successfully ✅")
    print('\n\n\n')
if __name__ == "__main__":
    main()