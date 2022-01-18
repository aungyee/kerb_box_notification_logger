import gspread

sa = gspread.service_account(filename='config/service_account.json')
sh = sa.open('Kerb Box Parsed Notifications')

wks = sh.worksheet("kerbbox-notif")


def append_row_to_google_sheets(message):
    wks.append_row(message)
