import pandas as pd
from pathlib import Path

def compare_csv_columns(file1_path, file2_path):
    """
    Compare the columns of two CSV files and show differences.
    
    Args:
        file1_path (str): Path to the first CSV file
        file2_path (str): Path to the second CSV file
    """
    
    try:
        # Read only the headers (first row) to get column names
        df1 = pd.read_csv(file1_path, nrows=0)
        df2 = pd.read_csv(file2_path, nrows=0)
        
        file1_name = Path(file1_path).name
        file2_name = Path(file2_path).name
        
        print("CSV Files Column Comparison")
        print("=" * 50)
        
        # Get column lists
        columns1 = list(df1.columns)
        columns2 = list(df2.columns)
        
        print(f"\n{file1_name}:")
        print(f"  - Number of columns: {len(columns1)}")
        print(f"  - Columns: {columns1}")
        
        print(f"\n{file2_name}:")
        print(f"  - Number of columns: {len(columns2)}")
        print(f"  - Columns: {columns2}")
        
        # Find common columns
        common_columns = set(columns1).intersection(set(columns2))
        print(f"\nCommon columns ({len(common_columns)}):")
        for col in sorted(common_columns):
            print(f"  - {col}")
        
        # Find columns only in file1
        only_in_file1 = set(columns1) - set(columns2)
        if only_in_file1:
            print(f"\nColumns only in {file1_name} ({len(only_in_file1)}):")
            for col in sorted(only_in_file1):
                print(f"  - {col}")
        
        # Find columns only in file2
        only_in_file2 = set(columns2) - set(columns1)
        if only_in_file2:
            print(f"\nColumns only in {file2_name} ({len(only_in_file2)}):")
            for col in sorted(only_in_file2):
                print(f"  - {col}")
        
        # Check if column order is the same
        print(f"\nColumn order comparison:")
        if columns1 == columns2:
            print("✅ Columns are identical and in the same order")
        elif set(columns1) == set(columns2):
            print("⚠️  Same columns but different order")
            print("Column order differences:")
            max_len = max(len(columns1), len(columns2))
            for i in range(max_len):
                col1 = columns1[i] if i < len(columns1) else "---"
                col2 = columns2[i] if i < len(columns2) else "---"
                if col1 != col2:
                    print(f"  Position {i+1}: '{col1}' vs '{col2}'")
        else:
            print("❌ Different column structures")
        
        # Check for potential duplicates in column names
        print(f"\nDuplicate column check:")
        
        duplicates1 = [col for col in set(columns1) if columns1.count(col) > 1]
        if duplicates1:
            print(f"  {file1_name} has duplicate columns: {duplicates1}")
        
        duplicates2 = [col for col in set(columns2) if columns2.count(col) > 1]
        if duplicates2:
            print(f"  {file2_name} has duplicate columns: {duplicates2}")
            
        if not duplicates1 and not duplicates2:
            print("  ✅ No duplicate column names found")
        
        return {
            'file1_columns': columns1,
            'file2_columns': columns2,
            'common_columns': list(common_columns),
            'only_in_file1': list(only_in_file1),
            'only_in_file2': list(only_in_file2),
            'identical_structure': columns1 == columns2
        }
        
    except Exception as e:
        print(f"Error comparing files: {str(e)}")
        return None

def compare_csv_data_types(file1_path, file2_path, sample_rows=1000):
    """
    Compare data types of common columns between two CSV files.
    
    Args:
        file1_path (str): Path to the first CSV file
        file2_path (str): Path to the second CSV file
        sample_rows (int): Number of rows to sample for data type inference
    """
    
    try:
        # Read sample data
        df1 = pd.read_csv(file1_path, nrows=sample_rows)
        df2 = pd.read_csv(file2_path, nrows=sample_rows)
        
        file1_name = Path(file1_path).name
        file2_name = Path(file2_path).name
        
        # Find common columns
        common_columns = set(df1.columns).intersection(set(df2.columns))
        
        if not common_columns:
            print("No common columns found for data type comparison")
            return
        
        print(f"\nData Type Comparison for Common Columns")
        print("=" * 50)
        
        for col in sorted(common_columns):
            dtype1 = str(df1[col].dtype)
            dtype2 = str(df2[col].dtype)
            
            status = "✅" if dtype1 == dtype2 else "⚠️"
            print(f"{status} {col}:")
            print(f"    {file1_name}: {dtype1}")
            print(f"    {file2_name}: {dtype2}")
            
            # Show sample values if types differ
            if dtype1 != dtype2:
                print(f"    Sample from {file1_name}: {df1[col].dropna().head(3).tolist()}")
                print(f"    Sample from {file2_name}: {df2[col].dropna().head(3).tolist()}")
            print()
            
    except Exception as e:
        print(f"Error comparing data types: {str(e)}")

def main():
    # File paths
    file1 = r"d:\Projects\value-partners-backend\api\data\updated_data\Activities Table MySella 01_04_2025_30_06_2025.csv"
    file2 = r"d:\Projects\value-partners-backend\api\data\updated_data\Activities Table MySella 01_01_2024_29_02_2024.csv"
    
    # Compare columns
    result = compare_csv_columns(file1, file2)
    
    if result:
        # Compare data types for common columns
        compare_csv_data_types(file1, file2)

if __name__ == "__main__":
    main()
