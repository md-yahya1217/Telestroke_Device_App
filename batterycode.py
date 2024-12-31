from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QTimer
import smbus

# Constants for the MAX17044 sensor
MAX17044_ADDRESS = 0x36
VOLTAGE_REGISTER = 0x02
SOC_REGISTER = 0x04
ALERT_REGISTER = 0x1B

# Function to read data from the MAX17044 sensor
def read_register(bus, address, register):
    data = bus.read_i2c_block_data(address, register, 2)
    return (data[0] << 8) | data[1]

# Main GUI application class
class FuelGaugeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAX17044 Fuel Gauge Monitor")

        # Layout and widgets
        self.layout = QVBoxLayout()
        self.voltage_label = QLabel("Voltage: 0 V")
        self.soc_label = QLabel("State of Charge: 0 %")
        self.alert_label = QLabel("Alert: Not triggered")
        self.refresh_button = QPushButton("Refresh")

        self.layout.addWidget(self.voltage_label)
        self.layout.addWidget(self.soc_label)
        self.layout.addWidget(self.alert_label)
        self.layout.addWidget(self.refresh_button)

        self.setLayout(self.layout)

        # Initialize I2C bus
        self.bus = smbus.SMBus(1)  # Use I2C bus 1

        # Connect button to refresh function
        self.refresh_button.clicked.connect(self.update_readings)

        # Timer for periodic updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_readings)
        self.timer.start(500)  # Update every 500 ms

    def update_readings(self):
        try:
            # Read voltage
            voltage_raw = read_register(self.bus, MAX17044_ADDRESS, VOLTAGE_REGISTER)
            voltage = (voltage_raw >> 4) * 0.00125
            self.voltage_label.setText(f"Voltage: {voltage:.2f} V")

            # Read state of charge (SoC)
            soc_raw = read_register(self.bus, MAX17044_ADDRESS, SOC_REGISTER)
            soc = soc_raw / 256.0
            self.soc_label.setText(f"State of Charge: {soc:.2f} %")

            # Read alert status
            alert = read_register(self.bus, MAX17044_ADDRESS, ALERT_REGISTER)
            alert_status = "Triggered" if alert & 0x01 else "Not triggered"
            self.alert_label.setText(f"Alert: {alert_status}")

        except Exception as e:
            self.voltage_label.setText("Error reading sensor")
            self.soc_label.setText(str(e))

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = FuelGaugeApp()
    window.show()
    sys.exit(app.exec())
