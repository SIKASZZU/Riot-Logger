
from helper import *
from PyQt6.QtWidgets import QWidget

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

            new_users = []
            for i in range(layout.count()):
                w = layout.itemAt(i).widget()
                if not w:
                    continue
                user_info = getattr(w, 'user_data', None)

                print(f"--- Widget {i} ---")
                import pprint
                pprint.pprint(vars(w))

                if user_info:
                    new_users.append(user_info)

            self.app.users = new_users
            from helper import save_data
            save_data(self.app.users)

            event.acceptProposedAction()
        except Exception as e:
            print('Drop handling failed:', e)
            event.ignore()