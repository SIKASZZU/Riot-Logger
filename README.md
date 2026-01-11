Store Your accounts so login into league takes less time! Forget about opening txt files or google drive to copy c and v the usernames and passcodes.

https://cdn.discordapp.com/attachments/1458766818574598229/1458767244334075937/image.png?ex=6964cadd&is=6963795d&hm=db0f87d3f4bbb68274b443631c3c3c2034cbeb121f4016cead552aef24ae5b00&

https://github.com/user-attachments/assets/6718ec71-e556-4386-9ab3-c802a109264a


Opening the LoL Account Manager.exe creates a acc_details.txt file. 
Program stores Your accounts locally. 
In that file every line is 1 account. 
Stored with principle: visible name, log in name, password

dependencies installed with pip:
    pygetwindow
    PyQt6
    dotenv
    argon2-cffi

how to build:
    pyinstaller --noconsole --onefile --icon=images/icon.ico --add-data="images;images" --name RiotLogger Beta_Main.py
