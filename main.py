import scipy.stats as stats
import matplotlib.pyplot as plt
from random import shuffle
from Passenger import Passenger
from Plane import Plane


def construct_passengers(num_passengers, average_aisle_to_seat_time, sd_aisle_to_seat_time):
    passengers = []
    aisle_to_seat_times = generate_truncated_normal_distribution(num_passengers, average_aisle_to_seat_time, sd_aisle_to_seat_time, 3, 200)
    # display_histogram(aisle_to_seat_times)

    seats = [x for x in range(num_passengers)]
    shuffle(seats)
    for i in range(num_passengers):
        passenger = Passenger(int(seats[i] / 6), seats[i] % 6, aisle_to_seat_times[i])
        passengers.append(passenger)
    return passengers


def generate_truncated_normal_distribution(size, mu, sigma, lower, upper):
    return stats.truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma).rvs(size).tolist()


def display_histogram(points):
    plt.hist(points, normed=True)
    plt.show()


def passenger_ordering(passengers, ordering):
    if ordering == 'random':
        return passengers
    else:
        raise NotImplementedError


def on_tick(line_of_passengers, walking_speed, distance_between_rows, tick, plane):
    for i, passenger in enumerate(line_of_passengers):
        if passenger.is_getting_in_seat:
            # Check if sufficient enough time has passed
            if tick >= passenger.starting_getting_in_seat_tick + passenger.aisle_to_seat_time:
                plane.occupy_seat(passenger.row + 1, passenger.column + 1)
                passenger.is_seated = True
                line_of_passengers.remove(passenger)
        else:
            # Check if someone is blocking the passenger from moving
            if i > 0 and line_of_passengers[i - 1].is_stopped:
                passenger.is_stopped = True
                pass
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
                    if passenger.column <= 3 and not plane.seats[passenger.row].left_side_boarding:
                        plane.seats[passenger.row].left_side_boarding = True
                        passenger.is_getting_in_seat = True
                        passenger.is_stopped = True
                        passenger.starting_getting_in_seat_tick = tick
                    # check if right side of row is boarding
                    if passenger.column > 3 and not plane.seats[passenger.row].right_side_boarding:
                        plane.seats[passenger.row].right_side_boarding = True
                        passenger.is_getting_in_seat = True
                        passenger.is_stopped = True
                        passenger.starting_getting_in_seat_tick = tick


def main():
    # Assumptions
    num_rows = 30
    distance_between_rows = 10
    average_aisle_to_seat_time = 10
    sd_aisle_to_seat_time = 10
    walking_speed = 8
    ordering = 'random'

    # Create passengers and order them
    passengers = construct_passengers(num_rows * 6, average_aisle_to_seat_time, sd_aisle_to_seat_time)
    line_of_passengers = passenger_ordering(passengers, ordering)

    # Create and board plane
    plane = Plane()
    ticks = 0
    while not plane.is_finished_boarding():
        on_tick(line_of_passengers, walking_speed, distance_between_rows, ticks, plane)
        ticks += 1
    print(f'Seconds to board plane: {ticks}')


if __name__ == '__main__':
    main()

