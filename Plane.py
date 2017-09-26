class Row:
    def __init__(self):
        self.left_side = [False, False, False]
        self.right_side = [False, False, False]
        self.left_side_boarding = False
        self.right_side_boarding = False

    def __str__(self):
        row = ''
        for i in self.left_side:
            row += '1' if i else '0'
        row += ' '
        for i in self.right_side:
            row += '1' if i else '0'
        return row


class Plane:
    def __init__(self, num_rows=30):
        self.num_rows = num_rows
        self.seats_per_row = 6
        self.seats = [Row() for _ in range(num_rows)]

    def __str__(self):
        plane = ''
        for r, row in enumerate(self.seats):
            plane += f'{r+1}. '
            if r < 9:
                plane += ' '
            plane += f'{row}\n'
        return plane

    def occupy_seat(self, row, column):
        if row > self.num_rows or column > self.seats_per_row or row < 1 or column < 1:
            raise Exception('Invalid seat position')
        plane_row = self.seats[row - 1]
        if column <= 3:
            plane_row.left_side[column - 1] = True
        else:
            plane_row.right_side[column - 4] = True

    def is_finished_boarding(self):
        for row in self.seats:
            for seat in row.left_side:
                if not seat:
                    return False
            for seat in row.right_side:
                if not seat:
                    return False
        return True
