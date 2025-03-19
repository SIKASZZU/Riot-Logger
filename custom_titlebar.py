import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel

class CustomTitleBar(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout for the custom title bar
        layout = QHBoxLayout()
        
        # Create a label for the title
        self.title_label = QLabel("Custom Window Title")
        layout.addWidget(self.title_label)
        
        # Add stretch space between the title and buttons to push the buttons to the right
        layout.addStretch()
        
        # Create buttons
        self.api_button = QPushButton("API")
        self.minimize_button = QPushButton("Minimize")
        self.exit_button = QPushButton("Exit")
        
        # Add buttons to the layout
        layout.addWidget(self.api_button)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.exit_button)
        
        # Connect the buttons to their respective functions
        self.exit_button.clicked.connect(self.close_window)
        self.minimize_button.clicked.connect(self.minimize_window)
        self.api_button.clicked.connect(self.api_action)
        
        # Set the layout for the custom title bar
        self.setLayout(layout)
    
    def close_window(self):
        self.window().close()
    
    def minimize_window(self):
        self.window().showMinimized()
    
    def api_action(self):
        # Placeholder for the API button action
        print("API button clicked")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set the custom title bar
        self.setMenuWidget(CustomTitleBar())
        
        # Main layout for the application content
        layout = QVBoxLayout()
        layout.addWidget(QPushButton("Main Window Content"))
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.setWindowTitle("Custom Title Bar Example")
        self.resize(400, 300)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec())
