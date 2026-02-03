import sys
import os
import keyring
from dotenv import load_dotenv

from helper import *
from Beta_Riot import RiotClient
from Beta_Open import check_open
from Beta_AccountManager import AccountManager
from Beta_CreateAccount import CreateAccount
from Beta_AccountDrag import DropArea

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea

class MainApp(QWidget):
    clicked_account = AccountManager.clicked_account

    def __init__(self, riot_client):
        super().__init__()
        self.riot_client = riot_client

        self.setWindowTitle("Riot Logger")  # App Name
        self.setFixedSize(542, 472)         # Prevent resizing

        # Set icon that appears in app's window header (top-left)
        self.setWindowIcon(QIcon(get_resource_path("images/icon.ico")))  # You can also use .ico

        # Set background color
        self.setStyleSheet("background-color: #242424; color: white;")

        layout = QVBoxLayout(self)
        self.service_name = "riot-acc-manager"

        # Create a scrollable area for the account buttons
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Hide the scrollbar
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = DropArea(scroll_area, self)
        self.scroll_layout = QVBoxLayout(scroll_content) 
        scroll_area.setWidget(scroll_content)

        # Load API key once for the app
        load_dotenv('getenv.env')
        self.api_key = os.getenv('api_key')
        if not self.api_key:
            raise ValueError('API key not found. Please set api_key in getenv.env')

        self.users = load_data()  # Load user data
        print('User count: ', len(self.users))
        # ---------- create account fields ---------- #

        for user in self.users:
            self.create_account(user, button_width, button_height, button_radius)

        # max_accounts_visible = 6
        # create_account_count = max_accounts_visible - len(self.users)
        # for i in range(create_account_count): 
        #    create_account_widget = CreateAccount(self, button_width, button_height, button_radius, scroll_area)
        #    self.scroll_layout.addWidget(create_account_widget)

        # if create_account_count <= 0:  # ehk visible acce on 6 voi rohkem ning peab lisama eraldi new acc buttoni 
        create_account_widget = CreateAccount(self, button_width, button_height, button_radius, scroll_area)
        self.scroll_layout.addWidget(create_account_widget)

        self.scroll_area = scroll_area
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def create_account(self, user, button_width, button_height, button_radius):
        account_button = AccountManager(user, button_width, button_height, button_radius, parent=self)
        account_button.user_data = user
        account_button.clicked_account.connect(self.on_signal_received)
        self.scroll_layout.addWidget(account_button)
        return account_button

    def on_signal_received(self, username, password):
        try:
            keyringPassword = keyring.get_password("riot-acc-manager", username)
            if keyringPassword == None:
                raise Exception
            else:
                password = keyringPassword
        except Exception as e:
            if password:
                print(e, ' Using arg password next')
            else:
                print('No password found anywhere.')

        print(f"Signal received with log in information")
        # going to Beta_Riot.py now to send username, password to there.
        self.riot_client.execute(username, password)

if __name__ == "__main__":
    if check_open('Logger') == True:
        sys.exit('*Forced exit*')

    # Load info
    # users = load_data()                   # Load user data
    q_app = QApplication(sys.argv)        # Create QApplication instance
    riot_client = RiotClient()            # Create RiotClient instance
    main_app = MainApp(riot_client)       # Create MainApp instance

    # Actually do something now with info
    check_open('Client')                  # Open Riot client connection
    main_app.show()                       # Show the main app

    sys.exit(q_app.exec())  # event loop
