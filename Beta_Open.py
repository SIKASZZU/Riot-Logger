import subprocess
import pygetwindow as gw

def check_open(title):
    """ title on kas 'Client' v 'Logger'. """
    windows = gw.getAllTitles()
    open_windows = [window for window in windows if window.strip()]
    
    print('\n', open_windows)
    
    if title == 'Client':

        if 'Riot Client' in open_windows: 
            print('Riot Client is open\n'); return True
        
        elif 'League of Legends' in open_windows:
            print('Riot client is open and already logged in\n'); return False
        
        print('Opening Riot Client\n')
        launch_options = '--launch-product=league_of_legends --launch-patchline=live'
        subprocess.Popen(rf"C:\Riot Games\Riot Client\RiotClientServices.exe {launch_options}")

        while True:
            # check again for new titles
            windows = gw.getAllTitles()
            open_windows = [window for window in windows if window.strip()]
            
            client_opened = False
            if 'Riot Client' in open_windows: 
                client_opened = True
   
            if client_opened == True:  
                print('Riot Client is open\n'); return True
            
    elif title == 'Logger':
        if 'Riot Logger' in open_windows:
            print('Riot Logger is already open'); return True
        
        else: print('Opening Riot Logger');       return False            