class Passenger:
    def __init__(self, row, column, aisle_to_seat_time):
        self.row = row
        self.column = column
        self.aisle_to_seat_time = aisle_to_seat_time
        self.location = 0
        self.is_seated = False
        self.is_getting_in_seat = False
        self.is_stopped = False
        self.starting_getting_in_seat_tick = None

    def __str__(self):
        return f'Passenger: {self.row}, {self.column}, {self.location}'
