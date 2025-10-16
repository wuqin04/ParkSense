from datetime import datetime
import random
import time

current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
slot_list = [1, 2, 3, 4, 5]

def update_time():
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return time

class Car:
    def __init__(self, car_plate, time_in, slot_id, time_out) -> None:
        self.car_plate = car_plate
        self.time_in = time_in
        self.slot_id = slot_id
        self.time_out = time_out
        
        print(f"Car plate: {self.car_plate}.")
        print(f"Time in: {self.time_in}.")
        print(f"Parking slot: {self.slot_id}.")
        print(f"Time out: {self.time_out}")    

    def set_time_out(self):
        self.time_out = update_time()
    
    def show_time_out(self):
        print(f"Time Out: {self.time_out}")

car1 = Car("ABC123",current_date_time, random.choice(slot_list), None)
time.sleep(2)
car1.set_time_out()
car1.show_time_out()
