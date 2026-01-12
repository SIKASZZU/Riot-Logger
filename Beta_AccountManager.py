import keyring
import requests
import webbrowser
import time

from Beta_Api import RiotAPI, get_data
from helper import *

from PyQt6.QtGui import QFont, QCursor, QDrag
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

        try:
            keyring.delete_password(self.app.service_name, self.username)
            print(f"Successfully removed password for {self.username}")
        except keyring.errors.PasswordDeleteError:
            print("No such entry existed (already removed or never saved)")
        except Exception as e:
            print(f"Failed to delete: {e}")

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
        self.account_label.setStyleSheet("background: transparent;")
        self.winrate_label.setStyleSheet("background: transparent;")
        self.rank_label.setStyleSheet("background: transparent;")

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

        # labels
        self.fade_label = None
        self.border_label = None
        self.account_label = None
        self.rank_label = None
        self.winrate_label = None
        self.hotStreak_label = None
        self.icon_label = None

        print(f'Loaded user: {user_data.get('riot_id')}')

        # Capture `app` reference from parent (MainApp) when available
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
        self.lastQuery = user_data.get('lastQuery') if user_data.get('lastQuery') != None else int( time.time() )
        self.lastKnownRankedInfo = user_data.get('lastKnownRankedInfo') if user_data.get('lastKnownRankedInfo') != None else {}
        self.iconID = user_data.get('iconID') if user_data.get('iconID') != None else None

        self.hotStreak = None
        self.winrate = None
        self.rank = 'Unranked'
        regionQuery = {
            'BR1': 'BR',
            'EUN1': 'EUNE',
            'EUW1': 'EUW',
            'JP1': 'JP',
            'KR': 'KR',
            'LA1': 'LA1',
            'LA2': 'LA2',
            'ME1': 'tra',
            'NA1': 'NA',
            'OC1': 'OCE',
            'RU': 'tra',
            'SG2': 'tra',
            'TR1': 'tra',
            'TW2': 'tra',
            'VN2': 'tra'
        }

        self.base_urls = {
            "icon": 'http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/',
            "opgg": f'https://op.gg/lol/summoners/{regionQuery[self.region]}/',
            "defaultIconPath": 'images/icon/default.png',
            'hotStreak_image_path': 'images/hotStreak.png'
        }

        # Get API key from parent app; MainApp should load it once.
        api_key = None
        if self.app and getattr(self.app, 'api_key', None):
            api_key = self.app.api_key
        if not api_key:
            raise ValueError('API key not found. MainApp must set `self.api_key`.')
        self.riot_api = RiotAPI(api_key, self.region)

        def assign_user_info(info: dict):
            self.winrate = f"{info.get('winrate')}%\n{info.get('wins')}W {info.get('losses')}L"
            if (info.get('ladderRank')):
                ladderRank = info.get('ladderRank')
                self.winrate = self.winrate + f"\nRank {ladderRank}"
                # if self.lastKnownRankedInfo.get('ladderRank') != ladderRank:
                    # rankDiff = self.lastKnownRankedInfo.get('ladderRank') - ladderRank
                    # self.winrate = self.winrate + f" ({rankDiff})"
            if info.get('tier') is not None:
                self.rank = f"{info.get('tier')} {info.get('rank')} {info.get('lp')}LP"
            self.hotStreak = info.get('hotStreak')

        def get_ranked_from_query(info: dict) -> dict:
            # ranked info
            rankedInfo = info.copy()

            # remove single variables
            rankedInfo.pop('iconID')
            return rankedInfo

        rankedInfo: dict = {}
        queryInfo: dict = {}
        queryDone: bool = False
        timeAfterLastQuery = (int( time.time() ) - self.lastQuery)
        queryTimer = 15 * 60
        print(f"Query every {queryTimer} sec")
        if (timeAfterLastQuery >= queryTimer):
            print(self.account_name, ' is doing a query. Time passed: ', timeAfterLastQuery / 60, 'min')

            queryInfo = get_data(self.riot_id, self.tagline, self.riot_api)
            if queryInfo:
                rankedInfo = get_ranked_from_query(queryInfo)
                queryDone = True
                self.lastQuery = int( time.time() )
                self.iconID = queryInfo.get('iconID')

        if self.riot_id == 'test' and self.tagline == 'test':
            print('TEST USER DETECTED!')
            rankedInfo = {
                'tier': 'Platinum', 
                'rank': 'IV', 
                'lp': 88, 
                'wins': 99, 
                'losses': 1, 
                'winrate': 99, 
                'hotStreak': True, 
                'iconID': 1234
            }
            if not self.lastKnownRankedInfo:
                self.lastKnownRankedInfo = {
                    'tier': 'Gold', 
                    'rank': 'IV', 
                    'lp': 1, 
                    'wins': 99, 
                    'losses': 1, 
                    'winrate': 99, 
                    'hotStreak': True, 
                    'ladderRank': None
                }

        lpDifferenceBetweenQueries = 0
        if rankedInfo and self.lastKnownRankedInfo:
            lpNow = lpForTier[rankedInfo.get('tier')] + lpForRank[rankedInfo.get('rank')] + rankedInfo.get('lp')
            lpLastKnown = lpForTier[self.lastKnownRankedInfo.get('tier')] + lpForRank[self.lastKnownRankedInfo.get('rank')] + self.lastKnownRankedInfo.get('lp')
            lpDifferenceBetweenQueries = lpNow - lpLastKnown

        confirmed_unranked: bool = (queryDone and not rankedInfo.get('tier'))

        image_fade_path = RANKS_PATH_FADE[rankedInfo.get('tier')]
        image_border_path = None
        # elif summoner level < 30: display level

        if rankedInfo:
            assign_user_info(rankedInfo)
            self.lastKnownRankedInfo = rankedInfo
            tier = rankedInfo.get('tier')
            image_fade_path = RANKS_PATH_FADE[tier]
            image_border_path = RANKS_PATH_BORDER[tier]

        elif confirmed_unranked:
            self.lastKnownRankedInfo = {}

        elif self.lastKnownRankedInfo:
            assign_user_info(self.lastKnownRankedInfo)
            saved_tier = self.lastKnownRankedInfo.get('tier')
            image_fade_path = RANKS_PATH_FADE[saved_tier]
            image_border_path = RANKS_PATH_BORDER[saved_tier]

        updated_user = {
            'puuid': self.puuid,
            'username': self.username,
            
            'riot_id': self.riot_id,
            'tagline': self.tagline,
            'region': self.region,
            
            'iconID': self.iconID,
            'lastQuery': self.lastQuery,
            'lastKnownRankedInfo': self.lastKnownRankedInfo
        }

        print(f'{self.account_name} | \
              \n lastQuery: {timeAfterLastQuery} sec ago \
              \n data {user_data}')

        found = False
        for i, u in enumerate(self.app.users):
            if u.get('riot_id') == self.riot_id and u.get('username') == self.username:
                self.app.users[i].update(updated_user)
                found = True
                break

        if not found:
            print('Error finding user from self.app.users. Did not update user data!')
        else:
            save_data(self.app.users, self.riot_id)

        print('\n')

        # Load background fade, border
        self.fade_pixmap = create_fade_image(image_fade_path, (width, height), radius)
        self.border_pixmap = create_border_image(image_border_path)

        # --------- IMAGES --------- #

        # Summoner Icon
        self.icon_label = QLabel(self)
        self.icon_label.setStyleSheet('background: transparent;')
        icon_label_width = 100
        icon_label_height = 100
        self.icon_label.setGeometry(icon_label_width // 3, 0, icon_label_width, icon_label_height)

        # Background labelq
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

            self.icon_label = QLabel(self)
            self.icon_label.setStyleSheet('background: transparent;')
            self.icon_label.setGeometry(border_width // 3 + 1, button_height // 3 - 2, 50, 50)

        if self.iconID != None:
            try:
                url = f"{self.base_urls['icon']}{self.iconID}.jpg"
                response = requests.get(url)
                if response.status_code == 200:
                    if self.border_pixmap is not None:
                        pixmap = create_circular_icon(response.content)
                    else:
                        pixmap = create_circular_icon(response.content, circular=False, width=button_height, height=button_height)
                else:
                    print(self.base_urls['defaultIconPath'])
                    if self.border_pixmap is not None:
                        pixmap = create_circular_icon(self.base_urls['defaultIconPath'])
                    else:
                        pixmap = create_circular_icon(self.base_urls['defaultIconPath'], circular=False, width=button_height, height=button_height)

                self.icon_label.setPixmap(pixmap)
                self.icon_label.raise_()
                self.icon_label.show()

                if response.status_code != 200:
                    raise Exception

            except Exception:
                print(f"Failed to load iconID image:")
                print(f'self.iconID: {self.iconID}')
                print(f'response code: {response.status_code}')
                print()

        # Text labels

        # Account name
        self.account_label = QLabel(self.account_name, self)
        self.account_label.setFont(QFont("Arial", 16))
        self.account_label.setStyleSheet("background: transparent;")
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
        self.winrate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winrate_label.setFont(QFont("Arial", 9))
        self.winrate_label.setStyleSheet("background: transparent;")
        winrate_start_x = button_width - button_width // 3
        winrate_start_y = button_height // 2
        self.winrate_label.setGeometry(
            winrate_start_x,
            winrate_start_y,
            button_width - winrate_start_x,
            winrate_start_y
        )

        # calculate difference + color
        if lpDifferenceBetweenQueries < 0:
            color = "red"
            lp_text = f"(↓{lpDifferenceBetweenQueries}lp)"
        elif lpDifferenceBetweenQueries > 0:
            color = "lightgreen"
            lp_text = f"(↑{lpDifferenceBetweenQueries}lp)"
        else:
            color = "black"
            lp_text = ""

        # combine with colored span
        label_text = f"{self.rank} <span style='color: {color};'>{lp_text}</span>"

        # set QLabel
        self.rank_label = QLabel(label_text, self)
        self.rank_label.setFont(QFont("Arial", 9))
        self.rank_label.setStyleSheet("background: transparent;")
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
            self.hotStreak_pixmap = create_hot_streak(self.base_urls['hotStreak_image_path'])
            self.hotStreak_label = QLabel(self)
            self.hotStreak_label.setPixmap(self.hotStreak_pixmap)
            self.hotStreak_label.setGeometry(0, round(button_height // 2.5), self.hotStreak_pixmap.width(), self.hotStreak_pixmap.height())
            self.hotStreak_label.setStyleSheet('background: transparent;')
            self.hotStreak_label.setToolTip('Hotstreak')
            self.hotStreak_label.raise_()

        self.opgg_btn = QPushButton("op.gg", self)
        self.opgg_btn.setGeometry(winrate_start_x, 6, button_width - winrate_start_x, 20)
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