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
import configs
import _thread
import urequests

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
                        data = {
                            "slot_id":  i,
                            "occupied": raw_status[i]
                        }
                        try:
                            response = urequests.post(f"http://{configs.PYTHON_SERVER_IP}:8890/update_status", json=data)
                            response.close()
                        except Exception as e:
                            print(f"Failed to send: {e}")
                        print(f"{key}: 🚗 Car Parked")
                    elif raw_status[i] - configs.INITIAL_STATUS[i] == -1 and parking_lot[key] == 1:
                        parking_lot[key] = 0
                        parking_slots[i].toggle_led(configs.LED_ON)
                        data = {
                            "slot_id":  i,
                            "occupied": raw_status[i]
                        }
                        try:
                            response = urequests.post(f"http://{configs.PYTHON_SERVER_IP}:8890/update_status", json=data)
                            response.close()
                        except Exception as e:
                            print(f"Failed to send: {e}")
                        print(f"{key}: 🏁 Car Left")

                    configs.INITIAL_STATUS[i] = raw_status[i]
                    stable_count[i] = 0
            else:
                stable_count[i] = 0
        time.sleep(0.5)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(configs.SSID, configs.PASSWORD)

if not wlan.isconnected():
    print("Connecting to Wi-Fi...")
    wlan.connect(configs.SSID, configs.PASSWORD)

    # wait up to 15 seconds
    for i in range(15):
        if wlan.isconnected():
            break
        print(f"  Waiting for connection... {i+1}/15")
        time.sleep(1)

if wlan.isconnected():
    print("✅ Connected successfully!")
    print("Network config:", wlan.ifconfig())
else:
    print("❌ Failed to connect. Check SSID/password/band and try connecting again.")
    sys.exit()

# Listen on corresponding port
addr = socket.getaddrinfo('0.0.0.0', configs.PORT)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(1)
print(f"Listening on {addr}...")

parking_lot = {
        "A1": 0,
        "B1": 0,
        "C1": 0,
        "D1": 0,
        "E1": 0
                }
available_slots = 5
nearest_slot = "A1" # defaulting the nearest parking slot to the first parking slot

# Ultrasonic Setup
parking_slots = [
    Ultrasonic(configs.TRIG_PIN_1, configs.ECHO_PIN_1, configs.LED_PIN_1, "A1"),
    Ultrasonic(configs.TRIG_PIN_2, configs.ECHO_PIN_2, configs.LED_PIN_2, "B1"),
    Ultrasonic(configs.TRIG_PIN_3, configs.ECHO_PIN_3, configs.LED_PIN_3, "C1"),
    Ultrasonic(configs.TRIG_PIN_4, configs.ECHO_PIN_4, configs.LED_PIN_4, "D1"),
    Ultrasonic(configs.TRIG_PIN_5, configs.ECHO_PIN_5, configs.LED_PIN_5, "E1")
]

# initial the led to power on
for parking_slot in parking_slots:
    parking_slot.toggle_led(configs.LED_ON)

# Gate Setup
entry_gate = Counter(configs.AIR_ENTRY_PIN, configs.SERVO_ENTRY_PIN, parking_lot,
                      configs.LCD_ENTRY_PIN, configs.I2C_SCL_ENTRY_PIN, configs.I2C_SDA_ENTRY_PIN)
exit_gate = Counter(configs.AIR_EXIT_PIN, configs.SERVO_EXIT_PIN, parking_lot,
                    configs.LCD_EXIT_PIN, configs.I2C_SCL_EXIT_PIN, configs.I2C_SDA_EXIT_PIN)

def send_response(client, status=200, body="OK", content_type="text/plain"):
    """Send an HTTP response with proper headers"""
    body_bytes = body.encode() if isinstance(body, str) else body
    headers = (
        f"HTTP/1.1 {status} OK\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        "Access-Control-Allow-Headers: Content-Type\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n\r\n"
    )
    client.send(headers)
    if body:
        client.send(body_bytes)


print("Starting ultrasonic thread...")
_thread.start_new_thread(run_ultrasonic, ())

# main loop
while True:
    client, addr = server.accept()
    print("Client connected from", addr)

    try:
        # Receive the first chunk of the request
        req = client.recv(1024).decode()
        if not req:
            client.close()
            continue

        # Show availability (non-blocking)
        entry_gate.show_availability()

        # --- Respond to CORS preflight OPTIONS ---
        if "OPTIONS" in req:
            send_response(client, status=200)
            client.close()
            continue

        # --- Handle POST /gate ---
        if "POST /gate" in req:
            try:
                body = req.split("\r\n\r\n", 1)[1]
                data = ujson.loads(body)
                gate = data.get("gate")
                action = data.get("action")
                print(f"Received command: {action} {gate} gate")

                if gate and action:
                    if gate == "entrance" and action == "open":
                        entry_gate.open_gate()
                        print("Admin has opened the gate entrance.")
                    elif gate == "entrance" and action == "close":
                        entry_gate.close_gate()
                        print("Admin has closed the gate entrance.")
                    elif gate == "exit" and action == "open":
                        exit_gate.open_gate()
                        print("Admin has opened the gate exit.")
                    elif gate == "exit" and action == "close":
                        exit_gate.close_gate()
                        print("Admin has closed the gate exit.")

                    response = ujson.dumps({"status": "ok", "gate": gate, "action": action})
                    send_response(client, status=200, body=response, content_type="application/json")
                else:
                    send_response(client, status=400, body="Invalid command")
            except Exception as e:
                print("Error:", e)
                send_response(client, status=400, body="Invalid request")
            finally:
                client.close()
            continue

        # --- Handle POST /data ---
        elif "POST /data" in req:
            try:
                # Split headers and partial body
                parts = req.split("\r\n\r\n", 1)
                headers = parts[0]
                body = parts[1] if len(parts) > 1 else ""

                # Extract Content-Length
                content_length = 0
                for line in headers.split("\r\n"):
                    if "Content-Length" in line:
                        content_length = int(line.split(":")[1].strip())
                        break

                # Read the rest of the body if incomplete
                while len(body) < content_length:
                    chunk = client.recv(1024)
                    if not chunk:
                        break
                    body += chunk.decode()

                print("📥 Full body received:", body)

                # Parse JSON safely
                data = ujson.loads(body)
                print("📦 Parsed data:", data)

                # ✅ Send HTTP response immediately
                send_response(client, status=200, body="Data received")

                # ✅ Allow time for TCP to flush the response
                import time
                time.sleep(0.1)

                # ✅ Then close the socket
                client.close()

                # Process car plate logic (non-blocking)
                plate = data.get("car_plate")
                if plate not in number_plates:
                    entry_gate.car_entry(plate)
                else:
                    fee = data.get("fee")
                    exit_gate.car_exit(plate, fee)
                    entry_gate.show_availability()

            except Exception as e:
                print("❌ Error parsing car data:", e)
                send_response(client, status=400, body="Invalid JSON")
                time.sleep(0.1)
                client.close()
            continue

        else:
            send_response(client, status=404, body="Not Found")
            time.sleep(0.1)
            client.close()


    except OSError as e:
        print(f"Connection error: {e}")
    finally:
        client.close()
        print("Connection closed, waiting for next client...")



