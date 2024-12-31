import sys
import cv2
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QSlider, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize variables
        self.video_path = "/home/rmt/Desktop/rsc/Video1.mp4"
        self.capture = cv2.VideoCapture(self.video_path)
        self.timer = QTimer()
        self.is_paused = True
        self.playback_speed = 30  # Default speed (milliseconds between frames)
        self.frame_index = 0  # Keeps track of the current frame

        # Set up GUI
        self.init_ui()

    def init_ui(self):
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Video display area
        self.video_label = QLabel(self)
        self.layout.addWidget(self.video_label)

        # Buttons
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_video)
        self.layout.addWidget(self.play_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_video)
        self.layout.addWidget(self.pause_button)

        # Speed slider
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(10)  # Minimum delay (faster)
        self.speed_slider.setMaximum(100)  # Maximum delay (slower)
        self.speed_slider.setValue(self.playback_speed)
        self.speed_slider.valueChanged.connect(self.adjust_speed)
        self.layout.addWidget(self.speed_slider)

        # Timer for video playback
        self.timer.timeout.connect(self.update_frame)

    def play_video(self):
        if self.is_paused:
            self.is_paused = False
            self.timer.start(self.playback_speed)

    def pause_video(self):
        self.is_paused = True
        self.timer.stop()

    def adjust_speed(self, value):
        self.playback_speed = value
        if not self.is_paused:
            self.timer.start(self.playback_speed)

    def update_frame(self):
        if self.capture.isOpened():
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.frame_index)  # Set frame to the current position
            ret, frame = self.capture.read()
            if ret:
                self.frame_index += 1  # Move to the next frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                step = channel * width
                qimg = QImage(frame.data, width, height, step, QImage.Format.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qimg))
            else:
                self.timer.stop()
                self.capture.release()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
