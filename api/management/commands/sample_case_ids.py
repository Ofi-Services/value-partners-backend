#!/usr/bin/env python3
"""
Script to create a random sample of data by selecting a percentage of unique case_ids
and keeping only rows with those selected case_ids.

Configuration is done by editing the variables in the main() function.
Simply run: python sample_case_ids.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import random
import sys


def sample_case_ids(input_file, output_file=None, sample_percentage=10, random_seed=None, verbose=True):
    """
    Create a random sample by selecting a percentage of unique case_ids.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to the output sampled CSV file (optional)
        sample_percentage (float): Percentage of unique case_ids to sample (0-100)
        random_seed (int): Random seed for reproducible results (optional)
        verbose (bool): Print detailed information about the sampling process
    
    Returns:
        pandas.DataFrame: Sampled DataFrame
    """
    
    # Convert to Path object
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_file}")
    
    if not 0 < sample_percentage <= 100:
        raise ValueError(f"Sample percentage must be between 0 and 100, got {sample_percentage}")
    
    # Set random seed for reproducibility
    if random_seed is not None:
        random.seed(random_seed)
        np.random.seed(random_seed)
        if verbose:
            print(f"Random seed set to: {random_seed}")
    
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
    
    # Check if case_id column exists
    if 'case_id' not in df.columns:
        raise ValueError("Column 'case_id' not found in the CSV file")
    
    # Get unique case_ids
    unique_case_ids = df['case_id'].dropna().unique()
    total_unique_case_ids = len(unique_case_ids)
    
    if verbose:
        print(f"\nCase ID Analysis:")
        print(f"  Total rows: {len(df):,}")
        print(f"  Unique case_ids: {total_unique_case_ids:,}")
        print(f"  Rows per case_id (average): {len(df) / total_unique_case_ids:.2f}")
    
    # Calculate sample size
    sample_size = max(1, int(total_unique_case_ids * (sample_percentage / 100)))
    
    if verbose:
        print(f"\nSampling Configuration:")
        print(f"  Sample percentage: {sample_percentage}%")
        print(f"  Case IDs to sample: {sample_size:,} out of {total_unique_case_ids:,}")
    
    # Randomly sample case_ids
    sampled_case_ids = np.random.choice(unique_case_ids, size=sample_size, replace=False)
    sampled_case_ids_set = set(sampled_case_ids)
    
    if verbose:
        print(f"  Selected case_ids: {len(sampled_case_ids):,}")
        print(f"  Sample of selected case_ids: {sorted(list(sampled_case_ids))[:10]}...")
    
    # Filter dataframe to keep only rows with sampled case_ids
    sampled_df = df[df['case_id'].isin(sampled_case_ids_set)].copy()
    
    # Calculate statistics
    original_rows = len(df)
    sampled_rows = len(sampled_df)
    rows_kept_percentage = (sampled_rows / original_rows) * 100 if original_rows > 0 else 0
    
    if verbose:
        print(f"\nSampling Results:")
        print(f"  Original rows: {original_rows:,}")
        print(f"  Sampled rows: {sampled_rows:,}")
        print(f"  Rows kept: {rows_kept_percentage:.2f}%")
        print(f"  Rows removed: {original_rows - sampled_rows:,}")
        
        # Verify all sampled case_ids are present
        resulting_unique_case_ids = sampled_df['case_id'].nunique()
        print(f"  Unique case_ids in result: {resulting_unique_case_ids:,}")
        
        # Show distribution of activities per case_id in sample
        case_id_counts = sampled_df['case_id'].value_counts()
        print(f"  Min activities per case_id: {case_id_counts.min()}")
        print(f"  Max activities per case_id: {case_id_counts.max()}")
        print(f"  Average activities per case_id: {case_id_counts.mean():.2f}")
    
    # Save sampled data if output file is provided
    if output_file:
        output_path = Path(output_file)
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if verbose:
            print(f"\nSaving sampled CSV to: {output_file}")
        
        sampled_df.to_csv(output_file, index=False)
        
        if verbose:
            print(f"Successfully saved sampled CSV with {len(sampled_df):,} rows")
            
            # Show file size comparison
            original_size = input_path.stat().st_size / (1024 * 1024)  # MB
            sampled_size = output_path.stat().st_size / (1024 * 1024)  # MB
            size_reduction = ((original_size - sampled_size) / original_size) * 100
            
            print(f"\nFile size comparison:")
            print(f"  Original: {original_size:.2f} MB")
            print(f"  Sampled: {sampled_size:.2f} MB")
            print(f"  Size reduction: {size_reduction:.2f}%")
    
    return sampled_df


def analyze_case_id_distribution(df, verbose=True):
    """
    Analyze the distribution of case_ids in the dataset.
    
    Args:
        df (pandas.DataFrame): DataFrame to analyze
        verbose (bool): Print detailed analysis
    
    Returns:
        dict: Analysis results
    """
    
    if verbose:
        print("\n" + "=" * 60)
        print("CASE ID DISTRIBUTION ANALYSIS")
        print("=" * 60)
    
    case_id_counts = df['case_id'].value_counts()
    
    results = {
        'total_rows': len(df),
        'unique_case_ids': len(case_id_counts),
        'min_activities': case_id_counts.min(),
        'max_activities': case_id_counts.max(),
        'mean_activities': case_id_counts.mean(),
        'median_activities': case_id_counts.median()
    }
    
    if verbose:
        print(f"Dataset Overview:")
        print(f"  Total rows: {results['total_rows']:,}")
        print(f"  Unique case_ids: {results['unique_case_ids']:,}")
        
        print(f"\nActivities per case_id:")
        print(f"  Minimum: {results['min_activities']}")
        print(f"  Maximum: {results['max_activities']}")
        print(f"  Mean: {results['mean_activities']:.2f}")
        print(f"  Median: {results['median_activities']:.2f}")
        
        print(f"\nTop 10 case_ids by activity count:")
        for i, (case_id, count) in enumerate(case_id_counts.head(10).items()):
            print(f"  {i+1:2d}. Case ID {case_id}: {count} activities")
        
        # Distribution analysis
        print(f"\nDistribution of activities per case_id:")
        bins = [1, 2, 5, 10, 20, 50, 100, float('inf')]
        labels = ['1', '2-4', '5-9', '10-19', '20-49', '50-99', '100+']
        
        for i, (lower, upper) in enumerate(zip(bins[:-1], bins[1:])):
            if upper == float('inf'):
                count = sum(1 for x in case_id_counts if x >= lower)
                range_label = labels[i]
            else:
                count = sum(1 for x in case_id_counts if lower <= x < upper)
                range_label = labels[i]
            
            if count > 0:
                pct = (count / len(case_id_counts)) * 100
                print(f"  {range_label:>6} activities: {count:,} case_ids ({pct:.1f}%)")
    
    return results


def main():
    """Main function to run the script."""
    
    # ==============================
    # CONFIGURATION - Edit these values as needed
    # ==============================
    
    # Input CSV file to sample
    INPUT_FILE = "api/data/merged_activities_data_cleaned.csv"
    
    # Output file name
    OUTPUT_FILE = "api/data/merged_activities_data_sample_10pct.csv"
    
    # Percentage of unique case_ids to sample (0-100)
    SAMPLE_PERCENTAGE = 10.0
    
    # Random seed for reproducible results (set to None for different results each time)
    RANDOM_SEED = 42
    
    # Set to True for detailed output, False for minimal output
    VERBOSE = True
    
    # Set to True to run detailed case_id distribution analysis
    RUN_ANALYSIS = True
    
    # ==============================
    # END CONFIGURATION
    # ==============================
    
    try:
        print(f"Configuration:")
        print(f"  Input file: {INPUT_FILE}")
        print(f"  Output file: {OUTPUT_FILE}")
        print(f"  Sample percentage: {SAMPLE_PERCENTAGE}%")
        print(f"  Random seed: {RANDOM_SEED}")
        print(f"  Verbose output: {VERBOSE}")
        print("=" * 50)
        
        # Load and analyze the original data first
        if RUN_ANALYSIS:
            df_original = pd.read_csv(INPUT_FILE)
            analyze_case_id_distribution(df_original, verbose=VERBOSE)
        
        # Sample the CSV file
        sampled_df = sample_case_ids(
            INPUT_FILE,
            OUTPUT_FILE,
            sample_percentage=SAMPLE_PERCENTAGE,
            random_seed=RANDOM_SEED,
            verbose=VERBOSE
        )
        
        print(f"\n✅ Successfully created sample dataset!")
        print(f"Input: {INPUT_FILE}")
        print(f"Output: {OUTPUT_FILE}")
        print(f"Final row count: {len(sampled_df):,}")
        print(f"Final unique case_ids: {sampled_df['case_id'].nunique():,}")
        
        # Show a sample of the sampled data
        if VERBOSE and len(sampled_df) > 0:
            print(f"\nSample of sampled data:")
            print(sampled_df.head(10))
            
            # Quick verification
            selected_case_ids = sampled_df['case_id'].unique()
            print(f"\nVerification - First 10 selected case_ids:")
            print(sorted(selected_case_ids)[:10])
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
