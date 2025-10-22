# Gate control system

from servo import Servo
from lcd_i2c import LCD
from machine import I2C, Pin, time_pulse_us
import _thread
import time



class Counter:
    def __init__(self, AIR_entry_pin, AIR_exit_pin, servo_entry_pin, servo_exit_pin, parking_lot, max_cars=5, i2c_scl=27, i2c_sda=26): #change when needed
        self.slot_sensors = parking_lot #get info from Parking_lot(line 167) to know each plot status
        self.max_cars = max_cars #max car can enter parking slot is 5
        self.num_plate = [] #for storing number plate purpose
        self.AIR_entry_pin = Pin(AIR_entry_pin, Pin.IN)
        self.AIR_exit_pin = Pin(AIR_exit_pin, Pin.IN)
        self.servo_entry = Servo(pin_id=servo_entry_pin)
        self.servo_exit = Servo(pin_id=servo_exit_pin)
        self.gate_entry_open = False #False meaning close gate and vice versa
        self.gate_exit_open = False #False meaning close gate and vice versa

        # Setup LCD
        I2C_ADDR = 0x27
        NUM_ROWS = 2
        NUM_COLS = 16
        i2c = I2C(1, scl=Pin(i2c_scl), sda=Pin(i2c_sda), freq=400000)
        self.lcd = LCD(addr=I2C_ADDR, cols=NUM_COLS, rows=NUM_ROWS, i2c=i2c)
        self.lcd.begin()#start lcd(light up)

    def display_lcd(self, line1="", line2=""):
        """Clear the LCD and print up to two lines of text."""
        self.lcd.clear()
        self.lcd.set_cursor(0, 0)
        self.lcd.print(line1)

        if line2 != "":
            self.lcd.set_cursor(0, 1)
            self.lcd.print(line2)

    # === Gate control ===
    def open_gate(self):
        print("🔓 Gate opened")
        self.servo_entry.write(90)  # Adjust if your servo angle differs
        time.sleep(.3)
        self.display_lcd("Gate Open", "Car entering...")
        time.sleep(3)


    def close_gate(self):
        print("🔒 Gate closed")
        self.servo_entry.write(0)
        time.sleep(.3)
        time.sleep(3)















