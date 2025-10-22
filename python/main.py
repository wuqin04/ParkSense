# THIS IS THE CLIENT'S SIDE OF TCP SERVER WHICH WILL SEND DATA TO THE SERVER TCP
# THIS PROGRAM SHOULD BE RUN AFTER THE SERVER SIDE OF CODE HAVE ALREADY RUNNING

import cv2 as cv
import easyocr
import time
from datetime import datetime, timedelta
import json
import os
import socket
from car import Car
import database

# Socket Setup
MICROPYTHON_IP = "10.38.61.193"
MICROPYTHON_PORT = 8888 # change the port if it doesn't connect

# TCP Client Setup
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(15)

try:
    sock.connect((MICROPYTHON_IP, MICROPYTHON_PORT))
    print(f"✅ Connected to MicroPython at {MICROPYTHON_IP}:{MICROPYTHON_PORT}")
except Exception as e:
    print(f"⚠️ Connection failed: {e}")
    sock = None

# OCR + Cam Setup
reader = easyocr.Reader(['en'], gpu=False)

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

confirmed_plates = []
font = cv.FONT_HERSHEY_SIMPLEX

# main loop
while True:
    recentresult = []

    # Capture 10 readings (~5 seconds)
    for x in range(10):
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
            
            # TIME_OUT UPDATE HERE
            for existing_car in all_data["cars"]:
                if existing_car["car_plate"] == car_data["car_plate"]:
                    car.update_time_out()
                    car.calculate_fee()
                    existing_car.update(car_data)    
                    found = True
                    break

            if not found:
                all_data["cars"].append(car_data)

            database.save_data(all_data, file_path)

            print("✅ JSON updated:", json.dumps(car_data, indent=4))

            # convert python data into json data
            json_data = json.dumps(car_data)

            # send to MicroPython
            if sock:
                try:
                    sock.send((json_data + "\n").encode())
                    print("📤 Sent to MicroPython:", json_data)
                except Exception as e:
                    print(f"⚠️ Failed to send: {e}")
            else:
                print("⚠️ No active socket connection.")

        else:
            print(f"Most frequent: {verify} ({frequency}/10)")
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

if sock:
    sock.close()
    print("🔌 Socket closed.")
