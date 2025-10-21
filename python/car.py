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
    def __init__(self, car_plate, enter_time, slot_id = None, exit_time = None, fee = None) -> None:
        self.car_plate = car_plate
        self.enter_time = enter_time
        self.slot_id = slot_id
        self.exit_time = exit_time
        self.fee = None

        self.enter_time_display = enter_time.strftime('%Y-%m-%d %H:%M:%S')
        self.exit_time_display = None
        
        print(f"Car plate: {self.car_plate}.")
        print(f"Time in: {self.enter_time_display}.")
        print(f"Parking slot: {self.slot_id}.")
        print(f"Time out: {self.exit_time_display}")    

    def update_time_out(self):
        self.exit_time, self.exit_time_display = update_time()
    
    def show_time_out(self):
        print(f"Time Out: {self.exit_time_display}")

    # fee/duration logic here
    def calculate_fee(self):
        self.duration = self.exit_time - self.enter_time
        self.total_hr = self.duration.total_seconds() / 3600
        self.fee = (self.total_hr / 2) * 5
        print(f"Total Fee: RM{self.fee:.2f}")

    def set_car_plate(self, car_plate):
        self.car_plate = car_plate

    # change the format to dict to store into the .json format
    def to_dict(self):
        return {
            "car_plate":    self.car_plate,
            "slot_id":      self.slot_id,
            "enter_time":   self.enter_time_display,
            "exit_time":    self.exit_time_display,
            "fee":          self.fee
        }

