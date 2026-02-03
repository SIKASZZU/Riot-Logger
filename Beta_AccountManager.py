import keyring
import requests
import webbrowser
import time

from Beta_Api import RiotAPI, get_data
from helper import *
from PyQt6.QtWidgets import QInputDialog, QMessageBox
from PyQt6.QtGui import QFont, QCursor, QDrag, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtWidgets import QMenu, QWidget, QLabel, QPushButton, QApplication

class AccountManager(QWidget):
    """Widget representing a single account entry."""

    clicked_account = pyqtSignal(str, str)

    def __init__(self, user_data, width, height, radius, image_path='images/default.png', parent=None):
        super().__init__(parent)

        print(f"Loaded user: {user_data.get('riot_id')}")

        # 1. Initialize Labels to None
        self.fade_label = None
        self.border_label = None
        self.account_label = None
        self.rank_label = None
        self.winrate_label = None
        self.hotStreak_label = None
        self.icon_label = None

        # 2. Base Attributes
        self.app = parent if (parent and hasattr(parent, 'users')) else None
        self.setFixedSize(width, height)
        self.radius = radius

        self.account_name_w_tagline = f"{user_data.get('riot_id')}#{user_data.get('tagline')}"
        self.account_name = f"{user_data.get('riot_id')}"
        self.puuid = user_data.get('puuid') if user_data.get('puuid') != None else None
        self.username = user_data.get('username')
        self.password = user_data.get('password')
        self.riot_id = user_data.get('riot_id')
        self.tagline = user_data.get('tagline')
        self.region = user_data.get('region')
        self.lastQuery = user_data.get('lastQuery') if user_data.get('lastQuery') != None else int(time.time())
        self.lastKnownRankedInfo = user_data.get('lastKnownRankedInfo') if user_data.get('lastKnownRankedInfo') != None else {}
        self.iconID = user_data.get('iconID') if user_data.get('iconID') != None else None

        self.hotStreak = None
        self.winrate = None
        self.rank = 'Unranked'

        api_key = self.app.api_key if self.app and getattr(self.app, 'api_key', None) else None
        if not api_key:
            raise ValueError('API key not found. MainApp must set `self.api_key`.')
        self.riot_api = RiotAPI(api_key, self.region)

        # 3. Execution
        self._refresh_account_data()
        self.init_ui(width, height, radius)

    def _assign_user_info(self, info: dict):
        self.winrate = f"{info.get('winrate')}%\n{info.get('wins')}W {info.get('losses')}L"
        if info.get('ladderRank'):
            self.winrate += f"\nRank {info.get('ladderRank')}"
        if info.get('tier') is not None:
            self.rank = f"{info.get('tier')} {info.get('rank')} {info.get('lp')}LP"
        self.hotStreak = info.get('hotStreak')

    def _refresh_account_data(self):
        regionQuery = {
            'BR1': 'BR', 'EUN1': 'EUN', 'EUW1': 'EUW', 'JP1': 'JP',
            'KR': 'KR', 'LA1': 'LA1', 'LA2': 'LA2', 'ME1': 'tra',
            'NA1': 'NA', 'OC1': 'OCE', 'RU': 'tra', 'SG2': 'tra',
            'TR1': 'tra', 'TW2': 'tra', 'VN2': 'tra'
        }

        self.base_urls = {
            "border": 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/ranked-emblem/wings/wings_TIER.png',
            "icon": 'http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/',
            "opgg": f'https://deeplol.gg/summoner/{regionQuery[self.region]}/',
            "defaultIconPath": 'images/icon/default.png',
            'hotStreak_image_path': 'images/hotStreak.png'
        }

        rankedInfo = {}
        queryDone = False
        timeAfterLastQuery = (int(time.time()) - self.lastQuery)
        queryTimer = 2000


        if timeAfterLastQuery >= queryTimer:
            queryInfo = get_data(self.riot_id, self.tagline, self.riot_api)
            if queryInfo:
                rankedInfo = queryInfo.copy()
                rankedInfo.pop('iconID', None)
                queryDone = True
                self.lastQuery = int(time.time())
                self.iconID = queryInfo.get('iconID')

        # Test User Logic
        if self.riot_id == 'test' and self.tagline == 'test':
            rankedInfo = {
                'tier': 'Platinum', 'rank': 'IV', 'lp': 88, 'wins': 99, 
                'losses': 1, 'winrate': 99, 'hotStreak': True, 'iconID': 1234
            }
            if not self.lastKnownRankedInfo:
                self.lastKnownRankedInfo = {
                    'tier': 'Gold', 'rank': 'IV', 'lp': 1, 'wins': 99, 
                    'losses': 1, 'winrate': 99, 'hotStreak': True, 'ladderRank': None
                }

        self.lpDifferenceBetweenQueries = 0
        if rankedInfo and self.lastKnownRankedInfo:
            lpNow = lpForTier[rankedInfo.get('tier')] + lpForRank[rankedInfo.get('rank')] + rankedInfo.get('lp')
            lpLastKnown = lpForTier[self.lastKnownRankedInfo.get('tier')] + lpForRank[self.lastKnownRankedInfo.get('rank')] + self.lastKnownRankedInfo.get('lp')
            self.lpDifferenceBetweenQueries = lpNow - lpLastKnown

        confirmed_unranked = (queryDone and not rankedInfo.get('tier'))

        self.image_fade_path = RANKS_PATH_FADE.get(rankedInfo.get('tier'))
        self.image_border_url = None

        current_tier = None
        if rankedInfo:
            self._assign_user_info(rankedInfo)
            self.lastKnownRankedInfo = rankedInfo
            current_tier = rankedInfo.get('tier')
        elif confirmed_unranked:
            self.lastKnownRankedInfo = {}
        elif self.lastKnownRankedInfo:
            self._assign_user_info(self.lastKnownRankedInfo)
            current_tier = self.lastKnownRankedInfo.get('tier')

        if current_tier:
            self.image_fade_path = RANKS_PATH_FADE[current_tier]
            self.image_border_url = self.base_urls["border"].replace("TIER", current_tier.lower())

        # Update and Save
        updated_user = {
            'puuid': self.puuid, 'username': self.username, 'riot_id': self.riot_id,
            'tagline': self.tagline, 'region': self.region, 'iconID': self.iconID,
            'lastQuery': self.lastQuery, 'lastKnownRankedInfo': self.lastKnownRankedInfo
        }

        for i, u in enumerate(self.app.users):
            if u.get('riot_id') == self.riot_id and u.get('username') == self.username:
                self.app.users[i].update(updated_user)
                save_data(self.app.users, self.riot_id)
                break

    def init_ui(self, width, height, radius):
        button_width, button_height = width, height

        # Load Background Fade
        self.fade_pixmap = create_fade_image(self.image_fade_path, (width, height), radius)
        self.fade_label = QLabel(self)
        self.fade_label.setPixmap(self.fade_pixmap)
        self.fade_label.setScaledContents(True)
        self.fade_label.setGeometry(0, 0, width, height)

        # Query Border Image from URL
        self.border_pixmap = None
        if self.image_border_url:
            try:
                border_res = requests.get(self.image_border_url)
                if border_res.status_code == 200:
                    px = QPixmap()
                    px.loadFromData(border_res.content)
                    self.border_pixmap = px
            except Exception as e:
                print(f"Failed to fetch border from URL: {e}")

        # Position Border and Icon
        self.icon_label = QLabel(self)
        self.icon_label.setStyleSheet('background: transparent;')
        
        if self.border_pixmap:
            b_w, b_h = self.border_pixmap.width(), self.border_pixmap.height()
            self.border_label = QLabel(self)
            self.border_label.setPixmap(self.border_pixmap)
            self.border_label.setScaledContents(True)
            self.border_label.setStyleSheet("background: transparent; border: none;")

            # 1. Scaled Border Dimensions (same as before)
            border_w = round(1.75 * button_height)
            border_h = round(2.2962 * button_height)
            border_x = 0
            border_y = - round(0.7038 * button_height)

            # 2. Calculate the Dynamic Icon Size
            # Based on the 1084/2296 ratio
            icon_size = round(border_w * (1084 / 2296))

            # 3. Calculate Centered Position
            # We use (icon_size / 2) instead of 50 to keep it centered
            icon_x = round((border_w * 0.5004) - (icon_size / 2) + 11)
            icon_y = round(border_y + (border_h * 0.6008) - (icon_size / 2))

            # 4. Apply Geometry
            self.border_label.setGeometry(border_x, border_y, border_w, border_h)
            self.icon_label.setGeometry(icon_x, icon_y, icon_size, icon_size)
        else:
            self.icon_label.setGeometry(100 // 3, 0, 100, 100)

        # Load Icon Image
        if self.iconID is not None:
            try:
                url = f"{self.base_urls['icon']}{self.iconID}.jpg"
                response = requests.get(url)
                if response.status_code == 200:
                    pixmap = create_circular_icon(response.content) if self.border_pixmap else create_circular_icon(response.content, circular=False, width=button_height, height=button_height)
                else:
                    pixmap = create_circular_icon(self.base_urls['defaultIconPath']) if self.border_pixmap else create_circular_icon(self.base_urls['defaultIconPath'], circular=False, width=button_height, height=button_height)

                self.icon_label.setPixmap(pixmap)
                self.icon_label.raise_()
                self.icon_label.show()
            except Exception:
                print(f"Failed to load iconID image: {self.iconID}")

        # Account Name
        self.account_label = QLabel(f'{self.account_name} #{self.tagline}', self)
        self.account_label.setFont(QFont("Arial", 16))
        self.account_label.setStyleSheet("background: transparent;")
        al_start_x = button_width // 3
        al_start_y = 0
        self.account_label.setGeometry(al_start_x, al_start_y, button_width - al_start_x, button_height - al_start_y)

        # Winrate Label
        self.winrate_label = QLabel(self.winrate, self)
        self.winrate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winrate_label.setFont(QFont("Arial", 9))
        self.winrate_label.setStyleSheet("background: transparent;")
        winrate_start_x = button_width - button_width // 3
        winrate_start_y = button_height // 2
        self.winrate_label.setGeometry(winrate_start_x, winrate_start_y, button_width - winrate_start_x, winrate_start_y)

        # Rank Label with LP color
        color = "black"
        lp_text = ""
        if self.lpDifferenceBetweenQueries < 0:
            color, lp_text = "red", f"(↓{self.lpDifferenceBetweenQueries}lp)"
        elif self.lpDifferenceBetweenQueries > 0:
            color, lp_text = "lightgreen", f"(↑{self.lpDifferenceBetweenQueries}lp)"
        
        label_text = f"{self.rank} <span style='color: {color};'>{lp_text}</span>"
        self.rank_label = QLabel(label_text, self)
        self.rank_label.setFont(QFont("Arial", 9))
        self.rank_label.setStyleSheet("background: transparent;")
        self.rank_label.setGeometry(al_start_x, winrate_start_y, button_width - winrate_start_x, winrate_start_y)

        # Hotstreak
        if self.hotStreak:
            self.hotStreak_pixmap = create_hot_streak(self.base_urls['hotStreak_image_path'])
            self.hotStreak_label = QLabel(self)
            self.hotStreak_label.setPixmap(self.hotStreak_pixmap)
            self.hotStreak_label.setGeometry(0, round(button_height // 2.5), self.hotStreak_pixmap.width(), self.hotStreak_pixmap.height())
            self.hotStreak_label.setStyleSheet('background: transparent;')
            self.hotStreak_label.setToolTip('Hotstreak')
            self.hotStreak_label.raise_()

        # Analysis Button
        self.analysis_website = QPushButton("deeplol.gg", self)
        self.analysis_website.setGeometry(winrate_start_x, 6, button_width - winrate_start_x, 20)
        self.analysis_website.setStyleSheet("background: rgba(0,0,0,0); color: #cfcfcf; border: none; font-size:10px;")
        self.analysis_website.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.analysis_website.clicked.connect(self.open_opgg)
        self.analysis_website.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.analysis_website.raise_()

        # Invisible overlay button
        self.button = QPushButton('', self)
        self.button.setGeometry(0, 0, width, height)
        self.button.setStyleSheet(f'background: transparent; border-radius: {radius}px; border: none;')
        self.button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def delete_account(self):
        if hasattr(self, 'app') and getattr(self.app, 'users', None) is not None:
            self.app.users = [u for u in self.app.users if not (u.get('riot_id') == self.riot_id and u.get('username') == self.username)]
            save_data(self.app.users)
            print(f"Deleted use successfully. {self.username}")
        else:
            print('Warning: could not find app.users to update')
        try:
            keyring.delete_password(self.app.service_name, self.username)
        except Exception as e:
            print(f"Failed to delete: {e}")
        self.setParent(None)
        self.deleteLater()

    def hide_delete_button(self):
        for attr in ['delete_button', 'delete_confirm_btn', 'delete_cancel_btn', '_delete_overlay']:
            if hasattr(self, attr):
                btn = getattr(self, attr)
                if btn: btn.hide()

    def show_delete_button(self):
        label_geom = self.account_label.geometry()
        btn_w, btn_h, spacing = 110, 24, 10
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

        if not hasattr(self, '_delete_overlay') or self._delete_overlay is None:
            self._delete_overlay = QLabel(self)
            self._delete_overlay.setStyleSheet(f'background: rgba(0,0,0,80); border-radius: {self.radius}px;')
        
        self._delete_overlay.setGeometry(0, 0, self.width(), self.height())
        self._delete_overlay.show()
        self.delete_confirm_btn.show()
        self.delete_cancel_btn.show()
        self._delete_overlay.raise_()
        self.delete_confirm_btn.raise_()
        self.delete_cancel_btn.raise_()

    def open_opgg(self):
        try:
            url = f"{self.base_urls['opgg']}{self.account_name}-{self.tagline}"
            webbrowser.open(url)
        except Exception as e:
            print(f"Failed to open site: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.show_delete_button()
        elif event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()
            self._dragging = False
            self.hide_delete_button()

    def enterEvent(self, event):
        self.account_label.setStyleSheet("color: #A5A2A3; background: transparent;")
        self.winrate_label.setStyleSheet("color: #A5A2A3; background: transparent;")
        self.rank_label.setStyleSheet("color: #A5A2A3; background: transparent;")

    def leaveEvent(self, event):
        self.account_label.setStyleSheet("background: transparent;")
        self.winrate_label.setStyleSheet("background: transparent;")
        self.rank_label.setStyleSheet("background: transparent;")

    def on_click(self):
        self.clicked_account.emit(self.username, self.password)

    def mouseMoveEvent(self, event):
        if getattr(self, '_drag_start_pos', None) is None or not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.pos() - self._drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return
        self._dragging = True
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(f"{self.riot_id}|{self.username}")
        drag.setMimeData(mime)
        drag.setPixmap(self.grab())
        drag.exec()

    def mouseReleaseEvent(self, event):
        if getattr(self, '_dragging', False):
            self._dragging = False
            self._drag_start_pos = None
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_account.emit(self.username, self.password)
            self._drag_start_pos = None

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        edit_action = menu.addAction("Edit Riot ID / Tagline...")
        delete_action = menu.addAction("Delete account")

        action = menu.exec(self.mapToGlobal(event.pos()))

        if action == edit_action:
            self.edit_riot_id_and_tagline()
        elif action == delete_action:
            self.delete_account()

    def edit_riot_id_and_tagline(self):
        current_riot_id = self.riot_id or ""
        current_tagline = self.tagline or ""

        # First: ask for new Riot ID (game name)
        new_riot_id, ok1 = QInputDialog.getText(
            self,
            "Change Riot ID",
            "New Riot ID (game name):",
            text=current_riot_id
        )

        if not ok1 or not new_riot_id.strip():
            return

        new_riot_id = new_riot_id.strip()

        # Second: ask for tagline
        new_tagline, ok2 = QInputDialog.getText(
            self,
            "Change Tagline",
            "New tagline (without #):",
            text=current_tagline
        )

        if not ok2:
            return

        new_tagline = new_tagline.strip().lstrip('#')  # remove accidental #

        if not new_tagline:
            QMessageBox.warning(self, "Invalid Tagline", "Tagline cannot be empty.")
            return

        # Optional: very basic validation
        if len(new_riot_id) < 3 or len(new_riot_id) > 22:
            QMessageBox.warning(self, "Invalid Riot ID", "Riot ID should be 3–22 characters.")
            return
        if len(new_tagline) < 3 or len(new_tagline) > 5:
            QMessageBox.warning(self, "Invalid Tagline", "Tagline should be 3–5 characters.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Change",
            f"Change account display to:\n\n"
            f"{new_riot_id}#{new_tagline}\n\n",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # ────────────────────────────────────────────────
        # Apply changes
        # ────────────────────────────────────────────────

        old_riot_id = self.riot_id
        old_tagline = self.tagline

        self.riot_id = new_riot_id
        self.tagline = new_tagline
        self.account_name = new_riot_id
        self.account_name_w_tagline = f"{new_riot_id}#{new_tagline}"

        # Update label immediately
        self.account_label.setText(f"{self.account_name} #{self.tagline}")

        # Update stored user data
        for i, u in enumerate(self.app.users):
            if u.get('riot_id') == old_riot_id and u.get('tagline') == old_tagline:
                self.app.users[i]['riot_id'] = new_riot_id
                self.app.users[i]['tagline'] = new_tagline
                # Also update display fields if you store them
                if 'account_name' in self.app.users[i]:
                    self.app.users[i]['account_name'] = new_riot_id
                break

        # Save to disk / secure storage
        save_data(self.app.users, self.riot_id)   # ← adjust if your save_data uses different args

        # Optional: force refresh ranked data with new name
        self._refresh_account_data()

        # Visual feedback
        # QMessageBox.information(self, "Updated", "Riot ID and tagline updated in the client.\n(Note: actual Riot account unchanged)")