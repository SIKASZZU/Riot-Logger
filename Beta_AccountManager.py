import os
import requests
import webbrowser

from Beta_Api import get_data
from helper import *

from PyQt6.QtGui import QPixmap, QFont, QCursor, QImage, QDrag
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QApplication

class AccountManager(QWidget):
    """Widget representing a single account entry."""

    clicked_account = pyqtSignal(str, str)

    def delete_account(self):
        if hasattr(self, 'app') and getattr(self.app, 'users', None) is not None:
            self.app.users = [u for u in self.app.users if not (u.get('riot_id') == self.riot_id and u.get('username') == self.username)]
            save_data(self.app.users)
        else:
            print('Warning: could not find app.users to update')

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
        # hide darker overlay when hiding delete buttons
        if hasattr(self, '_delete_overlay') and self._delete_overlay:
            try:
                self._delete_overlay.hide()
            except Exception:
                pass

    def show_delete_button(self):
        label_geom = self.account_label.geometry()
        btn_w, btn_h = 110, 24
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
        # create or show a semi-transparent overlay behind the delete buttons
        if not hasattr(self, '_delete_overlay') or self._delete_overlay is None:
            from PyQt6.QtWidgets import QLabel
            self._delete_overlay = QLabel(self)
            # darker overlay; alpha ~80
            self._delete_overlay.setStyleSheet(f'background: rgba(0,0,0,80); border-radius: {getattr(self, "radius", 0)}px;')
            self._delete_overlay.setGeometry(0, 0, self.width(), self.height())
        else:
            self._delete_overlay.setGeometry(0, 0, self.width(), self.height())

        self._delete_overlay.show()
        self.delete_confirm_btn.show()
        self.delete_cancel_btn.show()

        self._delete_overlay.raise_()
        self.delete_confirm_btn.raise_()
        self.delete_cancel_btn.raise_()

    def open_opgg(self):
        try:
            url = f"{self.base_urls['opgg']}{self.account_name}-{self.tagline}" # quote(self.riot_id)
            print('review site url: ', url)
            webbrowser.open(url)
        except Exception as e:
            print(f"Failed to open op.gg: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            if hasattr(self, 'delete_button') and self.delete_button and self.delete_button.isVisible():
                self.delete_button.hide()
            else:
                self.show_delete_button()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()
            self._dragging = False
            self.hide_delete_button()

        return

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
        self.clicked_account.emit(self.username, self.password)

    def mouseMoveEvent(self, event):
        # Start a drag if the left button was pressed and moved sufficiently
        if getattr(self, '_drag_start_pos', None) is None:
            return
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        dist = (event.pos() - self._drag_start_pos).manhattanLength()
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

        # Capture `app` reference from parent (MainApp) when available
        self.app = parent if (parent and hasattr(parent, 'users')) else None

        self.setFixedSize(width, height)
        self.radius = radius
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

        hotStreak_image_path = 'images/hotStreak.png'

        # Get API key from parent app; MainApp should load it once.
        api_key = None
        if self.app and getattr(self.app, 'api_key', None):
            api_key = self.app.api_key
        if not api_key:
            raise ValueError('API key not found. MainApp must set `self.api_key`.')

        ranked_info = get_data(self.riot_id, self.tagline, self.region, api_key)
        if ranked_info is None or ranked_info.get('tier') is None:
            ranked_info = 'Unranked'
            image_fade_path = RANKS_PATH_FADE[ranked_info]
            image_border_path = None
        else:
            self.winrate = f"{ranked_info['winrate']}%  {ranked_info['wins']}W {ranked_info['losses']}L"
            self.rank = f"{ranked_info['tier']} {ranked_info['rank']} {ranked_info['lp']}LP"
            self.iconID = ranked_info.get('iconID')
            self.hotStreak = ranked_info.get('hotStreak')
            tier = ranked_info['tier'].capitalize()

            if tier in RANKS:
                image_fade_path = RANKS_PATH_FADE[tier]
                image_border_path = RANKS_PATH_BORDER[tier]
        print(f'{self.account_name} | {ranked_info}\n')

        # Load rounded image
        self.fade_pixmap = create_fade_image(image_fade_path, (width, height), radius)
        self.border_pixmap = create_border_image(image_border_path)

        # --------- IMAGES --------- #

        # Background label
        self.fade_label = QLabel(self)
        self.fade_label.setPixmap(self.fade_pixmap)
        self.fade_label.setScaledContents(True)
        self.fade_label.setGeometry(0, 0, width, height)

        if self.border_pixmap is not None:
            border_width = self.border_pixmap.width()
            border_height = self.border_pixmap.height()
            self.border_label = QLabel(self)
            self.border_label.setPixmap(self.border_pixmap)
            self.border_label.setScaledContents(True)
            self.border_label.setStyleSheet("background: transparent; border: none;")
            self.border_label.setGeometry(0, -button_height//2, border_width, border_height)

            # Icon label
            self.icon_label = QLabel(self)
            self.icon_label.setGeometry(border_width // 3, button_height // 3, 50, 50)
            self.icon_label.setStyleSheet('background: transparent;')
            self.icon_label.hide()

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

        # Text labels

        # Account name
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

        # Winrate
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

        # Rank
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

        # Hotstreak
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

        # Invisible overlay button (transparent to mouse events so widget receives them)
        self.button = QPushButton('', self)
        self.button.setGeometry(0, 0, width, height)
        self.button.setStyleSheet(f'background: transparent; border-radius: {radius}px; border: none;')
        self.button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        # Ensure op.gg button is above the invisible overlay and doesn't steal focus
        if hasattr(self, 'opgg_btn'):
            self.opgg_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.opgg_btn.raise_()