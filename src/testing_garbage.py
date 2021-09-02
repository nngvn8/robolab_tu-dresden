import time
from robot import Robot
robot = Robot()

# motor positions
print(f"left_motor position: {robot.left_motor.position}")
print(f"right_motor position: {robot.right_motor.position}")

# color
while True:
    print(f"red: {robot.color_sensor.red}")
    print(f"green: {robot.color_sensor.green}")
    print(f"blue: {robot.color_sensor.blue}")
    time.sleep(2)

# luminance
print(f"{robot.calc_luminance()}")

# found_node
print(f"found_node: {robot.found_node()}")

# current and voltage
print(f"cur_voltage: {robot.cur_voltage()}")
print(f"cur_current: {robot.cur_current()}")


# key-board-interrupt
try:
    pass
except KeyboardInterrupt:
    print(time.time() - start_time)

# count motor pos
robot.left_motor.reset()
robot.right_motor.reset()
while True:
    try:
        robot.rotate()
    except KeyboardInterrupt:
        print(f"left_motor position: {robot.left_motor.position}")
        print(f"right_motor position: {robot.right_motor.position}")
        robot.left_motor.stop(stop_action='hold')
        robot.right_motor.stop(stop_action='hold')
        break

while True:
    try:
        robot.forward()
        robot.odometry.add_motor_pos(robot)
    except KeyboardInterrupt:
        robot.stop()
        break
robot.odometry.det_new_pos(robot)
print(f"left motor pos: {robot.left_motor.position}")
print(f"left motor pos: {robot.right_motor.position}")

# test turns
speed = 100
turn = 620/4
robot.left_motor.reset()
robot.right_motor.reset()
while robot.left_motor.position < turn:
    robot.left_motor.run_forever(speed_sp=speed)
    robot.right_motor.run_forever(speed_sp=-speed)

#


# measure time for rotation at certain speed
start_time = time.time()

counter = 0
laps = 1
while counter < 2 * laps:
    robot.rotate(100)
    luminance = 200
    while luminance > 80:
        print(f"{luminance}")
        luminance = robot.calc_luminance()
        robot.rotate(100)
    print(f"{luminance}")
    counter += 1
    time.sleep(0.2)
    print(f"counter: {counter}")
robot.stop()
print(time.time() - start_time)
