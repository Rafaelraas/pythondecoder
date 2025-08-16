import requests
import sys
from bs4 import BeautifulSoup

def print_grid_from_unstructured_doc(doc_url: str):
    
    try:
        print(f"Fetching data from: {doc_url}")
        response = requests.get(doc_url)
        response.raise_for_status()

        # Use BeautifulSoup to parse HTML and get only the text
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        table_data = []
        for row in table.find_all('tr'):
            row_data = []
            for cell in row.find_all(['td', 'th']):
                row_data.append(cell.get_text())
            table_data.append(row_data)

        points = []
        for row in table_data[1:]:
            x = int(row[0])
            char = row[1]
            y = int(row[2])
            points.append({'x': x, 'y': y, 'char': char})
        
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
        #print(f"\nCharacter grid ({max_y + 1} rows, {max_x + 1} columns):")
        for row in reversed(grid):
            print("".join(row))

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {type(e).__name__} - {e}", file=sys.stderr)


def create_staircase(nums):
  step = 1
  subsets = []
  while len(nums) != 0:
    if len(nums) >= step:
      subsets.append(nums[0:step])
      nums = nums[step:]
      step += 1
    else:
      return False
      
  return subsets

if __name__ == '__main__':
    print(create_staircase( [1, 2, 3, 4, 5, 6]))

    google_doc_url = input("Enter the published Google Doc URL: ")

    if google_doc_url.strip():
        # Esta nova função pode lidar com texto não estruturado
        print_grid_from_unstructured_doc(google_doc_url.strip())
    else:
        print("No URL entered. Please provide a URL from a published Google Doc.")
