import os
import requests
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_URL = "https://api.monday.com/v2"
MONDAY_TOKEN = os.environ["MONDAY_API_TOKEN"]

def _post(query):
    headers = {"Authorization": MONDAY_TOKEN, "Content-Type": "application/json"}
    resp = requests.post(MONDAY_API_URL, json={"query": query}, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]

def get_column_titles(board_id):
    """Maps auto-generated column IDs -> human-readable titles."""
    query = f'{{ boards(ids: [{board_id}]) {{ columns {{ id title }} }} }}'
    data = _post(query)
    columns = data["boards"][0]["columns"]
    return {c["id"]: c["title"] for c in columns}

def fetch_all_items(board_id):
    """Fetches every item on a board, handling pagination."""
    all_items = []
    query = f'''
    {{
      boards(ids: [{board_id}]) {{
        items_page(limit: 100) {{
          cursor
          items {{
            name
            column_values {{ id text value }}
          }}
        }}
      }}
    }}
    '''
    data = _post(query)
    page = data["boards"][0]["items_page"]
    all_items.extend(page["items"])
    cursor = page["cursor"]

    while cursor:
        query = f'''
        {{
          next_items_page(cursor: "{cursor}", limit: 100) {{
            cursor
            items {{
              name
              column_values {{ id text value }}
            }}
          }}
        }}
        '''
        data = _post(query)
        page = data["next_items_page"]
        all_items.extend(page["items"])
        cursor = page["cursor"]

    return all_items

def get_items_readable(board_id):
    """Returns items with human-readable column names instead of gibberish IDs."""
    col_map = get_column_titles(board_id)
    items = fetch_all_items(board_id)
    result = []
    for item in items:
        row = {"item_name": item["name"]}
        for cv in item["column_values"]:
            title = col_map.get(cv["id"], cv["id"])
            row[title] = cv["text"]
        result.append(row)
    return result