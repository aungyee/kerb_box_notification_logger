import gspread

sa = gspread.service_account(filename='config/service_account.json')
sh = sa.open('KERB Box Notification Logs')

notifSheet = sh.worksheet("kerbbox-notif")

supportSheet = sh.worksheet("customer-support-gate")


def append_row_to_notif_google_sheets(message):
    notifSheet.append_row(message, value_input_option="USER_ENTERED")


def append_row_to_customer_support_google_sheets(message):
    supportSheet.append_row(message, value_input_option="USER_ENTERED")
