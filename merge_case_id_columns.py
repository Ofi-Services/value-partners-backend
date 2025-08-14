import pandas as pd
import numpy as np
from pathlib import Path

def merge_case_id_columns(input_file, output_file=None):
    """
    Merge two CASE ID columns in a CSV file.
    If both columns have text, use the first one.
    If only one has text, use that one.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file (optional)
    
    Returns:
        pandas.DataFrame: DataFrame with merged CASE ID column
    """
    
    try:
        # Read the CSV file
        print(f"Reading file: {input_file}")
        df = pd.read_csv(input_file)
        
        print(f"Original shape: {df.shape}")
        print(f"Original columns: {list(df.columns)}")
        
        # Find columns that start with 'CASE'
        case_columns = [col for col in df.columns if col.strip().upper().startswith('CASE')]
        
        if len(case_columns) < 2:
            print(f"Found only {len(case_columns)} column(s) starting with 'CASE': {case_columns}")
            print(f"Need at least 2 columns to merge. Saving file as-is.")
            
            # Save the file as-is with the same naming structure
            if output_file:
                df.to_csv(output_file, index=False)
                print(f"File saved as-is to: {output_file}")
            
            return df
        
        # Use the first two CASE columns
        col1, col2 = case_columns[0], case_columns[1]
        print(f"Found CASE columns: {case_columns}")
        print(f"Will merge first two: '{col1}' and '{col2}'")
        
        print(f"Merging columns: '{col1}' and '{col2}'")
        
        # Show some sample data before merging
        print("\nSample data before merging:")
        sample_data = df[[col1, col2]].head(10)
        print(sample_data)
        
        # Count non-empty values in each column
        count1 = df[col1].notna().sum()
        count2 = df[col2].notna().sum()
        both_filled = (df[col1].notna() & df[col2].notna()).sum()
        
        print(f"\nData analysis:")
        print(f"  - '{col1}' has {count1} non-empty values")
        print(f"  - '{col2}' has {count2} non-empty values") 
        print(f"  - Both columns filled: {both_filled} rows")
        
        # Create merged column
        # Priority: first column if it has value, otherwise second column
        def merge_values(row):
            val1 = row[col1]
            val2 = row[col2]
            
            # If first column has a value (not NaN and not empty string), use it
            if pd.notna(val1) and str(val1).strip() != '':
                result = val1
            # Otherwise, use second column value (could be NaN)
            else:
                result = val2
            
            # Remove .0 suffix if it exists
            if pd.notna(result):
                result_str = str(result)
                if result_str.endswith('.0'):
                    result_str = result_str[:-2]  # Remove last 2 characters (.0)
                return result_str
            else:
                return result
        
        # Apply the merge function
        df['CASE_ID_MERGED'] = df.apply(merge_values, axis=1)
        
        # Show some sample data after merging
        print("\nSample data after merging:")
        sample_merged = df[[col1, col2, 'CASE_ID_MERGED']].head(10)
        print(sample_merged)
        
        # Count merged values
        merged_count = df['CASE_ID_MERGED'].notna().sum()
        print(f"\nMerged column has {merged_count} non-empty values")
        
        # Remove the original duplicate columns and rename the merged one
        df_final = df.drop(columns=[col1, col2])
        df_final.insert(1, 'CASE_ID', df['CASE_ID_MERGED'])  # Insert at position 1 (after SYSTEM_ID)
        df_final = df_final.drop(columns=['CASE_ID_MERGED'])
        
        print(f"\nFinal shape: {df_final.shape}")
        print(f"Final columns: {list(df_final.columns)}")
        
        # Save to output file if specified
        if output_file:
            df_final.to_csv(output_file, index=False)
            print(f"\nMerged file saved to: {output_file}")
        
        return df_final
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None

def merge_case_id_all_files_in_folder(folder_path, output_folder=None):
    """
    Merge CASE ID columns in all CSV files in a folder.
    
    Args:
        folder_path (str): Path to folder containing CSV files
        output_folder (str): Path to output folder (optional)
    """
    
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Folder not found: {folder}")
        return
    
    # Find all CSV files
    csv_files = list(folder.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {folder}")
        return
    
    print(f"Found {len(csv_files)} CSV files to process")
    
    # Set output folder
    if output_folder is None:
        output_folder = folder / "merged_case_id"
    else:
        output_folder = Path(output_folder)
    
    # Create output folder if it doesn't exist
    output_folder.mkdir(exist_ok=True)
    
    processed_count = 0
    
    for csv_file in csv_files:
        print(f"\n{'='*60}")
        print(f"Processing: {csv_file.name}")
        
        # Create output filename
        output_file = output_folder / f"merged_{csv_file.name}"
        
        # Process the file
        result = merge_case_id_columns(str(csv_file), str(output_file))
        
        if result is not None:
            processed_count += 1
            print(f"✅ Successfully processed: {csv_file.name}")
        else:
            print(f"❌ Failed to process: {csv_file.name}")
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"Successfully processed: {processed_count}/{len(csv_files)} files")
    print(f"Output folder: {output_folder}")

def main():
    """
    Main function - process all CSV files in the folder
    """
    
    # Process all files in the folder
    folder_path = r"d:\Projects\value-partners-backend\api\data\updated_data"
    output_folder = r"d:\Projects\value-partners-backend\api\data\updated_data\merged"
    
    print("Processing all CSV files in folder...")
    merge_case_id_all_files_in_folder(folder_path, output_folder)

if __name__ == "__main__":
    main()
