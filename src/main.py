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

    start_time = time.time()

    # go to first Node
    # while True:
    #     robot.follow_line()
    #     if robot.found_node():
    #         robot.stop()
    #         robot.enter_node()
    #         robot.stop()
    #         COMMUNICATION TELLS US THE NODE WE ARE ON
    #         robot.odometry.set_even_odd_nodes(node_x, node_y)
    #         break
    #

    # work on Planet
    while True:
        if robot.found_node():
            robot.stop()
            robot.enter_node()
            robot.stop()
            if not robot.on_ret_from_obst:
                robot.odometry.det_new_pos(robot)
            else:
                robot.on_ret_from_obst = False
                robot.x_coord = robot.last_node[0]
                robot.y_coord = robot.last_node[1]
                robot.direction = (robot.last_node[2] + 180) % 360
            print(f"edges: {robot.scan_for_edges()}")  # only if node not already known!
            # break
        elif robot.found_obstacle():
            robot.play_sound()
            robot.on_ret_from_obst = True
            robot.turn_around()
        else:
            robot.follow_line()




    print(time.time() - start_time)





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
