from machine import Pin, time_pulse_us
import time

# 🔹 Parking slots dictionary
Parking_lot = {"A01": "False", "A02": "False", "A03": "False", "A04": "False", "A05": "False"}
initial_status = [0, 0, 0, 0, 0]

# 🔹 Stability parameters
distance_threshold = 15   # cm — below this = car detected
stable_limit = 5          # number of consistent readings required
hold_time = 5             # optional delay for confirming car left

# 🔹 Per-slot counters
stable_count = [0, 0, 0, 0, 0]
last_change_time = [0, 0, 0, 0, 0]

# 🔹 Ultrasonic sensor class
class Ultrasonic:
    def __init__(self, trig_pin, echo_pin, unit="cm", timeout=30000):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.unit = unit
        self.timeout = timeout
        self.sound_speed = 343  # m/s at ~25°C

    def measure(self):
        self.trig.low()
        time.sleep_us(2)
        self.trig.high()
        time.sleep_us(10)
        self.trig.low()
        duration = time_pulse_us(self.echo, 1, self.timeout)
        distance_cm = (duration / 2) / 29.1  # convert to cm
        return distance_cm if self.unit == "cm" else distance_cm / 100


# 🔹 Initialize sensors (adjust pins as needed)
Sensors = [
    Ultrasonic(17, 18),
    Ultrasonic(16, 15),
    Ultrasonic(14, 13),
    Ultrasonic(12, 11),
    Ultrasonic(10, 9)
]

while True:
    distance_list = []
    for sensor in Sensors:
        distance = sensor.measure()
        distance_list.append(distance)

    print("📏 Distances (cm):", ["{:.1f}".format(d) for d in distance_list])

    # 🔹 Determine current raw states
    raw_status = []
    for dist in distance_list:
        raw_status.append(1 if dist <= distance_threshold else 0)

    # 🔹 Apply stability filtering
    for i, key in enumerate(Parking_lot.keys()):
        if raw_status[i] != initial_status[i]:
            # State fluctuating
            stable_count[i] += 1
            print(f"{key}: Reading unstable ({stable_count[i]}/{stable_limit})")

            # Confirm only after stable_limit consistent changes
            if stable_count[i] >= stable_limit:
                last_change_time[i] = time.time()

                # Car parked
                if raw_status[i] - initial_status[i] == 1 and Parking_lot[key] == "False":
                    Parking_lot[key] = "True"
                    print(f"{key}: 🚗 Car Parked")

                # Car left
                elif raw_status[i] - initial_status[i] == -1 and Parking_lot[key] == "True":
                    Parking_lot[key] = "False"
                    print(f"{key}: 🏁 Car Left")

                # Update status after confirmation
                initial_status[i] = raw_status[i]
                stable_count[i] = 0  # reset
        else:
            # Reset counter if stable
            stable_count[i] = 0

    # 🔹 Print summary
    print("🅿️ Parking Lot Status:", Parking_lot)
    print("-" * 50)

    # Fix: dicts don’t have count() — use list comprehension
    available_slot = list(Parking_lot.values()).count("False")
    print("Available slot(s):", available_slot)

    time.sleep(2)
   
   
   
   
   
   
   
   
  
    