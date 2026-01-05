Store Your accounts so login into league takes less time! Forget about opening txt files or google drive to copy c and v the usernames and passcodes.


https://github.com/user-attachments/assets/6718ec71-e556-4386-9ab3-c802a109264a


Opening the LoL Account Manager.exe creates a acc_details.txt file. 
Program stores Your accounts locally. 
In that file every line is 1 account. 
Stored with principle: visible name, log in name, password

dependencies installed with pip:
    pygetwindow
    PyQt6
    dotenv


how to build:
    pyinstaller --noconsole --onefile --icon=images/icon.ico --add-data="images;images" --name RiotLogger Beta_Main.py
