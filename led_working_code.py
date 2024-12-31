from gpiozero import LED
from time import sleep

# Define the MOSFETs as LEDs (since we're controlling them like switches)
mosfet1 = LED(17)  # GPIO pin 17 controls MOSFET 1 (LCD 1)
mosfet2 = LED(22)  # GPIO pin 22 controls MOSFET 2 (LCD 2)

def state1():
    """Both LCDs ON"""
    mosfet1.on()  # Turn on MOSFET 1 (LCD 1 ON)
    mosfet2.on()  # Turn on MOSFET 2 (LCD 2 ON)
    print("State 1: Both LCDs ON")

def state2():
    """LCD 1 ON, LCD 2 OFF"""
    mosfet1.on()  # Turn on MOSFET 1 (LCD 1 ON)
    mosfet2.off()  # Turn off MOSFET 2 (LCD 2 OFF)
    print("State 2: LCD 1 ON, LCD 2 OFF")

def state3():
    """LCD 2 ON, LCD 1 OFF"""
    mosfet1.off()  # Turn off MOSFET 1 (LCD 1 OFF)
    mosfet2.on()  # Turn on MOSFET 2 (LCD 2 ON)
    print("State 3: LCD 2 ON, LCD 1 OFF")

try:
    while True:
        state1()  # Both LCDs ON
        sleep(2)  # Wait for 2 seconds
        
        state2()  # LCD 1 ON, LCD 2 OFF
        sleep(2)  # Wait for 2 seconds
        
        state3()  # LCD 2 ON, LCD 1 OFF
        sleep(2)  # Wait for 2 seconds

except KeyboardInterrupt:
    print("Exiting program")
