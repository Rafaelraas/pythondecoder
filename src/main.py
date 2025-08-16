import pandas as pd
import requests
import io
import sys
import re
from bs4 import BeautifulSoup

def print_grid_from_data(data_string: str):
    """
    Parses data from a string and prints a grid of characters.

    Args:
        data_string: A string containing the character data in TSV format.
    """
    try:
        # Pre-process the string to remove empty lines and extra whitespace
        lines = [line.strip() for line in data_string.strip().split('\n') if line.strip()]
        if len(lines) <= 1:  # Header only or empty
            print("No data rows found.")
            return
        
        cleaned_data_string = "\n".join(lines)

        # Use pandas to read the tab-separated data
        data = pd.read_csv(io.StringIO(cleaned_data_string), sep='\t')

        # Define expected columns
        x_col, char_col, y_col = 'x-coordinate', 'Character', 'y-coordinate'
        required_cols = [x_col, y_col, char_col]

        # Check if required columns exist
        if not all(col in data.columns for col in required_cols):
            print(f"Input data is missing one of the required columns: {required_cols}")
            print(f"Available columns: {data.columns.tolist()}")
            return

        # Ensure coordinate columns are numeric, coercing errors
        for col in [x_col, y_col]:
            data[col] = pd.to_numeric(data[col], errors='coerce')

        # Drop rows with invalid coordinates
        data.dropna(subset=[x_col, y_col], inplace=True)

        # Convert coordinates to integers
        for col in [x_col, y_col]:
            data[col] = data[col].astype(int)

        # Find the dimensions of the grid
        if data.empty:
            print("No valid data to display.")
            return
            
        max_x = data[x_col].max()
        max_y = data[y_col].max()

        # Create an empty grid filled with spaces
        grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]

        # Populate the grid with characters
        for index, row in data.iterrows():
            x = row[x_col]
            y = row[y_col]
            char = str(row[char_col])  # Ensure character is a string
            if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
                grid[y][x] = char

        # Print the grid by joining characters in each row
        for row in grid:
            print("".join(row))

    except KeyError as e:
        print(f"A column is missing in the data: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {type(e).__name__} - {e}", file=sys.stderr)


def print_grid_from_unstructured_doc(doc_url: str):
    """
    Fetches an unstructured (published) Google Doc, extracts data using regex,
    and prints the character grid. Handles concatenated data without spaces.

    Args:
        doc_url: The URL of the Google Doc published to the web.
    """
    try:
        print(f"Fetching data from: {doc_url}")
        response = requests.get(doc_url)
        response.raise_for_status()

        # Use BeautifulSoup to parse HTML and get only the text
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()
        table = soup.find('table')
        table_data = []
        for row in table.find_all('tr'):
            row_data = []
            for cell in row.find_all(['td', 'th']):
                row_data.append(cell.get_text())
            table_data.append(row_data)
            print(row_data)
        # Regex to find patterns of (number)(non-digit char)(number)
        # This is for concatenated data like "0█01▀10"
        # (\d+)   - Captures one or more digits (x-coordinate)
        # (\D)    - Captures a single non-digit character
        # (\d+)   - Captures one or more digits (y-coordinate)
        pattern = re.compile(r"(\d+)(\D)(\d+)")
        
        matches = pattern.finditer(text_content)
        
        points = []
        for match in matches:
            x = int(match.group(1))
            char = match.group(2)
            y = int(match.group(3))
            points.append({'x': x, 'y': y, 'char': char})
        # Debugging output
        print(f"Table : {table_data}")
        #print(f"response contents:  {response.text}")
        #print(f"Text content: {text_content}")
        #print(f"Matches: {matches}")
        #print(f"Found {len(points)} points in the document.")
        #print(f"Points: {points}")
        
        if not points:
            print("No valid coordinate data found in the document.")
            return

        # Find grid dimensions
        max_x = max(p['x'] for p in points)
        max_y = max(p['y'] for p in points)

        # Create and populate the grid
        grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]
        for p in points:
            if 0 <= p['y'] < len(grid) and 0 <= p['x'] < len(grid[0]):
                grid[p['y']][p['x']] = p['char']

        # Print the grid
        for row in grid:
            print("".join(row))

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {type(e).__name__} - {e}", file=sys.stderr)


if __name__ == '__main__':
    # Para usar, publique seu Google Doc via "Arquivo > Compartilhar > Publicar na web"
    # e cole a URL gerada abaixo.
    
    google_doc_url = input("Enter the published Google Doc URL: ")

    if google_doc_url.strip():
        # Esta nova função pode lidar com texto não estruturado
        print_grid_from_unstructured_doc(google_doc_url.strip())
    else:
        print("No URL entered. Please provide a URL from a published Google Doc.")
