import pandas as pd
import os
import glob
from pathlib import Path

def join_csv_files(folder_path, output_file=None, pattern="*.csv"):
    """
    Join all CSV files in a folder into one CSV file.
    
    Args:
        folder_path (str): Path to the folder containing CSV files
        output_file (str): Path for the output file (optional)
        pattern (str): File pattern to match (default: "*.csv")
    
    Returns:
        pandas.DataFrame: Combined dataframe
    """
    
    # Convert to Path object for easier handling
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return None
    
    # Find all CSV files in the folder
    csv_files = list(folder_path.glob(pattern))
    
    if not csv_files:
        print(f"No CSV files found in '{folder_path}' matching pattern '{pattern}'")
        return None
    
    print(f"Found {len(csv_files)} CSV files to join:")
    for file in csv_files:
        print(f"  - {file.name}")
    
    # List to store all dataframes
    dataframes = []
    
    # Read each CSV file
    for file_path in csv_files:
        try:
            print(f"Reading: {file_path.name}")
            df = pd.read_csv(file_path)
            
            # Add a column to track source file
            df['source_file'] = file_path.name
            
            dataframes.append(df)
            print(f"  - Rows: {len(df)}, Columns: {len(df.columns)}")
            
        except Exception as e:
            print(f"Error reading {file_path.name}: {str(e)}")
            continue
    
    if not dataframes:
        print("No valid CSV files were read.")
        return None
    
    # Combine all dataframes
    print("\nCombining all dataframes...")
    combined_df = pd.concat(dataframes, ignore_index=True, sort=False)
    
    print(f"Combined dataframe:")
    print(f"  - Total rows: {len(combined_df)}")
    print(f"  - Total columns: {len(combined_df.columns)}")
    print(f"  - Columns: {list(combined_df.columns)}")
    
    # Save to output file if specified
    if output_file:
        try:
            combined_df.to_csv(output_file, index=False)
            print(f"\nCombined CSV saved to: {output_file}")
        except Exception as e:
            print(f"Error saving file: {str(e)}")
    
    return combined_df

def join_csv_files_simple(folder_path, output_file):
    """
    Simple version that joins CSV files without source tracking.
    
    Args:
        folder_path (str): Path to the folder containing CSV files
        output_file (str): Path for the output file
    """
    
    folder_path = Path(folder_path)
    csv_files = list(folder_path.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in '{folder_path}'")
        return
    
    print(f"Joining {len(csv_files)} CSV files...")
    
    # Read and combine all CSV files
    combined_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
    
    # Save the combined file
    combined_df.to_csv(output_file, index=False)
    
    print(f"Combined {len(combined_df)} rows into: {output_file}")

def analyze_csv_structure(folder_path):
    """
    Analyze the structure of CSV files in a folder to ensure they're compatible.
    
    Args:
        folder_path (str): Path to the folder containing CSV files
    """
    
    folder_path = Path(folder_path)
    csv_files = list(folder_path.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in '{folder_path}'")
        return
    
    print(f"Analyzing {len(csv_files)} CSV files for structure compatibility...\n")
    
    structures = {}
    
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path, nrows=0)  # Read only headers
            structures[file_path.name] = {
                'columns': list(df.columns),
                'column_count': len(df.columns)
            }
            
            # Get row count
            df_full = pd.read_csv(file_path)
            structures[file_path.name]['row_count'] = len(df_full)
            
        except Exception as e:
            print(f"Error reading {file_path.name}: {str(e)}")
            continue
    
    # Check if all files have the same structure
    if structures:
        first_file = next(iter(structures))
        first_columns = structures[first_file]['columns']
        
        compatible = True
        
        print("File Structure Analysis:")
        print("=" * 50)
        
        for filename, info in structures.items():
            print(f"\n{filename}:")
            print(f"  - Rows: {info['row_count']}")
            print(f"  - Columns: {info['column_count']}")
            print(f"  - Column names: {info['columns']}")
            
            if info['columns'] != first_columns:
                compatible = False
                print(f"  - ⚠️  WARNING: Different structure than {first_file}")
        
        print("\n" + "=" * 50)
        if compatible:
            print("✅ All files have the same structure - safe to join!")
            total_rows = sum(info['row_count'] for info in structures.values())
            print(f"Total rows after joining: {total_rows}")
        else:
            print("❌ Files have different structures - joining may cause issues!")
            print("Consider checking the files manually before joining.")

def main():
    """
    Main function with example usage.
    """
    
    # Configuration
    input_folder = r"d:\Projects\value-partners-backend\api\data\updated_data"
    output_file = r"d:\Projects\value-partners-backend\api\data\combined_csvs.csv"
    
    print("CSV File Joiner")
    print("=" * 30)
    
    # First, analyze the structure of files
    print("Step 1: Analyzing CSV file structures...")
    analyze_csv_structure(input_folder)
    
    print("\n" + "=" * 30)
    
    # Ask user if they want to continue
    response = input("\nDo you want to proceed with joining the files? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        print("\nStep 2: Joining CSV files...")
        combined_df = join_csv_files(input_folder, output_file)
        
        if combined_df is not None:
            print("\n✅ Files joined successfully!")
            
            # Show sample of combined data
            print("\nSample of combined data (first 5 rows):")
            print(combined_df.head())
            
            print(f"\nFile counts by source:")
            if 'source_file' in combined_df.columns:
                print(combined_df['source_file'].value_counts())
        else:
            print("\n❌ Failed to join files.")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()
