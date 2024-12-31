import sys
import cv2
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QSlider, QHBoxLayout
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QImage

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)

        self.video_capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.playing = False
        self.playback_speed = 1.0

        # UI setup
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.play_pause_button = QPushButton("Play", self)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)

        self.open_button = QPushButton("Open Video", self)
        self.open_button.clicked.connect(self.open_video)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.speed_slider.setRange(5, 15)  # Represents 0.5x to 1.5x
        self.speed_slider.setValue(10)  # Default is 1.0x
        self.speed_slider.valueChanged.connect(self.change_speed)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("0.5x"))
        slider_layout.addWidget(self.speed_slider)
        slider_layout.addWidget(QLabel("1.5x"))

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.play_pause_button)
        layout.addWidget(self.open_button)
        layout.addLayout(slider_layout)
        self.setLayout(layout)

    def open_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_path:
            self.video_capture = cv2.VideoCapture(file_path)
            if not self.video_capture.isOpened():
                self.video_capture = None
                self.video_label.setText("Failed to open video file.")
            else:
                self.playing = False
                self.play_pause_button.setText("Play")

    def toggle_play_pause(self):
        if self.video_capture is None:
            return

        if self.playing:
            self.timer.stop()
            self.play_pause_button.setText("Play")
        else:
            self.timer.start(int(30 / self.playback_speed))  # Adjust timer interval based on speed
            self.play_pause_button.setText("Pause")

        self.playing = not self.playing

    def change_speed(self):
        self.playback_speed = self.speed_slider.value() / 10.0
        if self.playing:
            self.timer.start(int(30 / self.playback_speed))

    def update_frame(self):
        if self.video_capture is None or not self.video_capture.isOpened():
            return

        ret, frame = self.video_capture.read()
        if not ret:
            self.timer.stop()
            self.playing = False
            self.play_pause_button.setText("Play")
            return

        # Convert the frame to RGB and display it
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = frame.shape
        qimg = QImage(frame.data, width, height, channels * width, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        if self.video_capture:
            self.video_capture.release()
        cv2.destroyAllWindows()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
