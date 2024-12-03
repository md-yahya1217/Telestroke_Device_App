import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QWidget, QPushButton, QGridLayout, QDialog

class VirtualKeyboard(QDialog):
    def __init__(self, input_field, main_window):
        super().__init__()
        self.input_field = input_field
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Virtual Keyboard")
        self.setGeometry(100, 100, 400, 250)

        # Define the layout for the keyboard
        layout = QGridLayout()
        self.setLayout(layout)

        # Define the keys
        keys = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
            'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P',
            'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L',
            'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<-', 'Space', 'Enter'
        ]

        row = 0
        col = 0
        for key in keys:
            button = QPushButton(key)
            button.clicked.connect(lambda _, k=key: self.key_clicked(k))
            layout.addWidget(button, row, col)

            col += 1
            if col > 9:
                col = 0
                row += 1

    def key_clicked(self, key):
        if key == '<-':
            current_text = self.input_field.text()
            self.input_field.setText(current_text[:-1])
        elif key == 'Space':
            self.input_field.insert(' ')
        elif key == 'Enter':
            # Close the keyboard window and disable reopening until manually refocused
            self.main_window.prevent_keyboard_open = True
            self.close()
        else:
            self.input_field.insert(key)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window with Virtual Keyboard")
        self.setGeometry(100, 100, 400, 200)

        # Create an input field
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Click to type...")

        # Create the layout
        layout = QVBoxLayout()
        layout.addWidget(self.input_field)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Flag to prevent immediate reopening of the keyboard
        self.prevent_keyboard_open = False

        # Connect focus event to show virtual keyboard
        self.input_field.focusInEvent = self.show_virtual_keyboard

    def show_virtual_keyboard(self, event):
        if not self.prevent_keyboard_open:
            self.keyboard = VirtualKeyboard(self.input_field, self)
            self.keyboard.show()
        else:
            # Reset the flag so that the keyboard can open again in future
            self.prevent_keyboard_open = False
        QLineEdit.focusInEvent(self.input_field, event)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
