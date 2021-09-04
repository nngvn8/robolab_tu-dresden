class PIDController:

    # time per Iteration: 0.12555, 0.12779 0.12345
    # oscilation period: 12.345/14 = 0.88  13.674/15 = 0.91 -> 0.895

    def __init__(self):
        # k parameters times 100
        self.kp = 50  # kc = 60
        self.ki = 4
        self.kd = 20  # 42.76
        self.integral = 0
        self.last_error = 0
        self.offset = 170  # determined by experiment on line

    def adjust_motors(self, luminance, robot):
        # calculating needed parameters
        error = luminance - self.offset
        derivative = error - self.last_error
        if error > 0 > self.last_error or error < 0 < self.last_error:
            self.integral = error  # = 0 ?
        else:
            self.integral = self.integral / 3 + error

        # actual calculation and application of the adjustment
        # caution! for this application sensor has to be on the left side of the line!
        turn = error * self.kp + self.integral * self.ki + derivative * self.kd
        robot.left_motor.speed_sp = self.cap_speed(robot.default_speed + turn / 100)
        robot.right_motor.speed_sp = self.cap_speed(robot.default_speed - turn / 100)

        # committing the new motor speeds
        robot.left_motor.command = "run-forever"
        robot.right_motor.command = "run-forever"

        # storing the error of this iteration for next one
        self.last_error = error

    def cap_speed(self, speed):
        if abs(speed) > 1000:
            if speed < 0:
                speed = -1000
            else:
                speed = 1000
        return speed