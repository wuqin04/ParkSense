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
        self.raw_status = 0

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

    def toggle_led(self, toggle):
        self.led.value(toggle)
        
    def get_parking_slot(self):
        return str(self.parking_slot)

