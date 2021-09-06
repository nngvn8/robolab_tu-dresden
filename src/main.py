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

            # initialize communication and odometry
            communication.testplanet_message("Boseman")  # ################### to be removed!!!
            communication.ready_message()
            robot.odometry.init(communication.startX, communication.startY, communication.startOrientation, robot)

            # add first node to map if not already in it with path unveil
            if not (robot.x_coord, robot.y_coord) in planet.map:
                planet.map[(robot.x_coord, robot.y_coord)] = {}

            open_edges = robot.scan_for_edges()

            # add open edges/node if not already known
            for edge in open_edges:
                if edge not in planet.map[(robot.x_coord, robot.y_coord)].keys():
                    planet.add_open_node((robot.x_coord, robot.y_coord), edge)

            # mark as scanned
            planet.scanned_nodes.append((robot.x_coord, robot.y_coord))
            print(f"scanned_nodes: {planet.scanned_nodes}")

            # EDGECASE: current node unveiled by communication before we could scan it
            # remove from open nodes if there are no open edges left
            if (robot.x_coord, robot.y_coord) in planet.edges_open_node \
                    and planet.edges_open_node[(robot.x_coord, robot.y_coord)] == []:
                del planet.edges_open_node[(robot.x_coord, robot.y_coord)]
                planet.open_nodes.remove((robot.x_coord, robot.y_coord))

            # DETERMINE NEW DIRECTION

            # set target as not reachable and only c    hange if it is
            path_to_target = None
            direction = None  # ### ??

            # if target set
            if planet.target is not None:
                path_to_target = planet.shortest_path((robot.x_coord, robot.y_coord), planet.target)

                # if reachable
                if path_to_target is not None:
                    direction = path_to_target[0][1]

            # Exploration if no target or target not reachable
            if planet.target is None or path_to_target is None:
                open_edges = planet.get_open_edges((robot.x_coord, robot.y_coord))

                # open edges at current node
                if open_edges != []:
                    direction = open_edges[0]

                # no open edges at current node
                else:
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
            robot.last_node = ((robot.x_coord, robot.y_coord), robot.direction)
            break  # continue with second while loop which works on the planet

    # WORK ON PLANET
    while True:

        if robot.found_node():
            print("############################NODE################################")
            robot.stop()
            robot.enter_node()
            robot.reset()

            pos_last_node = robot.last_node[0]
            dir_last_node = robot.last_node[1]

            # determine the node the robot is currently at
            # if path already known set end of path as current node
            if pos_last_node in planet.map and dir_last_node in planet.map[pos_last_node]:
                cur_position = planet.map[pos_last_node][dir_last_node][0]
                cur_direction = planet.map[pos_last_node][dir_last_node][1]
                current_node = (cur_position, cur_direction)
            elif robot.on_ret_from_obst:  # returning from an obstacle
                current_node = robot.last_node
            else:
                current_node = robot.odometry.det_new_pos(robot)

            # reset motor_positions
            robot.odometry.motor_positions = []

            # send driven path and correct position
            communication.path_message(robot.last_node, current_node, robot.on_ret_from_obst)
            robot.set_pos_and_dir(communication.endX, communication.endY, communication.endDirection)

            print(f"x_corr: {robot.x_coord}")
            print(f"y_corr: {robot.y_coord}")

            # mark target as reached if it is
            if (robot.x_coord, robot.y_coord) == planet.target:
                planet.target = None
                planet.task_done = True
                planet.type_task_done = "target reached"

            # scan node for edges if not already scanned or all for edges known
            if (robot.x_coord, robot.y_coord) not in planet.scanned_nodes:
                open_edges = robot.scan_for_edges()

                # add open edges/node if not already known
                for edge in open_edges:
                    if edge not in planet.map[(robot.x_coord, robot.y_coord)].keys():
                        planet.add_open_node((robot.x_coord, robot.y_coord), edge)

                # mark as scanned
                planet.scanned_nodes.append((robot.x_coord, robot.y_coord))
                print(f"scanned_nodes: {planet.scanned_nodes}")

                # EDGECASE: current node unveiled by communication before we could scan it
                # remove from open nodes if there are no open edges left
                if (robot.x_coord, robot.y_coord) in planet.edges_open_node and planet.edges_open_node[(robot.x_coord, robot.y_coord)] == []:
                    del planet.edges_open_node[(robot.x_coord, robot.y_coord)]
                    planet.open_nodes.remove((robot.x_coord, robot.y_coord))

            # DETERMINE NEW DIRECTION

            # set target as not reachable and only change if it is
            path_to_target = None

            print(f"open nodes LIST: {planet.open_nodes}")
            print(f"open nodes: {planet.edges_open_node}")
            print(f"target: {planet.target}")

            # if target set
            if planet.target is not None:
                path_to_target = planet.shortest_path((robot.x_coord, robot.y_coord), planet.target)
                print(f"path_to_target: {path_to_target}")

                # if reachable
                if path_to_target is not None:
                    direction = path_to_target[0][1]

            # Exploration if no target or target not reachable
            if planet.target is None or path_to_target is None:
                open_edges = planet.get_open_edges((robot.x_coord, robot.y_coord))
                print(f"local open edges: {open_edges}")

                # open edges at current node
                if open_edges != []:
                    direction = open_edges[0]

                # no open edges at current node
                else:

                    # closest nodes with open edges left
                    if planet.open_nodes != []:
                        path_to_node = planet.closest_open_node((robot.x_coord, robot.y_coord))
                        print(f"path to closest open node: {path_to_node}")

                        # handeling the hopefully fixed error that an empty list is returned
                        if path_to_node == []:
                            print(f"LIST EMPTY!!!")
                            print(f"MAP:")
                            for node in planet.map:
                                print(f"{node}: {planet.map[node]}")
                            path_to_node = None

                        if path_to_node is not None:
                            print(f"closest node: {path_to_node[-1]}")
                            direction = path_to_node[0][1]
                        else:  # unveiled nodes that cant be reached -> terminate exploration
                            planet.task_done = True
                            planet.type_task_done = "exploration completed"
                    else:
                        planet.task_done = True
                        planet.type_task_done = "exploration completed"

            # notify server if task done
            if planet.task_done:
                print(f"planet task done: {planet.task_done}")
                print(f"planet type task done: {planet.type_task_done}")
                if planet.type_task_done == "target reached":
                    communication.targetReached_message()
                elif planet.type_task_done == "exploration completed":
                    communication.explorationCompleted_message()

            # terminate if server confirms completed task
            if communication.task_done:
                break

            # submit chosen path, wait and exit communication
            communication.pathSelect_message(robot.x_coord, robot.y_coord, direction)
            communication.wait()
            robot.play_sound()

            print(f"communication order: {communication.startDirectionC}")
            # update direction, turn and update
            if communication.startDirectionC is not None \
                    and (robot.x_coord, robot.y_coord, communication.startDirectionC) not in planet.meteor_nodes:
                direction = communication.startDirectionC
            robot.turn_to_direction(direction)
            robot.last_node = ((robot.x_coord, robot.y_coord), robot.direction)

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
