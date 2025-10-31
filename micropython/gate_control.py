from servo import Servo
from lcd_i2c import LCD
from machine import I2C, Pin, time_pulse_us
import _thread
import time
import micropython.configs as configs

number_plates = []
class Counter:
    def __init__(self, AIR_pin, servo_pin, parking_lot, LCD_pin, i2c_scl, i2c_sda): #change when needed
        self.slot_sensors = parking_lot #get info from Parking_lot(line 167) to know each plot status
        self.AIR_PIN = Pin(AIR_pin, Pin.IN)
        self.servo = Servo(pin_id=servo_pin)
        self.LCD_pin = LCD_pin
        self.gate_open = False #False meaning close gate and vice versa
        self.i2c_scl = i2c_scl
        self.i2c_sda = i2c_sda

        # Setup LCD
        I2C_ADDR = 0x27
        NUM_ROWS = 2
        NUM_COLS = 16
        i2c = I2C(self.LCD_pin, scl=Pin(self.i2c_scl), sda=Pin(self.i2c_sda), freq=400000)
        self.lcd = LCD(addr=I2C_ADDR, cols=NUM_COLS, rows=NUM_ROWS, i2c=i2c)
        self.lcd.begin()#start lcd(light up)

    def AIR_detected(self):
        return self.AIR_PIN.value() == 1 #if 1 then return true(no detection), else false (have detection)
    
    def open_gate(self):
        print("Opening gate...")
        for angle in range(180, 91, -5):
            self.servo.write(angle)#opening gate from 0 to 90 degree with increment of 5
            time.sleep(0.03)
        self.gate_open = True #set value to open

    def close_gate(self):
        print("Closing gate...")
        for angle in range(90, 180, 5):
            self.servo.write(angle)#closing gate from 90 to 0 degree with decrement of 5
            time.sleep(0.03)
        self.gate_open = False #set value to close'
    
    def display_lcd(self, line1="", line2=""): #lcd has two lines, use self.display_lcd(line 1, line 2(optional))
        self.lcd.clear()
        self.lcd.set_cursor(0, 0)
        self.lcd.print(line1)
        if line2:
            self.lcd.set_cursor(0, 1)
            self.lcd.print(line2)

    def car_allowed(self, plate): #if have duplicate car plate in car parking then return False(means not allow car to go in) and vice versa
        if plate in number_plates:
            self.display_lcd("Duplicate Car", plate)
            print(f"Car {plate} already entered.")
            return False
        
        if self.car_count() >= configs.MAX_CAR:
            print(f"Car park is already full.")
            self.display_lcd("No parking", "available!")
            return False
        return True

    def get_info_nearest_slot(self):#get nearest slot
        for slot in sorted(self.slot_sensors.keys()): #sort dictionary of slot_sensors(Parking_lot#167 lines) to increasing order
            if self.slot_sensors[slot] == 0: #find which plot is not occupied from lowest key to highest key in dictionary
                return slot #return slot number to car entry
        return None #if fully occupied return none to car entry

    def car_entry(self, plate):

        if not self.car_allowed(plate):
            return

        nearest_slot = self.get_info_nearest_slot()
        self.display_lcd(f"Welcome! {plate}", f"Nearest slot: {nearest_slot}")
        print(f"Car {plate} eligible to enter. Nearest slot: {nearest_slot}")
        
        number_plates.append(plate)

        self.open_gate()
        print("Gate entry opened")

        while self.AIR_detected():
            print('Waiting car to enter the gate entry')
            time.sleep(0.1)

        while not self.AIR_detected():
            print("Car detected! Waiting for it to leave entry...")
            time.sleep(0.1)

        time.sleep(1)
        print("Car left. Closing gate entry")
        self.close_gate()
        self.show_availability()
        print("Gate entry closed.")
        time.sleep(1)


    def car_count(self): #calc length of list and return num cars value
        return len(number_plates)

    def show_all_cars(self):#for debug purpose
        print("All detected plates:")
        for plate in number_plates:
            print(plate)

    def car_exit(self, plate, fee):
        if plate in number_plates: #if plate scanned in the list, remove the plate from the list, open gate for car exit and close gate
            number_plates.remove(plate)
            self.display_lcd("Total fee is ", f"RM{fee:.2f}")
            time.sleep(3)
            self.display_lcd("Goodbye ", plate)
            print(f"Car {plate} exited. Total cars: {self.car_count()}")
            
            self.open_gate()
            print("Gate exit opened")

            while self.AIR_detected(): #looping until AIR return value 0(car detected)
                print('Waiting car to enter the gate exit')
                time.sleep(0.1)
        
            while not self.AIR_detected(): #looping until AIR return value 1(no car detected)
                print("Car detected! Waiting for it to leave exit...")
                time.sleep(0.1)

            time.sleep(1)
            self.close_gate()
            print("Gate exit closed.")
            time.sleep(1)

        else: #if no plate found in the list, need to manually click enter form terminal
            self.display_lcd("Not Found", plate)
            print(f"Plate {plate} not found.")
            time.sleep(5)
            self.display_lcd("Please wait for", "help!")
            input("Press Enter to Continue...")

    def show_availability(self):
        available_slots = configs.MAX_CAR - self.car_count()

        if available_slots <= 0:
            print("Parking full! Gate remains closed.")
            self.display_lcd("No parking", "available!")
        else:
            print(f"Available slots: {available_slots}")
            self.display_lcd("Available slots:",f"--------{available_slots}-------")
        time.sleep(1)

