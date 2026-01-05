import sys
import os
import requests
from PyQt6.QtGui import QImage, QPixmap

from helper import RANKS, RANKS_PATH_FADE, RANKS_PATH_BORDER, REGIONS, create_fade_image, create_circular_icon, create_border_image, get_resource_path, save_data, load_data
from helper import button_height, button_radius, button_width
from Beta_Api import get_data
from Beta_Riot import RiotClient
from Beta_Open import check_open

from dotenv import load_dotenv

from PyQt6.QtGui import QPixmap, QFont, QCursor, QIcon
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, \
    QVBoxLayout, QPushButton, QLineEdit, QScrollArea, QComboBox, QStyledItemDelegate

class AccountButton(QWidget):
    def show_delete_button(self):
        # Show two action buttons (Delete / Don't delete) centered under the account label.
        # Create buttons lazily.
        label_geom = self.account_label.geometry()
        btn_w = 110
        btn_h = 24
        spacing = 10
        total_w = btn_w * 2 + spacing
        start_x = label_geom.x() + max(0, (label_geom.width() - total_w) // 2)
        by = label_geom.y() + label_geom.height() // 2 - btn_h // 2

        if not hasattr(self, 'delete_confirm_btn'):
            self.delete_confirm_btn = QPushButton("Delete account", self)
            self.delete_confirm_btn.setStyleSheet('background: #c0392b; color: white; border-radius: 6px;')
            self.delete_confirm_btn.clicked.connect(self.delete_account)

        if not hasattr(self, 'delete_cancel_btn'):
            self.delete_cancel_btn = QPushButton("Don't delete", self)
            self.delete_cancel_btn.setStyleSheet('background: rgba(255,255,255,20); color: white; border-radius: 6px;')
            self.delete_cancel_btn.clicked.connect(self.hide_delete_button)

        self.delete_confirm_btn.setGeometry(start_x, by, btn_w, btn_h)
        self.delete_cancel_btn.setGeometry(start_x + btn_w + spacing, by, btn_w, btn_h)
        self.delete_confirm_btn.show()
        self.delete_cancel_btn.show()

    def delete_account(self):
        # Remove this account from data and UI
        # Find the app instance (walk up parents if needed)
        app = None
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'app'):
                app = parent.app
                break
            parent = parent.parent() if hasattr(parent, 'parent') else None
        if app is None and hasattr(self, 'app'):
            app = self.app
        # Remove from users and save
        if app and hasattr(app, 'users'):
            app.users = [u for u in app.users if not (u['riot_id'] == self.riot_id and u['username'] == self.username)]
            save_data(app.users)
            print('Current users:', app.users)
        # Remove widget from layout
        self.setParent(None)
        self.deleteLater()

    def hide_delete_button(self):
        if hasattr(self, 'delete_button') and self.delete_button:
            try:
                self.delete_button.hide()
            except Exception:
                pass
        if hasattr(self, 'delete_confirm_btn') and self.delete_confirm_btn:
            self.delete_confirm_btn.hide()
        if hasattr(self, 'delete_cancel_btn') and self.delete_cancel_btn:
            self.delete_cancel_btn.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            # Toggle delete button visibility on right-click
            if hasattr(self, 'delete_button') and self.delete_button and self.delete_button.isVisible():
                self.delete_button.hide()
            else:
                self.show_delete_button()
            return
        # Left / other clicks: hide delete button and emit signal
        self.hide_delete_button()
        self.clicked_account.emit(self.username, self.password)  # Emit signal with data
    clicked_account = pyqtSignal(str, str)  # Define signal with username and password

    def __init__(self, user_data, width, height, radius, image_path='images/default.png', parent=None):
        super().__init__(parent)

        self.setFixedSize(width, height)

        self.account_name_w_tagline = f"{user_data['riot_id']} # {user_data['tagline']}"
        self.account_name = f"{user_data['riot_id']}"
        self.username = user_data['username']
        self.password = user_data['password']
        self.riot_id = user_data['riot_id']
        self.tagline = user_data['tagline']
        self.region = user_data['region']

        self.winrate = None
        self.rank = None
        self.iconID = None
        self.base_urls = {
            "icon": 'http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/'
        }

        self.border_label = None

        load_dotenv('getenv.env')
        api_key = os.getenv('api_key')

        if not api_key:
            raise ValueError("API key not found. Check your .env file.")

        ranked_info = get_data(self.riot_id, self.tagline, self.region, api_key)
        if ranked_info == (None, None, None) or ranked_info == (None, None) or ranked_info == None:
            ranked_info = 'Unranked'
            image_fade_path = RANKS_PATH_FADE[ranked_info]
            image_border_path = None
            print(f'{self.account_name} | {ranked_info}')

        else:
            print(f'{self.account_name} | {ranked_info}')
            print(ranked_info)
            (rank, self.rank), self.winrate, _ = ranked_info
            self.iconID = ranked_info[-1]
            rank = rank.capitalize()

            if rank in RANKS:
                image_fade_path = RANKS_PATH_FADE[rank]
                image_border_path = RANKS_PATH_BORDER[rank]

        # Load rounded image
        self.fade_pixmap = create_fade_image(image_fade_path, (width, height), radius)
        self.border_pixmap = create_border_image(image_border_path)

        # --------- IMAGES --------- #

        # Background Label. Always present
        self.fade_label = QLabel(self)
        self.fade_label.setPixmap(self.fade_pixmap)
        self.fade_label.setScaledContents(True)
        self.fade_label.setGeometry(0, 0, width, height)

        # Border // if unranked crashes

        if (self.border_pixmap != None):
            border_width = self.border_pixmap.width()
            border_height = self.border_pixmap.height()
            self.border_label = QLabel(self)
            self.border_label.setPixmap(self.border_pixmap)
            self.border_label.setScaledContents(True)
            self.border_label.setStyleSheet("background: transparent; border: none;")
            self.border_label.setGeometry(0, -button_height//2, border_width, border_height)

            # --------- ICON LABEL --------- #
            self.icon_label = QLabel(self)
            self.icon_label.setGeometry(border_width // 3, button_height // 3, 50, 50)
            self.icon_label.setStyleSheet('background: transparent;')
            self.icon_label.hide()

            # If iconID is available, load and show the image as a circular icon
            if self.iconID:
                try:
                    url = f"{self.base_urls['icon']}{self.iconID}.jpg"
                    response = requests.get(url)
                    if response.status_code == 200:
                        pixmap = create_circular_icon(response.content)
                        self.icon_label.setPixmap(pixmap)
                        self.icon_label.show()
                except Exception as e:
                    print(f"Failed to load iconID image: {e}")

        # square icon image, if border // rank missing
        elif self.iconID:
            try:
                url = f"{self.base_urls['icon']}{self.iconID}.jpg"
                response = requests.get(url)
                if response.status_code == 200:
                    image = QImage.fromData(response.content)
                    pixmap = QPixmap.fromImage(image)
                    self.icon_label.setPixmap(pixmap)
                    self.icon_label.show()
            except Exception as e:
                print(f"Failed to load iconID image: {e}")

        # --------- TEXT --------- #

        # Account Name
        self.account_label = QLabel(self.account_name, self)
        self.account_label.setFont(QFont("Arial", 16))
        self.account_label.setStyleSheet("color: gray; background: transparent;")
        al_start_x = button_width // 3
        al_start_y = 0 # button_height // 3
        self.account_label.setGeometry(
            al_start_x,
            al_start_y,
            button_width - al_start_x,
            button_height - al_start_y
        )

        # Winrate (Centered)
        self.winrate_label = QLabel(self.winrate, self)
        self.winrate_label.setFont(QFont("Arial", 9))
        self.winrate_label.setStyleSheet("color: gray; background: transparent;")
        self.winrate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        winrate_start_x = button_width - button_width // 3
        winrate_start_y = button_height // 2
        self.winrate_label.setGeometry(
            winrate_start_x,
            winrate_start_y,
            button_width - winrate_start_x,
            winrate_start_y
        )

        # Rank (Centered)
        self.rank_label = QLabel(self.rank, self)
        self.rank_label.setFont(QFont("Arial", 9))
        self.rank_label.setStyleSheet("color: gray; background: transparent;")
        self.rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_start_x = button_width - button_width // 3
        rank_start_y = button_height // 3
        self.rank_label.setGeometry(
            al_start_x,
            winrate_start_y,
            button_width - rank_start_x,
            winrate_start_y
        )

        # Invisible Clickable Button
        self.button = QPushButton("", self)
        self.button.setGeometry(0, 0, width, height)
        self.button.setStyleSheet("background: transparent; border: none;")

        self.button.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                border-radius: {radius}px;
                border: none;
            }}
            QPushButton:hover {{
                background: rgba(150, 150, 150, 20);
            }}
            QPushButton:pressed {{
                background: rgba(150, 150, 150, 30);
            }}
            """
        )

        self.button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # Set cursor to hand
        self.button.clicked.connect(self.on_click)

        if (self.border_label):
            self.border_label.raise_()

    def enterEvent(self, event):
        """ Change account label color to white on hover """
        self.account_label.setStyleSheet("color: #A5A2A3; background: transparent;")
        self.winrate_label.setStyleSheet("color: #A5A2A3; background: transparent;")
        self.rank_label.setStyleSheet("color: #A5A2A3; background: transparent;")

    def leaveEvent(self, event):
        """ Change account label color back to gray when not hovered """
        self.account_label.setStyleSheet("color: gray; background: transparent;")
        self.winrate_label.setStyleSheet("color: gray; background: transparent;")
        self.rank_label.setStyleSheet("color: gray; background: transparent;")

    def on_click(self):
        self.clicked_account.emit(self.username, self.password)  # Emit signal with data


class CenterDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter
        super().paint(painter, option, index)


class CreateAccount(QWidget):
    def __init__(self, app, width, height, radius, parent=None):
        super().__init__(parent)
        self.app = app
        self.arg_width  = width
        self.arg_height = height
        self.radius = radius
        
        self.scroll_area = parent  # ScrollArea is passed as the parent

        self.default_height = height  # Store default height
        self.expanded_height = height + 120  # Adjust height for entries
        self.minimized_image_path = "images/fade/create_new.png"
        self.expanded_image_path = "images/fade/expanded_create_new.png"

        self.setFixedSize(width, self.default_height)

        # Load rounded image
        self.bg_pixmap = create_fade_image(self.minimized_image_path, (width, height), 0)

        # Background Label (Image)
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap(self.bg_pixmap))
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(0, 0, width, self.default_height)

        # Invisible Clickable Button
        self.button = QPushButton("", self)
        self.button.setGeometry(0, 0, width, self.default_height)
        self.button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                border-radius: {self.radius}px;
                border: none;
            }}
            QPushButton:hover {{
                background: rgba(150, 150, 150, 20);
            }}
            QPushButton:pressed {{
                background: rgba(150, 150, 150, 30);
            }}
            """
        )
        self.button.clicked.connect(self.expand_form)

        # Load fade image
        self.expanded_bg_pixmap = create_fade_image(self.expanded_image_path, (width, self.expanded_height), 0)

        # Background Label (Image)
        self.expanded_bg_label = QLabel(self)
        self.expanded_bg_label.setPixmap(QPixmap(self.expanded_bg_pixmap))
        self.expanded_bg_label.setScaledContents(True)
        self.expanded_bg_label.setGeometry(0, 0, width, self.expanded_height)
        self.expanded_bg_label.setStyleSheet("background: transparent;")
        self.expanded_bg_label.hide()

        # Input Fields (Hidden Initially)
        self.riot_id_entry = QLineEdit(self)
        self.riot_id_entry.setPlaceholderText("Riot ID")
        self.riot_id_entry.setGeometry(55, 10, 210, 30)
        self.riot_id_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.riot_id_entry.hide()

        self.tagline_entry = QLineEdit(self)
        self.tagline_entry.setPlaceholderText("Tagline")
        self.tagline_entry.setGeometry(285, 10, 70, 30)
        self.tagline_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tagline_entry.hide()

        self.username_entry = QLineEdit(self)
        self.username_entry.setPlaceholderText("Username")
        self.username_entry.setGeometry(80, 50, 240, 30)
        self.username_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.username_entry.hide()

        self.password_entry = QLineEdit(self)
        self.password_entry.setPlaceholderText("Password")
        self.password_entry.setGeometry(80, 90, 240, 30)
        self.password_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_entry.hide()

        # Region Selector Dropdown
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(REGIONS)
        self.combo_box.setItemDelegate(CenterDelegate(self.combo_box))
        self.combo_box.setGeometry(80, 130, 80, 30)
        self.combo_box.setEditable(True)
        self.combo_box.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.combo_box.lineEdit().setReadOnly(True)  # Prevent manual text input
        self.combo_box.hide()

        # Confirm & Cancel Buttons (Hidden Initially)
        self.confirm_button = QPushButton("Confirm", self)
        self.confirm_button.setGeometry(170, 130, 80, 30)
        self.confirm_button.clicked.connect(self.confirm)
        self.confirm_button.hide()

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setGeometry(240, 130, 80, 30)
        self.cancel_button.clicked.connect(self.reset_form)
        self.cancel_button.hide()


    def expand_form(self):
        """Expands the frame and shows the input fields"""
        self.setFixedSize(self.width(), self.expanded_height)
        self.bg_label.hide()  # Hide the image
        self.button.hide()  # Hide the button

        # Show input fields and buttons
        self.expanded_bg_label.show()

        # Brings entries to window
        self.riot_id_entry.show()
        self.tagline_entry.show()
        self.username_entry.show()
        self.password_entry.show()

        # Clears the entries
        self.riot_id_entry.clear()
        self.tagline_entry.clear()
        self.username_entry.clear()
        self.password_entry.clear()

        # Brings buttons to window
        self.confirm_button.show()
        self.cancel_button.show()

        self.combo_box.show()

        # Force layout update and then scroll to the bottom
        self.updateGeometry()  # This ensures the layout is refreshed
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

        # Alternatively, you can use ensureWidgetVisible (if specific widget visibility is required)
        self.scroll_area.ensureWidgetVisible(self)


    def reset_form(self):
        """ Resets the form back to the initial state with the image """
        self.setFixedSize(self.width(), self.default_height)
        self.bg_label.show()
        self.button.show()

        # Hide input fields and buttons
        self.riot_id_entry.hide()
        self.tagline_entry.hide()
        self.username_entry.hide()
        self.password_entry.hide()
        self.confirm_button.hide()
        self.cancel_button.hide()
        self.expanded_bg_label.hide()

        self.combo_box.hide()

        # Update the layout and adjust the parent window size
        self.parent().layout().update()  # Force the layout to refresh
        self.parent().adjustSize()  # Adjust the parent window size to fit the new layout

    def confirm(self):
        """ Confirms and adds the new account button """
        riot_id = self.riot_id_entry.text()
        tagline = self.tagline_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()
        region = self.combo_box.currentText()
        user = {"riot_id": riot_id, "tagline": tagline, "region": region, "username": username, "password": password}
        
        if not riot_id or not username or not password or region == "Region":
            print("Please fill all fields!")
            return

        # Create a new AccountButton with the provided data
        new_account = self.app.create_account(user, self.arg_width, self.arg_height, self.radius)
        
        self.app.users.append(user)

        save_data(self.app.users)  # save accounts to json
        
        # Get the layout of the parent widget
        parent_layout = self.parent().layout()

        # Find the last "Add Account" button
        add_account_button_index = None

        # Find the last widget (the "Add Account" button) and get its index
        add_account_button_index = -1
        for i in range(parent_layout.count()):
            widget = parent_layout.itemAt(i).widget()
            if widget and isinstance(widget, CreateAccount):
                add_account_button_index = i
                break

        if add_account_button_index != -1:
            # Insert the new account button before the "Add Account" button
            parent_layout.insertWidget(add_account_button_index, new_account)

        # Delete Add account button if we have less than 6 users in the list
        if len(self.app.users) < 6:
            parent_layout.itemAt(add_account_button_index + 1).widget().deleteLater()

        # Reset the form back to the initial state after confirming
        self.reset_form()


class MainApp(QWidget):
    clicked_account = AccountButton.clicked_account

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

        scroll_content = QWidget(scroll_area)
        self.scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        self.users = load_data()  # Load user data
        
        # Add account buttons to scrollable area
        max_accounts_visible = 6
        create_account_count = max_accounts_visible - len(self.users)
        
        for user in self.users:
            self.create_account(user, button_width, button_height, button_radius)
            
        # Add Create Account button
        for i in range(create_account_count):
           create_account_widget = CreateAccount(self, button_width, button_height, button_radius, scroll_area)
           self.scroll_layout.addWidget(create_account_widget)

        if create_account_count <= 0:  # ehk visible acce on 6 voi rohkem ning peab lisama eraldi new acc buttoni 
            create_account_widget = CreateAccount(self, button_width, button_height, button_radius, scroll_area)
            self.scroll_layout.addWidget(create_account_widget)

        # Add the scroll area to the main layout
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def create_account(self, user, button_width, button_height, button_radius):
        account_button = AccountButton(user, button_width, button_height, button_radius)
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
