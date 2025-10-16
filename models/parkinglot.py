from machine import Pin 
import time 

Parking_lot = {"A01": "False", "A02": "False", "A03": "False", "A04": "False", "A05": "False"}
Pir1 = Pin(14, Pin.IN)
Pir2 = Pin(11, Pin.IN)
Pir3 = Pin(15, Pin.IN)
Pir4 = Pin(13, Pin.IN)
Pir5 = Pin(12, Pin.IN)

Init_Occupancy = [0, 0, 0, 0, 0]
z = -1
keys = ["A01", "A02", "A03", "A04", "A05"]

# 🔹 stability + hold delay
stable_count = [0, 0, 0, 0, 0]
last_trigger_time = [0, 0, 0, 0, 0]
threshold = 2       # number of consistent readings before confirming
hold_time = 5       # seconds to wait to confirm car parked or left

while True:
    Occupancy = [Pir1.value(), Pir2.value(), Pir3.value(), Pir4.value(), Pir5.value()]
    print(Occupancy)
    current_time = time.time()

    for z, (x, y) in enumerate(zip(Occupancy, Init_Occupancy)):
        key = keys[z]

        # detect motion change
        if x != y:
            stable_count[z] += 1
        else:
            stable_count[z] = 0

        # only confirm if stable for a few cycles
        if stable_count[z] >= threshold:
            if x == 1:  
                # motion detected → record trigger time
                last_trigger_time[z] = current_time

            elif x == 0:  
                # no motion now → check time since last motion
                time_since_motion = current_time - last_trigger_time[z]

                if time_since_motion >= hold_time:
                    if Parking_lot[key] == "False":
                        # car has arrived and stayed → mark occupied
                        Parking_lot[key] = "True"
                        print(f"{key}: 🚗 Car Parked")
                    else:
                        # car was there, now left → mark empty
                        Parking_lot[key] = "False"
                        print(f"{key}: 🏁 Car Left")

            Init_Occupancy[z] = x
            stable_count[z] = 0  # reset after confirmation

    # 🔹 Count number of occupied slots (True)
    occupied_count = sum(1 for v in Parking_lot.values() if v == "True")
    total_slots = len(Parking_lot)
    print(Parking_lot)
    print(f"🅿️  Current Occupancy: {occupied_count}/{total_slots} slots occupied")

    time.sleep(1)