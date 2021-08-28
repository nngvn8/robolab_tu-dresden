#!/usr/bin/env python3

import ev3dev.ev3 as ev3
import logging
import os
import paho.mqtt.client as mqtt
import uuid
import signal

import time

from communication import Communication
from odometry import Robot
from planet import Direction, Planet

client = None  # DO NOT EDIT


def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client

    client_id = 'YOURGROUPID-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
    client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                         clean_session=True,  # We want a clean session after disconnect or abort/crash
                         protocol=mqtt.MQTTv311  # Define MQTT protocol version
                         )
    log_file = os.path.realpath(__file__) + '/../../logs/project.log'
    logging.basicConfig(filename=log_file,  # Define log file
                        level=logging.DEBUG,  # Define default mode
                        format='%(asctime)s: %(message)s'  # Define default logging format
                        )
    logger = logging.getLogger('RoboLab')

    # THE EXECUTION OF ALL CODE SHALL BE STARTED FROM WITHIN THIS FUNCTION.
    # ADD YOUR OWN IMPLEMENTATION HEREAFTER.

    robot = Robot()
    robot.turn_w_ticks()
    # robot.forward()
    # robot.find_edges()
    # start_time = time.time()
    #
    # counter = 0
    # laps = 1
    # while counter < 2 * laps:
    #     robot.rotate(100)
    #     luminance = 200
    #     while luminance > 80:
    #         print(f"{luminance}")
    #         luminance = robot.calc_luminance()
    #         robot.rotate(100)
    #     print(f"{luminance}")
    #     counter += 1
    #     time.sleep(0.2)
    #     print(f"counter: {counter}")
    # robot.stop()
    # print(time.time() - start_time)

    # robot.find_edges()
    # print(f"{robot.calc_luminance()}")


    # print(f"red: {robot.color_sensor.red}")
    # print(f"green: {robot.color_sensor.green}")
    # print(f"blue: {robot.color_sensor.blue}")

    # try:
    # except KeyboardInterrupt:
    #     print(time.time() - start_time)

    # while True:
    #     if robot.found_node():
    #         robot.scan_for_edges()
    #         break
    #     else:
    #         robot.follow_line()
    # print(f"{robot.found_node()}")

    robot.right_motor.run_to_rel_pos({'position_sp': -90 * 2 - 30, 'speed_sp': robot.rotation_speed})


# DO NOT EDIT
def signal_handler(sig=None, frame=None, raise_interrupt=True):
    if client and client.is_connected():
        client.disconnect()
    if raise_interrupt:
        raise KeyboardInterrupt()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    try:
        run()
        signal_handler(raise_interrupt=False)
    except Exception as e:
        signal_handler(raise_interrupt=False)
        raise e
