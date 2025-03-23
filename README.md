Store Your accounts so login into league takes less time! Forget about opening txt files or google drive to copy c and v the usernames and passcodes.

Opening the LoL Account Manager.exe creates a acc_details.txt file. 
Program stores Your accounts locally. 
In that file every line is 1 account. 
Stored with principle: visible name, log in name, password


how to build:
    pyinstaller --noconsole --onefile --icon=images/icon.ico --add-data="images;images" Beta_App.py