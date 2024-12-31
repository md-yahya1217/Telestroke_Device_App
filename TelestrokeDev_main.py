import json
import cv2
import subprocess
import os, sys
from PyQt6 import QtWidgets, QtGui, QtCore, uic
from PyQt6.QtGui import QPixmap, QImage, QIntValidator, QDoubleValidator, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget, QGridLayout
from PIL import Image, ImageOps
import dotenv
import asyncio
import threading
import websocket
import logging
import time # Imported time lib recently
import subprocess
from videosdk import MeetingConfig, VideoSDK
from Video_module.customvideo_events import VideoFileTrack
from Video_module.webcam_feed import WebcamVideoTrack  # Import your webcam video track
from Video_module.meeting_events import MyMeetingEventHandler
from Video_module.websocket import WebSocketClient
from PyQt6.QtMultimedia import QMediaPlayer  # Import QMediaPlayer from PyQt6.QtMultimedia
from PyQt6.QtMultimediaWidgets import QVideoWidget  # Import QVideoWidget from PyQt6.QtMultimediaWidgets
from PyQt6.QtWidgets import QVBoxLayout  
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import Qt, QMetaObject, Q_ARG, QTimer
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import QStringListModel  # Import QStringListModel for QListView
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtGui import QPainter, QPainterPath
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtCore import QUrl
import requests
from datetime import datetime

base_path = ""
# base_path = sys._MEIPASS #For build purpose

#To build this code make sure all paths have "/" to change directory.

