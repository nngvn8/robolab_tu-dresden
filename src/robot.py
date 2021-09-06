# !/usr/bin/env python3
import ev3dev.ev3 as ev3
import time
from odometry import Odometry
from pid_controller import PIDController


class Robot:

    TICKS360 = 620
    LUM_STOP_LINE = 300

    def __init__(self, movement_speed=170, rotation_speed=100):

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
        self.odometry = Odometry()

        # variable to store found node with color
        self.node_found = ""
        self.on_ret_from_obst = False

        # motor position counter and time period
        self.motor_pos_ctr = 1
        self.motor_pos_ct_T = 10

        # odometry information
        self.direction = 0
        self.x_coord = 0
        self.y_coord = 0

        self.last_node = ((0, 0), 0)

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

        # make turn with offset
        if turn_deg == -90:
            self.turn_w_ticks(turn_deg, -20)
        else:
            self.turn_w_ticks(turn_deg, -60)

        # find line (just use follow line?)
        while self.calc_luminance() > self.LUM_STOP_LINE:
            self.left_motor.run_forever(speed_sp=self.rotation_speed)
            self.right_motor.run_forever(speed_sp=-self.rotation_speed)

        self.direction = (self.direction + turn_deg) % 360

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

        if speed is None:
            speed = self.rotation_speed
        if degree < 0:
            speed = -speed

        self.left_motor.reset()
        self.right_motor.reset()

        while abs(self.left_motor.position) < abs(turn):
            self.left_motor.run_forever(speed_sp=speed)
            self.right_motor.run_forever(speed_sp=-speed)

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()

    def reset(self):
        self.left_motor.reset()
        self.right_motor.reset()

    def set_pos_and_dir(self, x_coord, y_coord, node_direction):
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.direction = (node_direction + 180) % 360

    def follow_line(self):
        luminance = self.calc_luminance()

        # add every tenth motor position
        if self.motor_pos_ctr == self.motor_pos_ct_T:
            self.odometry.add_motor_pos(self)
            # print(f"{self.odometry.motor_positions[-1]}")
            self.motor_pos_ctr = 1
        else:
            self.motor_pos_ctr += 1

        self.pid_controller.adjust_motors(luminance, self)

    def found_obstacle(self):
        if self.ultrasonic_sensor.distance_centimeters < 15:
            return True
        return False

    def found_node(self):
        (red, green, blue) = self.color_sensor.raw
        if red in range(90, 170) and green in range(0, 100) and blue in range(0, 75):
            self.node_found = "red"
            # print(f"color_node: {self.node_found}")
            # print(f"red: {red}")
            # print(f"green: {green}")
            # print(f"blue: {blue}")
            return True

        if red in range(0, 40) and green in range(50, 170) and blue in range(55, 120):
            self.node_found = "blue"
            # print(f"color_node: {self.node_found}")
            # print(f"red: {red}")
            # print(f"green: {green}")
            # print(f"blue: {blue}")
            return True

        self.node_found = ""
        return False

    def calc_luminance(self):
        (red, green, blue) = self.color_sensor.raw
        return 0.2126 * red + 0.7152 * green + 0.0722 * blue

    def play_sound(self):
        ev3.Sound.tone([(200, 100, 100), (500, 200)])
        # ev3.Sound.speak('Obstacle found!')

    def enter_node(self):
        self.pid_controller.integral = 0
        self.pid_controller.last_error = 0

        # position on the exact middle of node
        if self.node_found == "red":
            self.left_motor.run_to_rel_pos(position_sp=135, speed_sp=100)
            self.right_motor.run_to_rel_pos(position_sp=135, speed_sp=100)
            self.left_motor.wait_until_not_moving()
            self.right_motor.wait_until_not_moving()
        elif self.node_found == "blue":
            self.left_motor.run_to_rel_pos(position_sp=135, speed_sp=100)
            self.right_motor.run_to_rel_pos(position_sp=135, speed_sp=100)
            self.left_motor.wait_until_not_moving()
            self.right_motor.wait_until_not_moving()
        self.stop()

    def scan_for_edges(self):
        edges = []
        turn = self.TICKS360 * 0.95
        breakout = False

        # self.left_motor.run_to_rel_pos(position_sp=-15, speed_sp=100)
        # self.right_motor.run_to_rel_pos(position_sp=15, speed_sp=100)
        # self.left_motor.wait_until_not_moving()
        # self.right_motor.wait_until_not_moving()

        # reset to use motor.position
        self.left_motor.reset()
        self.right_motor.reset()

        # rotate 360 (break when original line found or 360)
        while True:
            # print(f"Motor Position: {self.left_motor.position}")

            # rotate while no line
            while self.calc_luminance() > 70:
                # rotate
                self.left_motor.run_forever(speed_sp=self.rotation_speed)
                self.right_motor.run_forever(speed_sp=-self.rotation_speed)

                # stop scan_for_edges if original line found or 360
                if self.left_motor.position > 550 and self.calc_luminance() < self.LUM_STOP_LINE or \
                        self.left_motor.position > turn:
                    self.left_motor.stop(stop_action='hold')
                    self.right_motor.stop(stop_action='hold')
                    breakout = True
                    break

            # exit if original line found or 360
            if breakout:
                break

            # remove stutter? -> other implementation needed

            # calc direction of edge
            current_rotation = self.left_motor.position * 1.3 / 2
            print(current_rotation)

            if current_rotation > 270:
                current_rotation = 270

            current_rotation = round(current_rotation / 90) * 90


            # add edge, but only if its not 180 (because we already know it)
            if current_rotation != 180:
                edges.append(current_rotation)

            # get away from black line
            self.left_motor.run_to_rel_pos(position_sp=40, speed_sp=self.rotation_speed)
            self.right_motor.run_to_rel_pos(position_sp=-40, speed_sp=-self.rotation_speed)
            self.right_motor.wait_until_not_moving()

        # order from right to left
        edges_return = []
        if 90 in edges:
            edges_return.append(90)
        if 0 in edges:
            edges_return.append(0)
        if 270 in edges:
            edges_return.append(270)

        print(f"scanned edges: {edges_return}")

        # transfrom to coordinates
        for i in range(len(edges_return)):
            edges_return[i] = (edges_return[i] + self.direction) % 360

        return edges_return

    def scan_for_edges2(self):
        edges = []
        line_found = False
        turn = self.TICKS360 * 0.95

        self.left_motor.reset()
        self.right_motor.reset()

        while self.left_motor.position < turn:
            self.left_motor.run_forever(speed_sp=self.rotation_speed)
            self.right_motor.run_forever(speed_sp=-self.rotation_speed)

            if self.calc_luminance() < 55 and not line_found:
                edges.append(self.left_motor.position)
                line_found = True

            if self.calc_luminance() > 200:
                line_found = False

        for i in range(len(edges)):
            edges[i] = (self.direction + (round(edges[i] * 1.3 / 2 / 90) * 90)) % 360

        return edges
