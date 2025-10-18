import cv2 as cv
import easyocr
import time
import json
import socket

# ====== SOCKET SETUP ======
# Change to your MicroPython IP and port
MICROPYTHON_IP = "192.168.250.193"   # adjust this (check with 'ifconfig' on Pico)
MICROPYTHON_PORT = 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)

try:
    sock.connect((MICROPYTHON_IP, MICROPYTHON_PORT))
    print(f"✅ Connected to MicroPython at {MICROPYTHON_IP}:{MICROPYTHON_PORT}")
except Exception as e:
    print(f"⚠️ Connection failed: {e}")
    sock = None

# ====== OCR + CAMERA SETUP ======
reader = easyocr.Reader(['en'], gpu=False)

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

authorized_plates = ["JPQ300", "ABC1234", "ABC5678", "VCN4961", "PMM6175", "MDM7000"]
confirmed_plates = []
font = cv.FONT_HERSHEY_SIMPLEX

# ====== MAIN LOOP ======
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
            recentresult.append(combined_text)

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

    # ====== ANALYZE RESULTS ======
    if recentresult:
        verify = max(set(recentresult), key=recentresult.count)
        frequency = recentresult.count(verify)

        if frequency >= 5 and verify not in confirmed_plates:
            confirmed_plates.append(verify)
            print(f"✅ Confirmed plate: {verify}")

            # Prepare JSON data with formatting
            data = {
                "timestamp": time.time(),
                "plate": verify,
                "authorized": verify in authorized_plates
            }

            json_data = json.dumps(data)

            # Save locally
            with open("detections.json", "a") as f:
                f.write(json_data + "\n")

            # Send to MicroPython
            if sock:
                try:
                    sock.send((json_data + "\n").encode())
                    print("📤 Sent to MicroPython:", json_data)
                except Exception as e:
                    print(f"⚠️ Failed to send: {e}")
            else:
                print("⚠️ No active socket connection.")

            # Local feedback
            if verify in authorized_plates:
                print("🚘 Authorized → Gate open signal sent")
            else:
                print("⛔ Unauthorized → Access denied")
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
