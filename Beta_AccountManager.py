import os
import requests
import webbrowser

from helper import *
from Beta_Api import get_data
from dotenv import load_dotenv

from PyQt6.QtGui import QPixmap, QFont, QCursor, QImage, QDrag
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton

class AccountManager(QWidget):
    def delete_account(self):
        app = None
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'app'):
                app = parent.app
                break
            parent = parent.parent() if hasattr(parent, 'parent') else None
        if app is None and hasattr(self, 'app'):
            app = self.app

        app.users = [u for u in app.users if not (u.get('riot_id') == self.riot_id and u.get('username') == self.username)]
        save_data(app.users)

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

    def show_delete_button(self):
        # Show two action buttons (Delete / Don't delete) centered under the account label.
        # Create buttons lazily.
        label_geom = self.account_label.geometry()
        btn_w = 110
        btn_h = 24
        spacing = 10
        total_w = btn_w * 2 + spacing
        start_x = label_geom.x() + max(0, (label_geom.width() - total_w))
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

    def open_opgg(self):
        try:
            url = f"{self.base_urls['opgg']}{self.account_name}-{self.tagline}" # quote(self.riot_id)
            print('review site url: ', url)
            webbrowser.open(url)
        except Exception as e:
            print(f"Failed to open op.gg: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            # Toggle delete button visibility on right-click
            if hasattr(self, 'delete_button') and self.delete_button and self.delete_button.isVisible():
                self.delete_button.hide()
            else:
                self.show_delete_button()
            return

        # Left/other clicks: prepare for possible drag; don't emit immediately
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()
            self._dragging = False
            self.hide_delete_button()

        return
    clicked_account = pyqtSignal(str, str)  # Define signal with username and password

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

    def mouseMoveEvent(self, event):
        # Start a drag if the left button was pressed and moved sufficiently
        if getattr(self, '_drag_start_pos', None) is None:
            return
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        dist = (event.pos() - self._drag_start_pos).manhattanLength()
        from PyQt6.QtWidgets import QApplication
        if dist < QApplication.startDragDistance():
            return

        # Begin drag
        self._dragging = True
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(f"{self.riot_id}|{self.username}")
        drag.setMimeData(mime)

        # Use a pixmap snapshot of the widget for the drag cursor
        try:
            pix = self.grab()
            drag.setPixmap(pix)
        except Exception:
            pass

        drag.exec()

    def mouseReleaseEvent(self, event):
        # If it wasn't a drag, treat as a click
        if getattr(self, '_dragging', False):
            self._dragging = False
            self._drag_start_pos = None
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_account.emit(self.username, self.password)
            self._drag_start_pos = None
            return

    def __init__(self, user_data, width, height, radius, image_path='images/default.png', parent=None):
        super().__init__(parent)

        self.setFixedSize(width, height)
        self.account_name_w_tagline = f"{user_data['riot_id']}#{user_data['tagline']}"
        self.account_name = f"{user_data['riot_id']}"
        self.username = user_data['username']
        self.password = user_data['password']
        self.riot_id = user_data['riot_id']
        self.tagline = user_data['tagline']
        self.region = user_data['region']

        self.hotStreak = None
        self.winrate = None
        self.rank = None
        self.iconID = None
        # regionStripped = self.region.rstrip("0123456789")
        regionQuery = {
            'BR1': 'BR',
            'EUN1': 'EUNE',
            'EUW1': 'EUW',
            'JP1': 'JP',
            'KR': 'KR',
            'LA1': 'LA',
            'LA2': 'LA',
            'ME1': 'BR',
            'NA1': 'NA',
            'OC1': 'OCE',
            'RU': 'BR',
            'SG2': 'BR',
            'TR1': 'BR',
            'TW2': 'BR',
            'VN2': 'BR'
        }

        self.base_urls = {
            "icon": 'http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/',
            "opgg": f'https://op.gg/lol/summoners/{regionQuery[self.region]}/'
        }

        load_dotenv('getenv.env')
        api_key = os.getenv('api_key')

        hotStreak_image_path = 'images/hotStreak.png'

        if not api_key:
            raise ValueError("API key not found. Check your .env file.")

        ranked_info = get_data(self.riot_id, self.tagline, self.region, api_key)
        if ranked_info == None or ranked_info['tier'] == None:
            ranked_info = 'Unranked'
            image_fade_path = RANKS_PATH_FADE[ranked_info]
            image_border_path = None

        else:

            self.winrate = f'{ranked_info['winrate']}%  {ranked_info['wins']}W {ranked_info['losses']}L'
            self.rank = f'{ranked_info['tier']} {ranked_info['rank']} {ranked_info['lp']}LP'
            self.iconID = ranked_info['iconID']
            self.hotStreak = ranked_info['hotStreak']
            tier = ranked_info['tier']
            tier = tier.capitalize()

            if tier in RANKS:
                image_fade_path = RANKS_PATH_FADE[tier]
                image_border_path = RANKS_PATH_BORDER[tier]
        print(f'{self.account_name} | {ranked_info}\n')

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

        # Rank (Centered)
        if (self.hotStreak):
            self.hotStreak_pixmap = create_hot_streak(hotStreak_image_path)
            self.hotStreak_label = QLabel(self)
            self.hotStreak_label.setPixmap(self.hotStreak_pixmap)
            self.hotStreak_label.setGeometry(0, round(button_height // 2.5), self.hotStreak_pixmap.width(), self.hotStreak_pixmap.height())
            self.hotStreak_label.setStyleSheet('background: transparent;')
            self.hotStreak_label.setToolTip('Hotstreak')
            self.hotStreak_label.raise_()

        self.opgg_btn = QPushButton("op.gg", self)
        self.opgg_btn.setGeometry(button_width - 64, 6, 48, 20)
        self.opgg_btn.setStyleSheet("background: rgba(0,0,0,0); color: #cfcfcf; border: none; font-size:10px;")
        self.opgg_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.opgg_btn.clicked.connect(self.open_opgg)

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
        # Let the parent widget receive mouse events so dragging works;
        # we handle clicks in mouseReleaseEvent instead.
        self.button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        # Ensure op.gg button is above the invisible overlay and doesn't steal focus
        if hasattr(self, 'opgg_btn'):
            self.opgg_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.opgg_btn.raise_()