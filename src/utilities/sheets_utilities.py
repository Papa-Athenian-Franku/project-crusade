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
    
def write_to_row(sheet_name, given_data):
    # Open the Google Sheets document by URL
    sheet = client.open_by_url(SHEET_URL)

    try:
        # Access the specific worksheet by name
        worksheet = sheet.worksheet(sheet_name)

        # Get all values from the worksheet
        values = worksheet.get_all_values()

        # Find number of rows
        number_of_rows = len(values)

        # Insert Data into next empty Row
        worksheet.insert_row(given_data, number_of_rows + 1)
        return True
            
    except gspread.exceptions.WorksheetNotFound:
        return False
    
def write_to_cell(sheet_name, column, given_data):
    # Open the Google Sheets document by URL
    sheet = client.open_by_url(SHEET_URL)

    try:
        # Access the specific worksheet by name
        worksheet = sheet.worksheet(sheet_name)

        # Get all values from the worksheet
        values = worksheet.get_all_values()

        # Find the row with the specified house_name
        for index, row in enumerate(values):
            if row and row[0] == given_data[0]:  # Assuming house_name is in the first column
                # Write the new data to the specified cell
                worksheet.update_cell(index + 1, column, given_data)
                return True
            
    except gspread.exceptions.WorksheetNotFound:
        return False
    
    except Exception:
        print(f"House '{given_data[0]}' not found in the sheet.")
        return False

# Testing Segment
if __name__ == "__main__":
    sheet_name = 'bot test sheet'
    # downloaded_data = get_sheet_by_name(sheet_name)
    data = ["this", "is", "bot", "written"]
    write_to_row(sheet_name, data)
