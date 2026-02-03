import time
import subprocess
import pygetwindow as gw

def check_open(title):

    """ title on kas 'Client' v 'Logger'. """
    open_windows = [window for window in gw.getAllTitles() if window.strip()]

    if title == 'Client':

        if 'Riot Client' in open_windows:
            print('Riot Client is open\n')
            return True

        elif 'League of Legends' in open_windows:
            print('Riot client is open and already logged in\n')
            return False

        print('Opening Riot Client\n')
        launch_options = '--launch-product=league_of_legends --launch-patchline=live'
        # subprocess.Popen(rf"C:\Riot Games\Riot Client\RiotClientServices.exe {launch_options}")

        opening_try_counter = 0

        while True:

            open_windows = [window for window in gw.getAllTitles() if window.strip()]
    
            if (opening_try_counter % 10 == 0):
                print('starting new subprocess.')
                subprocess.Popen(rf"C:\Riot Games\Riot Client\RiotClientServices.exe {launch_options}")

            opening_try_counter += 1
            print(f'Trying to open Riot client times: {opening_try_counter}x')

            if 'Riot Client' in open_windows:
                print('Riot Client is open\n')
                break

            time.sleep(1)

        return True

    elif title == 'Logger':
        if 'Riot Logger' in open_windows:
            print('Riot Logger is already open')
            return True
        else:
            print('Opening Riot Logger')
            return False
        

if __name__ == '__main__':
    statement = 0 % 10
    print(statement)