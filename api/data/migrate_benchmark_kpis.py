import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import datetime
import logging

# ---------- Load Environment Variables ----------
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# ---------- Configuration ----------
DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
EXCEL_PATH = "APQC Benchmarking.xlsx"
TABLE_NAME = "benchmark_kpis"
LOG_FILE = "migration_log.txt"

# ---------- Setup Logging ----------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_excel(path):
    try:
        return pd.read_excel(path)
    except Exception as e:
        logging.error(f"Failed to read Excel file: {e}")
        raise

def validate_columns(df, required_columns):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logging.error(f"Missing columns in Excel file: {missing_columns}")
        raise ValueError(f"Missing columns: {missing_columns}")

def clean_data(df):
    df_clean = df[["KPI/USE CASE", "PROCESS", "UNIT", "BENCHMARKING", "INDUSTRY"]].copy()
    df_clean.columns = ["kpi_name", "category", "unit", "benchmark_value", "source"]
    df_clean = df_clean.dropna(subset=["kpi_name", "category", "unit", "benchmark_value", "source"])
    df_clean = df_clean[pd.to_numeric(df_clean["benchmark_value"], errors="coerce").notnull()]
    df_clean["benchmark_value"] = df_clean["benchmark_value"].astype(float)
    df_clean = df_clean.drop_duplicates(subset=["kpi_name", "category", "unit", "source", "benchmark_value"])
    df_clean["updated_at"] = datetime.datetime.now(datetime.UTC)
    return df_clean

def insert_into_database(df, db_uri, table_name):
    engine = create_engine(db_uri)
    inserted_count = 0
    with engine.begin() as conn:  # Automatically commits or rolls back the transaction
        for _, row in df.iterrows():
            try:
                logging.info(f"Inserting row: {row.to_dict()}")
                insert_query = text(f"""
                    INSERT INTO {table_name} (kpi_name, category, unit, benchmark_value, source, updated_at)
                    VALUES (:kpi_name, :category, :unit, :benchmark_value, :source, :updated_at)
                    ON CONFLICT (kpi_name, category, unit, source) DO NOTHING
                """)
                conn.execute(insert_query, {
                    "kpi_name": row["kpi_name"],
                    "category": row["category"],
                    "unit": row["unit"],
                    "benchmark_value": row["benchmark_value"],
                    "source": row["source"],
                    "updated_at": row["updated_at"]
                })
                inserted_count += 1
            except Exception as e:
                logging.error(f"Failed to insert row {row.to_dict()}: {e}")
    return inserted_count

def run_migration():
    required_columns = ["KPI/USE CASE", "PROCESS", "UNIT", "BENCHMARKING", "INDUSTRY"]
    
    df_raw = load_excel(EXCEL_PATH)
    validate_columns(df_raw, required_columns)
    df_clean = clean_data(df_raw)
    inserted = insert_into_database(df_clean, DB_URI, TABLE_NAME)

    logging.info(f"Migration complete. {inserted} rows inserted.")
    print("Migration completed. See log for details.")

# ---------- Run Script ----------
if __name__ == "__main__":
    run_migration()
