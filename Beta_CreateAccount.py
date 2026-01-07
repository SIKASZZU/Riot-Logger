from helper import *

from PyQt6.QtGui import QCursor, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QComboBox, QStyledItemDelegate


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

    def check_data_dupes(self, new_user: dict):
        """Return True if a user with same riot_id+tagline+region already exists.

        Comparison is case-insensitive and ignores surrounding whitespace.
        """
        if not getattr(self, 'app', None) or not getattr(self.app, 'users', None):
            return False

        def norm(s):
            return (s or "").strip().lower()

        target_id = norm(new_user.get('riot_id'))
        target_tag = norm(new_user.get('tagline'))
        target_region = norm(new_user.get('region'))

        for u in self.app.users:
            if norm(u.get('riot_id')) == target_id and norm(u.get('tagline')) == target_tag and norm(u.get('region')) == target_region:
                return True
        return False

    def confirm(self):
        """ Confirms and adds the new account button """
        riot_id = self.riot_id_entry.text()
        tagline = self.tagline_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()
        region = self.combo_box.currentText()
        new_user = {
            "riot_id": riot_id,
            "tagline": tagline,
            "region": region,
            "username": username,
            "password": password,
            # Argon2 hash stored for security; plaintext kept in-memory for runtime
            "password_hash": hash_password(password),
            "lastKnownRankedInfo": {}
            }

        # Prevent duplicates (same Riot ID + Tagline + Region)
        if self.check_data_dupes(new_user):
            print("Duplicate account already exists!")
            return

        if not riot_id or not username or not password or region == "Region":
            print("Please fill all fields!")
            return

        # Create a new AccountManager with the provided data
        new_account = self.app.create_account(new_user, self.arg_width, self.arg_height, self.radius)

        self.app.users.append(new_user)
        save_data(self.app.users)

        parent_layout = self.parent().layout() if self.parent() is not None else self.app.scroll_layout

        create_idx = None
        for i in range(parent_layout.count() - 1, -1, -1):
            w = parent_layout.itemAt(i).widget()
            if isinstance(w, CreateAccount):
                create_idx = i
                break

        if create_idx is not None:
            # Insert the new account at the CreateAccount position, then remove the old CreateAccount
            parent_layout.insertWidget(create_idx, new_account)
            old = parent_layout.itemAt(create_idx + 1).widget()
            if isinstance(old, CreateAccount):
                old.deleteLater()
        else:
            # No existing Add button found — just append the new account
            parent_layout.addWidget(new_account)

        # Ensure exactly one Add button at the bottom
        create_account_widget = CreateAccount(self.app, button_width, button_height, button_radius, self.app.scroll_area)
        self.app.scroll_layout.addWidget(create_account_widget)

        self.reset_form()

