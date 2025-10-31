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

# Listen on port 80
addr = socket.getaddrinfo('0.0.0.0', configs.PORT)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("Listening on", addr)

parking_lot = {
        "A1": 0,
        "B1": 0,
        "C1": 0,
        "D1": 0,
        "E1": 0
                }

# Gate Setup
entry_gate = Counter(configs.AIR_ENTRY_PIN, configs.SERVO_ENTRY_PIN, parking_lot,
                      configs.LCD_ENTRY_PIN, configs.I2C_SCL_ENTRY_PIN, configs.I2C_SDA_ENTRY_PIN)
exit_gate = Counter(configs.AIR_EXIT_PIN, configs.SERVO_EXIT_PIN, parking_lot,
                    configs.LCD_EXIT_PIN, configs.I2C_SCL_EXIT_PIN, configs.I2C_SDA_EXIT_PIN)

def send_response(client, status=200, body="OK", content_type="text/plain"):
    """Send an HTTP response with proper CORS headers"""
    headers = (
        f"HTTP/1.1 {status} OK\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        "Access-Control-Allow-Headers: Content-Type\r\n"
        f"Content-Type: {content_type}\r\n"
        "Connection: close\r\n\r\n"
    )
    client.send(headers)
    if body:
        client.send(body)

while True:
    client, addr = s.accept()
    print("Client connected from", addr)
    req = client.recv(1024).decode()
    print("Request:", req)

    # Respond to CORS preflight OPTIONS
    if "OPTIONS" in req:
        send_response(client, status=200)
        client.close()
        continue

    # Handle POST /gate
    if "POST /gate" in req:
        try:
            # Extract JSON from request body
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

    elif "POST /data" in req:
        try:
            body = req.split("\r\n\r\n", 1)[1]
            data = ujson.loads(body)
            print("📥 Received car data:", data)
                        
            send_response(client, status=200, body="Data received")
            client.close()

            plate = data.get("car_plate")

             # entry_gate logic
            if plate not in number_plates:
                entry_gate.car_entry(plate)
            # exit_gate logic
            else:
                fee = data.get("fee")
                exit_gate.car_exit(plate, fee)
                entry_gate.show_availability()
            continue
        except Exception as e:
            print("❌ Error parsing car data:", e)
            send_response(client, status=400, body="Invalid JSON")
            client.close()
            continue
    else:
        send_response(client, status=404, body="Not Found")

    client.close()
    continue

