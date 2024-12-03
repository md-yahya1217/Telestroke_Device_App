from videosdk import Participant, MeetingEventHandler
# from participant_events import MyParticipantEventHandler
import cv2  # OpenCV library for capturing and displaying video
import asyncio
import os
from videosdk import MeetingConfig, VideoSDK
import dotenv
dotenv.load_dotenv()

VIDEOSDK_TOKEN = os.getenv("VIDEOSDK_TOKEN")
MEETING_ID = os.getenv("MEETING_ID")
NAME = "Wajahat"


class MyMeetingEventHandler(MeetingEventHandler):
    def __init__(self):
        super().__init__()
        

    def on_error(self, data):
        print("Meeting Error: ", data)

    def on_meeting_joined(self, data):
        print("Meeting joined")
        # Capture video from the webcam
        # cap = cv2.VideoCapture(0)  # 0 is the default camera

        # if not cap.isOpened():
        #     print("Error: Could not open video device")
        #     return

        # while True:
        #     ret, frame = cap.read()
        #     if not ret:
        #         print("Error: Could not read frame")
        #         break

        #     # Display the resulting frame
        #     cv2.imshow('Webcam', frame)

        #     # Break the loop on 'q' key press
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break

        # # Release the capture when done
        # cap.release()
        # cv2.destroyAllWindows()

    def on_meeting_left(self, data):
        print("Meeting left")

    def on_participant_joined(self, participant: Participant):
        print("Participant joined:", participant.display_name)
        # participant.add_event_listener(
        #     MyParticipantEventHandler(participant_id=participant.id))

    def on_participant_left(self, participant):
        print("Participant left:", participant)

    def on_speaker_changed(self, data):
        print("Speaker changed:", data)

    def on_meeting_state_change(self, data):
        print("Meeting state changed:", data)
