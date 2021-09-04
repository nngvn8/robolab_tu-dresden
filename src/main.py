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

    # GO TO FIRST NODE
    while True:
        robot.follow_line()
        if robot.found_node():
            robot.stop()
            robot.enter_node()
            robot.stop()

            # initialialize communication and odometry
            communication.testplanet_message("Chadwick")  #################### to be removed!!!
            communication.ready_message()
            robot.odometry.init(communication.startX, communication.startY, communication.startOrientation, robot)

            # scan for edges
            open_edges = robot.scan_for_edges()
            for edge in open_edges:
                planet.add_open_node((robot.x_coord, robot.y_coord), edge)
            planet.scanned_nodes.append((robot.x_coord, robot.y_coord))


            # DETERMINE NEW DIRECTION

            # set target as not reachable and only c    hange if it is
            path_to_target = None
            direction = None  #### ??

            # if target set
            if planet.target is not None:
                path_to_target = planet.shortest_path((robot.x_coord, robot.y_coord), planet.target)

                # if reachable
                if path_to_target is not None:
                    direction = path_to_target[1]

            # Exploration if no target or target not reachable
            if planet.target is None or path_to_target is None:
                open_edges = planet.get_open_edges((robot.x_coord, robot.y_coord))

                # open edges at current node
                if open_edges != []:
                    direction = open_edges[0]

                # no open edges at current node
                else:
                    path_to_node = None
                    # unveiled nodes left
                    if planet.open_nodes != []:
                        path_to_node = planet.closest_open_node((robot.x_coord, robot.y_coord))

                    direction = path_to_node[0][1]

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

    # WORK ON PLANET
    while True:

        if robot.found_node():
            robot.stop()
            robot.enter_node()
            robot.reset()

            # update position of robots
            if not robot.on_ret_from_obst:
                robot.odometry.det_new_pos(robot)
            else:
                robot.set_pos_and_dir(robot.last_node[0], robot.last_node[1], robot.last_node[2])

            # send driven path and correct position
            robot.current_node = (robot.x_coord, robot.y_coord, (robot.direction + 180) % 360)
            communication.path_message(robot.last_node, robot.current_node, robot.on_ret_from_obst)
            robot.set_pos_and_dir(communication.endX, communication.endY, communication.endDirection)

            if (robot.x_coord, robot.y_coord) == planet.target:
                planet.task_done = True
                planet.type_task_done = "target reached"

            # scan node for edges if not already known
            if (robot.x_coord, robot.y_coord) not in planet.scanned_nodes:
                open_edges = robot.scan_for_edges()
                for edge in open_edges:
                    planet.add_open_node((robot.x_coord, robot.y_coord), edge)
                planet.scanned_nodes.append((robot.x_coord, robot.y_coord))

            # DETERMINE NEW DIRECTION

            # set target as not reachable and only change if it is
            path_to_target = None

            # if target set
            if planet.target is not None:
                path_to_target = planet.shortest_path((robot.x_coord, robot.y_coord), planet.target)

                # if reachable
                if path_to_target is not None:
                    direction = path_to_target[1]

            # Exploration if no target or target not reachable
            if planet.target is None or path_to_target is None:
                open_edges = planet.get_open_edges((robot.x_coord, robot.y_coord))

                # open edges at current node
                if open_edges != []:
                    direction = open_edges[0]

                # no open edges at current node
                else:
                    # closest nodes with open edges left
                    if planet.open_nodes != []:
                        path_to_node = planet.closest_open_node((robot.x_coord, robot.y_coord))
                        if path_to_node is not None:
                            direction = path_to_node[0][1]
                        else:  # unveiled nodes that cant be reached -> terminate exploration
                            planet.task_done = True
                            planet.type_task_done = "exploration completed"
                    else:
                        planet.task_done = True
                        planet.type_task_done = "exploration completed"

            # terminate if task done
            if planet.task_done:
                if planet.type_task_done == "target reached":
                    communication.targetReached_message()
                elif planet.type_task_done == "exploration completed":
                    communication.explorationCompleted_message()
                break

            # submit chosen path, wait and exit communication
            communication.pathSelect_message(robot.x_coord, robot.y_coord, direction)
            communication.wait()
            robot.play_sound()

            # update direction, turn and update
            if communication.startDirectionC is not None \
                    and (robot.x_coord, robot.y_coord, communication.startDirectionC) not in planet.meteor_nodes:
                direction = communication.startDirectionC
            robot.turn_to_direction(direction)
            robot.last_node = (robot.x_coord, robot.y_coord, robot.direction)

            # resetting
            robot.on_ret_from_obst = False
            robot.reset()

        elif robot.found_obstacle():
            robot.play_sound()
            robot.on_ret_from_obst = True
            robot.turn_around()

        else:
            robot.follow_line()



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
