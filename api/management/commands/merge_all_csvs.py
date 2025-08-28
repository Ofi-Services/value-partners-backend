#!/usr/bin/env python3
"""
Script to merge all CSV files in a folder into one big CSV file.
All CSV files should have the same column structure.

Configuration is done by editing the variables in the main() function.
Simply run: python merge_all_csvs.py
"""

import pandas as pd
import os
import glob
from pathlib import Path
import sys


def merge_csv_files(input_folder, output_file=None, file_pattern="*.csv"):
    """
    Merge all CSV files in a folder into one big CSV file.
    
    Args:
        input_folder (str): Path to the folder containing CSV files
        output_file (str): Path to the output merged CSV file (optional)
        file_pattern (str): Pattern to match CSV files (default: "*.csv")
    
    Returns:
        pandas.DataFrame: Merged DataFrame
    """
    
    # Convert to Path object for easier manipulation
    input_path = Path(input_folder)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")
    
    if not input_path.is_dir():
        raise ValueError(f"Input path is not a directory: {input_folder}")
    
    # Find all CSV files in the folder
    csv_files = list(input_path.glob(file_pattern))
    
    if not csv_files:
        raise ValueError(f"No CSV files found in {input_folder} with pattern {file_pattern}")
    
    print(f"Found {len(csv_files)} CSV files to merge:")
    for file in csv_files:
        print(f"  - {file.name}")
    
    # List to store all DataFrames
    dataframes = []
    
    # Read each CSV file and add to the list
    for i, csv_file in enumerate(csv_files):
        try:
            print(f"\nProcessing file {i+1}/{len(csv_files)}: {csv_file.name}")
            
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Add source file column to track which file each row came from
            df['source_file'] = csv_file.name
            
            print(f"  - Rows: {len(df)}, Columns: {len(df.columns)}")
            
            # Check if this is the first file or if columns match
            if i == 0:
                expected_columns = set(df.columns) - {'source_file'}
                print(f"  - Expected columns: {sorted(expected_columns)}")
            else:
                current_columns = set(df.columns) - {'source_file'}
                if current_columns != expected_columns:
                    print(f"  - WARNING: Column mismatch in {csv_file.name}")
                    print(f"    Expected: {sorted(expected_columns)}")
                    print(f"    Found: {sorted(current_columns)}")
                    print(f"    Missing: {sorted(expected_columns - current_columns)}")
                    print(f"    Extra: {sorted(current_columns - expected_columns)}")
            
            dataframes.append(df)
            
        except Exception as e:
            print(f"  - ERROR reading {csv_file.name}: {e}")
            continue
    
    if not dataframes:
        raise ValueError("No valid CSV files were processed")
    
    # Merge all DataFrames
    print(f"\nMerging {len(dataframes)} DataFrames...")
    merged_df = pd.concat(dataframes, ignore_index=True, sort=False)
    
    print(f"Merged DataFrame:")
    print(f"  - Total rows: {len(merged_df)}")
    print(f"  - Total columns: {len(merged_df.columns)}")
    print(f"  - Columns: {sorted(merged_df.columns)}")
    
    # Show summary by source file
    print(f"\nRows by source file:")
    source_counts = merged_df['source_file'].value_counts().sort_index()
    for source, count in source_counts.items():
        print(f"  - {source}: {count} rows")
    
    # Save to file if output_file is provided
    if output_file:
        output_path = Path(output_file)
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\nSaving merged CSV to: {output_file}")
        merged_df.to_csv(output_file, index=False)
        print(f"Successfully saved merged CSV with {len(merged_df)} rows")
        
        # Show file size
        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        print(f"File size: {file_size:.2f} MB")
    
    return merged_df


def main():
    """Main function to run the script."""
    
    # ==============================
    # CONFIGURATION - Edit these values as needed
    # ==============================
    
    # Input folder containing CSV files to merge
    INPUT_FOLDER = "api/data/updated_data/filtered"
    
    # Output file name (will be created in the root directory)
    OUTPUT_FILE = "merged_activities_data.csv"
    
    # File pattern to match (e.g., "*.csv", "Activities*.csv", etc.)
    FILE_PATTERN = "*.csv"
    
    # Set to True if you want to remove the source_file column from output
    REMOVE_SOURCE_COLUMN = False
    
    # ==============================
    # END CONFIGURATION
    # ==============================
    
    try:
        print(f"Configuration:")
        print(f"  Input folder: {INPUT_FOLDER}")
        print(f"  Output file: {OUTPUT_FILE}")
        print(f"  File pattern: {FILE_PATTERN}")
        print(f"  Remove source column: {REMOVE_SOURCE_COLUMN}")
        print("-" * 50)
        
        # Merge CSV files
        merged_df = merge_csv_files(
            INPUT_FOLDER,
            OUTPUT_FILE,
            FILE_PATTERN
        )
        
        # Remove source_file column if requested
        if REMOVE_SOURCE_COLUMN and 'source_file' in merged_df.columns:
            merged_df = merged_df.drop('source_file', axis=1)
            merged_df.to_csv(OUTPUT_FILE, index=False)
            print("Removed source_file column from output")
        
        print(f"\n✅ Successfully merged CSV files!")
        print(f"Output: {OUTPUT_FILE}")
        print(f"Total rows: {len(merged_df)}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
