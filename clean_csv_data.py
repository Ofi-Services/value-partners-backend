#!/usr/bin/env python3
"""
Script to clean CSV files by removing rows with missing data.
Configuration is done by editing the variables in the main() function.
Simply run: python clean_csv_data.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys


def clean_csv_data(input_file, output_file=None, how='any', subset=None, verbose=True):
    """
    Clean CSV file by removing rows with missing data.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to the output cleaned CSV file (optional)
        how (str): How to determine if row has missing data:
                   - 'any': Drop if any column has missing data
                   - 'all': Drop only if all columns have missing data
        subset (list): List of column names to check for missing data (optional)
                      If None, checks all columns
        verbose (bool): Print detailed information about the cleaning process
    
    Returns:
        pandas.DataFrame: Cleaned DataFrame
    """
    
    # Convert to Path object
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_file}")
    
    if verbose:
        print(f"Loading CSV file: {input_file}")
        
    # Read the CSV file
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    if verbose:
        print(f"Original data shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("-" * 50)
    
    # Analyze missing data before cleaning
    if verbose:
        print("Missing data analysis BEFORE cleaning:")
        missing_stats = df.isnull().sum()
        total_rows = len(df)
        
        for col in df.columns:
            missing_count = missing_stats[col]
            missing_pct = (missing_count / total_rows) * 100
            print(f"  {col}: {missing_count} missing ({missing_pct:.2f}%)")
        
        total_missing = df.isnull().sum().sum()
        print(f"\nTotal missing values: {total_missing}")
        
        # Count rows with any missing data
        rows_with_missing = df.isnull().any(axis=1).sum()
        rows_missing_pct = (rows_with_missing / total_rows) * 100
        print(f"Rows with any missing data: {rows_with_missing} ({rows_missing_pct:.2f}%)")
        
        # Count rows with all missing data
        rows_all_missing = df.isnull().all(axis=1).sum()
        rows_all_missing_pct = (rows_all_missing / total_rows) * 100
        print(f"Rows with all missing data: {rows_all_missing} ({rows_all_missing_pct:.2f}%)")
        print("-" * 50)
    
    # Clean the data by removing rows with missing values
    original_row_count = len(df)
    
    if subset:
        # Check only specific columns
        if verbose:
            print(f"Checking for missing data in columns: {subset}")
        cleaned_df = df.dropna(subset=subset, how=how)
    else:
        # Check all columns
        if verbose:
            print(f"Checking for missing data in all columns (how='{how}')")
        cleaned_df = df.dropna(how=how)
    
    cleaned_row_count = len(cleaned_df)
    rows_removed = original_row_count - cleaned_row_count
    removal_pct = (rows_removed / original_row_count) * 100
    
    if verbose:
        print(f"\nCleaning results:")
        print(f"  Original rows: {original_row_count}")
        print(f"  Cleaned rows: {cleaned_row_count}")
        print(f"  Rows removed: {rows_removed} ({removal_pct:.2f}%)")
        
        if cleaned_row_count > 0:
            print(f"\nMissing data analysis AFTER cleaning:")
            missing_stats_after = cleaned_df.isnull().sum()
            for col in cleaned_df.columns:
                missing_count = missing_stats_after[col]
                missing_pct = (missing_count / cleaned_row_count) * 100
                print(f"  {col}: {missing_count} missing ({missing_pct:.2f}%)")
    
    # Save cleaned data if output file is provided
    if output_file:
        output_path = Path(output_file)
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if verbose:
            print(f"\nSaving cleaned CSV to: {output_file}")
        
        cleaned_df.to_csv(output_file, index=False)
        
        if verbose:
            print(f"Successfully saved cleaned CSV with {len(cleaned_df)} rows")
            
            # Show file size comparison
            original_size = input_path.stat().st_size / (1024 * 1024)  # MB
            cleaned_size = output_path.stat().st_size / (1024 * 1024)  # MB
            size_reduction = ((original_size - cleaned_size) / original_size) * 100
            
            print(f"\nFile size comparison:")
            print(f"  Original: {original_size:.2f} MB")
            print(f"  Cleaned: {cleaned_size:.2f} MB")
            print(f"  Reduction: {size_reduction:.2f}%")
    
    return cleaned_df


def analyze_missing_data_patterns(df, verbose=True):
    """
    Analyze patterns in missing data to help understand the data quality.
    
    Args:
        df (pandas.DataFrame): DataFrame to analyze
        verbose (bool): Print detailed analysis
    
    Returns:
        dict: Analysis results
    """
    
    if verbose:
        print("\n" + "=" * 60)
        print("DETAILED MISSING DATA PATTERN ANALYSIS")
        print("=" * 60)
    
    results = {}
    
    # Basic statistics
    total_rows = len(df)
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    missing_percentage = (missing_cells / total_cells) * 100
    
    results['total_rows'] = total_rows
    results['total_cells'] = total_cells
    results['missing_cells'] = missing_cells
    results['missing_percentage'] = missing_percentage
    
    if verbose:
        print(f"Dataset Overview:")
        print(f"  Total rows: {total_rows:,}")
        print(f"  Total columns: {len(df.columns)}")
        print(f"  Total cells: {total_cells:,}")
        print(f"  Missing cells: {missing_cells:,} ({missing_percentage:.2f}%)")
    
    # Pattern analysis
    if verbose:
        print(f"\nMissing Data Patterns:")
        
        # Rows with different amounts of missing data
        missing_counts = df.isnull().sum(axis=1).value_counts().sort_index()
        for missing_count, row_count in missing_counts.items():
            if missing_count > 0:
                pct = (row_count / total_rows) * 100
                print(f"  Rows with {missing_count} missing values: {row_count} ({pct:.2f}%)")
    
    return results


def main():
    """Main function to run the script."""
    
    # ==============================
    # CONFIGURATION - Edit these values as needed
    # ==============================
    
    # Input CSV file to clean
    INPUT_FILE = "api/data/merged_activities_data.csv"
    
    # Output file name (will be created in the same directory as input)
    OUTPUT_FILE = "api/data/merged_activities_data_cleaned.csv"
    
    # How to handle missing data:
    # 'any' = remove row if ANY column has missing data
    # 'all' = remove row only if ALL columns have missing data
    HOW_TO_CLEAN = 'any'
    
    # Specific columns to check for missing data (optional)
    # Set to None to check all columns
    # Example: SUBSET_COLUMNS = ['name', 'case_id']
    SUBSET_COLUMNS = None
    
    # Set to True for detailed output, False for minimal output
    VERBOSE = False
    
    # Set to True to run detailed missing data pattern analysis
    RUN_ANALYSIS = False
    
    # ==============================
    # END CONFIGURATION
    # ==============================
    
    try:
        print(f"Configuration:")
        print(f"  Input file: {INPUT_FILE}")
        print(f"  Output file: {OUTPUT_FILE}")
        print(f"  Cleaning method: {HOW_TO_CLEAN}")
        print(f"  Subset columns: {SUBSET_COLUMNS}")
        print(f"  Verbose output: {VERBOSE}")
        print("=" * 50)
        
        # Load and analyze the original data first
        if RUN_ANALYSIS:
            df_original = pd.read_csv(INPUT_FILE)
            analyze_missing_data_patterns(df_original, verbose=VERBOSE)
        
        # Clean the CSV file
        cleaned_df = clean_csv_data(
            INPUT_FILE,
            OUTPUT_FILE,
            how=HOW_TO_CLEAN,
            subset=SUBSET_COLUMNS,
            verbose=VERBOSE
        )
        
        print(f"\n✅ Successfully cleaned CSV file!")
        print(f"Input: {INPUT_FILE}")
        print(f"Output: {OUTPUT_FILE}")
        print(f"Final row count: {len(cleaned_df):,}")
        
        # Show a sample of the cleaned data
        if VERBOSE and len(cleaned_df) > 0:
            print(f"\nSample of cleaned data:")
            print(cleaned_df.head())
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
