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
    {"riot_id": "Gandalf", "tagline": "WEST", "username": "youShallNotPass", "password": "mellon"},
    {"riot_id": "Yoda", "tagline": "NA", "username": "forceMaster", "password": "doOrDoNot"},
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


class RoundedButton(QWidget):
    def __init__(self, user_data, image_path, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 60)

        w = random.randint(0, 1000)
        l = random.randint(0, 1000)
        winrate = 0 if (w + l) == 0 else round((w / (w + l)) * 100)

        self.rank = random.choice(RANKS)
        self.account_name = f"{user_data['riot_id']} # {user_data['tagline']}"
        self.username = user_data['username']
        self.password = user_data['password']


        # Load rounded image
        self.bg_pixmap = create_rounded_image(image_path, (400, 60), 20)

        # Background Label (Image)
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(0, 0, 400, 60)

        # Account Name
        self.account_label = QLabel(self.account_name, self)
        self.account_label.setFont(QFont("Arial", 14))
        self.account_label.setStyleSheet("color: white; background: transparent;")
        self.account_label.setGeometry(10, 15, 250, 30)

        # Winrate (Centered)
        self.winrate_label = QLabel(f"{w}W/{l}L {winrate:.1f}%", self)
        self.winrate_label.setFont(QFont("Arial", 10))
        self.winrate_label.setStyleSheet("color: gray; background: transparent;")
        self.winrate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winrate_label.setGeometry(260, 5, 140, 20)

        # Rank (Centered)
        self.rank_label = QLabel(self.rank, self)
        self.rank_label.setFont(QFont("Arial", 10))
        self.rank_label.setStyleSheet("color: gray; background: transparent;")
        self.rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rank_label.setGeometry(260, 30, 140, 20)

        # Invisible Clickable Button
        self.button = QPushButton("", self)
        self.button.setGeometry(0, 0, 400, 60)
        self.button.setStyleSheet("background: transparent; border: none;")
        self.button.clicked.connect(self.on_click)

        # Click effect
        self.button.setStyleSheet(
            """
            QPushButton {
                background: transparent; border: none;
                border-radius: 20px;

            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 30); /* Light click effect */
            }
            """
        )

        self.button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # Set cursor to hand
        self.button.clicked.connect(self.on_click)

    def on_click(self):
        print(f"Username: {self.username}, Password: {self.password}")


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 User Profiles")
        self.setGeometry(100, 100, 450, 500)

        # Set background color
        self.setStyleSheet("background-color: #242424; color: white;")

        layout = QVBoxLayout(self)

        # Generate profile buttons for each user
        for user in users:
            layout.addWidget(RoundedButton(user, "bronze.png"))

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
