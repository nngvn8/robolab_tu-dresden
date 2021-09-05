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


# DIJKSTRA OLD
    # checks if we dont even know the start or target
    if start not in self.map or target not in self.map:
        return None

    distance = copy.deepcopy(self.map)
    predecessor = copy.deepcopy(self.map)
    for i in self.map:
        predecessor[i] = None
        distance[i] = inf
    distance[start] = 0
    NodeWO = copy.deepcopy(list(self.map.keys()))
    while bool(NodeWO):
        u = next(iter(NodeWO))
        for it in distance:
            if distance[it] < distance[u] and it in NodeWO:
                u = it
        if u == target:  ##################################
            break
        print(f"distance to {u}: {distance[u]}")
        if distance[u] == inf:
            return None
        NodeWO.remove(u)
        # del distancehelp[u]
        nachbarn = []
        for i in self.map[u]:
            nachbarn.append(self.map[u][i][0])
        for v in nachbarn:
            if v in NodeWO:
                ########################################################## distanz_update
                distanceuv = 0
                for o in self.map[u]:
                    if self.map[u][o][0] == v:
                        distanceuv = self.map[u][o][2]
                if distanceuv < 0:
                    continue
                alternativ = distance[u] + distanceuv
                if alternativ < distance[v]:
                    distance[v] = alternativ
                    predecessor[v] = u

    #####################################################
    Weg = [target]
    ab = target

    while bool(predecessor[ab]):  # Der predecessor des Startknotens ist null
        ab = predecessor[ab]
        Weg.insert(0, ab)

    ret = []
    currentdirection = Direction.SOUTH

    iter2 = 1
    for i in Weg:
        currentweight = inf
        for direction in self.map[i]:
            if iter2 < len(Weg):
                if Weg[iter2] == self.map[i][direction][0] and self.map[i][direction][2] < currentweight:
                    currentdirection = direction
                    currentweight = self.map[i][direction][2]

        ret.append((i, currentdirection))
        iter2 += 1
    ret.pop()
    return ret