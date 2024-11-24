import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope and credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('src/credentials.json', scope)

# Authorize the client
client = gspread.authorize(credentials)

# The Sheet URL is Constant.
SHEET_URL = "https://docs.google.com/spreadsheets/d/1JeRiqEGnnFask40FoHWZGbbhzpc9yNoj3myK7aOE3VA"

def get_sheet_by_name(sheet_name):
    # Open the Google Sheets document by URL
    sheet = client.open_by_url(SHEET_URL)

    try:
        # Access the specific worksheet by name
        worksheet = sheet.worksheet(sheet_name)

        # Get all values from the worksheet
        values = worksheet.get_all_values()

        # Return 2d Array of Values
        return values

    except gspread.exceptions.WorksheetNotFound:
        print(f"Sheet '{sheet_name}' not found.")
        return None
    
def write_sheet_by_name(sheet_name, given_data):
    # Open the Google Sheets document by URL
    sheet = client.open_by_url(SHEET_URL)

    try:
        # Access the specific worksheet by name
        worksheet = sheet.worksheet(sheet_name)

        # Process `given_data` to ensure lists are stored as single-cell strings
        processed_data = [
            ", ".join(item) if isinstance(item, list) else str(item)
            for item in given_data
        ]

        # Insert Data into the next empty Row (using append_row instead of insert_row)
        worksheet.append_row(processed_data)
        return True
            
    except gspread.exceptions.WorksheetNotFound:
        print(f"Worksheet '{sheet_name}' not found.")
        return False
    except Exception as e:
        print(f"Error writing to sheet {sheet_name}: {e}")
        return False

def overwrite_sheet_by_name(sheet_name, given_data):
    """
    Overwrites the entire sheet with new data.
    Clears the existing content and writes the new data.
    """
    # Open the Google Sheets document by URL
    sheet = client.open_by_url(SHEET_URL)

    try:
        # Access the specific worksheet by name
        worksheet = sheet.worksheet(sheet_name)

        # Clear all existing content in the sheet
        worksheet.clear()

        # Write the new data row by row, starting from the first row
        for row in given_data:
            # Process `given_data` to ensure lists are stored as single-cell strings
            processed_row = [
                ", ".join(item) if isinstance(item, list) else str(item)
                for item in row
            ]
            worksheet.append_row(processed_row)

        return True

    except gspread.exceptions.WorksheetNotFound:
        print(f"Worksheet '{sheet_name}' not found.")
        return False
    except Exception as e:
        print(f"Error overwriting sheet {sheet_name}: {e}")
        return False