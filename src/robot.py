# !/usr/bin/env python3
import ev3dev.ev3 as ev3
import time
from robot_controls import PidController, Odometry


class Robot:

    ROTATION_SPEED = 700
    ROTATION_VOL = 7565866  # 7635666
    ROTATION_CUR = 305333  # 233333

    def __init__(self, movement_speed=200, rotation_speed=200):

        # initialize motors
        self.default_speed = movement_speed  # never slower than 25, or better 30
        self.rotation_speed = rotation_speed
        self.left_motor = ev3.LargeMotor("outA")
        self.right_motor = ev3.LargeMotor("outD")
        self.left_motor.stop_action = "brake"
        self.right_motor.stop_action = "brake"

        # initialize color sensor
        self.color_sensor = ev3.ColorSensor()
        self.color_sensor.mode = 'RGB-RAW'

        # initialize pid controller
        self.pid_controller = PidController()
        self.odometry = Odometry(self)

        # variable to store found node with color
        self.node_found = ""

        # motor position counter and time period
        self.motor_pos_ctr = 1
        self.motor_pos_ct_T = 10

        #
        self.direction = 0
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

    def turn_w_time(self, degree=90):
        turning_time = self.TIME360_AT100 * degree / 360
        start_time = time.time()
        while time.time() - start_time <= turning_time + 0.1:
            self.rotate()
        self.stop()

    def turn_w_ticks(self, degree=90, speed=None):
        self.left_motor.reset()
        self.right_motor.reset()
        turn = round(degree*2*0.95)
        if speed is None:
            speed = self.rotation_speed
        self.left_motor.run_to_rel_pos(position_sp=turn, speed_sp=speed)  # correcting?
        self.right_motor.run_to_rel_pos(position_sp=-turn, speed_sp=-speed)  # correcting?
        while self.left_motor.is_running and self.right_motor.is_running:
            pass
        # self.left_motor.stop(stop_action='hold')
        # self.right_motor.stop(stop_action='hold')
        # for find edges
        self.left_motor.stop(stop_action='coast')
        self.right_motor.stop(stop_action='coast')

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()

    def follow_line(self):
        luminance = self.calc_luminance()
        if self.motor_pos_ctr == 10:
            self.odometry.add_motor_pos(self)
            print(f"{self.odometry.motor_positions[-1]}")
            self.motor_pos_ctr = 1
        else:
            self.motor_pos_ctr += 1
        self.pid_controller.adjust_motors(luminance, self)

    def found_node(self):
        # if 180 > self.color_sensor.red > 140 and 80 > self.color_sensor.green > 40 and 45 > self.color_sensor.blue > 5:
        if self.color_sensor.red * 10 > (self.color_sensor.green + self.color_sensor.blue) * 16.47:
            self.node_found = "red"
            return True
        if 55 > self.color_sensor.red > 35 and 180 > self.color_sensor.green > 155 and 130 > self.color_sensor.blue > 110:
            self.node_found = "blue"
            return True
        self.node_found = ""
        return False

    def calc_luminance(self):
        return 0.2126 * self.color_sensor.red + 0.7152 * self.color_sensor.green + 0.0722 * self.color_sensor.blue

    def scan_for_edges(self):
        # drive while on node (color sensor on node)
        node_found = self.node_found
        # while self.calc_luminance() < 300:
        #     self.left_motor.run_forever(speed_sp=100)
        #     self.right_motor.run_forever(speed_sp=120)

        while self.found_node():
            self.forward(100)
        # position on the exact middle of node
        if node_found == "red":
            self.left_motor.run_to_rel_pos(position_sp=70)
            self.right_motor.run_to_rel_pos(position_sp=50)
            self.left_motor.wait_until_not_moving()
        elif node_found == "blue":
            self.left_motor.run_to_rel_pos(position_sp=110)
            self.right_motor.run_to_rel_pos(position_sp=55)
            self.left_motor.wait_until_not_moving()
        self.stop()
        return self.find_edges_black()

    def find_edges_black(self):
        edges = []
        turn = 720  # turn 360
        breakout = False
        self.left_motor.reset()
        self.right_motor.reset()
        while self.left_motor.position < turn:
            # get away from black line
            self.left_motor.run_to_rel_pos(position_sp=40, speed_sp=100)
            self.right_motor.run_to_rel_pos(position_sp=-40, speed_sp=-100)
            self.left_motor.wait_until_not_moving()

            # rotate while no line
            while self.calc_luminance() > 55:
                # rotate
                self.left_motor.run_forever(speed_sp=100)
                self.right_motor.run_forever(speed_sp=-100)
                # stop rotation if original line found
                if self.left_motor.position > 550 and self.calc_luminance() < 170:
                    self.left_motor.stop(stop_action='hold')
                    self.right_motor.stop(stop_action='hold')
                    breakout = True
                    break

            # black found
            print(self.left_motor.position * 1.3 / 2)
            current_rotation = round(self.left_motor.position * 1.3 / 2 / 90) * 90
            edges.append((self.direction + current_rotation) % 360)
            # exit if original line found
            if breakout:
                break
        return edges


    def find_edges_45(self):
        pass

    def find_edges_old(self):
        edges = []
        m_pos_ctr = 1
        self.left_motor.reset()
        self.right_motor.reset()
        turn = 360*2*0.90
        while self.left_motor.position < turn and self.right_motor.position > -turn:
            self.rotate()
            luminance = self.calc_luminance()
            print(luminance)
            if luminance < 70 and m_pos_ctr == 2:
                edges.append('a')
                m_pos_ctr = 1
            else:
                m_pos_ctr += 1
        self.left_motor.stop(stop_action='hold')
        self.right_motor.stop(stop_action='hold')
        return edges


    def get_cur_voltage(self):
        voltage_file = open('/sys/class/power_supply/lego-ev3-battery/voltage_now')
        return int(voltage_file.read())

    def get_cur_current(self):
        current_file = open('/sys/class/power_supply/lego-ev3-battery/current_now')
        return int(current_file.read())



