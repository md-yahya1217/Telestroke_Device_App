import sys
import cv2
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel, QSlider
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stimulus screen")
        self.resize(1920, 1080)

        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Video display label
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.video_label)

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

        # self.next_button = QPushButton("Next Video")
        # self.next_button.clicked.connect(self.play_next_video)
        # self.layout.addWidget(self.next_button)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_video)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_video)
        self.layout.addWidget(self.stop_button)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(30)  # Default to 30 ms per frame
        self.speed_slider.valueChanged.connect(self.adjust_speed)
        self.layout.addWidget(self.speed_slider)

        # Timer for updating the video frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        # Initialize OpenCV VideoCapture object
        self.cap = None
        self.playback_speed = 30  # Default speed in ms

    def play_video(self):
        if not self.video_list:
            return

        video_path = self.video_list[self.current_video_index]
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            print("Error: Could not open video.")
            return

        self.timer.start(self.playback_speed)  # Update according to current speed

    # def play_next_video(self):
    #     self.current_video_index += 1
    #     if self.current_video_index >= len(self.video_list):
    #         self.current_video_index = 0
    #     self.play_video()

    def start_video(self):
        if self.cap and not self.timer.isActive():
            self.timer.start(self.playback_speed)

    def stop_video(self):
        if self.timer.isActive():
            self.timer.stop()

    def adjust_speed(self):
        self.playback_speed = self.speed_slider.value()
        if self.timer.isActive():
            self.timer.start(self.playback_speed)

    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Convert the frame to RGB format for QLabel
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, _ = rgb_image.shape

                # Create the QImage using the RGB frame
                q_image = QImage(rgb_image.data, w, h, 3 * w, QImage.Format.Format_RGB888)

                # Scale the image to fit the label size (stretching the image to fit the available space)
                scaled_pixmap = QPixmap.fromImage(q_image).scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                # Set the scaled image to the QLabel
                self.video_label.setPixmap(scaled_pixmap)
            else:
                self.cap.release()
                self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
