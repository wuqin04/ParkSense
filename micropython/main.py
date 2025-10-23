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
from gate_control import Counter, number_plates
from machine import I2C, Pin
import configs as configs
import _thread

def run_ultrasonic():        
    global parking_lot, parking_slots
    stable_count = [0, 0, 0, 0, 0]

    while True:
        distance_list = [parking_slot.measure() for parking_slot in parking_slots]
        # print("\n📏 Distances (cm):", ["{:.1f}".format(d) for d in distance_list])

        raw_status = [1 if d <= configs.DISTANCE_THRESHOLD else 0 for d in distance_list]

        for i, key in enumerate(parking_lot.keys()):
            if raw_status[i] != configs.INITIAL_STATUS[i]:
                stable_count[i] += 1
                print(f"{key}: Unstable ({stable_count[i]}/{configs.STABLE_LIMIT})")

                if stable_count[i] >= configs.STABLE_LIMIT:
                    if raw_status[i] - configs.INITIAL_STATUS[i] == 1 and parking_lot[key] == 0:
                        parking_lot[key] = 1
                        parking_slots[i].toggle_led(configs.LED_OFF)
                        print(f"{key}: 🚗 Car Parked")
                    elif raw_status[i] - configs.INITIAL_STATUS[i] == -1 and parking_lot[key] == 1:
                        parking_lot[key] = 0
                        parking_slots[i].toggle_led(configs.LED_ON)
                        print(f"{key}: 🏁 Car Left")

                    configs.INITIAL_STATUS[i] = raw_status[i]
                    stable_count[i] = 0
            else:
                stable_count[i] = 0

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
parking_slots = [
    Ultrasonic(configs.TRIG_PIN_1, configs.ECHO_PIN_1, configs.LED_PIN_1, parking_lot["A1"]),
    Ultrasonic(configs.TRIG_PIN_2, configs.ECHO_PIN_2, configs.LED_PIN_2, parking_lot["A2"]),
    Ultrasonic(configs.TRIG_PIN_3, configs.ECHO_PIN_3, configs.LED_PIN_3, parking_lot["A3"]),
    Ultrasonic(configs.TRIG_PIN_4, configs.ECHO_PIN_4, configs.LED_PIN_4, parking_lot["A4"]),
    Ultrasonic(configs.TRIG_PIN_5, configs.ECHO_PIN_5, configs.LED_PIN_5, parking_lot["A5"])
]

# Gate Setup
entry_gate = Counter(configs.AIR_ENTRY_PIN, configs.SERVO_ENTRY_PIN, parking_lot,
                      configs.LCD_ENTRY_PIN, configs.I2C_SCL_ENTRY_PIN, configs.I2C_SDA_ENTRY_PIN)
exit_gate = Counter(configs.AIR_EXIT_PIN, configs.SERVO_EXIT_PIN, parking_lot,
                    configs.LCD_EXIT_PIN, configs.I2C_SCL_EXIT_PIN, configs.I2C_SDA_EXIT_PIN)


_thread.start_new_thread(run_ultrasonic, ())
while True:
    conn, addr = server.accept()
    print(f"Connection from {addr}")
    
    try:
        while True:
            entry_gate.show_availability()
            
            configs.Debug("Starting Ultrasonic Thread")

            while True:
                data = conn.recv(1024)
                if not data:
                    print("Client disconnected.")
                    break
                try:
                    info = ujson.loads(data)
                except ValueError:
                    print(f"Invalid JSON received.")
                    continue
                
                print(f"Received: {info}")
                plate = info.get("car_plate")

                # entry_gate logic
                if plate not in number_plates:
                    entry_gate.car_entry(plate)
                # exit_gate logic
                else:
                    print(plate)
                    fee = info.get("fee")
                    exit_gate.car_exit(plate, fee)

    except OSError as e:
        print("Connection error:", e)
    finally:
        conn.close()
        print("Connection closed, waiting for next client...")


