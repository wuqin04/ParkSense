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
        self.lcd_busy = False #<--------initiate lcd_busy for lcd_idle_loop


        # Setup LCD
        I2C_ADDR = 0x27
        NUM_ROWS = 2
        NUM_COLS = 16
        i2c = I2C(1, scl=Pin(i2c_scl), sda=Pin(i2c_sda), freq=400000)
        self.lcd = LCD(addr=I2C_ADDR, cols=NUM_COLS, rows=NUM_ROWS, i2c=i2c)
        self.lcd.begin()#start lcd(light up)

    def AIR_entry_detected(self):
        return self.AIR_entry_pin.value() == 1 #if 1 then return true(no detection), else false (have detection)
    
    def AIR_exit_detected(self):
        return self.AIR_exit_pin.value() == 1 #if 1 then return true(no detection), else false (have detection)

    def open_gate_entry(self):
        print("Opening gate entry...")
        for angle in range(0, 91, 5):
            self.servo_entry.write(angle)#opening gate from 0 to 90 degree with increment of 5
            time.sleep(0.03)
        self.gate_entry_open = True #set value to open

    def close_gate_entry(self):
        print("Closing gate entry...")
        for angle in range(90, -1, -5):
            self.servo_entry.write(angle)#closing gate from 90 to 0 degree with decrement of 5
            time.sleep(0.03)
        self.gate_entry_open = False #set value to close'

    def open_gate_exit(self):
        print("Opening gate exit...")
        for angle in range(0, 91, 5):
            self.servo_exit.write(angle)#opening gate from 0 to 90 degree with increment of 5
            time.sleep(0.03)
        self.gate_exit_open = True #set value to open

    def close_gate_exit(self):
        print("Closing gate exit...")
        for angle in range(90, -1, -5):
            self.servo_exit.write(angle)#closing gate from 90 to 0 degree with decrement of 5
            time.sleep(0.03)
        self.gate_exit_open = False #set value to close'
    
    def display_lcd(self, line1="", line2=""): #lcd has two lines, use self.display_lcd(line 1, line 2(optional))
        self.lcd.clear()
        self.lcd.set_cursor(0, 0)
        self.lcd.print(line1)
        if line2:
            self.lcd.set_cursor(0, 1)
            self.lcd.print(line2)

    def car_allowed(self, plate): #if have duplicate car plate in car parking then return False(means not allow car to go in) and vice versa
        if plate in self.num_plate:
            self.display_lcd("Duplicate Car", plate)
            print(f"Car {plate} already entered.")
            return False
        return True

    def get_info_nearest_slot(self):#get nearest slot
        for slot in sorted(self.slot_sensors.keys()): #sort dictionary of slot_sensors(Parking_lot#167 lines) to increasing order
            if self.slot_sensors[slot] == 0: #find which plot is not occupied from lowest key to highest key in dictionary
                return slot #return slot number to car entry
        return None #if fully occupied return none to car entry

    def car_entry(self, plate):
        self.lcd_busy = True  # 👈 Pause background LCD updates

        if not self.car_allowed(plate):
            self.lcd_busy = False  # 👈 Resume before exit
            return

        nearest_slot = self.get_info_nearest_slot()
        self.display_lcd("Welcome!", f"Nearest: Slot {nearest_slot}")
        print(f"Car {plate} eligible to enter. Nearest slot: {nearest_slot}")
        
        self.num_plate.append(plate)

        self.open_gate_entry()
        print("Gate entry opened")

        while self.AIR_entry_detected():
            print('Waiting car to enter the gate entry')
            time.sleep(0.1)

        while not self.AIR_entry_detected():
            print("Car detected! Waiting for it to leave entry...")
            time.sleep(0.1)

        time.sleep(1)
        print("Car left. Closing gate entry")
        self.close_gate_entry()
        print("Gate entry closed.")
        time.sleep(1)

        self.lcd_busy = False  # 👈 Resume background LCD updates here


    def car_count(self): #calc length of list and return num cars value
        return len(self.num_plate)

    def show_all_cars(self):#for debug purpose
        print("All detected plates:")
        for plate in self.num_plate:
            print(plate)

    def car_exit(self, plate):
        if plate in self.num_plate: #if plate scanned in the list, remove the plate from the list, open gate for car exit and close gate
            self.num_plate.remove(plate)
            self.display_lcd("Goodbye", plate)
            print(f"Car {plate} exited. Total cars: {self.car_count()}")
            
            self.open_gate_exit()
            print("Gate exit opened")

            while self.AIR_exit_detected(): #looping until AIR return value 0(car detected)
                print('Waiting car to enter the gate exit')
                time.sleep(0.1)
        
            while not self.AIR_exit_detected(): #looping until AIR return value 1(no car detected)
                print("Car detected! Waiting for it to leave exit...")
                time.sleep(0.1)

            time.sleep(1)
            self.close_gate_exit()
            print("Gate exit closed.")
            time.sleep(1)
            time.sleep(2)
            
        else: #if no plate found in the list, need to manually click enter form terminal
            self.display_lcd("Not Found", plate)
            print(f"Plate {plate} not found.")
            time.sleep(5)
            self.display_lcd("Please wait for", "help!")
            input("Press Enter to Continue...")

    def lcd_idle_loop(self):
        while True:
            if not self.lcd_busy: #if lcd_busy return false then run the code below
                    available_slots = self.max_cars - self.car_count()

                    if available_slots <= 0:
                        print("Parking full! Gate remains closed.")
                        self.display_lcd("No parking", "available!")
                    else:
                        print(f"Available slots: {available_slots}")
                        self.display_lcd("Available slots:",f"--------{available_slots}-------")
            time.sleep(1)


