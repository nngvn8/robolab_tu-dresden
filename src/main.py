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

    # robot.turn_w_ticks(360)
    # print(f"cur_voltage: {robot.cur_voltage()}")
    # print(f"cur_current: {robot.cur_current()}")
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



    # try:
    # except KeyboardInterrupt:
    #     print(time.time() - start_time)

    while True:
        # print(f"robot position {robot.left_motor.position}")
        # print(f"robot position {robot.right_motor.position}")
        if robot.found_node():
            robot.odometry.det_new_pos()  # robot as attribute of odometry?
            print(f"edges: {robot.scan_for_edges()}")     # should include det_new_pos?
            break
        else:
            robot.follow_line()

    # speed = 100
    # turn = 720*0.8
    # robot.left_motor.run_to_rel_pos(position_sp=turn, speed_sp=speed)  # correcting?
    # robot.right_motor.run_to_rel_pos(position_sp=-turn, speed_sp=-speed)  # correcting?
    # robot.left_motor.wait_until_not_moving()
    # print(robot.calc_luminance())
    # robot.left_motor.run_direct(duty_cycle_sp=40)
    # robot.right_motor.run_direct(duty_cycle_sp=-40)



    # robot.forward_w_ticks(360*14+100)
    # robot.odometry.det_new_pos()

    print(f"length of array with motor positions: {len(robot.odometry.motor_positions)}")

    # print(f"{robot.found_node()}")


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
