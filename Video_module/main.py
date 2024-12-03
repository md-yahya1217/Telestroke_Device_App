import sys
import os
import asyncio
import dotenv
import threading
from PyQt5 import QtWidgets, uic
from videosdk import MeetingConfig, VideoSDK
from customvideo_events import VideoFileTrack
from webcam_feed import WebcamVideoTrack  # Import your webcam video track
from meeting_events import MyMeetingEventHandler

dotenv.load_dotenv()

VIDEOSDK_TOKEN = os.getenv("VIDEOSDK_TOKEN")
MEETING_ID = os.getenv("MEETING_ID")
NAME = "Wajahat"

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('mainwindow.ui', self)

        # Find the widgets by their object names
        self.label_status = self.findChild(QtWidgets.QLabel, 'label_status')
        self.btn_joinMeeting = self.findChild(QtWidgets.QPushButton, 'btn_joinMeeting')

        # Connect the button to the function
        self.btn_joinMeeting.clicked.connect(self.join_meeting)

        # Start the asyncio event loop in a separate thread
        self.loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.start_event_loop, args=(self.loop,))
        t.start()

    def start_event_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def join_meeting(self):
        self.label_status.setText("Status: Joining...")
        asyncio.run_coroutine_threadsafe(self.start_meeting(), self.loop)

    async def start_meeting(self):
        # Initialize custom webcam video track
        webcam_track = WebcamVideoTrack()

        meeting_config = MeetingConfig(
            meeting_id=MEETING_ID,
            name=NAME,
            mic_enabled=True,
            token=VIDEOSDK_TOKEN,
            custom_camera_video_track=webcam_track
        )

        self.meeting = VideoSDK.init_meeting(**meeting_config)
        self.meeting.add_event_listener(MyMeetingEventHandler())

        try:
            await self.meeting.async_join()
            self.label_status.setText("Status: Joined")
            print("Joined successfully")
        except Exception as e:
            self.label_status.setText(f"Status: Error - {e}")
            print(f"Error while joining the meeting: {e}")
            return

        local_participant = self.meeting.local_participant
        print("Local participant:", local_participant.id, local_participant.display_name)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
