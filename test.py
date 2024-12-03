from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget  # Correct import for QVideoWidget

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)
        
        # Set up the layout
        layout = QVBoxLayout()

        # Set up the video widget to display video
        self.videoWidget = QVideoWidget()
        layout.addWidget(self.videoWidget)

        # Set up the media player
        self.mediaPlayer = QMediaPlayer(self)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Play button to load the video
        self.playButton = QPushButton('Play Video', self)
        self.playButton.clicked.connect(self.play_video)
        layout.addWidget(self.playButton)

        # Set the layout of the QWidget
        self.setLayout(layout)

    def play_video(self):
        # Load the video from the correct path
        video_path = '/home/rmt/Desktop/rsc/Video1.mp4'  # Full path to your video file
        self.mediaPlayer.setSource(QUrl.fromLocalFile(video_path))
        self.mediaPlayer.play()

if __name__ == '__main__':
    app = QApplication([])
    window = VideoPlayer()
    window.show()
    app.exec()
