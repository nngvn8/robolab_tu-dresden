# !/usr/bin/env python3
import ev3dev.ev3 as ev3
import time
from odometry import Odometry
from pid_controller import PIDController


class Robot:

    TICKS360 = 620
    LUM_STOP_LINE = 200

    def __init__(self, movement_speed=200, rotation_speed=100):

        # initialize motors
        self.default_speed = movement_speed  # never slower than 25, or better 30
        self.rotation_speed = rotation_speed
        self.left_motor = ev3.LargeMotor("outA")
        self.right_motor = ev3.LargeMotor("outD")
        self.left_motor.stop_action = "brake"
        self.right_motor.stop_action = "brake"

        # initialize color sensor and ultrasonic sensor
        self.color_sensor = ev3.ColorSensor()
        self.color_sensor.mode = 'RGB-RAW'
        self.ultrasonic_sensor = ev3.UltrasonicSensor()
        self.ultrasonic_sensor.mode = 'US-DIST-CM'

        # initialize pid controller
        self.pid_controller = PIDController()
        self.odometry = Odometry(self)

        # variable to store found node with color
        self.node_found = ""

        # motor position counter and time period
        self.motor_pos_ctr = 1
        self.motor_pos_ct_T = 10

        # odometry information
        self.direction = 270
        self.x_coord = 0
        self.y_coord = 0

        self.TIME360_AT100 = 5.7

    def forward(self, speed=None):
        if speed is None:
            speed = self.default_speed
        self.left_motor.run_forever(speed_sp=speed)
        self.right_motor.run_forever(speed_sp=speed)

    def forward_w_ticks(self, ticks, speed=None):
        if speed is None:
            speed = self.default_speed
        self.left_motor.run_to_rel_pos(position_sp=ticks, speed_sp=speed)
        self.right_motor.run_to_rel_pos(position_sp=ticks, speed_sp=speed)
        while self.left_motor.is_running and self.right_motor.is_running:
            self.odometry.add_motor_pos(self)
        self.stop()

    def rotate(self, speed=None):
        if speed is None:
            speed = self.rotation_speed
        self.left_motor.run_forever(speed_sp=speed)
        self.right_motor.run_forever(speed_sp=-speed)

    def turn_to_direction(self, direction):
        if self.direction == direction:
            return

        turn_deg = (direction - self.direction) % 360

        # turn left if shorter
        if turn_deg == 270:
            turn_deg = -90

        print(f"turn_deg: {turn_deg}")

        # make turn with offset
        if turn_deg == -90:
            self.turn_w_ticks(turn_deg, -20)
        else:
            self.turn_w_ticks(turn_deg, -60)

        # find line (just use follow line?)
        while self.calc_luminance() > self.LUM_STOP_LINE:
            self.left_motor.run_forever(speed_sp=self.rotation_speed)
            self.right_motor.run_forever(speed_sp=-self.rotation_speed)

    def turn_around(self):
        self.direction = (self.direction + 180) % 360
        self.turn_w_ticks(180, -30)
        while self.calc_luminance() > self.LUM_STOP_LINE:
            self.left_motor.run_forever(speed_sp=self.rotation_speed)
            self.right_motor.run_forever(speed_sp=-self.rotation_speed)
        self.left_motor.stop(stop_action='hold')
        self.right_motor.stop(stop_action='hold')

    def turn_w_ticks(self, degree=90, offset=0, speed=None):
        # turn = round(degree*2*0.95)
        turn = round(self.TICKS360 / 360 * degree) + offset
        print(f"turn: {turn}")

        if speed is None:
            speed = self.rotation_speed
        if degree < 0:
            speed = -speed
        print(f"speed: {speed}")

        self.left_motor.reset()
        self.right_motor.reset()
        print(f"left_motor_pos: {self.left_motor.position}")

        while abs(self.left_motor.position) < abs(turn):
            self.left_motor.run_forever(speed_sp=speed)
            self.right_motor.run_forever(speed_sp=-speed)


    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()

    def follow_line(self):
        luminance = self.calc_luminance()

        # add every tenth motor position
        if self.motor_pos_ctr == 10:
            self.odometry.add_motor_pos(self)
            print(f"{self.odometry.motor_positions[-1]}")
            self.motor_pos_ctr = 1
        else:
            self.motor_pos_ctr += 1

        self.pid_controller.adjust_motors(luminance, self)

    def found_obstacle(self):
        if self.ultrasonic_sensor.distance_centimeters < 11:
            return True
        return False

    def found_node(self):
        # if 180 > self.color_sensor.red > 140 and 80 > self.color_sensor.green > 40 and 45 > self.color_sensor.blue > 5:

        if self.color_sensor.red * 10 > (self.color_sensor.green + self.color_sensor.blue) * 16.47:
            self.node_found = "red"
            return True

        if 55 > self.color_sensor.red > 30 and 180 > self.color_sensor.green > 140 and 130 > self.color_sensor.blue > 100:
            self.node_found = "blue"
            return True

        self.node_found = ""
        return False

    def calc_luminance(self):
        return 0.2126 * self.color_sensor.red + 0.7152 * self.color_sensor.green + 0.0722 * self.color_sensor.blue

    def enter_node(self):
        # position on the exact middle of node
        if self.node_found == "red":
            self.left_motor.run_to_rel_pos(position_sp=115)
            self.right_motor.run_to_rel_pos(position_sp=115)
            self.right_motor.wait_until_not_moving()
        elif self.node_found == "blue":
            self.left_motor.run_to_rel_pos(position_sp=115)
            self.right_motor.run_to_rel_pos(position_sp=115)
            self.right_motor.wait_until_not_moving()
        self.stop()

    def scan_for_edges(self):
        edges = []
        turn = self.TICKS360 * 1
        breakout = False

        # reset to use motor.position
        self.left_motor.reset()
        self.right_motor.reset()

        # rotate 360 (break when original line found or 360)
        while True:
            # print(f"Motor Position: {self.left_motor.position}")

            # rotate while no line
            while self.calc_luminance() > 55:
                # rotate
                self.left_motor.run_forever(speed_sp=self.rotation_speed)
                self.right_motor.run_forever(speed_sp=-self.rotation_speed)

                # stop scan_for_edges if original line found or 360
                if self.left_motor.position > 550 and self.calc_luminance() < self.LUM_STOP_LINE or self.left_motor.position > turn:
                    self.left_motor.stop(stop_action='hold')
                    self.right_motor.stop(stop_action='hold')
                    breakout = True
                    break

            # exit if original line found
            if breakout:
                break

            # remove stutter?

            # store found edge
            print(self.left_motor.position * 1.3 / 2)
            current_rotation = round(self.left_motor.position * 1.3 / 2 / 90) * 90
            edges.append((self.direction + current_rotation) % 360)

            # get away from black line
            self.left_motor.run_to_rel_pos(position_sp=40, speed_sp=self.rotation_speed)
            self.right_motor.run_to_rel_pos(position_sp=-40, speed_sp=-self.rotation_speed)
            self.right_motor.wait_until_not_moving()

        print(f"Motor Position: {self.left_motor.position}")
        return edges
