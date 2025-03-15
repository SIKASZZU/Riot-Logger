import subprocess
import pygetwindow as gw
import random
import time
import win32api
import win32gui
import win32con

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
print(selected_account)
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

################# Find Riot Client window (doesnt have to be focused) #################

riot_window = gw.getWindowsWithTitle('Riot Client')[0]
hwnd = win32gui.FindWindow(None, riot_window.title)  # insert argument riot client name
time.sleep(0.5)  # Optionally, give some time for the window to become active

################# Log into the account #################

def scale_coords(original_coords, window_size, normalized_size):
    """Scale coordinates proportionally to the current window size."""
    scale_x = window_size.width / normalized_size[0]
    scale_y = window_size.height / normalized_size[1]
    return (int(original_coords[0] * scale_x), int(original_coords[1] * scale_y))

normalized_size = (1536, 864)
user_xy         = (200, 275)
pass_xy         = (200, 320)
login_button_xy = (200, 700)

print(riot_window.width, riot_window.height)
if riot_window.width == normalized_size[0] and riot_window.height == normalized_size[1]:
    print('Window is normal sized')
    user_xy = (200, 275)
    pass_xy = (200, 320)
    login_button_xy = (200, 700)

elif riot_window.width < normalized_size[0] and riot_window.height < normalized_size[1]:
    print('Window is undersized')
    user_xy = scale_coords((200, 275), riot_window, normalized_size)
    pass_xy = scale_coords((200, 320), riot_window, normalized_size)
    login_button_xy = scale_coords((200, 700), riot_window, normalized_size)

elif riot_window.width > normalized_size[0] and riot_window.height > normalized_size[1]:
    print('Window is oversized')
    user_xy = scale_coords((200, 275), riot_window, normalized_size)
    pass_xy = scale_coords((200, 320), riot_window, normalized_size)
    login_button_xy = scale_coords((200, 700), riot_window, normalized_size)

print(f"user_xy: {user_xy}")
print(f"pass_xy: {pass_xy}")
print(f"login_button_xy: {login_button_xy}")

# Get the window's position and size (left, top, width, height)
left, top, width, height = riot_window.left, riot_window.top, riot_window.width, riot_window.height

# Adjust the click coordinates relative to the Riot Client window
adjusted_user_xy = (left + user_xy[0], top + user_xy[1])
adjusted_pass_xy = (left + pass_xy[0], top + pass_xy[1])
adjusted_login_button_xy = (left + login_button_xy[0], top + login_button_xy[1])

################# Clickin username1 password1g #################

random_sleep = random.uniform(0.002, 0.005)

def send_click(coords_x, coord_y):
    client_x, client_y = win32gui.ScreenToClient(hwnd, (coords_x, coord_y))
    lParam = win32api.MAKELONG(client_x, client_y)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)

def send_text(text):
    """Send text to a window using SendMessage."""
    for char in text:
        win32api.SendMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
        time.sleep(random_sleep)  # Small delay to simulate natural typing

# Click and type username
send_click(adjusted_user_xy[0], adjusted_user_xy[1])
time.sleep(random_sleep)
send_text(account_name)

# Click and type password
send_click(adjusted_pass_xy[0], adjusted_pass_xy[1])
time.sleep(random_sleep)
send_text(account_pass)

# Click the login button
send_click(adjusted_login_button_xy[0], adjusted_login_button_xy[1])