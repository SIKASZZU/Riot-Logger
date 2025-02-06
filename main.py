import subprocess
import pygetwindow as gw
import pyautogui
import tkinter as tk
import time

from acc_details import acc_details  # Ensure acc_details is a dictionary with account info

################# open riot client #################
subprocess.Popen(r"C:\Riot Games\Riot Client\RiotClientServices.exe")
print('Opening Riot Client\n')

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

################# Window, select account #################

account_selected = None
def on_button_click(key):
    global account_selected
    account_selected = key
    root.destroy()

root = tk.Tk()
root.title("Account Details Keys")

label = tk.Label(root, text="Choose account")
label.pack(pady=10)

# Create buttons for each account in acc_details dictionary
for key in acc_details.keys():
    button = tk.Button(root, text=key, command=lambda key=key: on_button_click(key))
    button.pack(pady=5)

root.mainloop()

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