import sys
import random
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap, QFont, QCursor
from PyQt6.QtCore import Qt
from PIL import Image, ImageDraw

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QCursor, QFont
from PyQt6.QtCore import Qt, QPropertyAnimation, QSize

# Available ranks
RANKS = [
    "Iron I",
    "Iron II",
    "Iron III",
    "Iron VI",

    "Bronze I",
    "Bronze II",
    "Bronze III",
    "Bronze VI",

    "Silver I",
    "Silver II",
    "Silver III",
    "Silver VI",

    "Gold I",
    "Gold II",
    "Gold III",
    "Gold VI",

    "Platinum I",
    "Platinum II",
    "Platinum III",
    "Platinum VI",

    "Diamond I",
    "Diamond II",
    "Diamond III",
    "Diamond VI",

    "Master",

    "Challenger"]

# User data dictionary
users = [
    {"riot_id": "SikzuOnRäigeAutist", "tagline": "Asia", "username": "darkwizard", "password": "avadaKedavra"},
]


def create_rounded_image(image_path, size, radius):
    """Creates a rounded image with PIL and converts it to QPixmap."""
    img = Image.open(image_path).convert("RGBA")
    img = img.resize(size, Image.LANCZOS)

    # Create rounded mask
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius, fill=255)

    # Apply rounded mask to image
    img.putalpha(mask)

    # Convert to QPixmap
    img.save("temp_rounded.png")  # Temporary save for conversion
    return QPixmap("temp_rounded.png")


class AccountButton(QWidget):
    def __init__(self, user_data, image_path, w, l, width, height, radius, parent=None):
        super().__init__(parent)

        self.setFixedSize(width, height)
        winrate = 0 if (w + l) == 0 else round((w / (w + l)) * 100)

        self.rank = random.choice(RANKS)
        self.account_name = f"{user_data['riot_id']} # {user_data['tagline']}"
        self.username = user_data['username']
        self.password = user_data['password']

        # Load rounded image
        self.bg_pixmap = create_rounded_image(image_path, (width, height), radius)

        # Background Label (Image)
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(0, 0, width, height)

        # Account Name
        self.account_label = QLabel(self.account_name, self)
        self.account_label.setFont(QFont("Arial", 14))
        self.account_label.setStyleSheet("color: gray; background: transparent;")
        self.account_label.setGeometry(10, 15, 250, 20)

        # Winrate (Centered)
        self.winrate_label = QLabel(f"{w}W/{l}L {winrate:.1f}%", self)
        self.winrate_label.setFont(QFont("Arial", 10))
        self.winrate_label.setStyleSheet("color: gray; background: transparent;")
        self.winrate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winrate_label.setGeometry(260, 7, 140, 20)

        # Rank (Centered)
        self.rank_label = QLabel(self.rank, self)
        self.rank_label.setFont(QFont("Arial", 10))
        self.rank_label.setStyleSheet("color: gray; background: transparent;")
        self.rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rank_label.setGeometry(260, 22, 140, 20)

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
        print(f"Username: {self.username}, Password: {self.password}")


class CreateAccount(QWidget):
    def __init__(self, width, height, radius, parent=None):
        super().__init__(parent)

        self.default_height = height  # Store default height
        self.expanded_height = height + 120  # Adjust height for entries
        self.radius = radius
        self.minimized_image_path = "create_new.png"
        self.expanded_image_path = "expanded_create_new.png"

        self.setFixedSize(width, self.default_height)


        # Load rounded image
        self.bg_pixmap = create_rounded_image(self.minimized_image_path, (width, height), radius)

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
        self.button.clicked.connect(self.expand_form)

        # Load rounded image
        self.expanded_bg_pixmap = create_rounded_image(self.expanded_image_path, (width, self.expanded_height), 0)

        # Background Label (Image)
        self.expanded_bg_label = QLabel(self)
        self.expanded_bg_label.setPixmap(QPixmap(self.expanded_bg_pixmap))
        self.expanded_bg_label.setScaledContents(True)
        self.expanded_bg_label.setGeometry(0, 0, width, self.expanded_height)
        self.expanded_bg_label.hide()
        self.expanded_bg_label.setStyleSheet("background: transparent;")

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

        # Confirm & Cancel Buttons (Hidden Initially)
        self.confirm_button = QPushButton("Confirm", self)
        self.confirm_button.setGeometry(50, 130, 100, 30)
        self.confirm_button.clicked.connect(self.confirm)
        self.confirm_button.hide()

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setGeometry(180, 130, 100, 30)
        self.cancel_button.clicked.connect(self.reset_form)
        self.cancel_button.hide()

    def expand_form(self):
        """ Expands the frame and shows the input fields """
        self.setFixedSize(self.width(), self.expanded_height)
        self.bg_label.hide()  # Hide the image
        self.button.hide()  # Hide the button

        # Show input fields and buttons
        self.expanded_bg_label.show()
        self.riot_id_entry.show()
        self.tagline_entry.show()
        self.username_entry.show()
        self.password_entry.show()
        self.confirm_button.show()
        self.cancel_button.show()

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

        # Update the layout and adjust the parent window size
        self.parent().layout().update()  # Force the layout to refresh
        self.parent().adjustSize()  # Adjust the parent window size to fit the new layout

    def confirm(self):
        """ Confirms and adds the new account button """
        riot_id = self.riot_id_entry.text()
        tagline = self.tagline_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()

        if not riot_id or not username or not password:
            print("Please fill all fields!")
            return

        # Create a new AccountButton with the provided data
        new_account = AccountButton(
            {"riot_id": riot_id, "tagline": tagline, "username": username, "password": password},
            "bronze.png",  # Use a default image for now
            w=random.randint(0, 1000),  # Random wins count for now
            l=random.randint(0, 1000),  # Random losses count for now
            width=400,  # Use a fixed width
            height=50,  # Use a fixed height
            radius=15  # Use a fixed radius
        )

        # Get the layout of the parent widget
        parent_layout = self.parent().layout()

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

        # Reset the form back to the initial state after confirming
        self.reset_form()


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Riot Logger")
        self.setGeometry(100, 100, 100, 100)  # x, y, w, h

        # Set background color
        self.setStyleSheet("background-color: #242424; color: white;")

        layout = QVBoxLayout(self)

        # Button sizes
        width = 400
        height = 50
        radius = 15

        # Calculate create account buttons count
        max_accounts_visible = 6
        create_account_count = max_accounts_visible - len(users)

        # Generate profile buttons for each user
        for user in users:
            w = random.randint(0, 1000)
            l = random.randint(0, 1000)
            layout.addWidget(AccountButton(user, "bronze.png", w, l, width, height, radius))

        # Generate account buttons
        layout.addWidget(CreateAccount(width, height, radius))

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
