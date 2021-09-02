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

    client_id = '131' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
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
    planet = Planet()
    communication = Communication(client, logger, planet)

    # go to first Node
    while True:
        robot.follow_line()
        if robot.found_node():
            robot.stop()
            robot.enter_node()
            robot.stop()

            # scan for edges
            edges = robot.scan_for_edges()

            # initialialize communication and odometry
            communication.testplanet_message("Gromit")  #################### to be removed!!!
            communication.ready_message()
            robot.odometry.init(communication.startX, communication.startY, communication.startOrientation, robot)

            # determine new direction
            direction = robot.direction  # INTELLIGENCE

            # submit chosen path, wait and exit communication
            communication.pathSelect_message(robot.x_coord, robot.y_coord, direction)
            communication.wait()
            robot.play_sound()

            if communication.startDirectionC is not None:
                direction = communication.startDirectionC
            robot.turn_to_direction(direction)
            robot.reset()
            robot.last_node = (robot.x_coord, robot.y_coord, robot.direction)
            break

    # print(f"com_x: {communication.startX}")
    # print(f"com_y: {communication.startY}")
    # print(f"com_dir: {communication.startOrientation}")

    # work on Planet
    while True:

        if robot.found_node():
            robot.stop()
            robot.enter_node()
            robot.stop()

            # update position of robot
            if not robot.on_ret_from_obst:
                robot.odometry.det_new_pos(robot)
            else:
                robot.set_pos_and_dir(robot.last_node[0], robot.last_node[1], robot.last_node[2])
                robot.path_message()

            # scan for edges
            # only if node not already known!
            edges = robot.scan_for_edges()

            # send driven path and correct position
            robot.current_node = (robot.x_coord, robot.y_coord, (robot.direction + 180) % 360)
            communication.path_message(robot.last_node, robot.current_node, robot.on_ret_from_obst)
            robot.set_pos_and_dir(communication.endX, communication.endY, communication.endDirection)

            # determine new direction
            direction = robot.direction  # INTELLIGENCE

            # submit chosen path, wait and exit communication
            communication.pathSelect_message(robot.x_coord, robot.y_coord, direction)
            communication.wait()
            robot.play_sound()

            # terminate if task done
            if planet.task_done:
                if planet.type_task_done == "target reached":
                    communication.targetReached_message()
                elif planet.type_task_done == "exploration completed":
                    communication.explorationCompleted_message()
                break

            # update direction and exit node
            print(f"startDirection: {communication.startDirectionC}")
            if communication.startDirectionC is not None:
                direction = communication.startDirectionC
            robot.turn_to_direction(direction)
            robot.last_node = (robot.x_coord, robot.y_coord, robot.direction)
            robot.on_ret_from_obst = False
            robot.reset()
            # break
        elif robot.found_obstacle():
            robot.play_sound()
            robot.on_ret_from_obst = True
            robot.turn_around()
        else:
            robot.follow_line()

    # while True:
    #     try:
    #         if robot.found_node():
    #             robot.stop()
    #             robot.enter_node()
    #             robot.stop()
    #             robot.odometry.det_new_pos(robot)
    #
    #             # scan for edges
    #             edges = robot.scan_for_edges()
    #         else:
    #             robot.follow_line()
    #     except KeyboardInterrupt:
    #         robot.stop()
    #         break



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
