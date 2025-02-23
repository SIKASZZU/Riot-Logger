import subprocess
import pygetwindow as gw
import pyautogui
import time

from window import activate_window

################# Read acc_details.txt #################

def read_acc_details():
    """ txt file has to be acc_details.txt and a new line == new account
        acc with format: name, accname, password.    """

    accounts = []

    for row in open('acc_details.txt'):
        row = row.strip()
        values = row.split(',')
        
        username = values[0]
        account_name = values[1]
        account_pass = values[2]

        accounts.append((username, account_name, account_pass))

    return accounts

accounts_list = read_acc_details()
print(accounts_list)

################# Open riot client #################

launch_options = '--launch-product=league_of_legends --launch-patchline=live'
subprocess.Popen(rf"C:\Riot Games\Riot Client\RiotClientServices.exe {launch_options}")
print('Opening Riot Client\n')

################# Create tk window #################

selected_account = activate_window(accounts_list)
account_name, account_pass = selected_account

################# Check if client opened #################
while True:
    client_opened = False
    windows = gw.getAllTitles()
    open_windows = [window for window in windows if window.strip()]
    for title in open_windows:
        if title == 'Riot Client':
            client_opened = True
    if client_opened == True:  break

print('Riot Client is open\n')


################# Active window Riot Client #################
riot_window = gw.getWindowsWithTitle('Riot Client')[0]  # Find the first window with the title 'Riot Client'
riot_window.activate()  # Activate the window to bring it to the foreground

time.sleep(0.5)  # Optionally, give some time for the window to become active

################# Log into the account #################
user_xy         = (200, 275)
pass_xy         = (200, 320)
login_button_xy = (200, 700)

# Get the window's position and size (left, top, width, height)
left, top, width, height = riot_window.left, riot_window.top, riot_window.width, riot_window.height

# Adjust the click coordinates relative to the Riot Client window
adjusted_user_xy = (left + user_xy[0], top + user_xy[1])
adjusted_pass_xy = (left + pass_xy[0], top + pass_xy[1])
adjusted_login_button_xy = (left + login_button_xy[0], top + login_button_xy[1])

################# Clicking #################
pyautogui.click(adjusted_user_xy)
pyautogui.typewrite(account_name)

pyautogui.click(adjusted_pass_xy)
pyautogui.typewrite(account_pass)

pyautogui.click(adjusted_login_button_xy)