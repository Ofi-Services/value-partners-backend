import pandas as pd
from pathlib import Path
import os

def keep_only_columns(input_file, output_file, columns_to_keep):
    """
    Simple function to keep only specified columns from a CSV file.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file  
        columns_to_keep (list): List of column names to keep
    """
    
    try:
        # Read CSV
        df = pd.read_csv(input_file)
        
        # Find which columns actually exist
        existing_columns = [col for col in columns_to_keep if col in df.columns]
        missing_columns = [col for col in columns_to_keep if col not in df.columns]
        
        print(f"Processing: {Path(input_file).name}")
        print(f"  Original columns: {len(df.columns)}")
        print(f"  Keeping columns: {len(existing_columns)}")
        print(f"  Found columns: {existing_columns}")
        
        if missing_columns:
            print(f"  Missing columns: {missing_columns}")
        
        if not existing_columns:
            print(f"  ❌ No matching columns found! Skipping file.")
            return False
        
        # Filter and save
        filtered_df = df[existing_columns]
        filtered_df.to_csv(output_file, index=False)
        
        print(f"  ✅ Saved filtered file: {Path(output_file).name} ({len(filtered_df)} rows)")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {Path(input_file).name}: {str(e)}")
        return False

def filter_all_csv_files_in_folder(input_folder, output_folder, columns_to_keep, suffix="_filtered"):
    """
    Process all CSV files in a folder and keep only specified columns.
    
    Args:
        input_folder (str): Path to folder containing CSV files
        output_folder (str): Path to folder for filtered files
        columns_to_keep (list): List of column names to keep
        suffix (str): Suffix to add to output filenames
    """
    
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # Create output folder if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all CSV files
    csv_files = list(input_path.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {input_folder}")
        return
    
    print(f"Found {len(csv_files)} CSV files to process")
    print(f"Columns to keep: {columns_to_keep}")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for csv_file in csv_files:
        # Create output filename
        output_filename = csv_file.stem + suffix + ".csv"
        output_file = output_path / output_filename
        
        # Process the file
        if keep_only_columns(str(csv_file), str(output_file), columns_to_keep):
            successful += 1
        else:
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Processing complete!")
    print(f"✅ Successfully processed: {successful} files")
    if failed > 0:
        print(f"❌ Failed to process: {failed} files")
    print(f"Output folder: {output_folder}")

# Example usage
if __name__ == "__main__":
    
    # Define which columns to keep
    COLUMNS_TO_KEEP = [
        'CASE_ID',
        'CASE ID',  
        'ACTIVITY',
        'LG_OPCODE_DESCRIPTION', 
        'LG_LOG_TIME_TIMESTAMP'
    ]
    
    # Process all CSV files in a folder
    input_folder = r"d:\Projects\value-partners-backend\api\data\updated_data"
    output_folder = r"d:\Projects\value-partners-backend\api\data\updated_data\filtered"
    
    filter_all_csv_files_in_folder(input_folder, output_folder, COLUMNS_TO_KEEP)
    
    # Alternative: Process a single file (uncomment if needed)
    # input_file = r"d:\Projects\value-partners-backend\api\data\updated_data\Activities Table MySella 01_04_2025_30_06_2025.csv"
    # output_file = r"d:\Projects\value-partners-backend\api\data\updated_data\cleaned\Activities_2025_filtered.csv"
    # keep_only_columns(input_file, output_file, COLUMNS_TO_KEEP)
