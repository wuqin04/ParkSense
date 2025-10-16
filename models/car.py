from datetime import datetime, timedelta
import random
import time

current_date_time = datetime.now()
time_to_add = timedelta(hours=5)
future_time = time_to_add + current_date_time
slot_list = [1, 2, 3, 4, 5]

# helper func
def update_time():
    now = datetime.now()
    now_display = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return now, now_display

class Car:
    def __init__(self, car_plate, time_in, slot_id, time_out) -> None:
        self.car_plate = car_plate
        self.time_in = time_in
        self.slot_id = slot_id
        self.time_out = time_out

        self.time_in_display = time_in.strftime('%Y-%m-%d %H:%M:%S')
        self.time_out_display = time_out.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Car plate: {self.car_plate}.")
        print(f"Time in: {self.time_in_display}.")
        print(f"Parking slot: {self.slot_id}.")
        print(f"Time out: {self.time_out_display}")    

    def update_time_out(self):
        self.time_out, self.time_out_display = update_time()
    
    def show_time_out(self):
        print(f"Time Out: {self.time_out_display}")

    # fee/duration logic here
    def calculate_fee(self):
        self.duration = self.time_out - self.time_in
        self.total_hr = self.duration.total_seconds() / 3600
        self.fee = (self.total_hr / 2)* 5
        print(f"Total Fee: RM{self.fee:.2f}")

    def set_car_plate(self, car_plate):
        self.car_plate = car_plate

car1 = Car("ABC123",current_date_time, random.choice(slot_list), future_time)
time.sleep(2)
car1.show_time_out()
car1.calculate_fee()
