import pandas as pd
import ast
import os

def simple_explode_csv(input_file, output_file=None):
    """
    Simple function to explode the CSV by the list in the fourth column.
    Creates a new row for each item in the list while copying all other data.
    """
    try:
        # Read the CSV file
        print(f"Reading: {input_file}")
        df = pd.read_csv(input_file)
        
        print(f"Original data: {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        
        # Assume the list column is the last column (4th column)
        list_column = df.columns[-1]  # SM_DS_REQUEST_processed
        print(f"List column: {list_column}")
        
        exploded_rows = []
        
        for _, row in df.iterrows():
            list_value = row[list_column]
            
            # Parse the list string
            try:
                if pd.isna(list_value) or str(list_value).strip() == '':
                    items = ['']
                else:
                    # Convert string representation of list to actual list
                    items = ast.literal_eval(str(list_value))
                    if not isinstance(items, list):
                        items = [items]
            except:
                # If parsing fails, treat as single item
                items = [str(list_value)]
            
            # Create a new row for each item in the list
            for item in items:
                new_row = row.copy()
                new_row[list_column + '_individual'] = item
                exploded_rows.append(new_row)
        
        # Create new dataframe
        result_df = pd.DataFrame(exploded_rows)
        
        print(f"Exploded data: {len(result_df)} rows")
        print(f"New rows created: {len(result_df) - len(df)}")
        
        # Show sample
        print(f"\nSample results:")
        sample_cols = [df.columns[0], list_column, list_column + '_individual']
        print(result_df[sample_cols].head(10))
        
        # Save if output file specified
        if output_file:
            result_df.to_csv(output_file, index=False)
            print(f"\nSaved to: {output_file}")
        
        return result_df
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    input_file = r"d:\Projects\value-partners-backend\api\data\Activity Table Tickets_processed.csv"
    output_file = r"d:\Projects\value-partners-backend\api\data\Activity Table Tickets_exploded_simple.csv"
    
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return
    
    result = simple_explode_csv(input_file, output_file)
    
    if result is not None:
        print("\n" + "="*50)
        print("SUCCESS! CSV exploded by list items.")
        print("="*50)
        
        # Show some statistics
        original_df = pd.read_csv(input_file)
        
        # Count rows with multiple items
        multi_item_count = 0
        for _, row in original_df.iterrows():
            try:
                items = ast.literal_eval(str(row[original_df.columns[-1]]))
                if isinstance(items, list) and len(items) > 1:
                    multi_item_count += 1
            except:
                pass
        
        print(f"Original rows with multiple list items: {multi_item_count}")
        print(f"Total original rows: {len(original_df)}")
        print(f"Total exploded rows: {len(result)}")
        print(f"Expansion ratio: {len(result) / len(original_df):.2f}x")

if __name__ == "__main__":
    main()
