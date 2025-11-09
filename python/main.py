# THIS IS THE CLIENT'S SIDE OF TCP SERVER WHICH WILL SEND DATA TO THE SERVER TCP
# THIS PROGRAM SHOULD BE RUN AFTER THE SERVER SIDE OF CODE HAVE ALREADY RUNNING

import cv2 as cv
import easyocr
import time
from datetime import datetime, timedelta
import json
import socket
from car import Car
import database
import requests
import threading
import sys
import os

# Get the parent directory of the current file
parent_dir = os.path.dirname(os.path.dirname(__file__))

# Add parent directory to sys.path
sys.path.append(parent_dir)

# Now you can import
import micropython.configs as configs

# Socket Setup
MICROPYTHON_IP = configs.MICROPYTHON_IP
MICROPYTHON_PORT = 8888

# OCR + Cam Setup
reader = easyocr.Reader(['en'], gpu=True)

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

confirmed_plates = []
font = cv.FONT_HERSHEY_SIMPLEX

def send_to_esp(data, label=""):
    try:
        response = requests.post(f"http://{MICROPYTHON_IP}:{MICROPYTHON_PORT}/data", json=data, timeout=3)
        print(f"📤 Sent to ESP ({label}): {data}")
        print(f"📥 ESP response: {response.text}")
    except Exception as e:
        print(f"❌ Failed to send {label} data: {e}")

def occupancy_listener():
    HOST = "0.0.0.0"
    OCCUPANCY_PORT = 8890

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, OCCUPANCY_PORT))
    server.listen(3)
    print(f"Occupancy listener running on {HOST}:{OCCUPANCY_PORT}...")

    database.default_occupancy()
    
    while True:
        client, addr = server.accept()
        print("📡 Occupancy connection from", addr)

        try:
            # accumulate headers
            req = b""
            while b"\r\n\r\n" not in req:
                req += client.recv(1024)

            headers, body = req.split(b"\r\n\r\n", 1)
            headers_text = headers.decode()
            path_line = headers_text.split("\r\n")[0]
            method, path, _ = path_line.split(" ")

            if method == "POST" and path == "/update_status":
                # get content-length
                content_length = 0
                for line in headers_text.split("\r\n"):
                    if line.lower().startswith("content-length"):
                        content_length = int(line.split(":")[1].strip())

                while len(body) < content_length:
                    body += client.recv(1024)

                data = json.loads(body.decode())
                print("📥 Received occupancy update:", data)

                 # ✅ Load existing data
                with open("occupancy.json", "r") as f:
                    occupancy_data = json.load(f)

                # ✅ Update the matching slot_id
                updated = False
                for slot in occupancy_data:
                    if slot["slot_id"] == data["slot_id"]:
                        slot["occupancy"] = data["occupancy"]
                        updated = True
                        break

                if not updated:
                    print(f"⚠️ Slot ID {data['slot_id']} not found — ignoring update.")
                database.save_data(occupancy_data, path="occupancy.json")

                client.send(b"HTTP/1.1 200 OK\r\nContent-Length: 8\r\n\r\nReceived")

            else:
                client.send(b"HTTP/1.1 404 Not Found\r\nContent-Length: 9\r\n\r\nNot Found")

        except Exception as e:
            print("❌ Occupancy error:", e)
            client.send(b"HTTP/1.1 400 Bad Request\r\nContent-Length: 5\r\n\r\nError")
        finally:
            client.close()

