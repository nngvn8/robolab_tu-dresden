# !/usr/bin/env python3
import ev3dev.ev3 as ev3
import time
from robot_controls import PidController, Odometry



class Robot:
    def __init__(self, movement_speed=200, rotation_speed=200):
        """
        Initializes odometry module
        """

        # initialize motors
        self.default_speed = movement_speed # never slower than 25, or better 30
        self.rotation_speed = rotation_speed
        self.left_motor = ev3.LargeMotor("outA")
        self.right_motor = ev3.LargeMotor("outD")
        self.left_motor.stop_action = "brake"
        self.right_motor.stop_action = "brake"

        # initialize colour sensor
        self.color_sensor = ev3.ColorSensor()
        self.color_sensor.mode = 'RGB-RAW'

        # initialize pid controller
        self.pid_controller = PidController()
        self.odometry = Odometry()

        self.node_found = ""

        self.TIME360_AT100 = 5.7

    def forward(self, speed=None):
        if speed is None:
            speed = self.default_speed
        self.left_motor.speed_sp = speed
        self.right_motor.speed_sp = speed
        self.left_motor.command = "run-forever"
        self.right_motor.command = "run-forever"

    def rotate(self, speed=None):
        if speed is None:
            speed = self.rotation_speed
        self.left_motor.speed_sp = -speed
        self.right_motor.speed_sp = speed
        self.left_motor.command = "run-forever"
        self.right_motor.command = "run-forever"

    def turn_w_time(self, degree=90):
        turning_time = self.TIME360_AT100 * degree / 360
        start_time = time.time()
        while time.time() - start_time <= turning_time + 0.1:
            self.rotate()
        self.stop()

    def turn_w_ticks(self, degree=90):
        self.left_motor.position_sp = -degree*2 - 30
        self.right_motor.position_sp = degree*2 - 30
        self.left_motor.command = "run-to-rel-pos"
        self.right_motor.command = "run-to-rel-pos"
        while self.left_motor.is_running and self.right_motor.is_running:
            pass
        self.stop()


    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()

    def reset(self):
        self.left_motor.reset()
        self.right_motor.reset()

    def wait(self):
        self.left_motor.wait()
        self.right_motor.wait()

    def follow_line(self):
        luminance = self.calc_luminance()
        self.pid_controller.adjust_motors(luminance, self)

    def found_node(self):
        if self.color_sensor.red * 2 > (self.color_sensor.green + self.color_sensor.blue) * 3:
            self.node_found = "red"
            print("red")
            return True
        if 55 > self.color_sensor.red > 35 and 180 > self.color_sensor.green > 155 and 130 > self.color_sensor.blue > 110:
            self.node_found = "blue"
            print("blue")
            return True
        self.node_found = ""
        return False

    def calc_luminance(self):
        return 0.2126 * self.color_sensor.red + 0.7152 * self.color_sensor.green + 0.0722 * self.color_sensor.blue

    def scan_for_edges(self):
        bool = self.found_node()
        print(f"first: {bool}")
        while bool:
            self.forward()
            print(bool)
            bool = self.found_node()
        print(f"last: {bool}")
        self.stop()
        return self.find_edges()

    def find_edges(self):
        edges = []
        start_time = time.time()
        while time.time() - start_time < self.TIME360_AT100:
            self.rotate(100)
            luminance = 100
            while luminance > 90:
                luminance = self.calc_luminance()
                self.rotate(100)
            time.sleep(0.2)
            edges.append('a')
            print(edges)
        return edges

    def cur_voltage(self):
        voltage_file = open('/sys/class/power_supply/lego-ev3-battery/voltage_now')
        return int(voltage_file.read())

    def cur_current(self):
        current_file = open('/sys/class/power_supply/lego-ev3-battery/current_now')
        return int(current_file.read())



