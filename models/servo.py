from servo import Servo
import time

my_servo = Servo(pin_id=28)
my_servo.write(0)
time.sleep(1)
for angle in range(0,90, 5):
    my_servo.write(angle)
    time.sleep(0.1)
time.sleep(5)
for angle in range(0,90, 5):
    my_servo.write(90-angle)
    time.sleep(0.1)