import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel, QFileDialog)
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player")
        self.resize(800, 600)

        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Video widget
        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)

        # Media Player
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)

        # Load video list
        base_path = ""  # Set your base path here
        self.video_list = [
            base_path + r"./rsc/Video1.mp4",
            base_path + r"./rsc/Video2.mp4"
        ]
        self.current_video_index = 0

        # Control buttons
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_video)
        self.layout.addWidget(self.play_button)

        self.next_button = QPushButton("Next Video")
        self.next_button.clicked.connect(self.play_next_video)
        self.layout.addWidget(self.next_button)

    def play_video(self):
        if not self.video_list:
            return

        video_path = self.video_list[self.current_video_index]
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        self.media_player.play()

    def play_next_video(self):
        self.current_video_index += 1
        if self.current_video_index >= len(self.video_list):
            self.current_video_index = 0
        self.play_video()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
