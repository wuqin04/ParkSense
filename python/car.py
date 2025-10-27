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
        self.fee = 0

        self.enter_time_display = enter_time.strftime('%Y-%m-%d %H:%M:%S')
        self.exit_time_display = None   

    def exit(self):
        self.exit_time, self.exit_time_display = update_time()
        self.fee = self.calculate_fee()
    
    def show_exit_time(self):
        print(f"Time Out: {self.exit_time_display}")

    # fee/duration logic here
    def calculate_fee(self):
        duration = self.exit_time - self.enter_time
        total_secs = duration.total_seconds()
        fee =  round(total_secs / 100)
        return 20 if fee >= 20 else fee

    # change the format to dict to store into the .json format
    def to_dict(self):
        return {
            "car_plate":    self.car_plate,
            "entry_time":   self.enter_time_display,
            "exit_time":    self.exit_time_display,
            "fee":          self.fee
        }

