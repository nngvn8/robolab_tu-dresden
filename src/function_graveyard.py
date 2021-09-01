# robot
def get_cur_voltage(self):
    voltage_file = open('/sys/class/power_supply/lego-ev3-battery/voltage_now')
    return int(voltage_file.read())


def get_cur_current(self):
    current_file = open('/sys/class/power_supply/lego-ev3-battery/current_now')
    return int(current_file.read())

def turn_w_time(self, degree=90):
    turning_time = self.TIME360_AT100 * degree / 360
    start_time = time.time()
    while time.time() - start_time <= turning_time + 0.1:
        self.rotate()
    self.stop()

    def find_edges_old(self):
        edges = []
        m_pos_ctr = 1
        self.left_motor.reset()
        self.right_motor.reset()
        turn = 360*2*0.90
        while self.left_motor.position < turn and self.right_motor.position > -turn:
            self.rotate()
            luminance = self.calc_luminance()
            print(luminance)
            if luminance < 70 and m_pos_ctr == 2:
                edges.append('a')
                m_pos_ctr = 1
            else:
                m_pos_ctr += 1
        self.left_motor.stop(stop_action='hold')
        self.right_motor.stop(stop_action='hold')
        return edges