#self.button_A.setIcon(QIcon(base_path+"/rsc/rsc3.png"))
appointment_list = []
token_list = []
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(base_path+r'./telestroke_device.ui', self)

        ########################### TEST CODE BEGIN ###########################



        ########################### TEST CODE END ###########################
        
        # Create a layout to hold available network frames
        self.network_layout = QtWidgets.QVBoxLayout(self)  # Assuming you have a central layout for the widget
        self.network_frames = []  # List to hold QFrame references

        # Create a red dot QLabel for eye-tracking
        self.red_dot = QLabel(self)
        self.red_dot.setStyleSheet("background-color: red; border-radius: 75px;")
        self.red_dot.setFixedSize(150, 150) #Change from 70
        self.red_dot.hide()  # Initially hide the red dot
        self.join = False

        self.additional_windows_created = False  # Flag to prevent multiple window creation
        self.additional_window_1 = None  # Reference to the first additional window
        self.additional_window_2 = None  # Reference to the second additional window
        self.screen_number = 1
        self.meeting_id = None
        self.meeting = None
        self.token = None
        self.prev_scr = None
        # Initialize custom webcam video track
        # self.webcam_track = WebcamVideoTrack()
        self.webcam_track = None
        # self.current_screen = None  # Initialize current_screen

        # Initialize WebSocket client
        self.websocket_client = WebSocketClient("ws://192.168.0.189:3001", self.handle_command)
        self.websocket_client.run()

        # Example JSON data
        # self.json_data = [
        #     {"meetingId": "i4iu-856b-fihd", "AppointmentTime": "09:00 am", "AppointmentDate": "30th February, 2024", "DoctorName": "Dr. Raymond Reddington"},
        #     {"meetingId": "3fp5-l0ww-86lg", "AppointmentTime": "11:00 am", "AppointmentDate": "1st March, 2024", "DoctorName": "Dr. Liz Keen"}
        # ]

        
        self.listView.clicked.connect(lambda: self.on_network_double_clicked)
        self.listView_2.clicked.connect(self.handle_item_clicked)


        self.appointment_1.hide()

        # self.listView.clicked.connect(lambda: self.connect_to_network)
        self.available_network.hide()
    
        self.screen = 1
        self.handle_screen_change(1)
        

        self.btn_1.pressed.connect(lambda: self.handle_screen_change(3))
        # self.btn_2.pressed.connect(lambda: self.register_device())
        self.btn_6.pressed.connect(lambda: self.handle_screen_change(1))
        # self.btn_8.pressed.connect(lambda: self.update_ui_with_message(f"Fetching Appointments..{'\n'}Please wait"))
        self.btn_8.pressed.connect(lambda: self.handle_fetch_appointments())

        self.btn_11.pressed.connect(lambda: self.toggle_wifi())
        
        # self.btn_3.clicked.connect(lambda: asyncio.run_coroutine_threadsafe(self.leave_meeting()))

        self.pushButton_back.clicked.connect(lambda: self.handle_screen_change(1))
        # self.pushButton_2.clicked.connect(lambda: self.handle_screen_change(4))

        # self.handle_screen_change(6)
    
        
        # Start the asyncio event loop in a separate thread
        self.loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.start_event_loop, args=(self.loop,))
        t.start()

        self.btn_3.clicked.connect(lambda: self.leave_meeting())
        self.btn_7.clicked.connect(lambda: self.update_networks())

    def handle_fetch_appointments(self):
        # Update the UI with a message
        self.update_ui_with_message(f"Fetching Appointments..{'\n'}Please wait")
        # Introduce a delay before fetching appointments
        time.sleep(0.5)  # Delay for 3 seconds
        # Fetch the appointments
        self.fetch_appointments()

    def toggle_wifi(self):
        print(f"Toggle Wifi....... Self.prev_scr = {self.prev_scr}")
        if self.screen not in (6, 7):
            self.prev_scr = self.screen
            self.handle_screen_change(6)
        else:
            self.handle_screen_change(self.prev_scr)

    def handle_item_clicked(self, index):
        print("Clicked item index:", index.row())
        self.meeting_id = appointment_list[index.row()]
        print(token_list)
        self.token = token_list[index.row()]
        print(self.meeting_id)

        self.handle_screen_change(4)  

    def fetch_appointments(self):
        print("I've reached fetch_appointment")
        def background_fetch():
            print("I've reached fetch_appointment")
            max_retries = 3  # Maximum number of retries
            retry_delay = 2  # Delay in seconds between retries

            try:
                for attempt in range(max_retries):
                    try:
                        # Define the URL and parameters
                        url = 'http://192.168.0.189:5000/api/appointments'
                        params = {
                            'Dev_ID': 1000,  # Replace with the actual device ID
                            'status': 'Pending'  # Replace with the actual status value
                        }

                        # Send the GET request
                        response = requests.get(url, params=params, timeout=5)  # Add a timeout for the request

                        # Check the response status
                        if response.status_code == 200:
                            res = response.json()
                            self.update_ui_with_appointments(res)
                            return  # Exit after a successful response

                        else:
                            print(f"Attempt {attempt + 1}/{max_retries}: Server error with status code {response.status_code}")
                            self.update_ui_with_error(f"Retrying..{'\n'}Attempt: {attempt + 1}/{max_retries}")

                    except requests.exceptions.RequestException as e:
                        print(f"Attempt {attempt + 1}/{max_retries}: Error occurred: {e}")
                        self.update_ui_with_error(f"Retrying.. Attempt: {attempt + 1}/{max_retries}")

                    time.sleep(retry_delay)  # Wait before retrying

                # If all retries fail, update the UI with an error message
                self.update_ui_with_error(f"Cannot Fetch Appointments...{'\n'}Check your server or internet connection.")

            except Exception as e:
                # Handle unexpected exceptions
                self.update_ui_with_error(f"Unexpected Error: {e}")
                print(f"An unexpected error occurred: {e}")

        # Start the background thread
        threading.Thread(target=background_fetch, daemon=True).start()

    def update_ui_with_appointments(self, res):
        """Update the UI with appointment data on the main thread."""
        if res == []:
            self.label_22.show()
            self.label_22.setText(f"No Appointments Found.{'\n'}Kindly check with your Doctor.")
            self.listView_2.hide()
            return
        elif res:
            self.label_22.hide()
            self.listView_2.show()
            self.populate_appointments_in_listview(res)
            return

    def update_ui_with_error(self, error_message):
        """Update the UI with an error message on the main thread."""
        self.listView_2.hide()
        self.label_22.show()
        self.label_22.setStyleSheet("color: rgb(192, 28, 40);")
        self.label_22.setText(f"Error: {error_message}")

    def update_ui_with_message(self, message):
        """Update the UI with a general message on the main thread."""
        self.listView_2.hide()
        self.label_22.show()
        self.label_22.setStyleSheet("color: black;")
        self.label_22.setText(f"{message}")
        # return

    def get_wifi_ssids():
        try:
            # Run the nmcli command
            result = subprocess.run(['nmcli', 'dev', 'wifi'], stdout=subprocess.PIPE, text=True)
            
            # Split the output into lines
            lines = result.stdout.splitlines()
            
            # Extract SSIDs from the lines
            ssids = []
            for line in lines[1:]:  # Skip the header line
                parts = line.split()
                if len(parts) > 0:
                    ssid = " ".join(parts[0:-6])  # Adjust slicing based on your nmcli output
                    ssids.append(ssid.strip())
            
            return ssids
        
        except Exception as e:
            print(f"Error fetching Wi-Fi SSIDs: {e}")
            return []
        
    # def get_current_network():
    #     try:
    #         result = subprocess.run(['iwgetid', '-r'], stdout=subprocess.PIPE, text=True)
    #         return result.stdout.strip()  # Strip removes any trailing newline characters
    #  python    except Exception as e:
    #         print(f"Error fetching Current Wi-Fi Network: {e}")
    #         return None

    def play_video(self):
        # Logic to play video
        print("Playing video")

    def pause_video(self):
        # Logic to pause video
        print("Pausing video")
        

    def closeEvent(self, event):
        # Ensure WebSocketClient is stopped properly on window close
        if self.websocket_client:
            self.websocket_client.stop()
        super().closeEvent(event)
        
    def start_event_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()


    def join_meeting(self, token, meeting_id):
        """Modified to accept token and meeting ID."""
        print("ab yahan bhi pohnch gaye hain")
                
        print("MeetingID: ",meeting_id)
        # self.start_meeting(token, meeting_id)
        asyncio.run_coroutine_threadsafe(self.start_meeting(token, meeting_id), self.loop)

    # def leave_meeting(self):
    #     if self.meeting is None:
    #         print("No active meeting to leave.")
    #         return
    #     print(f"Meeting object: {self.meeting}")
    #     try:
    #         print("Attempting to leave the meeting...")
    #         self.meeting.leave()  # Ensure this is the correct async method to leave the meeting
    #         print("Meeting left successfully.")
    #         print(f"Meeting object: {self.meeting}")
    #         # self.handle_screen_change(3)
    #     except Exception as e:
    #         print(f"Error while leaving the meeting: {e}")
    #         self.meeting = None
    #         self.handle_screen_change(3)
    #     finally:
    #         self.meeting = None
    #         print(f"Meeting object: {self.meeting}")
    #         self.handle_screen_change(3)

    # def leave_meeting(self):
    #     try:
    #         print("Attempting to leave the meeting...")
    #         if self.meeting:
    #             # Call the synchronous leave method
    #             self.meeting.leave()
    #             # self.meeting.end()
    #             print("Meeting left successfully.")
    #             print(f"Before cleanup: {self.meeting}")
    #             self.meeting.remove_all_listeners()  # Clear the meeting reference after leaving
    #             # self.meeting = None
    #             print(f"After cleanup: {self.meeting}")
    #         else:
    #             print("No active meeting to leave.")
    #         self.handle_screen_change(3)  # Navigate to the desired screen
    #     except Exception as e:
    #         print(f"Error while leaving the meeting: {e}")



    def leave_meeting(self):
            self.webcam_track = None
            asyncio.run_coroutine_threadsafe(self.leave_meeting_sdk(), self.loop)
            print("I'm leaving the meeting..")
            # self.meeting.end()
            self.handle_screen_change(3)

    async def leave_meeting_sdk(self):
        # try:
            # Ensure `self.meeting` exists and leave the meeting
        if self.meeting:
            meet = self.meeting
            print(meet.listeners)

            print(f"Meeting Info from leave: {meet}")
            # self.meeting.disable_webcam()
            self.meeting.release()
            # self.meeting.disable_mic()
            await self.meeting.leave()  # Use `async_leave()` if provided by VideoSDK
            # self.meeting = None
            await self.webcam_track.stop()
            await self.webcam_track.cap.release()
            self.webcam_track = None
            # self.webcam_track = WebcamVideoTrack()
            # self.join = False
            print("Successfully left the meeting.")
            return
        else:
            print("No active meeting to leave.")
        # except Exception as e:
        #     self.meeting = None
        #     print(f"Error while leaving the meeting: {e}")

    # Call this method in the appropriate event loop
    # def leave_meeting_safe(self):
    #     asyncio.run_coroutine_threadsafe(self.leave_meeting(), self.loop)
    #     print("Initiated leave meeting...")
    #     self.handle_screen_change(3)

    async def end_meeting(self):

        self.meeting.leave()
        # print("im here also")
        self.join = False
        self.handle_screen_change(3)


    # async def start_meeting(self):
        
    #     if self.join == False:
    #         self.join = True
    #         dotenv.load_dotenv()
    #         # self.webcam_track = WebcamVideoTrack()

    #         VIDEOSDK_TOKEN = os.getenv("VIDEOSDK_TOKEN")
    #         MEETING_ID = os.getenv("MEETING_ID")
    #         NAME = "Wajahat"
            

    #         meeting_config = MeetingConfig(
    #             meeting_id=MEETING_ID,
    #             name=NAME,
    #             mic_enabled=True,
    #             token=VIDEOSDK_TOKEN,
    #             custom_camera_video_track=self.webcam_track
    #         )

    #         self.meeting = VideoSDK.init_meeting(**meeting_config)
    #         self.meeting.add_event_listener(MyMeetingEventHandler())

    #         try:
    #             await self.meeting.async_join()
    #             print("Joined successfully")
    #             # Assuming you have a `meeting` object initialized and joined
    #             participants = self.meeting.participants

    #             # Check the number of participants
    #             total_participants = len(participants)
    #             print(f"Total number of participants: {total_participants}")
                
    #         except Exception as e:
    #             print(f"Error while joining the meeting: {e}")
    #             return

    #         local_participant = self.meeting.local_participant
    #         print("Local participant:", local_participant.id, local_participant.display_name)

    #     else:
    #         print("No need")
    #         # self.handle_screen_change(4)

    def get_token(self):
        try:
            # Constructing the URL using an environment variable
            backend_url = "http://192.168.0.189:5000"

            url = f"{backend_url}/get-token"
            response = requests.get(url)
            print(f"Received Token: ${response}")
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Extracting the token from the JSON response
            data = response.json()
            token = data.get("token")
            print("Token received:", token)
            return token
        except requests.exceptions.RequestException as e:
            print("Error fetching token:", e)
            return None
        except ValueError as e:
            print("Error:", e)
            return None

    async def start_meeting(self, token, meeting_id):
        try:
            if not self.join:  # Join only if not already joined
                self.join = True
                # self.webcam_track = WebcamVideoTrack()


            if self.webcam_track is None:
                print(f"Self.webcam_track: {self.webcam_track}")
                self.webcam_track = WebcamVideoTrack()

            print(f"webcam track: {self.webcam_track}")

            VIDEOSDK_TOKEN = self.get_token()
            MEETING_ID = meeting_id
            NAME = "Anonymous"

            # self.meeting = None
            print(f"Meeting: {self.meeting}")

            # Reinitialize the meeting object
            meeting_config = MeetingConfig(
                meeting_id=MEETING_ID,
                name=NAME,
                mic_enabled=True,
                token=VIDEOSDK_TOKEN,
                custom_camera_video_track=self.webcam_track
            )

                # speaker_enable = True,
            print(f"Meeting: {self.meeting}")

            self.meeting = VideoSDK.init_meeting(**meeting_config)
            self.meeting.add_event_listener(MyMeetingEventHandler())

            await self.meeting.async_join()
            print("Joined successfully")
        
        except Exception as e:
            print(f"Error while joining the meeting: {e}")
            self.meeting = None  # Reset meeting object on failure
            self.join = False

    # async def start_meeting(self, token, meeting_id):
    #     try:
    #         if not self.join:  # Join only if not already joined
    #             self.join = True

    #         VIDEOSDK_TOKEN = self.get_token()
    #         MEETING_ID = meeting_id
    #         NAME = "Anonymous"

    #         # self.meeting = None
    #         print(f"Meeting: {self.meeting}")

    #         # Reinitialize the meeting object
    #         meeting_config = MeetingConfig(
    #             meeting_id=MEETING_ID,
    #             name=NAME,
    #             mic_enabled=True,
    #             token=VIDEOSDK_TOKEN,
    #             custom_camera_video_track=self.webcam_track
    #         )

    #             # speaker_enable = True,
    #         print(f"Meeting: {self.meeting}")

    #         self.meeting = VideoSDK.init_meeting(**meeting_config)
    #         self.meeting.add_event_listener(MyMeetingEventHandler())

    #         await self.meeting.async_join()
    #         print("Joined successfully")
        
    #     except Exception as e:
    #         print(f"Error while joining the meeting: {e}")
    #         self.meeting = None  # Reset meeting object on failure
    #         self.join = False

    # async def start_meeting(self, token, meeting_id):
    #     if self.join == False:
    #         self.join = True
    #         dotenv.load_dotenv()

    #         VIDEOSDK_TOKEN = self.get_token()  # Use the token passed from the selected appointment
    #         MEETING_ID = meeting_id  # Use the meeting ID passed from the selected appointment
    #         NAME = "Anonymous"

    #         meeting_config = MeetingConfig(
    #             meeting_id=MEETING_ID,
    #             name=NAME,
    #             mic_enabled=True,
    #             token=VIDEOSDK_TOKEN,
    #             custom_camera_video_track=self.webcam_track
    #         )

    #         self.meeting = VideoSDK.init_meeting(**meeting_config)
    #         self.meeting.add_event_listener(MyMeetingEventHandler())

    #         try:
    #             await self.meeting.async_join()
    #             print("Joined successfully")
    #             participants = self.meeting.participants

    #             # Check the number of participants
    #             total_participants = len(participants)
    #             print(f"Total number of participants: {total_participants}")
                
    #         except Exception as e:
    #             print(f"Error while joining the meeting: {e}")
    #             return

    #         local_participant = self.meeting.local_participant
    #         print("Local participant:", local_participant.id, local_participant.display_name)

    #     else:
    #         print("No need")    

    def process_command_on_window(self, window, command):
        if command['stop'] == False:
            window.play_video()
        elif command.get('command') == 'pause':
            window.pause_video()
        elif command['stop'] == True:
            window.pause_video()
        elif command.get('command') == 'speed':
            window.set_speed(command.get('rate'))


    def handle_command(self, command):
        print('Im in handle_cmd of WS')
        print(command['exam_mode'])
        screen = command['eye_camera_control']
        self.additional_window_1.show()
        if screen == 'left':
                # self.screen_number = 1
                self.webcam_track.set_screen_number(2)  # Update the webcam feed to show the left half
                # Optional: You can bring the window to the front or set focus if needed
                # self.additional_window_2.hide()
        elif screen == 'right':
                # self.screen_number = 1
                # Optional: You can bring the window to the front or set focus if needed
                self.webcam_track.set_screen_number(1)  # Update the webcam feed to show the right half
                # self.additional_window_1.show()
                # self.additional_window_2.show()
        if command['exam_mode'] == 'Quadrant':
            if 'x' in command['coordinates'] and 'y' in command['coordinates']:
                x = command['coordinates'].get('x')
                y = command['coordinates'].get('y')
                print("x = ",x,"y = ",y)
                if self.screen_number == 1:
                    QMetaObject.invokeMethod(self.additional_window_1, "move_red_dot", Qt.ConnectionType.QueuedConnection, Q_ARG(int, x), Q_ARG(int, y))
        #         elif self.screen_number == 2:
        #             QMetaObject.invokeMethod(self.additional_window_2, "move_red_dot", Qt.ConnectionType.QueuedConnection, Q_ARG(int, x), Q_ARG(int, y))
        elif command['exam_mode'] == 'CenterFocus':
            video_id = command['stimulus_type']
            # if self.screen_number == 1:
            self.additional_window_1.load_video_by_id(video_id)
            print("iM HERE")
            self.process_command_on_window(self.additional_window_1, command)
            # else:
            #     self.additional_window_2.load_video_by_id(video_id) 
            #     self.process_command_on_window(self.additional_window_2, command)

               
    def handle_screen_change(self, value):
        # if self.screen == value:  # Avoid unnecessary changes
        #     return

        self.screen = value
        self.icon_wifi.show()
        self.icon_battery.show()
        self.top_bar.show()


        if self.screen == 1:
            self.screen_1.show()
            self.screen_2.hide()
            self.screen_3.hide()
            self.screen_4.hide()
            self.screen_5.hide()
            self.screen_6.hide()
            self.screen_7.hide()
            # self.init_screen6()

        elif self.screen == 2:
            self.screen_1.hide()
            self.screen_2.show()
            self.screen_3.hide()
            self.screen_4.hide()
            self.screen_5.hide()
            self.screen_6.hide()
            self.screen_7.hide()
            self.init_screen2()

        elif self.screen == 3:
            self.screen_3.show()
            self.screen_1.hide()
            self.screen_2.hide()
            self.screen_4.hide()
            self.screen_5.hide()
            self.screen_6.hide()
            self.screen_7.hide()
            self.init_screen3()

        elif self.screen == 4:
                
            if self.meeting_id and self.token:
                # Call join_meeting with the stored meeting_id and token
                print("yahan pohnch gaye hain")
                self.join_meeting(self.token, self.meeting_id)

            # if not self.additional_windows_created:
            #     self.create_two_additional_windows()
            #     self.additional_windows_created = True
            self.screen_4.show()
            self.screen_3.hide()
            self.screen_1.hide()
            self.screen_2.hide()
            self.screen_5.hide()
            self.screen_6.hide()
            self.screen_7.hide()
            self.init_screen4()

        elif self.screen == 6:
            self.screen_3.hide()
            self.screen_1.hide()
            self.screen_2.hide()
            self.screen_4.hide()
            self.screen_5.hide()
            self.screen_6.show()
            self.screen_7.hide()
            self.init_screen6()

        elif self.screen == 7:
            self.screen_1.hide()
            self.screen_2.hide()
            self.screen_3.hide()
            self.screen_4.hide()
            self.screen_5.hide()
            self.screen_6.hide()
            self.screen_7.show()
            self.init_screen7()

    def init_screen2(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(13, 30, 91, 160))
        self.btn_2.setGraphicsEffect(shadow)
        print("Im screen 2")
        self.label_20.hide()

    # def register_device(self):
    #     patientid = self.lineEdit.text()
    #     print(f"Patient ID Entered: {patientid}")

    #     # The URL of the API endpoint
    #     url = 'http://192.168.0.192:5000/api/device_registration'

    #     # The data to be sent in the POST request
    #     data = {
    #         'ID': patientid,
    #         'DeviceID': 1007
    #     }

    #     try:
    #         # Sending the POST request
    #         response = requests.post(url, json=data)

    #         # Handle the response based on status code
    #         if response.status_code == 200:
    #             result = response.json()
    #             if result.get('message') == 'Successful':
    #                 self.label_20.hide()  # Hide the error label if it was shown previously
    #                 self.handle_screen_change(3)  # Assuming this changes to the next screen
    #             else:
    #                 self.label_20.show()
    #                 self.label_20.setText("Unexpected success response.")
    #                 self.label_20.setStyleSheet("color:red;")

    #         elif response.status_code == 400:
    #             result = response.json()
    #             if result.get('error') == 'ID and Device ID are required.':
    #                 self.label_20.show()
    #                 self.label_20.setText("Error: ID and Device ID are required.")
    #                 self.label_20.setStyleSheet("color:red;")

    #         elif response.status_code == 404:
    #             result = response.json()
    #             if result.get('error') == 'No such ID':
    #                 self.label_20.show()
    #                 self.label_20.setText("Error: No patient found with the provided ID.")
    #                 self.label_20.setStyleSheet("color:red;")

    #         elif response.status_code == 500:
    #             result = response.json()
    #             if result.get('error') == 'An error occurred while updating DeviceID.':
    #                 self.label_20.show()
    #                 self.label_20.setText("Error: Internal server error.")
    #                 self.label_20.setStyleSheet("color:red;")
    #             else:
    #                 self.label_20.show()
    #                 self.label_20.setText("Unexpected server error.")
    #                 self.label_20.setStyleSheet("color:red;")

    #         else:
    #             self.label_20.show()
    #             self.label_20.setText(f"Unexpected status code {response.status_code}: {response.text}")
    #             self.label_20.setStyleSheet("color:red;")

    #     except requests.exceptions.RequestException as e:
    #         # Handle exceptions like connection errors
    #         self.label_20.show()
    #         self.label_20.setText(f"Request failed: {e}")
    #         self.label_20.setStyleSheet("color:red;")

    #     # If no Patient ID was entered
    #     if not patientid:
    #         self.label_20.show()
    #         self.label_20.setText("Error: Patient ID not Entered!")
    #         self.label_20.setStyleSheet("color:red;")
    #     self.handle_screen_change(3)

    def show_keyboard(self, event):
        self.keyboard.show()
        return super().focusInEvent(event)


    def init_screen3(self):
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(60)
        shadow1.setOffset(0, 10)
        self.appointment_1.setGraphicsEffect(shadow1)
        self.label_22.hide()
        self.listView_2.hide()
        # self.populate_appointments_in_listview(self.json_data)

        self.pushButton_2.clicked.connect(lambda: self.handle_screen_change(4))

    def init_screen4(self):
        # # Additional initialization logic for screen 4 (if any)
        # model = self.listView_2.model()
        # network = model.itemFromIndex(index).data(QtCore.Qt.UserRole)  # Retrieve the network data
        if not self.additional_windows_created:
                self.create_two_additional_windows()
                self.additional_windows_created = True
        # self.join_meeting()
        pass

    def populate_appointments_in_listview(self, appointments):
        model = QtGui.QStandardItemModel()

        for appointment in appointments:
            item = QtGui.QStandardItem()
            item.setData(appointment, QtCore.Qt.ItemDataRole.UserRole)  # Storing appointment data
            model.appendRow(item)

        self.listView_2.setModel(model)
        self.listView_2.setItemDelegate(AppointmentDelegate(self.listView_2))

        # Connect double-click signal to the handler
        # self.listView_2.Clicked.connect(self.handle_item_double_click)
        
    def handle_item_double_click(self, index):
        # Retrieve the appointment data from the clicked item
        model = self.listView_2.model()
        appointment = model.itemFromIndex(index).data(QtCore.Qt.ItemDataRole.UserRole)

        # Get the meeting_id and token from the appointment data
        meeting_id = appointment.get('meetingId')  # Ensure 'meetingId' exists in the appointment data
        token = appointment.get('token')  # Ensure 'token' exists in the appointment data

        # Call join_meeting with the relevant information
        if meeting_id and token:
            self.join_meeting(meeting_id, token)
        else:
            print("Meeting ID or token missing.")


    def scan_networks(self):
        print("Inside scan_networks")
        # Start scanning networks
        self.update_current_network_info()

        # Simulate scanning delay using a singleShot timer
        QtCore.QTimer.singleShot(2500, self.update_networks)
        return

    # def scan_networks(self):
    #     print("Inside scan_networks")
    #     # Start scanning networks
    #     self.interface.scan()  # Start scanning
    #     self.update_current_network_info()
    #     QtCore.QTimer.singleShot(2500, self.update_networks)  # Wait for results

    #     return

    # def update_networks(self):
    #     try:
    #         # self.interface.scan()  # Start the scan
    #         results = self.interface.scan_results()  # Get scan results
            
    #         if results is None:
    #             print("No scan results found.")
    #             return
            
    #         print("Inside update_networks: ", results)
    #         print("Number of networks found: ", len(results))  # Check the number of networks

    #         # Check if the model exists, and clear it if so
    #         model = self.listView.model()
    #         if model is None:
    #             model = QtGui.QStandardItemModel()  # Initialize a new model if none exists
    #             self.listView.setModel(model)
    #         else:
    #             model.clear()  # Clear the model before re-populating
            
    #         # Populate the QListView with scanned networks
    #         self.populate_networks_in_listview(results)

    #     except Exception as e:
    #         print(f"Error during network scanning: {e}").

    def update_networks(self):
        try:
            # Fetch network scan results using the subprocess-based function
            results = self.get_wifi_info()  # Replace with your updated function
            current_network = self.get_current_network()
            self.label_17.setText(current_network)
            if not results:
                print("No scan results found.")
                return

            print("Inside update_networks: ", results)
            print("Number of networks found: ", len(results))

            # Check if the model exists, and clear it if so
            model = self.listView.model()
            if model is None:
                model = QtGui.QStandardItemModel()  # Initialize a new model if none exists
                self.listView.setModel(model)
            else:
                model.clear()  # Clear the model before re-populating

            # Populate the QListView with scanned networks
            self.populate_networks_in_listview(results)

        except Exception as e:
            print(f"Error during network scanning: {e}")

    def on_network_double_clicked(self, index):
        print("Double Clicked Function Triggered!!!")
        model = self.listView.model()
        network = model.itemFromIndex(index).data(QtCore.Qt.UserRole)  # Retrieve the network data
        
        # Trigger the connection process (or prompt screen_7 for secured network)
        self.connect_to_network(network)  # Ensure this triggers the right function


    def clear_network_frames(self):
        for frame in self.network_frames:
            frame.deleteLater()  # Remove the frame from the layout
        self.network_frames.clear()  # Clear the list

    # def get_current_network(self):
        # Check if the interface is connected
        # print(f"Interface status: {self.iface.status()}")
        # if self.iface.status() == 4:
            # Get the current network profile from the connected networks
            # profiles = self.iface.network_profiles()  # Get saved profiles
            # print(f"Profiles found: {len(profiles)}")
            
            # for profile in profiles:
                # Check if the profile is active and has a valid BSSID
                # if profile.ssid is not None:
                #     print(f"Connected to: {profile.ssid}")
                #     return profile.ssid  # Return the SSID of the connected network

        print("Interface is not connected or no valid profiles found.")
        return None  # Return None if no network connected

    def populate_networks_in_listview(self, networks):
        # Create a standard item model
        model = QtGui.QStandardItemModel()

        # Populate the model with networks
        for network in networks:
            item = QtGui.QStandardItem()
            item.setData(network, QtCore.Qt.ItemDataRole.UserRole)  # Store the network object in UserRole
            model.appendRow(item)

        # Set the model in the QListView
        self.listView.setModel(model)

        # Use the custom delegate to display network information
        delegate = NetworkDelegate(self.listView)
        self.listView.setItemDelegate(delegate)

    def get_wifi_info(self):
        try:
            # Run the nmcli command to list available Wi-Fi networks
            result = subprocess.run(['nmcli', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi'], stdout=subprocess.PIPE, text=True)

            # Split the output into lines
            lines = result.stdout.splitlines()

            # Extract SSID, Signal Strength, and Security from the lines
            wifi_networks = []
            for line in lines[1:]:  # Skip the header line
                parts = line.split()

                if len(parts) >= 3:  # Ensure the line has at least SSID, SIGNAL, and SECURITY
                    # Dynamically find the signal strength column by checking for valid percentage values
                    signal_index = next((i for i, p in enumerate(parts) if p.isdigit() and 0 <= int(p) <= 100), None)

                    if signal_index is not None:
                        ssid = " ".join(parts[:signal_index]).strip()
                        signal_strength = parts[signal_index]
                        security = " ".join(parts[signal_index + 1:]).strip() or "OPEN"

                        wifi_networks.append({
                            'ssid': ssid,
                            'signal': signal_strength,
                            'security': security,
                        })

            return wifi_networks

        except Exception as e:
            print(f"Error fetching Wi-Fi networks: {e}")
            return []

    def get_current_network(self):
        try:
            # Use iwgetid to get the current connected network's SSID
            result = subprocess.run(['iwgetid', '-r'], stdout=subprocess.PIPE, text=True)
            # current_network = self.get_current_network()
            self.label_17.setText(result.stdout.strip())
            return result.stdout.strip()  # Strip removes any trailing newline characters
        except Exception as e:
            print(f"Error fetching current Wi-Fi network: {e}")
            return None
        
    # def on_network_double_clicked(self, index):
    #     print("Double Clicked Function Triggered!!!")
    #     model = self.listView.model()
    #     network = model.itemFromIndex(index).data(QtCore.Qt.ItemDataRole.UserRole)  # Retrieve the network data

    #     # Check if the network is secured
    #     secured_akm_types = [const.AKM_TYPE_WPA, const.AKM_TYPE_WPA2, const.AKM_TYPE_WPA2PSK]
    #     is_secured = network.akm and any(akm in secured_akm_types for akm in network.akm)

    #     if is_secured:
    #         # Show screen_7 if the network is secured
            
    #         print(f"Switched to screen_7 for secured network: {network.ssid} Type of network: {type(network)}")
    #         self.selectedNetwork = network
    #         self.handle_screen_change(7)
    #     else:
    #         # Connect to open network or handle it accordingly
    #         self.connect_to_open_network(network)

    def on_network_double_clicked(self, index):
        print("Double Clicked Function Triggered!!!")
        model = self.listView.model()
        network = model.itemFromIndex(index).data(QtCore.Qt.ItemDataRole.UserRole)  # Retrieve the network data

        # Check if the network is secured
        is_secured = network.get("security", "Open") != "--"

        if is_secured:
            print(f"Switched to screen_7 for secured network: {network.get('ssid')} Type of network: {type(network)}")
            print(f"Network object: {network}")
            self.selectedNetwork = network
            self.handle_screen_change(7)
        else:
            self.connect_to_open_network(network)




    # def connect_to_secured_network(self, network, password):
    #     print(f"Entered Password in Secured Network Function: {password}")
    #     profile = Profile()

    #     if not hasattr(network, 'ssid'):
    #         print("Invalid network object; it does not have an SSID.")
    #         return

    #     profile.ssid = network.ssid
    #     profile.akm.append(const.AKM_TYPE_WPA2PSK)
    #     profile.cipher = const.CIPHER_TYPE_CCMP
    #     profile.auth = const.AUTH_ALG_OPEN
    #     profile.key = password  # Use the entered password

    #     try:
    #         self.interface.remove_all_network_profiles()
    #         self.interface.add_network_profile(profile)
    #         self.interface.connect(profile)

    #         # Wait for a few seconds to allow connection to establish
    #         print("Connecting...")
    #         time.sleep(5)  # Adjust the delay as needed

    #         # Check the status after a delay
    #         status = self.interface.status()
    #         print(f"Status after waiting: {status}")

    #         if status == const.IFACE_CONNECTED:
    #             print(f"Successfully connected to {profile.ssid}")
    #         else:
    #             print("Failed to connect, interface status is not connected.")

    #     except Exception as e:
    #         print(f"An error occurred while connecting: {e}")

    #     self.update_current_network_info()
    #     self.handle_screen_change(6)

    def check_os_connection(self):
        """ Check if the OS reports a connection to the network. """
        try:
            output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
            return "State" in output and "connected" in output.lower()
        except Exception as e:
            print(f"Error checking OS connection: {e}")
            return False

    def connect_to_secured_network(self, network, password):
        print(f"Entered Password in Secured Network Function: {password}")

        # Validate the network object
        ssid = network.get("ssid")
        if not ssid:
            print("Invalid network object; it does not have an SSID.")
            self.label_19.setText("Connection Failed: Invalid Network")
            return

        try:
            self.label_19.setText("Connecting...")

            print("Connecting to a network..")
            # Construct the command to connect to the network
            connect_command = [
                "nmcli", "dev", "wifi", "connect", ssid, "password", password
            ]
            print(f"Running command: {' '.join(connect_command)}")
            
            # Execute the connection command
            result = subprocess.run(
                connect_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check the result of the command
            if result.returncode == 0:
                print(f"Successfully connected to {ssid}")
                self.label_19.setText(f"Connected to {ssid}")
                # Update network info and switch back to the previous screen
                current_network = self.get_current_network()
                self.label_17.setText(current_network)
                self.handle_screen_change(6)
            else:
                print(f"Failed to connect: {result.stderr}")
                self.label_19.setText(f"Connection Failed: {result.stderr}")

        except Exception as e:
            print(f"An error occurred while connecting: {e}")
            self.label_19.setText("Connection Error")


    def connect_to_open_network(self, network):
        """
        Connect to an open Wi-Fi network.
        :param network: Dictionary containing network details (e.g., SSID)
        """
        try:
            # Get the SSID from the network dictionary
            ssid = network.get('ssid', 'Unknown Network')

            if not ssid:
                print("Error: SSID is required to connect to a network.")
                return

            print(f"Connecting to open network: {ssid}")
            
            # Run the nmcli command to connect to the open network
            result = subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Check the result of the command
            if result.returncode == 0:
                print(f"Successfully connected to open network: {ssid}")
            else:
                print(f"Failed to connect to open network: {ssid}")
                print(f"Error: {result.stderr}")
        except Exception as e:
            print(f"An error occurred while connecting to the open network: {e}")


    def init_screen6(self):
        
        current_network = self.get_current_network()
        self.label_17.setText(current_network)

        # Initialize the listView model if it's not already set
        if self.listView.model() is None:
            self.listView.setModel(QtGui.QStandardItemModel())
        
        self.listView.doubleClicked.connect(self.on_network_double_clicked)


    def init_screen7(self): 
        # Navigate back to screen 6 when btn_9 is clicked
        self.btn_9.clicked.connect(lambda: self.handle_screen_change(6))
        
        # Get the SSID and security type from the selected network
        ssid = self.selectedNetwork.get('ssid', 'Unknown Network')
        security = self.selectedNetwork.get('security', 'Open')

        if security == '--':
            # Directly connect to the open network
            self.connect_to_open_network(self.selectedNetwork)
            return
        else:
            # Update the label to prompt for a password
            self.label_19.setText(f"Enter Password for {ssid}")
            
            # Connect to the secured network when btn_10 is clicked
            self.btn_10.pressed.connect(lambda: self.connect_to_secured_network(self.selectedNetwork, self.lineEdit_2.text()))


    def play_video_on_screen(self, screen_number, video_path):
        try:
            self.screen_number = screen_number
            if screen_number == 1:
                if self.additional_window_2:
                    self.additional_window_2.close()  # Close the right window
                if not self.additional_window_1:
                    self.additional_window_1 = AdditionalScreen()  # Create the left window if not already created
                self.additional_window_1.show()
                self.additional_window_1.load_video(video_path)  # Load video without playing
            elif screen_number == 2:
                if self.additional_window_1:
                    self.additional_window_1.close()  # Close the left window
                if not self.additional_window_2:
                    self.additional_window_2 = AdditionalScreen()  # Create the right window if not already created
                self.additional_window_2.show()
                self.additional_window_2.load_video(video_path)  # Load video without playing
        except Exception as e:
            print(f"Error playing video on screen {screen_number}: {e}")


    # def create_two_additional_windows(self):
    #     self.additional_window_1 = AdditionalScreen()  # Store reference to avoid garbage collection
    #     self.additional_window_1.show()

    #     self.additional_window_2 = AdditionalScreen()  # Store reference to avoid garbage collection
    #     self.additional_window_2.show()

    def create_two_additional_windows(self):
        # screen_count = QApplication.desktop().screenCount()
        # app = QtWidgets.QApplication(sys.argv)

        # if screen_count < 2:
        #     print("At least 2 screens are required.")
        #     return

        # screens = app.screens()

        # Choose the second screen (index 1, as index 0 is the primary screen)
        # second_screen = screens[1]
        # Create and show additional windows
        screens = QGuiApplication.screens()
        # Create and show additional windows
        self.additional_window_1 = AdditionalScreen()
        # self.additional_window_2 = AdditionalScreen()

        # Get the geometry of the first and second screens
        # screen_geometry_1 = screens[0].geometry()  # Geometry of the primary screen
        # screen_geometry_2 = screens[0].geometry()  # Geometry of the second screen
        # Iterate over the screens to find the one with the resolution 1024x768
        target_screen = None
        for screen in screens:
            size = screen.size()
            if size.width() == 2880 and size.height() == 1440:
                target_screen = screen
                print("Resolution of 2880x1440 screen found")
                break
        
        if target_screen:
            # Set the window to open on the target screen
            screen_geometry = target_screen.geometry()
            self.additional_window_1.setGeometry(screen_geometry)
            # self.additional_window_1.setGeometry(screen_geometry.left(), screen_geometry.top(), 2880, 1440)
        else:
            print("No screen with resolution 1440X2880 found.")

        # Set geometry for each additional window
        # self.additional_window_1.setGeometry(screen_geometry_1)
        # self.additional_window_1.setGeometry(500, 0, 1920, 1080)


        self.additional_window_1.showFullScreen()
        # self.additional_window_2.show()

class AdditionalScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(AdditionalScreen, self).__init__()
        self.setFixedSize(2880, 1440)
        self.setWindowTitle("Stimulus Screen")

        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # self.move(1920, 0)

        # Video display label
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.video_label)

        # Initialize video list
        self.video_mapping = {
            '1': base_path + r"./rsc/Video1.mp4",
            '2': base_path + r"./rsc/Video2.mp4",
            # Add more mappings as needed
        }
        self.current_video_index = 0

        # Control buttons
        # self.play_button = QPushButton("Play")
        # self.play_button.clicked.connect(self.play_video)
        # self.layout.addWidget(self.play_button)

        # self.next_button = QPushButton("Next Video")
        # self.next_button.clicked.connect(self.play_next_video)
        # self.layout.addWidget(self.next_button)

        # Timer for updating the video frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # Initialize OpenCV VideoCapture object
        self.cap = None

        # Set up the red dot for eye-tracking stimulus
        self.red_dot = QLabel(self)
        self.red_dot.setStyleSheet("background-color: red; border-radius: 75px;")
        self.red_dot.setFixedSize(150, 150)
        self.red_dot.hide()  # Initially hide the red dot

        self.is_paused = False
        self.playback_speed = 1.0  # Default playback speed (medium)

    def load_video_by_id(self, video_id):
        video_path = self.video_mapping.get(video_id)
        if video_path:
            self.red_dot.hide()
            self.central_widget.show()  
            self.load_video(video_path)
        else:
            print(f"No video found for ID: {video_id}")

    def load_video(self, video_path=None):
        # Load the video using OpenCV (no QMediaPlayer)
        if video_path:
            print("Loading video:", video_path)
            self.cap = cv2.VideoCapture(video_path)

            if not self.cap.isOpened():
                print("Error: Could not open video.")
                return

            # self.timer.start(30)  # Update the frame every 30 ms

    def pause_video(self):
        """Pause the video."""
        if not self.is_paused and self.cap:
            self.is_paused = True
            # self.current_frame_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            print(f"Video paused at frame {self.current_frame_pos}")

            # Safely stop the timer
            if self.timer.isActive():
                # self.timer.stop()
                QMetaObject.invokeMethod(self.timer, "stop", Qt.ConnectionType.QueuedConnection)


    def play_video(self):
        """Resume or start the video."""
        if self.cap is None:
            print("Error: No video loaded.")
            return

        if self.is_paused:
            print("Resuming video...")

            # Use QMetaObject to safely start the timer
            self.cap.set(self.current_frame_pos)  # Resume from saved position
            QMetaObject.invokeMethod(self.timer, "start", Qt.ConnectionType.QueuedConnection, Q_ARG(int, self.playback_speed))

            self.is_paused = False
        else:
            print("Starting video playback...")

            # Don't reload video if already loaded
            if self.cap is None or not self.cap.isOpened():
                self.load_video(self.current_video_index)  # Start the video from the beginning if not loaded
            else:
                # Start the timer to update frames if the video is already loaded
                # self.timer.start(self.playback_speed)
                QMetaObject.invokeMethod(self.timer, "start", Qt.ConnectionType.QueuedConnection, Q_ARG(int, self.playback_speed))

    def set_speed(self, speed):
        """Set playback speed. 'slow', 'medium', and 'high'."""
        if speed == "slow":
            self.playback_speed = 0.5
            print("Playback speed set to slow (0.5x)")
        elif speed == "medium":
            self.playback_speed = 1.0
            print("Playback speed set to medium (1.0x)")
        elif speed == "high":
            self.playback_speed = 2.0
            print("Playback speed set to high (2.0x)")
        else:
            print("Error: Invalid speed. Choose from 'slow', 'medium', or 'high'.")
            
    def play_next_video(self):
        self.current_video_index += 1
        if self.current_video_index >= len(self.video_mapping):
            self.current_video_index = 0
        self.play_video()

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
            # else:
            #     self.cap.release()
            #     self.timer.stop()
    
    @pyqtSlot(int, int)
    def move_red_dot(self, x, y):
        print(f"Received coordinates: x={x}, y={y}")  # Debugging line

        x_pos = max(0, min(x, self.width() - self.red_dot.width()))
        y_pos = max(0, min(y, self.height() - self.red_dot.height()))
        
        print(f"Calculated position: x={x_pos}, y={y_pos}")  # Debugging line
        
        self.red_dot.move(x_pos, y_pos)
        self.red_dot.show()
        self.central_widget.hide()

    def populate_appointments_in_listview(self, appointments):
        # Create a standard item model
        model = QtGui.QStandardItemModel()

        # Populate the model with appointments
        for appointment in appointments:
            item = QtGui.QStandardItem()
            item.setData(appointment, QtCore.Qt.UserRole)  # Store the appointment object in UserRole
            model.appendRow(item)

        # Set the model in the QListView
        self.listView_2.setModel(model)

        # Use the custom delegate to display appointment information
        delegate = AppointmentDelegate(self.listView_2)
        self.listView_2.setItemDelegate(delegate)


class NetworkDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Start by calling the parent paint method
        super().paint(painter, option, index)
        
        # Fetch the network data
        network = index.data(Qt.ItemDataRole.UserRole)

        # Ensure that 'network' is a dictionary with the expected keys
        if isinstance(network, dict):
            ssid = network.get('ssid', 'Unknown SSID')
            signal_strength = network.get('signal')
            security_status = network.get('security', 'Open')

            if security_status != '--':
                security_status = 'Secured'
            else:
                security_status = 'Open'

            # Check if signal_strength is a valid number (integer) for signal strength
            try:
                signal_strength_int = int(signal_strength)
                if signal_strength_int > 50:
                    signal_strength = "Excellent"
                elif signal_strength_int > 70:
                    signal_strength = "Good"
                else:
                    signal_strength = "Weak"
            except ValueError:
                # If signal_strength is not a valid integer (e.g., 'WPA1' security type), handle it as 'Unknown'
                signal_strength = "Normal"

            # Set up painting
            painter.save()
            rect = option.rect

            # Define bottom margin
            bottom_margin = 7  # Margin at the bottom
            adjusted_rect = QtCore.QRect(rect.x(), rect.y(), rect.width(), rect.height() - bottom_margin)

            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))  # White background
            painter.setPen(QtCore.Qt.PenStyle.NoPen)  # Set no pen to avoid borders
            painter.drawRoundedRect(adjusted_rect, 30, 30)  # Rounded corners

            # Set up icon position and size
            icon_rect = QtCore.QRect(rect.x() + 25, rect.y() + 20, 50, 50)  # Adjusted size
            icon_pixmap = QtGui.QPixmap('./rsc/icon_wifi.png')

            if icon_pixmap.isNull():
                print("Failed to load the icon.")
            else:
                icon_pixmap = icon_pixmap.scaled(50, 50, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                painter.drawPixmap(icon_rect, icon_pixmap)

            # Draw SSID with Product Sans font
            painter.setFont(QtGui.QFont("Product Sans", 16, QtGui.QFont.Weight.Bold))
            painter.setPen(QtGui.QColor(0, 0, 0))  # Black for SSID
            painter.drawText(rect.x() + 100, rect.y() + 40, f"{ssid}")

            # Draw signal strength and security status
            painter.setFont(QtGui.QFont("Product Sans", 16, QtGui.QFont.Weight.Bold))
            painter.setPen(QtGui.QColor(192, 74, 50))  # Color for signal and status
            painter.drawText(rect.x() + 100, rect.y() + 70, f"{signal_strength} | {security_status}")

            # Restore painter settings
            painter.restore()

        # Set up icon position and size
        icon_rect = QtCore.QRect(rect.x() + 25, rect.y() + 20, 50, 50)  # Adjusted size
        icon_pixmap = QtGui.QPixmap('./rsc/icon_wifi.png')

        if icon_pixmap.isNull():
            print("Failed to load the icon.")
        else:
            icon_pixmap = icon_pixmap.scaled(50, 50, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(icon_rect, icon_pixmap)


        # # Set up text (SSID and signal strength/security status)
        # print(f"Networks: {network}")
        # ssid = network.ssid
        # signal_strength = "Excellent" if int(network.signal) > -50 else "Good" if int(network.signal) > -70 else "Weak"
        # # Update the security status check
        # # Remove WPA3 since it might not be available in pywifi.const
        # secured_akm_types = [const.AKM_TYPE_WPA, const.AKM_TYPE_WPA2, const.AKM_TYPE_WPA2PSK]

        # security_status = "Secured" if network.akm and any(akm in secured_akm_types for akm in network.akm) else "Open"


        # # Draw SSID with Product Sans font
        # painter.setFont(QtGui.QFont("Product Sans", 16, QtGui.QFont.Bold))
        # painter.setPen(QtGui.QColor(0, 0, 0))  # Black for SSID
        # painter.drawText(rect.x() + 100, rect.y() + 40, f"{ssid}")

        # # Draw signal strength and security status with different color
        # painter.setFont(QtGui.QFont("Product Sans", 16, QtGui.QFont.Bold))
        # painter.setPen(QtGui.QColor(192, 74, 50))  # Color for signal and status
        # painter.drawText(rect.x() + 100, rect.y() + 70, f"{signal_strength} | {security_status}")

    def sizeHint(self, option, index):
        # Set the item size (width, height)
        return QtCore.QSize(350, 100)  # Increased height for more spacing
    
class AppointmentDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Fetch the appointment data
        appointment = index.data(QtCore.Qt.ItemDataRole.UserRole)
        # Draw shadow first (to give the illusion of elevation)
        self.draw_shadow(painter, option.rect)

        # Draw the background (white, rounded) with no border and bottom margin
        painter.save()
        rect = option.rect
        bottom_margin = 10  # Margin at the bottom

        # Adjust the rectangle height to create bottom margin
        adjusted_rect = QtCore.QRect(rect.x(), rect.y(), rect.width(), rect.height() - bottom_margin)

        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))  # White background
        painter.setPen(QtCore.Qt.PenStyle.NoPen)  # No border
        painter.drawRoundedRect(adjusted_rect, 30, 30)  # Rounded corners

        painter.restore()
        
        # Get Appointment ID
        
        if appointment['meetingId'] not in appointment_list:
            appointment_list.append(appointment['meetingId'])

        if appointment['token'] not in token_list:
            token_list.append(appointment['token'])
    

        # Draw appointment details (time, date, and doctor name)
        painter.setFont(QtGui.QFont("Product Sans", 16, QtGui.QFont.Weight.Bold))
        painter.setPen(QtGui.QColor(0, 0, 0))  # Black for time and date

        # Draw time.
        appointment_time = appointment['AppointmentTime']
        if appointment_time == None:
            painter.drawText(rect.x() + 20, rect.y() + 40, f"Instant Meeting")
        else:
            time_obj = datetime.strptime(appointment_time, "%H:%M")  # Convert to datetime object
            formatted_time = time_obj.strftime("%I:%M %p")
            painter.drawText(rect.x() + 20, rect.y() + 40, f"{formatted_time}")

        # Draw date
        appointment_date = appointment['AppointmentDate']
        if appointment_time == None:
            painter.drawText(rect.x() + 20, rect.y() + 70, f"")
        else:
            date_obj = datetime.strptime(appointment_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            painter.drawText(rect.x() + 20, rect.y() + 70, f"{formatted_date}")

        # Draw doctor name
        painter.setPen(QtGui.QColor(120, 120, 120))  # Grey for doctor name
        painter.drawText(rect.x() + 20, rect.y() + 110, f"{appointment['Doctor']}")

        # Draw the 'Join' button with hover effect
        button_rect = QtCore.QRect(rect.x() + 350, rect.y() + 20, 100, 40)  # Adjust button position
        self.draw_button(painter, button_rect, option, "Join")

        #################################################################################################################

        #################################################################################################################

    def sizeHint(self, option, index):
        # Set the item size (width, height)
        return QtCore.QSize(300, 150)  # Adjust the height for more spacing

    def draw_button(self, painter, rect, option, text):
        """Draws a custom rounded button with hover and pressed states."""
        painter.save()
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # Define default button colors
        button_color = QtGui.QColor(0, 91, 233)  # Blue
        text_color = QtGui.QColor(255, 255, 255)  # White

        # Hover effect: transparent background with blue outline and text
        if option.state & QtWidgets.QStyle.StateFlag.State_MouseOver:
            painter.setBrush(QtCore.Qt.GlobalColor.transparent)  # Transparent background
            painter.setPen(button_color)  # Blue outline
            text_color = button_color  # Blue text
        else:
            # Default button (blue background, no outline)
            painter.setBrush(QtGui.QBrush(button_color))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)

        # Draw the rounded rectangle button (outline or filled depending on state)
        painter.drawRoundedRect(rect, 20, 20)

        # Draw the button text (change color depending on hover state)
        painter.setPen(text_color)
        painter.setFont(QtGui.QFont("Product Sans", 16, QtGui.QFont.Weight.Bold))

        painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, text)


        painter.restore()

    def draw_shadow(self, painter, rect):
        """Simulates a drop shadow around the appointment card."""
        shadow_color = QtGui.QColor(0, 0, 0, 150)  # Light shadow with some transparency
        shadow_offset = 20  # Distance from the item for shadow
        shadow_blur_radius = 30  # Softness of the shadow edges

        shadow_rect = rect.adjusted(shadow_offset, shadow_offset, -shadow_offset, -shadow_offset)
        
        painter.save()
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # Set the shadow color and blur effect
        painter.setBrush(QtGui.QBrush(shadow_color))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)  # No outline for the shadow
        painter.drawRoundedRect(shadow_rect, shadow_blur_radius, shadow_blur_radius)  # Draw shadow rectangle

        painter.restore()


