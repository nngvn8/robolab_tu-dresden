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
            self.integral = error # = 0 ?
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

    @staticmethod
    def check_motor_speeds(self, robot1):
        # check left motor speed
        if abs(robot1.left_motor.speed_sp) > 1000:
            if robot1.left_motor.speed_sp < 0:
                robot1.left_motor.speed_sp = -1000
            else:
                robot1.left_motor.speed_sp = 1000

        # check right motor speed
        if abs(robot1.right_motor.speed_sp) > 1000:
            if robot1.right_motor.speed_sp < 0:
                robot1.right_motor.speed_sp = -1000
            else:
                robot1.right_motor.speed_sp = 1000

    def cap_speed(self, speed):
        if abs(speed) > 1000:
            if speed < 0:
                speed = -1000
            else:
                speed = 1000
        return speed


class Odometry:

    def __intit__(self):
        pass
