import pandas as pd
import os
import re
def process_first_column(text):
    """
    Example function to process the first column.
    This function calculates the length of the text.
    You can modify this function to implement any logic you need.
    """
    #Look for all texts with the structure GBS#####
    pattern = r'GBS\d{5}'
    matches = re.findall(pattern, str(text))
    if not matches:
        return "['GBS']"
    return matches
    
def process_csv_file(input_file, output_file=None):
    """
    Reads a CSV file, processes the first column, and creates a new column with the result.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to the output CSV file (optional)
    
    Returns:
        pandas.DataFrame: The processed dataframe
    """
    try:
        # Read the CSV file
        print(f"Reading CSV file: {input_file}")
        df = pd.read_csv(input_file)
        
        # Get the first column name
        first_column = df.columns[0]
        print(f"First column: {first_column}")
        
        # Apply the function to the first column and create a new column
        new_column_name = f"{first_column}_processed"
        df[new_column_name] = df[first_column].apply(process_first_column)
        
        print(f"Created new column: {new_column_name}")
        
        # Display some statistics
        print(f"\nDataset info:")
        print(f"- Total rows: {len(df)}")
        print(f"- Columns: {list(df.columns)}")
        print(f"\nFirst few rows of the new column:")
        print(df[[first_column, new_column_name]].head())
        
        # Save to output file if specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"\nProcessed data saved to: {output_file}")
        
        return df
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return None
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None

def main():
    # Configuration
    input_file = r"d:\Projects\value-partners-backend\api\data\Activity Table Tickets copy.csv"
    output_file = r"d:\Projects\value-partners-backend\api\data\Activity Table Tickets_processed.csv"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    # Process the CSV
    processed_df = process_csv_file(input_file, output_file)
    
    if processed_df is not None:
        print("\nProcessing completed successfully!")
        
        # Show some sample results
        print("\nSample results:")
        print(processed_df[['SM_DS_REQUEST', 'CASE_IDs']].head(10))

if __name__ == "__main__":
    main()
