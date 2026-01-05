import sys

from helper import *
from Beta_Riot import RiotClient
from Beta_Open import check_open
from Beta_AccountManager import AccountManager
from Beta_CreateAccount import CreateAccount

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea
from PyQt6.QtCore import QEvent


class DropArea(QWidget):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        try:
            text = event.mimeData().text()
            if '|' not in text:
                event.ignore()
                return
            riot_id, username = text.split('|', 1)

            layout = self.app.scroll_layout

            source_idx = -1
            source_widget = None
            for i in range(layout.count()):
                w = layout.itemAt(i).widget()
                if not w:
                    continue
                if getattr(w, 'riot_id', None) == riot_id and getattr(w, 'username', None) == username:
                    source_idx = i
                    source_widget = w
                    break

            if source_idx == -1 or source_widget is None:
                event.ignore()
                return

            # Determine target index based on drop y position
            pos = event.position().toPoint()
            target_idx = layout.count() - 1
            for i in range(layout.count()):
                w = layout.itemAt(i).widget()
                if not w:
                    continue
                # Skip counting if it's the source widget itself
                if w is source_widget:
                    continue
                mid_y = w.y() + w.height() // 2
                if pos.y() < mid_y:
                    target_idx = i
                    break

            # Remove the source widget from layout
            # Need to find the item index again because layout indices may shift
            for i in range(layout.count()):
                if layout.itemAt(i).widget() is source_widget:
                    layout.takeAt(i)
                    break

            # Adjust target_idx if source was before target
            if source_idx < target_idx:
                target_idx -= 1

            # Insert the widget at the new position
            if target_idx < 0:
                layout.insertWidget(0, source_widget)
            else:
                layout.insertWidget(target_idx, source_widget)

            # Rebuild users list from current layout order and save
            new_users = []
            for i in range(layout.count()):
                w = layout.itemAt(i).widget()
                if not w:
                    continue
                # Only include account widgets (they have riot_id attribute)
                if hasattr(w, 'riot_id') and getattr(w, 'riot_id'):
                    new_users.append({
                        'riot_id': getattr(w, 'riot_id'),
                        'tagline': getattr(w, 'tagline', ''),
                        'region': getattr(w, 'region', ''),
                        'username': getattr(w, 'username', ''),
                        'password': getattr(w, 'password', '')
                    })

            # Update app users and persist
            self.app.users = new_users
            from helper import save_data
            save_data(self.app.users)

            event.acceptProposedAction()
        except Exception as e:
            print('Drop handling failed:', e)
            event.ignore()


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

        self.username = None
        self.password = None

        # Create a scrollable area for the account buttons
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Hide the scrollbar
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = DropArea(scroll_area, self)
        self.scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        self.users = load_data()  # Load user data
        print('User count: ', len(self.users))
        # ---------- create account fields ---------- #

        for user in self.users:
            self.create_account(user, button_width, button_height, button_radius)

        create_account_widget = CreateAccount(self, button_width, button_height, button_radius, scroll_area)
        self.scroll_layout.addWidget(create_account_widget)

        # Add the scroll area to the main layout
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def create_account(self, user, button_width, button_height, button_radius):
        account_button = AccountManager(user, button_width, button_height, button_radius)
        # Attach a reference to the main app so account widgets can access users/save
        account_button.app = self
        account_button.clicked_account.connect(self.on_signal_received)
        self.scroll_layout.addWidget(account_button)
        return account_button

    def on_signal_received(self, username, password):
        self.username = username
        self.password = password
        print(f"Signal received with log in information")
        
        # going to Beta_Riot.py now to send username, password to there.
        self.riot_client.execute(username, password)

if __name__ == "__main__":

    if check_open('Logger') == True:
        sys.exit('*Forced exit*')

    else:

        # Load info
        users = load_data()                   # Load user data
        q_app = QApplication(sys.argv)        # Create QApplication instance
        riot_client = RiotClient()            # Create RiotClient instance
        main_app = MainApp(riot_client)       # Create MainApp instance

        # Actually do something now with info
        check_open('Client')                  # Open Riot client connection
        main_app.show()                       # Show the main app

        sys.exit(q_app.exec())  # event loop
