from itertools import product
import scipy.stats as stats
import matplotlib.pyplot as plt
from random import shuffle
from Passenger import Passenger
from Plane import Plane


def construct_passengers(num_passengers, average_aisle_to_seat_time, sd_aisle_to_seat_time, lower_bound_aisle_to_seat_time, upper_bound_aisle_to_seat_time):
    passengers = []
    aisle_to_seat_times = generate_truncated_normal_distribution(
        num_passengers,
        average_aisle_to_seat_time,
        sd_aisle_to_seat_time,
        lower_bound_aisle_to_seat_time,
        upper_bound_aisle_to_seat_time
    )
    # display_histogram(aisle_to_seat_times)

    seats = [x for x in range(num_passengers)]
    shuffle(seats)
    for i in range(num_passengers):
        passengers.append(Passenger(int(seats[i] / 6), seats[i] % 6, aisle_to_seat_times[i]))
    return passengers


def generate_truncated_normal_distribution(size, mu, sigma, lower, upper):
    return stats.truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma).rvs(size).tolist()


def display_histogram(points):
    plt.hist(points, normed=True)
    plt.show()


def passenger_ordering(passengers, ordering, distance_between_passengers):
    if ordering == 'random':
        ordered_passengers = passengers
    elif ordering == 'back_to_front':
        ordered_passengers = sorted(passengers, key=lambda p: (p.row, p.column), reverse=True)
    elif ordering == 'front_to_back':
        ordered_passengers = sorted(passengers, key=lambda p: (p.row, p.column))
    elif ordering == 'five_boarding_groups_back_to_front':
        ordered_passengers = shuffle_passengers_in_boarding_groups(passengers, True)
    elif ordering == 'five_boarding_groups_front_to_back':
        ordered_passengers = shuffle_passengers_in_boarding_groups(passengers, False)
    else:
        raise NotImplementedError
    for i, passenger in enumerate(ordered_passengers):
        passenger.location = -distance_between_passengers * i
    return ordered_passengers


def shuffle_passengers_in_boarding_groups(passengers, reverse):
    passengers.sort(key=lambda p: (p.row, p.column))
    groups = [
        passengers[:36],
        passengers[36:72],
        passengers[72:108],
        passengers[108:144],
        passengers[144:]
    ]
    for _ in groups:
        shuffle(_)
    ordered_passengers = [item for sublist in groups for item in sublist]
    if reverse:
        ordered_passengers.reverse()
    return ordered_passengers


def on_tick(line_of_passengers, walking_speed, distance_between_rows, tick, plane):
    for i, passenger in enumerate(line_of_passengers):
        if passenger.is_getting_in_seat:
            # Check if sufficient enough time has passed
            if tick >= passenger.starting_getting_in_seat_tick + passenger.aisle_to_seat_time:
                passenger.is_seated = True
                plane.occupy_seat(passenger.row + 1, passenger.column + 1)
                if passenger.column <= 2:
                    plane.seats[passenger.row].left_side_boarding = False
                else:
                    plane.seats[passenger.row].right_side_boarding = False
                line_of_passengers.remove(passenger)
        else:
            # Check if someone is blocking the passenger from moving
            if i > 0 and line_of_passengers[i - 1].is_stopped:
                passenger.is_stopped = True
            else:
                passenger.is_stopped = False
                passenger_row_location = passenger.row * distance_between_rows
                # Move passenger to row location if within step distance
                if passenger_row_location < passenger.location + walking_speed:
                    passenger.location = passenger_row_location
                # Otherwise move passenger step distance
                else:
                    passenger.location += walking_speed
                # Check if passenger is at seat row to board
                if passenger.location == passenger_row_location:
                    # check if left side of row is boarding
                    if passenger.column <= 2 and not plane.seats[passenger.row].left_side_boarding:
                        plane.seats[passenger.row].left_side_boarding = True
                        passenger.is_getting_in_seat = True
                        passenger.is_stopped = True
                        passenger.starting_getting_in_seat_tick = tick
                    # check if right side of row is boarding
                    if passenger.column > 2 and not plane.seats[passenger.row].right_side_boarding:
                        plane.seats[passenger.row].right_side_boarding = True
                        passenger.is_getting_in_seat = True
                        passenger.is_stopped = True
                        passenger.starting_getting_in_seat_tick = tick


def board_plane(ordering, average_aisle_to_seat_time, sd_aisle_to_seat_time):
    # Assumptions
    num_rows = 30
    distance_between_rows = 10
    distance_between_passengers = 2
    walking_speed = 8
    lower_bound_aisle_to_seat_time = 1
    upper_bound_aisle_to_seat_time = 200

    # Create passengers and order them
    passengers = construct_passengers(
        num_rows * 6,
        average_aisle_to_seat_time,
        sd_aisle_to_seat_time,
        lower_bound_aisle_to_seat_time,
        upper_bound_aisle_to_seat_time
    )
    line_of_passengers = passenger_ordering(passengers, ordering, distance_between_passengers)

    # Create and board plane
    plane = Plane()
    ticks = 0
    while not plane.is_finished_boarding():
        on_tick(line_of_passengers, walking_speed, distance_between_rows, ticks, plane)
        ticks += 1
    return ticks / 60


def main():
    orderings = [
        'random',
        'back_to_front',
        'front_to_back',
        'five_boarding_groups_back_to_front',
        'five_boarding_groups_front_to_back'
    ]
    average_aisle_to_seat_times = [5, 10, 15]
    sd_aisle_to_seat_times = [3, 6, 9]
    iterations = 100
    with open('output.csv', 'w') as output_file:
        header = ''
        board_times_per_ordering = {}
        for order, mean_time, sd_time in product(orderings, average_aisle_to_seat_times, sd_aisle_to_seat_times):
            times_to_board = []
            for i in range(iterations):
                times_to_board.append(board_plane(order, mean_time, sd_time))
            key = f'{order}({mean_time}, {sd_time})'
            header += key + ','
            board_times_per_ordering[key] = times_to_board
        header = header[:-1]
        output_file.write(header + '\n')

        for i in range(iterations):
            to_write = ''
            for time in board_times_per_ordering.values():
                to_write += f'{time[i]},'
            to_write = to_write[:-1]
            if i != iterations - 1:
                to_write += '\n'
            output_file.write(to_write)


if __name__ == '__main__':
    main()
