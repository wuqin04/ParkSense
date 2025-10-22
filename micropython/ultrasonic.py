# ultrasonic.py
from machine import Pin, time_pulse_us
import time
import configs

class Ultrasonic:
    def __init__(self, trig_pin, echo_pin, led_pin, parking_slot, unit="cm", timeout=30000):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.led = Pin(led_pin, Pin.OUT)
        self.parking_slot = parking_slot
        self.unit = unit
        self.timeout = timeout

    # measure the distance in unit cm
    def measure(self):
        self.trig.low()
        time.sleep_us(2)
        self.trig.high()
        time.sleep_us(10)
        self.trig.low()
        duration = time_pulse_us(self.echo, 1, self.timeout)
        distance_cm = (duration / 2) / 29.1
        return distance_cm if self.unit == "cm" else distance_cm / 100
    
    def run(self):
        while True:
            self.stable_count = 0
            self.distance = self.measure()
            self.raw_status = 1 if self.distance <= configs.DISTANCE_THRESHOLD else 0 

            self.update_status(self.parking_slot)


        # self.distance_list = [sensor.measure() for sensor in sensors]
        # print("\n📏 Distances (cm):", ["{:.1f}".format(d) for d in self.distance_list])

        # self.raw_status = [1 if d <= configs.DISTANCE_THRESHOLD else 0 for d in self.distance_list]

    def update_status(self, parking_slot): 
        self.stable_count = 0

        if self.raw_status != configs.INITIAL_STATUS:
            self.stable_count += 1
            if self.stable_count >= configs.STABLE_LIMIT:
                parking_lot = self.raw_status
                self.led.value(self.raw_status)
                configs.INITIAL_STATUS = self.raw_status
                self.stable_count = 0
        else:
            self.stable_count = 0
            