from Beta_Open import check_open
import subprocess
import pygetwindow as gw
import random
import time
import win32api
import win32gui
import win32con


class RiotClient:
    def __init__(self):

        self.normalized_size        = (1536, 864)
        self.normal_user_xy         = (200, 275)
        self.normal_pass_xy         = (200, 320)
        self.normal_login_button_xy = (200, 700)
        
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


    def send_info(self, scaled_coords, username, password):
        scaled_user_xy, scaled_pass_xy, scaled_login_button_xy = scaled_coords

        adjusted_user_xy = (self.left + scaled_user_xy[0], self.top + scaled_user_xy[1])
        adjusted_pass_xy = (self.left + scaled_pass_xy[0], self.top + scaled_pass_xy[1])
        adjusted_login_button_xy = (self.left + scaled_login_button_xy[0], self.top + scaled_login_button_xy[1])

        time.sleep(0.5)  # wait a little to give riot client time to open fully.
        
        # Click and type username
        self.send_click(adjusted_user_xy[0], adjusted_user_xy[1])
        time.sleep(self.random_sleep)
        self.send_text(username)

        # Click and type password
        self.send_click(adjusted_pass_xy[0], adjusted_pass_xy[1])
        time.sleep(self.random_sleep)
        self.send_text(password)

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

        # kirjuta self valued yle, sest i dont fucking know. 
        # see shit crashib muidu, kui riot juba lahti ja appi avad ja yritad logida.
        self.riot_window = gw.getWindowsWithTitle('Riot Client')[0]
        self.hwnd = win32gui.FindWindow(None, self.riot_window.title)
        self.left, self.top, self.width, self.height = self.riot_window.left, self.riot_window.top, self.riot_window.width, self.riot_window.height

        if self.riot_window.width == self.normalized_size[0] and self.riot_window.height == self.normalized_size[1]:
            print('Window is normal sized')
            return (self.user_xy, self.pass_xy, self.login_button_xy)

        elif self.riot_window.width < self.normalized_size[0] and self.riot_window.height < self.normalized_size[1]:
            print('Window is undersized')
            scaled_user_xy = self.scale_coords(self.user_xy, self.riot_window, self.normalized_size)
            scaled_pass_xy = self.scale_coords(self.pass_xy, self.riot_window, self.normalized_size)
            scaled_login_button_xy = self.scale_coords(self.login_button_xy, self.riot_window, self.normalized_size)
            return (scaled_user_xy, scaled_pass_xy, scaled_login_button_xy)

        elif self.riot_window.width > self.normalized_size[0] and self.riot_window.height > self.normalized_size[1]:
            print('Window is oversized')
            scaled_user_xy = self.scale_coords(self.user_xy, self.riot_window, self.normalized_size)
            scaled_pass_xy = self.scale_coords(self.pass_xy, self.riot_window, self.normalized_size)
            scaled_login_button_xy = self.scale_coords(self.login_button_xy, self.riot_window, self.normalized_size)
            return (scaled_user_xy, scaled_pass_xy, scaled_login_button_xy)

    
    def scale_coords(self, original_coords, window_size, normalized_size):
        """Scale coordinates proportionally to the current window size."""
        scale_x = window_size.width / normalized_size[0]
        scale_y = window_size.height / normalized_size[1]
        return (int(original_coords[0] * scale_x), int(original_coords[1] * scale_y))


    def execute(self, username, password):
        
        # FIXME: siin on mingi veider bug, et kui windowi ei ole v midagi taolist ss crashib.
        boolean_is_open = check_open('Client')
        if boolean_is_open == False:  return               # League of Legendi ei saa andmeid kirjutada. Return
        
        scaled_coords = self.scale()                       # return user_xy, pass_xy and login_xy coords relative to riot client window size
        self.send_info(scaled_coords, username, password)  # use scaled coords to type log in info and click log in


if __name__ == '__main__':
    riot = RiotClient()
    riot.open()