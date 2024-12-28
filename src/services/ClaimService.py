from utils.sheets.GoogleSheetUtils import GoogleSheetUtils

class ClaimService:
    def __init__(self):
        self.sheet_utils = GoogleSheetUtils()

    def get_claims(self):
        return self.sheet_utils.get_sheet_by_name("Claims")

    def is_duplicate_claim(self, house_name, user_id):
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
        self.sheet_utils.write_to_row("Claims", [house_name.strip(), str(user_id)])
        return f"You have successfully claimed {house_name.strip()}."

    def delete_claim(self, identifier):
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
