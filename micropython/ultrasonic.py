# ultrasonic.py
from machine import Pin, time_pulse_us
import time

class Ultrasonic:
    def __init__(self, trig_pin, echo_pin, unit="cm", timeout=30000):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.unit = unit
        self.timeout = timeout

    def measure(self):
        self.trig.low()
        time.sleep_us(2)
        self.trig.high()
        time.sleep_us(10)
        self.trig.low()
        duration = time_pulse_us(self.echo, 1, self.timeout)
        distance_cm = (duration / 2) / 29.1
        return distance_cm if self.unit == "cm" else distance_cm / 100
