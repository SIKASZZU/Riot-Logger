import sys
import random
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap, QFont, QCursor
from PyQt6.QtCore import Qt
from PIL import Image, ImageDraw

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
    {"riot_id": "HarryPotter", "tagline": "EUNE", "username": "thechosenone", "password": "expelliarmus"},
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
    def __init__(self, image_path, width, height, radius, parent=None):
        super().__init__(parent)

        self.setFixedSize(width, height)

        # Load rounded image
        self.bg_pixmap = create_rounded_image(image_path, (width, height), radius)

        # Background Label (Image)
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(0, 0, width, height)

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

    @staticmethod
    def on_click():
        print("Create new")



class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Riot Logger")
        self.setGeometry(100, 100, 100, 100)

        # Set background color
        self.setStyleSheet("background-color: #242424; color: white;")

        layout = QVBoxLayout(self)

        width = 400
        height = 50
        radius = 10

        max_accounts_visible = 6

        create_account_count = max_accounts_visible - len(users)

        # Generate profile buttons for each user
        for user in users:
            w = random.randint(0, 1000)
            l = random.randint(0, 1000)
            layout.addWidget(AccountButton(user, "bronze.png", w, l, width, height, radius))

        if create_account_count > 0:
            for i in range(create_account_count):
                layout.addWidget(CreateAccount("create_new.png", width, height, radius))

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