def run_ultrasonic():
    global Sensors, Parking_lot, initial_status, stable_count, last_change_time, distance_threshold, stable_limit, hold_time
        
    while True:
        distance_list = [sensor.measure() for sensor in Sensors]
        print("\n📏 Distances (cm):", ["{:.1f}".format(d) for d in distance_list])

        raw_status = [1 if d <= distance_threshold else 0 for d in distance_list]

        for i, key in enumerate(Parking_lot.keys()):
            if raw_status[i] != initial_status[i]:
                stable_count[i] += 1
                print(f"{key}: Unstable ({stable_count[i]}/{stable_limit})")

                if stable_count[i] >= stable_limit:
                    last_change_time[i] = time.time()

                    if raw_status[i] - initial_status[i] == 1 and Parking_lot[key] == 0:
                        Parking_lot[key] = 1
                        print(f"{key}: 🚗 Car Parked")
                    elif raw_status[i] - initial_status[i] == -1 and Parking_lot[key] == 1:
                        Parking_lot[key] = 0
                        print(f"{key}: 🏁 Car Left")

                    initial_status[i] = raw_status[i]
                    stable_count[i] = 0
            else:
                stable_count[i] = 0

        print("🅿️ Parking Lot Status:", Parking_lot)
        print("Available slots:", list(Parking_lot.values()).count(0))
        print("-" * 50)
        time.sleep(2)

# Parking slot map: 0 = empty, 1 = occupied
Parking_lot = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0
}

initial_status = [0, 0, 0, 0, 0]
distance_threshold = 15  # cm — below this = car detected
stable_limit = 5 # number of consistent readings required
hold_time = 5 # optional delay for confirming car left

# 🔹 Per-slot counters
stable_count = [0, 0, 0, 0, 0]
last_change_time = [0, 0, 0, 0, 0]

# Initialize sensors (change when needed)
Sensors = [
        Ultrasonic(17, 18),
        Ultrasonic(16, 15),
        Ultrasonic(14, 13),
        Ultrasonic(12, 11),
        Ultrasonic(10, 9)
]

# Initialize gate/IR/LCD system (change when needed)
AIR_servo_sensors = Counter(AIR_entry_pin=19, AIR_exit_pin=20, servo_entry_pin=21, servo_exit_pin=22, parking_lot=Parking_lot)

# Main Program
if __name__ == "__main__":
    # Start ultrasonic monitor in background
    try:
        print("Starting ultrasonic monitoring in background...")
        _thread.start_new_thread(run_ultrasonic, ())
        
    except Exception as e:
        print("⚠️ Failed to start ultrasonic thread:", e)

    # Simulate car entry while ultrasonic is running in background
    try:
        while True:
            cmd = input("Enter 'in' or 'out' or 'showcars' or 'exit': ").strip().lower()
            if cmd == 'in':
                Plate = input("Enter plate number: ").strip().upper()
                AIR_servo_sensors.car_entry(Plate)
                AIR_servo_sensors.show_all_cars()

            elif cmd == 'out':
                Plate = input("Enter plate number: ").strip().upper()
                AIR_servo_sensors.car_exit(Plate)
                AIR_servo_sensors.show_all_cars()
            elif cmd == 'exit':
                print("Exiting program.")
                break
            else:
                print("Invalid command. Please type 'in', 'out', or 'exit'.")
                
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user. Exiting safely.")