# main loop
frame_count = 0
threading.Thread(target=occupancy_listener, daemon=True).start()
while True:
    recentresult = []

    # Capture 5 readings (~5 seconds)
    for x in range(5):
        ret, frame = cap.read()

        if not ret:
            print("⚠️ Camera frame not captured.")
            break

        # OCR read
        results = reader.readtext(frame)
        extracted_texts = [text for (_, text, _) in results]

        # Combine all text in this frame
        combined_text = " ".join(extracted_texts).strip() if extracted_texts else None
        if combined_text:
            # Separate alphabets and numbers
            letters = "".join(ch for ch in combined_text if ch.isalpha())
            numbers = "".join(ch for ch in combined_text if ch.isdigit())

            # Combine with letters first, numbers after
            formatted_plate = letters + numbers

            recentresult.append(formatted_plate)

        # Draw bounding boxes
        for (bbox, text, confidence) in results:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            cv.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            cv.putText(frame, text, (top_left[0], top_left[1] - 10),
            cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        # Display detected text
        if combined_text:
            cv.putText(frame, f"Detected: {combined_text}", (30, 40), font, 0.7, (0, 255, 0), 2)
        else:
            cv.putText(frame, "No text detected", (30, 40), font, 0.7, (0, 0, 255), 2)

        cv.imshow("License Plate Detection", frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv.destroyAllWindows()
            exit()

        time.sleep(0.5)

    # analyze result
    if recentresult:
        # get the most detected car plate as the result
        verify = max(set(recentresult), key=recentresult.count)
        frequency = recentresult.count(verify)

        if frequency >= 5 and verify not in confirmed_plates:
            confirmed_plates.append(verify)
            print(f"✅ Confirmed plate: {verify}")

            # handle database and .json format here
            file_path = "data.json"
            all_data = database.load_data(file_path)

            existing_car = next((c for c in all_data["cars"] if c["car_plate"] == verify), None)

            now = datetime.now()
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
            
            car = Car(verify, now)
            car_data = car.to_dict()

            found = False

            for existing_car in all_data["cars"]:
                if existing_car["car_plate"] == car_data["car_plate"]:
                    found = True
                    # Check if this car already exited → allow re-entry
                    if existing_car.get("exit_time"):
                        print(f"🔁 {verify} re-entering (previously exited).")
                        existing_car.update(car_data)
                    else:
                        print(f"⚠️ {verify} is already parked — ignoring duplicate entry.")
                    break

            if not found:
                # Count only active cars (without exit_time)
                active_cars = [c for c in all_data["cars"] if c.get("exit_time") is None]

                if len(active_cars) < 5:
                    all_data["cars"].append(car_data)
                    print(f"✅ Added new car {verify}. Active count: {len(active_cars)+1}/5")
                else:
                    print("🚫 Parking full (5 active cars). Entry denied.")
                    continue  # skip saving if lot is full

            database.save_data(all_data, file_path)

            print("✅ JSON updated:", json.dumps(car_data, indent=4))

            # convert python data into json data
            json_data = json.dumps(car_data)

            # send to MicroPython
            try:
                threading.Thread(target=send_to_esp, args=(car_data, "entry"), daemon=True).start()
            except Exception as e:
                print(f"Failed to send data: {e}")

        elif frequency >= 5 and verify in confirmed_plates:
            # handle json data here
            file_path = "data.json"
            all_data = database.load_data(file_path)

            existing_car = next((c for c in all_data["cars"] if c["car_plate"] == verify), None)

            now = datetime.now()
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')

            if existing_car:
                entry_time = datetime.strptime(existing_car["entry_time"], "%Y-%m-%d %H:%M:%S")
                car = Car(existing_car["car_plate"], entry_time)

                car.exit()

                updated_data = car.to_dict()
                existing_car.update(updated_data)

                database.save_data(all_data, file_path)

                confirmed_plates.remove(verify)

                # exit_data = updated_data.copy()
                print("✅ JSON updated:", json.dumps(updated_data, indent=4))

                # json_data = json.dumps(exit_data)
                try:
                    threading.Thread(target=send_to_esp, args=(updated_data, "exit"), daemon=True).start()
                except Exception as e:
                    print(f"Failed to send the exit data: {e}")
            else:
                print("Warning! Car not found in JSON.")
    else:
        print("⚠️ No text detected in last 10 frames.")

    # Display confirmed plates
    if confirmed_plates:
        text_y = 80
        for plate in confirmed_plates[-3:]:
            cv.putText(frame, f"Confirmed: {plate}", (30, text_y), font, 0.7, (255, 255, 0), 2)
            text_y += 35

    cv.imshow("License Plate Detection", frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
