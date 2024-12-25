from utils.sheets.GoogleSheetUtils import GoogleSheetUtils

class ClaimService:
    def __init__(self):
        self.sheet_utils = GoogleSheetUtils()

    def get_claims(self):
        """
        Retrieve all claims from the 'Claims' sheet.
        """
        return self.sheet_utils.get_sheet_by_name("Claims")

    def is_duplicate_claim(self, house_name, user_id):
        """
        Check if a claim already exists for the given house name or user ID.
        """
        claims = self.get_claims()
        if not claims:
            return False, "No claims found."

        for claim in claims[1:]:  # Skip the header row
            if claim[0].strip() == house_name.strip():
                return True, "House name already claimed."
            if claim[1].strip() == str(user_id):
                return True, "User has already made a claim."

        return False, None

    def create_claim(self, house_name, user_id):
        """
        Add a new claim to the 'Claims' sheet if it's valid.
        """
        self.sheet_utils.write_to_row("Claims", [house_name.strip(), str(user_id)])
        return f"You have successfully claimed {house_name.strip()}."

    def delete_claim(self, identifier):
        """
        Delete a claim from the 'Claims' sheet by house name or user ID.
        """
        sheet_values = self.get_claims()
        if not sheet_values:
            return "The Claims sheet is empty or missing."

        updated_rows = [sheet_values[0]]  # Keep the header row
        claim_removed = False

        for row in sheet_values[1:]:
            if row[0].strip() == identifier.strip() or row[1].strip() == identifier.strip():
                claim_removed = True
            else:
                updated_rows.append(row)

        if claim_removed:
            self.sheet_utils.update_sheet_by_name("Claims", updated_rows)
            return f"The claim '{identifier}' has been successfully removed."
        else:
            return f"No claim matching '{identifier}' was found."
