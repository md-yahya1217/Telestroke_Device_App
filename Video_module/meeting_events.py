from videosdk import Participant, MeetingEventHandler
# from participant_events import MyParticipantEventHandler
import cv2  # OpenCV library for capturing and displaying video
import asyncio
import os
from videosdk import MeetingConfig, VideoSDK
import dotenv


class MyMeetingEventHandler(MeetingEventHandler):
    def __init__(self):
        super().__init__()
        # self.app = app_instance  # Store the app instance to access and update the meeting state

    def on_error(self, data):
        print("Meeting Error: ", data)

    def on_meeting_joined(self, data):
        print(f"Meeting joined: {data}")

    def on_meeting_left(self, data: None):
        print(f"Meeting left from meeting events ")

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
        