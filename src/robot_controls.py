import time
from math import sin, cos, pi


class PidController:

    def __init__(self):
        # k parameters times 100
        self.kp = 75  # not greater than kc = 100 evt smaller scaling const proportional part 65
        self.ki = 5  # to be set scaling const integral part dt = 46.897/1000 = 0.0469 Pc = 0.2
        self.kd = 50  # 32 to be set scaling const derivative part
        self.integral = 0
        self.last_error = 0
        self.offset = 170  # determined by experiment on line

    def adjust_motors(self, luminance, robot):
        # calculating needed parameters
        error = luminance - self.offset
        derivative = error - self.last_error
        if error > 0 > self.last_error or error < 0 < self.last_error:
            self.integral = error  # = 0 ?
        else:
            self.integral = self.integral / 3 + error

        # actual calculation and application of the adjustment
        # caution! for this application sensor has to be on the left side of the line!
        turn = error * self.kp + self.integral * self.ki + derivative * self.kd
        robot.left_motor.speed_sp = self.cap_speed(robot.default_speed + turn / 100)
        robot.right_motor.speed_sp = self.cap_speed(robot.default_speed - turn / 100)

        # committing the new motor speeds
        robot.left_motor.command = "run-forever"
        robot.right_motor.command = "run-forever"

        # storing the error of this iteration for next one
        self.last_error = error

    def cap_speed(self, speed):
        if abs(speed) > 1000:
            if speed < 0:
                speed = -1000
            else:
                speed = 1000
        return speed


class Odometry:

    WHEEL_DISTANCE = 90  # 88 # 105 middle to middle but 105 much better  # middle to middle
    DISTANCE_PER_TICK = 2000 / 5140  # 0.41 # mm / tick    ## BEFORE: pi * 55 / 360  # pi * d / number_ticks360 in mm / tick

    def __init__(self, robot):
        self.motor_positions = []

    def det_new_pos(self, x=0, y=0, direction=0):

        direction = self.cood_to_math(direction)  # transform into math representation
        direction_rad = direction / 180 * pi      # convert into radians

        # iterating over pairs of motor_positions with i referring to the first of them
        for i in range(len(self.motor_positions) - 1):
            dist_lwheel, dist_rwheel = self.dist_wheels(i)
            alpha = (dist_rwheel - dist_lwheel) / self.WHEEL_DISTANCE  # change of direction at the end of movement
            beta = alpha / 2                                           # change of direction at the begin of movement
            if alpha == 0:
                distance_moved = dist_lwheel  # == dist_rwheel
            else:
                distance_moved = (dist_lwheel + dist_rwheel) / alpha * sin(beta)
            x += cos(direction_rad + beta) * distance_moved  # polar coordinate -> cartesian
            y += sin(direction_rad + beta) * distance_moved  # polar coordinate -> cartesian
            direction_rad += alpha
        print(f"distance travelled x (mm): {x}")
        print(f"distance travelled y (mm): {y}")

        print(f"direction: {self.math_to_cood(direction_rad / pi * 180)}")
        x = round(x / 500)
        y = round(y / 500)

        direction = (direction_rad / pi * 180) % 360  # convert to degree
        direction = (round(direction / 90) * 90)      # direction is multiple of 90
        direction = self.math_to_cood(direction)      # transform into coordinate representation

        print(f"x: {x}")
        print(f"y: {y}")
        print(f"direction (rounded): {direction}")

        return x, y, direction

    def dist_wheels(self, i):
        d_lmotor = self.motor_positions[i+1][0] - self.motor_positions[i][0]  # difference in motor_position
        d_rmotor = self.motor_positions[i+1][1] - self.motor_positions[i][1]  # difference in motor_position
        return d_lmotor * self.DISTANCE_PER_TICK, d_rmotor * self.DISTANCE_PER_TICK  # return moved_distance

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
