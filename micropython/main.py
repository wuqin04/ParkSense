# THIS IS THE SERVER SIDE OF TCP SERVER WHICH WILL RECEIVE ANY DATA SENT BY CLIENT'S SIDE ON PYTHON
# THIS PROGRAM SHOULD ALWAYS BE RUNNING FIRST TO TEST THE SERVER CONNECTION

import network
import socket
import ujson
import time
import sys
from servo import Servo
from lcd_i2c import LCD
from ultrasonic import Ultrasonic
from gate_control import Counter
from machine import I2C, Pin
import configs as configs
import _thread

# Wi-Fi Setup
SSID = "Ming's"
PASSWORD = "88888888"

PORT = 8888

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

if not wlan.isconnected():
    print("Connecting to Wi-Fi...")
    wlan.connect(SSID, PASSWORD)

    # wait up to 15 seconds
    for i in range(15):
        if wlan.isconnected():
            break
        print(f"  Waiting... {i+1}/15")
        time.sleep(1)

if wlan.isconnected():
    print("✅ Connected successfully!")
    print("Network config:", wlan.ifconfig())
else:
    print("❌ Failed to connect. Check SSID/password/band.")
    sys.exit()

# TCP Server Setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", PORT))
server.listen(1)
print(f"Listening on port {PORT}...")

# Variables initialise
# parking slot map: 0 = empty, 1 = occupied
parking_lot = {
        "A1": 0,
        "A2": 0,
        "A3": 0,
        "A4": 0,
        "A5": 0
                }
available_slots = 5
nearest_slot = "A1" # defaulting the nearest parking slot to the first parking slot

# Ultrasonic Setup

parking_slot_1 = Ultrasonic(configs.TRIG_PIN_1, configs.ECHO_PIN_1, configs.LED_PIN_1, parking_lot["A1"])
parking_slot_2 = Ultrasonic(configs.TRIG_PIN_2, configs.ECHO_PIN_2, configs.LED_PIN_2, parking_lot["A2"])
parking_slot_3 = Ultrasonic(configs.TRIG_PIN_3, configs.ECHO_PIN_3, configs.LED_PIN_3, parking_lot["A3"])
parking_slot_4 = Ultrasonic(configs.TRIG_PIN_4, configs.ECHO_PIN_4, configs.LED_PIN_4, parking_lot["A4"])
parking_slot_5 = Ultrasonic(configs.TRIG_PIN_5, configs.ECHO_PIN_5, configs.LED_PIN_5, parking_lot["A5"])


# Gate Setup
entry_gate = Counter(configs.AIR_ENTRY_PIN, configs.SERVO_ENTRY_PIN, parking_lot, configs.LCD_ENTRY_PIN,
                        configs.I2C_SCL_ENTRY_PIN, configs.I2C_SDA_ENTRY_PIN)
exit_gate = Counter(configs.AIR_EXIT_PIN, configs.SERVO_EXIT_PIN, parking_lot, configs.LCD_EXIT_PIN,
                        configs.I2C_SCL_EXIT_PIN, configs.I2C_SDA_EXIT_PIN)


while True:
    conn, addr = server.accept()
    print(f"Connection from {addr}")
    
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                print("Client disconnected.")
                break

            try:
                configs.Debug("Starting LCD Thread")
                _thread.start_new_thread(entry_gate.lcd_idle_loop, ())

                while True:
                    info = ujson.loads(data)
                    print(f"Received: {info}")
                    plate = info.get("car_plate")

                    # entry_gate logic
                    if plate not in entry_gate.num_plate:
                        entry_gate.car_entry(plate)
                        plate = None
                    # exit_gate logic
                    else:
                        fee = info.get("fee")
                        exit_gate.car_exit(plate, fee)

                    while True:
                        print("Enter the loop")
                        print(parking_slot_1.measure())
                        parking_slot_1.run()

                # # === Parking Lot Setup ===
                # Parking_lot = {1: 0}  # 1 slot (0 = empty, 1 = occupied)
                # stable_count = [0]
                # last_change_time = [0]
                # initial_status = [0]

                # # === Stability Control Parameters ===
                # distance_threshold = 15   # cm
                # stable_limit = 3
                # hold_time = 5

                # # === Globals for status tracking ===
                # available_slot = 1
                # nearest_slot = 1  # default for single-slot setup
                # total_slot = 1

                # # === Hardware Setup ===
                # Sensors = [Ultrasonic(trig_pin=20, echo_pin=21)]
                # AIR = Pin(27, Pin.IN)  # IR sensor near gate
                # gate = Counter(AIR_entry_pin=27, AIR_exit_pin=15,
                #                servo_entry_pin=28, servo_exit_pin=12,
                #                parking_lot=Parking_lot)

                # # === Ultrasonic Background Thread ===
                # def run_ultrasonic():
                #     global Parking_lot, initial_status, stable_count, last_change_time
                #     global available_slot, nearest_slot

                #     while True:
                #         distance_list = [sensor.measure() for sensor in Sensors]
                #         raw_status = [1 if d is not None and d <= distance_threshold else 0 for d in distance_list]

                #         for i, key in enumerate(Parking_lot.keys()):
                #             if raw_status[i] != initial_status[i]:
                #                 stable_count[i] += 1
                #                 if stable_count[i] >= stable_limit:
                #                     Parking_lot[key] = raw_status[i]
                #                     initial_status[i] = raw_status[i]
                #                     stable_count[i] = 0
                #             else:
                #                 stable_count[i] = 0

                #         available_slot = sum(1 for v in Parking_lot.values() if v == 0)
                #         nearest_slot = None if available_slot == 0 else 1

                #         time.sleep(2)

                # # Start background thread
                # _thread.start_new_thread(run_ultrasonic, ())
                
                # # === Main Program Loop ===
                # while True:
                #     if total_slot > 0:
                #         gate.display_lcd("Available:", str(total_slot))
                #     else:
                #         gate.display_lcd("PARKING FULL", "")
                #         nearest_slot = None
                    
                #     plate_detected = None
                #     if plate is not None:
                #         plate_detected = True
                #     else:
                #         plate_detected = False

                #     # entrance servo
                #     if plate_detected and total_slot >= 1:
                #         gate.display_lcd("Nearest Slot:", str(nearest_slot))
                #         gate.display_lcd("Proceed to Slot", str(nearest_slot))
                #         gate.open_gate()
                #         while AIR.value() == 1:
                #             print("Waiting for car to enter...")
                #             time.sleep(0.5)
                #         while AIR.value() == 0:
                #             print("Car detected, waiting for it to pass...")
                #             time.sleep(0.5)
                #         print("✅ Car passed — closing gate.")
                #         gate.close_gate()
                #         total_slot-=1

                    # === Car Exiting ===
#                     elif action == 'exit':
#                         gate.display_lcd("Thank You", "See You Again!")
#                         gate.open_gate()
#                         while AIR.value() == 1:
#                             print("Waiting for car at exit...")
#                             time.sleep(0.5)
#                         while AIR.value() == 0:
#                             print("Car leaving...")
#                             time.sleep(0.5)
#                         print("✅ Car left — closing gate.")
#                         gate.close_gate()
#                         total_slot+=1

                    # exit servo logic here
                                
                ## example below is to create response and format as .json
                # response = {"status": "authorized", "plate": plate}
                
                ## example below is to send the response created earlier to client's side
                # conn.send(ujson.dumps(response).encode())

            except ValueError:
                conn.send(b'{"error":"invalid_json"}')

    except OSError as e:
        print("Connection error:", e)
    finally:
        conn.close()
        print("Connection closed, waiting for next client...")


