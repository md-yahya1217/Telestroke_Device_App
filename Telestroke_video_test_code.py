import json
import cv2
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
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import Qt, QMetaObject, Q_ARG, QTimer
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import QStringListModel  # Import QStringListModel for QListView
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtCore import QUrl
# from PyQt6.QtMultimedia import QMediaContent


# import pywifi
# from pywifi import const, Profile
import requests

base_path = ""
# base_path = sys._MEIPASS #For build purpose

#To build this code make sure all paths have "/" to change directory.

#self.button_A.setIcon(QIcon(base_path+"/rsc/rsc3.png"))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(base_path+r'./telestroke_device.ui', self)

        # Initialize PyWiFi
        # self.wifi = pywifi.PyWiFi()
        # self.interface = self.wifi.interfaces()[0]
        # self.iface = self.wifi.interfaces()[0]  # Get the first wireless interface
        # interfaces = self.wifi.interfaces()
        # if len(interfaces) > 0:
        #     self.interface = interfaces[0]
        # else:
        #     print("No Wi-Fi interfaces found")

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
        # Initialize custom webcam video track
        self.webcam_track = WebcamVideoTrack()
        # self.current_screen = None  # Initialize current_screen

        # Initialize WebSocket client
        self.websocket_client = WebSocketClient("ws://192.168.0.192:3001", self.handle_command)
        self.websocket_client.run()

        # Connect buttons to their respective slots
        #self.pushButton_left.clicked.connect(lambda: self.play_video_on_screen(1, "./rsc/Video1.mp4"))
        #self.pushButton_right.clicked.connect(lambda: self.play_video_on_screen(2, "./rsc/Video1.mp4"))
        # Example JSON data
        self.json_data = [
            {"meetingId": "i4iu-856b-fihd", "AppointmentTime": "09:00 am", "AppointmentDate": "30th February, 2024", "DoctorName": "Dr. Raymond Reddington"},
            {"meetingId": "3fp5-l0ww-86lg", "AppointmentTime": "11:00 am", "AppointmentDate": "1st March, 2024", "DoctorName": "Dr. Liz Keen"}
        ]

        #self.btn_9.clicked.connect(lambda: self.handle_screen_change(6))

        self.listView.doubleClicked.connect(lambda: self.on_network_double_clicked)
        self.listView_2.doubleClicked.connect(lambda: self.handle_screen_change(4))

        self.appointment_1.hide()

        # self.listView.clicked.connect(lambda: self.connect_to_network)
        self.available_network.hide()
    
        self.screen = 1
        # self.handle_screen_change(1)
        

        self.btn_1.clicked.connect(lambda: self.handle_screen_change(2))
        self.btn_2.clicked.connect(lambda: self.register_device())
        self.btn_6.clicked.connect(lambda: self.handle_screen_change(1))
        
        # self.btn_3.clicked.connect(lambda: asyncio.run_coroutine_threadsafe(self.leave_meeting()))

        self.pushButton_back.clicked.connect(lambda: self.handle_screen_change(2))
        # self.pushButton_2.clicked.connect(lambda: self.handle_screen_change(4))

        # self.handle_screen_change(6)
    
        
        # Start the asyncio event loop in a separate thread
        self.loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.start_event_loop, args=(self.loop,))
        t.start()

        self.btn_3.clicked.connect(lambda: self.leave_meeting())


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

    def join_meeting(self):
        asyncio.run_coroutine_threadsafe(self.start_meeting(), self.loop)

    def leave_meeting(self):
        asyncio.run_coroutine_threadsafe(self.end_meeting(), self.loop)



    async def end_meeting(self):

        self.meeting.leave()
        # print("im here also")
        self.join = False
        self.handle_screen_change(3)


    async def start_meeting(self):
        
        if self.join == False:
            self.join = True
            dotenv.load_dotenv()
            # self.webcam_track = WebcamVideoTrack()

            VIDEOSDK_TOKEN = os.getenv("VIDEOSDK_TOKEN")
            MEETING_ID = os.getenv("MEETING_ID")
            NAME = "Wajahat"
            

            meeting_config = MeetingConfig(
                meeting_id=MEETING_ID,
                name=NAME,
                mic_enabled=True,
                token=VIDEOSDK_TOKEN,
                custom_camera_video_track=self.webcam_track
            )

            self.meeting = VideoSDK.init_meeting(**meeting_config)
            self.meeting.add_event_listener(MyMeetingEventHandler())

            try:
                await self.meeting.async_join()
                print("Joined successfully")
                # Assuming you have a `meeting` object initialized and joined
                participants = self.meeting.participants

                # Check the number of participants
                total_participants = len(participants)
                print(f"Total number of participants: {total_participants}")
                
            except Exception as e:
                print(f"Error while joining the meeting: {e}")
                return

            local_participant = self.meeting.local_participant
            print("Local participant:", local_participant.id, local_participant.display_name)

        else:
            print("No need")
            # self.handle_screen_change(4)
        

    def process_command_on_window(self, window, command):
        if command['stop'] == False:
            window.play_video()
        elif command.get('command') == 'pause':
            window.pause_video()
        elif command['stop'] == True:
            window.stop_video()
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


        if self.screen == 1:
            self.screen_1.hide()
            self.screen_2.hide()
            self.screen_3.hide()
            self.screen_4.hide()
            self.screen_5.hide()
            self.screen_6.show()
            self.screen_7.hide()
            self.init_screen6()

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
            if not self.additional_windows_created:
                self.create_two_additional_windows()
                self.additional_windows_created = True
            self.screen_4.show()
            self.screen_3.hide()
            self.screen_1.hide()
            self.screen_2.hide()
            self.screen_5.hide()
            self.screen_6.hide()
            self.screen_7.hide()
            self.init_screen4()

        elif self.screen == 6:
            self.screen_3.show()
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

    def register_device(self):
     #   patientid = self.lineEdit.text()
     #   print(f"Patient ID Entered: {patientid}")

        # # The URL of the API endpoint
        # url = 'http://192.168.0.185:5000/api/device_registration'

        # # The data to be sent in the POST request
        # data = {
        #     'ID': PatientID,
        #     'DeviceID': 1007
        # }

        # try:
        #     # Sending the POST request
        #     response = requests.post(url, json=data)

        #     # Handle the response based on status code
        #     if response.status_code == 200:
        #         result = response.json()
        #         if result.get('message') == 'Successful':
        #             self.label_20.hide()  # Hide the error label if it was shown previously
        #             self.handle_screen_change(3)  # Assuming this changes to the next screen
        #         else:
        #             self.label_20.show()
        #             self.label_20.setText("Unexpected success response.")
        #             self.label_20.setStyleSheet("color:red;")

        #     elif response.status_code == 400:
        #         result = response.json()
        #         if result.get('error') == 'ID and Device ID are required.':
        #             self.label_20.show()
        #             self.label_20.setText("Error: ID and Device ID are required.")
        #             self.label_20.setStyleSheet("color:red;")

        #     elif response.status_code == 404:
        #         result = response.json()
        #         if result.get('error') == 'No such ID':
        #             self.label_20.show()
        #             self.label_20.setText("Error: No patient found with the provided ID.")
        #             self.label_20.setStyleSheet("color:red;")

        #     elif response.status_code == 500:
        #         result = response.json()
        #         if result.get('error') == 'An error occurred while updating DeviceID.':
        #             self.label_20.show()
        #             self.label_20.setText("Error: Internal server error.")
        #             self.label_20.setStyleSheet("color:red;")
        #         else:
        #             self.label_20.show()
        #             self.label_20.setText("Unexpected server error.")
        #             self.label_20.setStyleSheet("color:red;")

        #     else:
        #         self.label_20.show()
        #         self.label_20.setText(f"Unexpected status code {response.status_code}: {response.text}")
        #         self.label_20.setStyleSheet("color:red;")

        # except requests.exceptions.RequestException as e:
        #     # Handle exceptions like connection errors
        #     self.label_20.show()
        #     self.label_20.setText(f"Request failed: {e}")
        #     self.label_20.setStyleSheet("color:red;")

        # # If no Patient ID was entered
        # if not PatientID:
        #     self.label_20.show()
        #     self.label_20.setText("Error: Patient ID not Entered!")
        #     self.label_20.setStyleSheet("color:red;")
        self.handle_screen_change(3)

    def show_keyboard(self, event):
        self.keyboard.show()
        return super().focusInEvent(event)


    def init_screen3(self):
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(60)
        shadow1.setOffset(0, 10)
        self.appointment_1.setGraphicsEffect(shadow1)
        self.populate_appointments_in_listview(self.json_data)

        self.pushButton_2.clicked.connect(lambda: self.handle_screen_change(4))

    def init_screen4(self):
        # # Additional initialization logic for screen 4 (if any)
        # model = self.listView_2.model()
        # network = model.itemFromIndex(index).data(QtCore.Qt.UserRole)  # Retrieve the network data
        self.create_two_additional_windows()
        self.join_meeting()
        pass

    def populate_appointments_in_listview(self, appointments):
        model = QtGui.QStandardItemModel()

        for appointment in appointments:
            item = QtGui.QStandardItem()
            item.setData(appointment, QtCore.Qt.ItemDataRole.UserRole)
            model.appendRow(item)

        self.listView_2.setModel(model)
        self.listView_2.setItemDelegate(AppointmentDelegate(self.listView_2))


    def scan_networks(self):
        print("Inside scan_networks")
        # Start scanning networks
        self.interface.scan()  # Start scanning
        self.update_current_network_info()
        QtCore.QTimer.singleShot(2500, self.update_networks)  # Wait for results

        return

    def update_networks(self):
        try:
            # self.interface.scan()  # Start the scan
            results = self.interface.scan_results()  # Get scan results
            
            if results is None:
                print("No scan results found.")
                return
            
            print("Inside update_networks: ", results)
            print("Number of networks found: ", len(results))  # Check the number of networks

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

    def get_current_network(self):
        # Check if the interface is connected
        print(f"Interface status: {self.iface.status()}")
        if self.iface.status() == 4:
            # Get the current network profile from the connected networks
            profiles = self.iface.network_profiles()  # Get saved profiles
            print(f"Profiles found: {len(profiles)}")
            
            for profile in profiles:
                # Check if the profile is active and has a valid BSSID
                if profile.ssid is not None:
                    print(f"Connected to: {profile.ssid}")
                    return profile.ssid  # Return the SSID of the connected network

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

    def update_current_network_info(self):
        ssid = self.get_current_network()  # Get the current SSID from pywifi
        print("Get Current Network:",ssid)
        if ssid is not None:  # If there is a current network
            self.label_17.setText(ssid)  # Set the SSID to label_17
            self.current_network.show()  # Show current_network QFrame
            self.label_10.show()  # Show label_10
            self.label_17.setStyleSheet("color: :rgb(35, 78, 232);")
            self.label_15.show()
        else:
            self.label_17.setText("Not Connected")  # Set the SSID to label_17
            self.label_17.setStyleSheet("color: red;")
            self.label_15.hide()
            self.current_network.show()  # Show current_network QFrame
            self.label_10.show()  # Hide label_10


    def connect_to_network(self, network):
        # Check if the network is secured
        if network.akm and network.akm[0] == 'wpa-psk':
            # Instead of showing a password dialog, switch to screen_7
            self.screen_7.show()  # Assuming screen_7 is part of a QStackedWidget
            print("Switched to screen_7 for secured network:", network.ssid)
        else:
            # Handle open network connection here
            self.connect_to_open_network(network)

    def on_network_double_clicked(self, index):
        print("Double Clicked Function Triggered!!!")
        model = self.listView.model()
        network = model.itemFromIndex(index).data(QtCore.Qt.UserRole)  # Retrieve the network data

        # Check if the network is secured
        secured_akm_types = [const.AKM_TYPE_WPA, const.AKM_TYPE_WPA2, const.AKM_TYPE_WPA2PSK]
        is_secured = network.akm and any(akm in secured_akm_types for akm in network.akm)

        if is_secured:
            # Show screen_7 if the network is secured
            
            print(f"Switched to screen_7 for secured network: {network.ssid} Type of network: {type(network)}")
            self.selectedNetwork = network
            self.handle_screen_change(7)
        else:
            # Connect to open network or handle it accordingly
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
        self.label_19.setText("Connecting...")
        print(f"Entered Password in Secured Network Function: {password}")
        profile = Profile()

        if not hasattr(network, 'ssid'):
            print("Invalid network object; it does not have an SSID.")
            return

        profile.ssid = network.ssid
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.auth = const.AUTH_ALG_OPEN
        profile.key = password  # Use the entered password

        try:
            # Remove existing profiles and add the new one
            self.interface.remove_all_network_profiles()
            self.interface.add_network_profile(profile)
            self.interface.connect(profile)

            self.label_19.setText("Connecting...")
            print("Connecting...")
            # Wait for a bit to allow connection to establish
            time.sleep(10)  # Increase wait time if necessary

            # Polling for the connection status
            for _ in range(30):  # Check status for up to 30 seconds
                status = self.interface.status()
                profiles = self.interface.network_profiles()  # Log current profiles
                print(f"Current interface status: {status}")
                print(f"Active profiles: {[p.ssid for p in profiles]}")  # Log active profiles
                
                if status == 4:
                    print(f"Successfully connected to {profile.ssid}")
                    break
                # elif status == 4:  # Transitional state
                #     print("Still in transitional state... waiting to connect.")
                else:
                    print("Connection failed or not in a valid state.")
                    break  # Exit if not in a connecting state
                
                # Check OS connection as a fallback
                # if self.check_os_connection():
                #     print("Connected according to OS.")
                #     break

                # time.sleep(1)  # Sleep for a second before checking again
            else:
                print("Failed to connect within the given timeframe.")

            # Update network info and potentially change the screen afterward
            self.update_current_network_info()
            self.handle_screen_change(6)

        except Exception as e:
            print(f"An error occurred while connecting: {e}")




    def init_screen6(self):
        self.btn_7.clicked.connect(lambda: self.scan_networks())
        
        self.update_current_network_info()

        # Initialize the listView model if it's not already set
        if self.listView.model() is None:
            self.listView.setModel(QtGui.QStandardItemModel())
        
        self.listView.doubleClicked.connect(self.on_network_double_clicked)


    def init_screen7(self): 
        self.btn_9.clicked.connect(lambda: self.handle_screen_change(6))
        self.label_19.setText(f"Enter Password for {self.selectedNetwork.ssid}")
        print(f"Entered Password: {self.lineEdit_2.text()}")
        
        self.btn_10.clicked.connect(lambda: self.connect_to_secured_network(self.selectedNetwork,self.lineEdit_2.text()))


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
        screen_geometry_2 = screens[1].geometry()  # Geometry of the second screen

        # Set geometry for each additional window
        # self.additional_window_1.setGeometry(screen_geometry_1)
        self.additional_window_1.setGeometry(screen_geometry_2)

        self.additional_window_1.show()
        # self.additional_window_2.show()

class AdditionalScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(AdditionalScreen, self).__init__()
        self.setFixedSize(1920, 1080)
        self.setWindowTitle("Stimulus Screen")

        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

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
        # self.layout.addWidget(self.next_button)r

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

    def play_video(self):
        """Start or resume video playback."""
        if not self.video_mapping:
            return

        video_path = self.video_mapping[self.current_video_index]
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            print("Error: Could not open video.")
            return

        # Resume the video playback if it was paused
        self.is_paused = False
        # self.timer.start(30)  # Start with 30 ms delay for normal speed (medium)

    def pause_video(self):
        """Pause the video playback."""
        self.is_paused = True

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
        network = index.data(QtCore.Qt.UserRole)

        # Draw the background (white, rounded) with no border and bottom margin
        painter.save()
        rect = option.rect

        # Define bottom margin
        bottom_margin = 7  # Margin at the bottom

        # Adjust the rectangle height to create bottom margin
        adjusted_rect = QtCore.QRect(rect.x(), rect.y(), rect.width(), rect.height() - bottom_margin)

        # Set rendering hints
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))  # White background
        painter.setPen(QtCore.Qt.NoPen)  # Set no pen to avoid borders

        # Draw rounded rectangle with no border
        painter.drawRoundedRect(adjusted_rect, 30, 30)  # Rounded corners

        # Restore painter settings
        painter.restore()

        # Set up icon position and size
        icon_rect = QtCore.QRect(rect.x() + 25, rect.y() + 20, 50, 50)  # Adjusted size
        icon_pixmap = QtGui.QPixmap('./rsc/icon_wifi.png')

        if icon_pixmap.isNull():
            print("Failed to load the icon.")
        else:
            icon_pixmap = icon_pixmap.scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            painter.drawPixmap(icon_rect, icon_pixmap)


        # Set up text (SSID and signal strength/security status)
        ssid = network.ssid
        signal_strength = "Excellent" if int(network.signal) > -50 else "Good" if int(network.signal) > -70 else "Weak"
        # Update the security status check
        # Remove WPA3 since it might not be available in pywifi.const
        secured_akm_types = [const.AKM_TYPE_WPA, const.AKM_TYPE_WPA2, const.AKM_TYPE_WPA2PSK]

        security_status = "Secured" if network.akm and any(akm in secured_akm_types for akm in network.akm) else "Open"




        # Draw SSID with Product Sans font
        painter.setFont(QtGui.QFont("Product Sans", 16, QtGui.QFont.Bold))
        painter.setPen(QtGui.QColor(0, 0, 0))  # Black for SSID
        painter.drawText(rect.x() + 100, rect.y() + 40, f"{ssid}")

        # Draw signal strength and security status with different color
        painter.setFont(QtGui.QFont("Product Sans", 16, QtGui.QFont.Bold))
        painter.setPen(QtGui.QColor(192, 74, 50))  # Color for signal and status
        painter.drawText(rect.x() + 100, rect.y() + 70, f"{signal_strength} | {security_status}")

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

        # Draw appointment details (time, date, and doctor name)
        painter.setFont(QtGui.QFont("Product Sans", 16, QtGui.QFont.Weight.Bold))
        painter.setPen(QtGui.QColor(0, 0, 0))  # Black for time and date

        # Draw time
        painter.drawText(rect.x() + 20, rect.y() + 40, f"{appointment['AppointmentTime']}")

        # Draw date
        painter.drawText(rect.x() + 20, rect.y() + 70, f"{appointment['AppointmentDate']}")

        # Draw doctor name
        painter.setPen(QtGui.QColor(120, 120, 120))  # Grey for doctor name
        painter.drawText(rect.x() + 20, rect.y() + 110, f"{appointment['DoctorName']}")

        # Draw the 'Join' button with hover effect
        button_rect = QtCore.QRect(rect.x() + 350, rect.y() + 20, 100, 40)  # Adjust button position
        self.draw_button(painter, button_rect, option, "Join")

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
    window = MainWindow()
     # Get the list of available screens
    screens = app.screens()

    # Choose the second screen (index 1, as index 0 is the primary screen)
    second_screen = screens[0]  # This is for the second screen
    # Fetch and print the maximum resolution of each screen
    for index, screen in enumerate(screens):
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        print(f"Screen {index + 1}: {screen_width}x{screen_height}")

    # Get the geometry of the second screen
    screen_geometry = second_screen.geometry()
    # player = AdditionalScreen()
    # player.show()
    # Set the window geometry based on the second screen's geometry
    window.setGeometry(screen_geometry)
    window.showFullScreen()
    sys.exit(app.exec())



if __name__ == '__main__':
    main()