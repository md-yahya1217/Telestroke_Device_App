import sys
import asyncio
import cv2
from PyQt6 import QtWidgets, QtGui, QtCore
from av import VideoFrame
from videosdk import CustomVideoTrack
import time
import fractions
from vsaiortc.mediastreams import MediaStreamError

class WebcamVideoTrack(CustomVideoTrack):
    def __init__(self):
        super().__init__()
        self.kind = "video"
        self.cap = cv2.VideoCapture(1)  # or try cv2.CAP_GSTREAMER
        if not self.cap.isOpened():
            raise Exception("Could not open webcam")
        
        # Set the frame width and height
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        
        self._start = time.time()
        self._timestamp = 0
        self.screen_number = 1  # Default to showing the left half

    async def recv(self) -> VideoFrame:
        pts, time_base = await self.next_timestamp()

        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Failed to capture frame from webcam")

        height, width, _ = frame.shape

        if self.screen_number == 1:
            frame_cropped = frame[:, :width // 2]
        elif self.screen_number == 2:
            frame_cropped = frame[:, width // 2:]

        frame_rgb = cv2.cvtColor(frame_cropped, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame_rgb, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame

    async def next_timestamp(self) -> tuple[int, fractions.Fraction]:
        VIDEO_PTIME = 1 / 30  # Packet time for 30fps
        VIDEO_CLOCK_RATE = 90000  # Clock rate for video
        VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)

        if self.readyState != "live":
            raise MediaStreamError

        if hasattr(self, "_timestamp"):
            self._timestamp += int(VIDEO_PTIME * VIDEO_CLOCK_RATE)
            wait = self._start + (self._timestamp / VIDEO_CLOCK_RATE) - time.time()
            await asyncio.sleep(max(0, wait))
        else:
            self._start = time.time()
            self._timestamp = 0

        return self._timestamp, VIDEO_TIME_BASE

    def set_screen_number(self, screen_number: int):
        if screen_number in [1, 2]:
            self.screen_number = screen_number
        else:
            raise ValueError("Invalid screen number. Must be 1 (left) or 2 (right).")

    def stop(self):
        print("stop webcam called")
        if self.cap is not None:
            print("stop webcam called")
            self.cap.release()