# class PasswordDialog(QtWidgets.QDialog):
#     def __init__(self, ssid, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle(f"Connect to {ssid}")
#         self.setModal(True)  # This makes it a modal dialog
        
#         self.layout = QtWidgets.QVBoxLayout(self)

#         self.label = QtWidgets.QLabel("Enter Wi-Fi Password:")
#         self.layout.addWidget(self.label)

#         self.password_input = QtWidgets.QLineEdit(self)
#         self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
#         self.layout.addWidget(self.password_input)

#         self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
#         self.layout.addWidget(self.button_box)

#         self.button_box.accepted.connect(self.accept)
#         self.button_box.rejected.connect(self.reject)

#     def get_password(self):
#         return self.password_input.text()

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Create the main window
    window = MainWindow()
    
    # Get the list of available screens
    screens = app.screens()
    print(f"screens: {screens}")
    
    # Iterate over the screens to find the one with the resolution 1024x768
    target_screen = None
    for screen in screens:
        size = screen.size()
        if size.width() == 600 and size.height() == 1024:
            target_screen = screen
            print("1024x600 screen found..")
            break
    
    if target_screen:
        # Set the window to open on the target screen
        screen_geometry = target_screen.geometry()
        window.setGeometry(screen_geometry.left(), screen_geometry.top(), 1024, 600)
    else:
        print("No screen with resolution 1024x600 found.")
    
    # Show the window
    window.showFullScreen()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
