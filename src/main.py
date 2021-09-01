#!/usr/bin/env python3

import ev3dev.ev3 as ev3
import logging
import os
import paho.mqtt.client as mqtt
import uuid
import signal

import time

from communication import Communication
from robot import Robot
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

    # # 10 laps
    # robot.left_motor.reset()
    # robot.right_motor.reset()
    # while True:
    #     try:
    #         robot.rotate()
    #     except KeyboardInterrupt:
    #         print(f"left_motor position: {robot.left_motor.position}")
    #         print(f"right_motor position: {robot.right_motor.position}")
    #         robot.left_motor.stop(stop_action='hold')
    #         robot.right_motor.stop(stop_action='hold')
    #         break

    # while True:
    #     robot.follow_line()
    #     if robot.found_obstacle():
    #         robot.turn_around()
    robot.turn_to_direction(180)
    # while True:
    #     if robot.found_node():
    #         robot.enter_node()
    #         robot.odometry.det_new_pos()
    #         robot.stop()
    #         print(f"edges: {robot.scan_for_edges()}")  # only if node not already known!
    #         # break
    #     elif robot.found_obstacle():
    #         # robot.turn(180)
    #         pass
    #     else:
    #         robot.follow_line()


    print(f"length of array with motor positions: {len(robot.odometry.motor_positions)}")


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
