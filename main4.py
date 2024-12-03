import sys
import time
import pywifi
from pywifi import PyWiFi, const, Profile
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QListWidget, QMessageBox, QInputDialog, QLabel, QLineEdit)

# WORKING CODE FOR WIFI..
class WifiManager(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Wi-Fi Manager")
        self.setGeometry(100, 100, 400, 300)
        
        self.layout = QVBoxLayout()
        
        self.statusLabel = QLabel("Status: Not connected")
        self.layout.addWidget(self.statusLabel)
        
        self.networkList = QListWidget()
        self.layout.addWidget(self.networkList)
        
        self.scanButton = QPushButton("Scan for Networks")
        self.scanButton.clicked.connect(self.scan_networks)
        self.layout.addWidget(self.scanButton)
        
        self.connectButton = QPushButton("Connect to Selected Network")
        self.connectButton.clicked.connect(self.connect_to_selected_network)
        self.layout.addWidget(self.connectButton)
        
        self.setLayout(self.layout)
        
        self.wifi = PyWiFi()
        self.interface = self.wifi.interfaces()[0]  # Use the first wireless interface

    def scan_networks(self):
        """Scan for available Wi-Fi networks and display them in the list."""
        self.networkList.clear()
        self.interface.scan()  # Start scanning
        time.sleep(2)  # Wait for scan results
        
        scan_results = self.interface.scan_results()
        for network in scan_results:
            self.networkList.addItem(network.ssid)  # Add the SSID to the list

        if not scan_results:
            QMessageBox.information(self, "Info", "No networks found.")

    def connect_to_selected_network(self):
        """Connect to the selected Wi-Fi network."""
        selected_item = self.networkList.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "Please select a network.")
            return
        
        ssid = selected_item.text().strip()  # Get the selected SSID
        password, ok = QInputDialog.getText(self, 'Enter Password', f'Enter password for {ssid}:', QLineEdit.Password)
        if ok:
            self.connect_to_wifi(ssid, password)

    def connect_to_wifi(self, ssid, password=None):
        """Connect to the specified Wi-Fi network."""
        self.interface.disconnect()  # Disconnect from any currently connected network
        
        profile = Profile()
        profile.ssid = ssid

        if password:  # Check if password is provided
            profile.auth = const.AUTH_ALG_OPEN
            profile.akm.append(const.AKM_TYPE_WPA2PSK)  # Use WPA2 for secured networks
            profile.cipher = const.CIPHER_TYPE_CCMP
            profile.key = password  # Set the password
        else:  # Open network
            profile.auth = const.AUTH_ALG_OPEN
            profile.akm.append(const.AKM_TYPE_NONE)  # No key management for open networks
            profile.cipher = const.CIPHER_TYPE_NONE  # No cipher for open networks

        self.interface.remove_all_network_profiles()  # Remove all previous profiles
        tmp_profile = self.interface.add_network_profile(profile)  # Add the new profile
        
        self.interface.connect(tmp_profile)  # Connect to the network
        time.sleep(10)  # Wait for a moment to check if the connection is successful

        if self.interface.status() == const.IFACE_CONNECTED:
            self.statusLabel.setText(f"Status: Connected to {ssid}")
            QMessageBox.information(self, "Success", f"Connected to {ssid}")
        else:
            self.statusLabel.setText("Status: Connection failed")
            QMessageBox.warning(self, "Error", "Failed to connect to the network.")


    def disconnect_wifi(self):
        """Disconnect from the current Wi-Fi network."""
        self.interface.disconnect()
        self.statusLabel.setText("Status: Disconnected")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = WifiManager()
    manager.show()
    sys.exit(app.exec_())
