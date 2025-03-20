import subprocess
import pygetwindow as gw
import random
import time
import win32api
import win32gui
import win32con
from window import activate_window


class RiotClient:
    def __init__(self):

        self.normalized_size = (1536, 864)
        self.user_xy         = (200, 275)
        self.pass_xy         = (200, 320)
        self.login_button_xy = (200, 700)
    
        self.riot_window = None
        self.hwnd   = None
        self.left   = 0
        self.top    = 0
        self.width  = 0
        self.height = 0

        self.random_sleep = random.uniform(0.002, 0.005)
    
    def open(self):
        launch_options = '--launch-product=league_of_legends --launch-patchline=live'
        subprocess.Popen(rf"C:\Riot Games\Riot Client\RiotClientServices.exe {launch_options}")
        print('Opening Riot Client\n')

        while True:
            client_opened = False
            windows = gw.getAllTitles()
            open_windows = [window for window in windows if window.strip()]
            for title in open_windows:
                if title == 'Riot Client':
                    client_opened = True
            
            if client_opened == True:  
                self.riot_window = gw.getWindowsWithTitle('Riot Client')[0]
                self.hwnd = win32gui.FindWindow(None, self.riot_window.title)
                self.left, self.top, self.width, self.height = self.riot_window.left, self.riot_window.top, self.riot_window.width, self.riot_window.height

                print('Riot Client is open\n')
                break


    def select_account(self):
        accounts_list = self.read_acc_details()
        selected_account = activate_window(accounts_list)
        self.account_name, self.account_pass = selected_account


    def send_info(self):
        # Adjust the click coordinates relative to the Riot Client window
        adjusted_user_xy = (self.left + self.user_xy[0], self.top + self.user_xy[1])
        adjusted_pass_xy = (self.left + self.pass_xy[0], self.top + self.pass_xy[1])
        adjusted_login_button_xy = (self.left + self.login_button_xy[0], self.top + self.login_button_xy[1])

        ################# Clickin username1 password1g #################

        # Click and type username
        self.send_click(adjusted_user_xy[0], adjusted_user_xy[1])
        time.sleep(self.random_sleep)
        self.send_text(self.account_name)

        # Click and type password
        self.send_click(adjusted_pass_xy[0], adjusted_pass_xy[1])
        time.sleep(self.random_sleep)
        self.send_text(self.account_pass)

        # Click the login button
        self.send_click(adjusted_login_button_xy[0], adjusted_login_button_xy[1])


    def send_click(self, coords_x, coord_y):
        client_x, client_y = win32gui.ScreenToClient(self.hwnd, (coords_x, coord_y))
        lParam = win32api.MAKELONG(client_x, client_y)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, lParam)


    def send_text(self, text):
        """Send text to a window using SendMessage."""
        for char in text:
            win32api.SendMessage(self.hwnd, win32con.WM_CHAR, ord(char), 0)
            time.sleep(self.random_sleep)  # Small delay to simulate natural typing
    

    def scale(self):
        print(self.riot_window.width, self.riot_window.height)
        if self.riot_window.width == self.normalized_size[0] and self.riot_window.height == self.normalized_size[1]:
            print('Window is normal sized')

        elif self.riot_window.width < self.normalized_size[0] and self.riot_window.height < self.normalized_size[1]:
            print('Window is undersized')
            user_xy = self.scale_coords(user_xy, self.riot_window, self.normalized_size)
            pass_xy = self.scale_coords(pass_xy, self.riot_window, self.normalized_size)
            login_button_xy = self.scale_coords(login_button_xy, self.riot_window, self.normalized_size)

        elif self.riot_window.width > self.normalized_size[0] and self.riot_window.height > self.normalized_size[1]:
            print('Window is oversized')
            user_xy = self.scale_coords(user_xy, self.riot_window, self.normalized_size)
            pass_xy = self.scale_coords(pass_xy, self.riot_window, self.normalized_size)
            login_button_xy = self.scale_coords(login_button_xy, self.riot_window, self.normalized_size)

    
    def scale_coords(original_coords, window_size, normalized_size):
        """Scale coordinates proportionally to the current window size."""
        scale_x = window_size.width / normalized_size[0]
        scale_y = window_size.height / normalized_size[1]
        return (int(original_coords[0] * scale_x), int(original_coords[1] * scale_y))


    def read_acc_details():
        """ txt file has to be acc_details.txt and a new line == new account
            acc with format: name, accname, password.    """
        
        try:
            open("acc_details.txt", "a").close()  # Creates the file if it doesn’t exist
        except Exception as e:
            print(f"Error creating acc_details.txt: {e}")

        # Load existing accounts from file
        try:
            with open("acc_details.txt", "r") as f:
                accounts_list = [tuple(line.strip().split(", ")) for line in f if line.strip()]
        except FileNotFoundError:
            accounts_list = []

        return accounts_list

    def execute(self):
        self.open()
        self.select_account()
        self.scale()
