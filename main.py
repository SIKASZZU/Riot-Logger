import subprocess
import pygetwindow as gw
import pyautogui
import time

from window import activate_window

from acc_details import acc_details  # Ensure acc_details is a dictionary with account info

################# open riot client #################
launch_options = '--launch-product=league_of_legends --launch-patchline=live'
subprocess.Popen(rf"C:\Riot Games\Riot Client\RiotClientServices.exe {launch_options}")
print('Opening Riot Client\n')

################# Window, select account #################

account_selected = activate_window()

################# check if client opened #################
while True:
    client_opened = False
    windows = gw.getAllTitles()
    open_windows = [window for window in windows if window.strip()]
    for title in open_windows:
        if title == 'Riot Client':
            client_opened = True
    if client_opened == True:  break

print('Riot Client is open\n')


print('ACCOUNT', account_selected, '\n')
username = acc_details[account_selected][0]
passcode = acc_details[account_selected][1]

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
pyautogui.typewrite(username)

pyautogui.click(adjusted_pass_xy)
pyautogui.typewrite(passcode)

pyautogui.click(adjusted_login_button_xy)