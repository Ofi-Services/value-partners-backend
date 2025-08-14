import pandas as pd
import sys
from pathlib import Path

def filter_csv_columns(input_file, output_file, columns_to_keep):
    """
    Keep only specified columns from a CSV file and delete all others.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
        columns_to_keep (list): List of column names to keep
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    try:
        # Read the CSV file
        print(f"Reading file: {input_file}")
        df = pd.read_csv(input_file)
        
        print(f"Original file has {len(df)} rows and {len(df.columns)} columns")
        print(f"Original columns: {list(df.columns)}")
        
        # Check which columns exist in the dataframe
        existing_columns = list(df.columns)
        valid_columns = [col for col in columns_to_keep if col in existing_columns]
        missing_columns = [col for col in columns_to_keep if col not in existing_columns]
        
        if missing_columns:
            print(f"\n⚠️  Warning: These columns were not found in the file:")
            for col in missing_columns:
                print(f"  - {col}")
        
        if not valid_columns:
            print("❌ Error: None of the specified columns exist in the file!")
            return False
        
        print(f"\n✅ Keeping {len(valid_columns)} columns:")
        for col in valid_columns:
            print(f"  - {col}")
        
        removed_columns = [col for col in existing_columns if col not in valid_columns]
        print(f"\n🗑️  Removing {len(removed_columns)} columns:")
        for col in removed_columns:
            print(f"  - {col}")
        
        # Filter the dataframe to keep only specified columns
        filtered_df = df[valid_columns]
        
        # Save the filtered dataframe
        filtered_df.to_csv(output_file, index=False)
        
        print(f"\n✅ Successfully saved filtered file: {output_file}")
        print(f"Filtered file has {len(filtered_df)} rows and {len(filtered_df.columns)} columns")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found.")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def filter_csv_columns_interactive():
    """
    Interactive version that asks user for input.
    """
    
    print("CSV Column Filter Tool")
    print("=" * 30)
    
    # Get input file
    input_file = input("Enter path to input CSV file: ").strip().strip('"')
    
    if not Path(input_file).exists():
        print(f"❌ File not found: {input_file}")
        return
    
    # Show current columns
    try:
        df_preview = pd.read_csv(input_file, nrows=0)
        print(f"\nCurrent columns in the file ({len(df_preview.columns)}):")
        for i, col in enumerate(df_preview.columns, 1):
            print(f"  {i:2d}. {col}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Get columns to keep
    print("\nEnter the column names you want to keep (one per line).")
    print("Type 'done' when finished, or 'cancel' to exit:")
    
    columns_to_keep = []
    while True:
        col_name = input("Column name: ").strip()
        if col_name.lower() == 'done':
            break
        elif col_name.lower() == 'cancel':
            print("Operation cancelled.")
            return
        elif col_name:
            columns_to_keep.append(col_name)
            print(f"  Added: {col_name}")
    
    if not columns_to_keep:
        print("❌ No columns specified.")
        return
    
    # Get output file
    output_file = input("Enter path for output CSV file: ").strip().strip('"')
    
    # Confirm operation
    print(f"\nOperation Summary:")
    print(f"  Input file: {input_file}")
    print(f"  Output file: {output_file}")
    print(f"  Columns to keep: {columns_to_keep}")
    
    confirm = input("\nProceed? (y/n): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("Operation cancelled.")
        return
    
    # Execute the filtering
    success = filter_csv_columns(input_file, output_file, columns_to_keep)
    
    if success:
        print("\n🎉 Operation completed successfully!")
    else:
        print("\n❌ Operation failed.")

def main():
    """
    Main function with example usage and command line support.
    """
    
    # Example usage with predefined values
    if len(sys.argv) == 1:
        # Interactive mode
        filter_csv_columns_interactive()
    else:
        # Command line mode
        if len(sys.argv) < 4:
            print("Usage: python filter_columns.py <input_file> <output_file> <column1> <column2> ...")
            print("Example: python filter_columns.py data.csv filtered_data.csv SYSTEM_ID LG_USER_ID LG_LOG_TIME_TIMESTAMP")
            return
        
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        columns_to_keep = sys.argv[3:]
        
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        print(f"Columns to keep: {columns_to_keep}")
        
        success = filter_csv_columns(input_file, output_file, columns_to_keep)
        
        if not success:
            sys.exit(1)

# Example function for your specific use case
def filter_activity_tables():
    """
    Example function to filter the activity table files with common columns.
    """
    
    # Define the columns you want to keep
    columns_to_keep = [
        'SYSTEM_ID',
        'CASE_ID',  # Note: might be 'CASE ID' in older files
        'LG_USER_ID',
        'LG_ID_SOGGETTO', 
        'LG_LOG_TIME_TIMESTAMP',
        'LG_OPERATION_CODE',
        'LG_OPERATION_RESULT',
        'LG_APPLICATION',
        'LG_OPERATION_TYPE',
        'LG_CHANNEL',
        'LG_ROLE'
    ]
    
    # Input files
    file1 = r"d:\Projects\value-partners-backend\api\data\updated_data\Activities Table MySella 01_04_2025_30_06_2025.csv"
    file2 = r"d:\Projects\value-partners-backend\api\data\updated_data\Activities Table MySella 01_01_2024_29_02_2024.csv"
    
    # Output files
    output1 = r"d:\Projects\value-partners-backend\api\data\updated_data\Activities_2025_filtered.csv"
    output2 = r"d:\Projects\value-partners-backend\api\data\updated_data\Activities_2024_filtered.csv"
    
    print("Filtering Activity Tables")
    print("=" * 30)
    
    # Filter first file
    print("\nProcessing 2025 file...")
    success1 = filter_csv_columns(file1, output1, columns_to_keep)
    
    # Filter second file (handle different column name)
    print("\nProcessing 2024 file...")
    columns_to_keep_2024 = columns_to_keep.copy()
    # Replace CASE_ID with CASE ID for the 2024 file
    if 'CASE_ID' in columns_to_keep_2024:
        columns_to_keep_2024.remove('CASE_ID')
        columns_to_keep_2024.append('CASE ID')
    
    success2 = filter_csv_columns(file2, output2, columns_to_keep_2024)
    
    if success1 and success2:
        print("\n🎉 Both files filtered successfully!")
        print(f"Filtered files saved as:")
        print(f"  - {output1}")
        print(f"  - {output2}")
    else:
        print("\n❌ Some operations failed.")

if __name__ == "__main__":
    # Uncomment the line below to run the example for activity tables
    # filter_activity_tables()
    
    # Run main function for interactive/command line use
    main()
