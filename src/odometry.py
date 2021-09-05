import time
from math import sin, cos, pi, floor, ceil


class Odometry:

    WHEEL_DISTANCE = 100  # 88 # 105 middle to middle but 105 much better  # middle to middle
    DISTANCE_PER_TICK = 2000 / 4225 # 4230  # 0.41 # mm / tick    ## BEFORE: pi * 55 / 360  # pi * d / number_ticks360 in mm / tick

    def __init__(self, even_node="blue", odd_node="red"):
        self.motor_positions = []
        self.even_node = even_node
        self.odd_node = odd_node

    def init(self, node_x, node_y, direction, robot):

        robot.x_coord = node_x
        robot.y_coord = node_y
        robot.direction = direction

        # set odd and even node
        if (node_x + node_y) % 2 == 0:
            self.even_node = robot.node_found
            if self.even_node == "blue":
                self.odd_node = "red"
            else:
                self.odd_node = "blue"
        else:
            self.odd_node = robot.node_found
            if self.odd_node == "red":
                self.even_node = "blue"
            else:
                self.odd_node = "red"

        self.motor_positions = []

    def det_new_pos(self, robot):

        dist_trav_x = 0
        dist_trav_y = 0

        direction = self.cood_to_math(robot.direction)  # transform into math representation
        direction_rad = direction / 180 * pi                 # convert into radians

        # iterating over pairs of motor_positions with i referring to the first of them
        for i in range(len(self.motor_positions) - 1):
            dist_l_wheel = (self.motor_positions[i+1][0] - self.motor_positions[i][0]) * self.DISTANCE_PER_TICK
            dist_r_wheel = (self.motor_positions[i+1][1] - self.motor_positions[i][1]) * self.DISTANCE_PER_TICK

            alpha = (dist_r_wheel - dist_l_wheel) / self.WHEEL_DISTANCE  # change of direction at the end of movement
            beta = alpha / 2                                             # change of direction at the begin of movement
            if alpha == 0:
                distance_moved = dist_l_wheel  # == dist_r_wheel
            else:
                distance_moved = (dist_l_wheel + dist_r_wheel) / alpha * sin(beta)

            dist_trav_x += cos(direction_rad + beta) * distance_moved  # polar coordinate -> cartesian
            dist_trav_y += sin(direction_rad + beta) * distance_moved  # polar coordinate -> cartesian
            direction_rad += alpha

        print(f"distance travelled x (mm): {dist_trav_x}")
        print(f"distance travelled y (mm): {dist_trav_y}")

        direction = (direction_rad / pi * 180) % 360  # convert to degree
        direction = (round(direction / 90) * 90)      # direction is multiple of 90
        direction = self.math_to_cood(direction)      # transform into coordinate representation

        print(f"direction: {self.math_to_cood(direction_rad / pi * 180)}")

        x = robot.x_coord + dist_trav_x / 500
        y = robot.y_coord + dist_trav_y / 500
        x = round(x)
        y = round(y)
        # x, y = self.closest_possible_xy(x, y, robot.node_found)

        print(f"direction (rounded): {direction}")
        print(f"x: {x}")
        print(f"y: {y}")

        robot.x_coord = x
        robot.y_coord = y
        robot.direction = direction
        robot.current_node = (x, y, (direction + 180) % 360)

        self.motor_positions = []

    def closest_possible_xy(self, x, y, found_color):
        x_floor = floor(x)
        y_floor = floor(y)
        x_ceil = ceil(x)
        y_ceil = ceil(y)

        # cases (1,red) and (0,blue)
        # lower left node has same color has same color as found node
        if (x_floor + y_floor) % 2 == 1 and found_color == self.odd_node or (
                x_floor + y_floor) % 2 == 0 and found_color == self.even_node:
            # lower left or upper right closer? (pythagoras)
            if (x - x_floor) ** 2 + (y - y_floor) ** 2 < (x_ceil - x) ** 2 + (y_ceil - y) ** 2:
                return x_floor, y_floor
            else:
                return x_ceil, y_ceil

        # cases (0,red) and (1,blue)
        # lower left node has NOT the same color has same color as found node
        if (x_floor + y_floor) % 2 == 0 and found_color == self.odd_node or (
                x_floor + y_floor) % 2 == 1 and found_color == self.even_node:
            # upper left or lower right closer? (pythagoras)
            if (x - x_floor) ** 2 + (y_ceil - y) ** 2 < (x_ceil - x) ** 2 + (y - y_floor) ** 2:
                return x_floor, y_ceil
            else:
                return x_ceil, y_floor

    def add_motor_pos(self, robot):
        self.motor_positions.append((robot.left_motor.position, robot.right_motor.position))

    def cood_to_math(self, direction):
        direction = (direction - 90) % 360
        direction = -direction % 360
        return direction

    def math_to_cood(self, direction):
        direction = -direction % 360
        direction = (direction + 90) % 360
        return direction
