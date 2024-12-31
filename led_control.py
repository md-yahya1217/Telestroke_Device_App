from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from gpiozero import LED
import os
import sys

# GPIO setup
mosfet1 = LED(17)  # GPIO pin 17 controls MOSFET 1 (LCD 1)
mosfet2 = LED(27)  # GPIO pin 22 controls MOSFET 2 (LCD 2)

class LCDControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Window title and geometry
        self.setWindowTitle("LCD Control")
        self.setGeometry(100, 100, 300, 200)

        # Label to display the current state
        self.label = QLabel("Select an LCD:", self)

        # Left button
        self.left_button = QPushButton("Left LCD", self)
        self.left_button.clicked.connect(self.activate_left_lcd)

        # Right button
        self.right_button = QPushButton("Right LCD", self)
        self.right_button.clicked.connect(self.activate_right_lcd)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.left_button)
        layout.addWidget(self.right_button)

        self.setLayout(layout)

    def activate_left_lcd(self):
        mosfet1.on()  # Turn on MOSFET 1 (LCD 1 ON)
        mosfet2.off()  # Turn off MOSFET 2 (LCD 2 OFF)
        self.label.setText("State: LCD 1 ON, LCD 2 OFF")
        print("State: LCD 1 ON, LCD 2 OFF")

    def activate_right_lcd(self):
        mosfet1.off()  # Turn off MOSFET 1 (LCD 1 OFF)
        mosfet2.on()  # Turn on MOSFET 2 (LCD 2 ON)
        self.label.setText("State: LCD 2 ON, LCD 1 OFF")
        print("State: LCD 2 ON, LCD 1 OFF")

if __name__ == "__main__":
    # Adjust permissions to avoid using sudo
    if os.geteuid() != 0:
        try:
            os.system("sudo chmod 666 /dev/gpiomem")
        except Exception as e:
            print(f"Error setting GPIO permissions: {e}")
            sys.exit(1)

    app = QApplication(sys.argv)
    window = LCDControlApp()
    window.show()
    sys.exit(app.exec())
