import numpy as np
import random as rd
import pygame
import pygame.locals
import sys
import time


class Network:
    def __init__(self, size):
        self.network = np.zeros((size, size))
        self.size = size

    def add_segment(self, coord_1, coord_2):
        self.network[coord_1, coord_2] = 1

    def del_segment(self, coord_1, coord_2):
        self.network[coord_1, coord_2] = 0

    def check_if_segment(self, coord_1, coord_2):
        if self.network[coord_1, coord_2] == 1:
            return True
        else:
            return False

    def check_if_trap(self, coord_1, coord_2):
        # The segment will be surrounded by another segment if True
        if self.check_if_segment(coord_1, coord_2 - 1) and \
                self.check_if_segment(coord_1 - 1, coord_2) and \
                self.check_if_segment((coord_1 + 1) % self.size, coord_2) and \
                self.check_if_segment(coord_1, (coord_2 + 1) % self.size):
            return True
        else:
            return False

    def return_network(self):
        return self.network


class InitialConfig:
    def __init__(self, segment_count):
        self.segment_count = segment_count
        self.network = Network(segment_count)

    def create_config(self):
        failed_count = 0
        history = []
        where_put_segment = self.where_put_segment()
        history.append(where_put_segment)
        self.network.add_segment(where_put_segment[0], where_put_segment[1])
        while len(history) != self.segment_count:
            if self.network.check_if_trap(history[-1][0], history[-1][1]):
                failed_count += 1
                if failed_count < 10:
                    try:
                        for i in range(5):
                            self.network.del_segment(history[-1][0], history[-1][1])
                            del history[-1]
                            if len(history) == 0:
                                where_put_segment = self.where_put_segment()
                                history.append(where_put_segment)
                    except:
                        where_put_segment = self.where_put_segment()
                        history.append(where_put_segment)
                        self.network.add_segment(where_put_segment[0], where_put_segment[1])
                else:
                    failed_count = 0
                    history = []
                    where_put_segment = self.where_put_segment()
                    history.append(where_put_segment)
                    self.network.add_segment(where_put_segment[0], where_put_segment[1])
            else:
                where_put_segment = self.generate_position(history[-1])
                if not self.network.check_if_segment(where_put_segment[0], where_put_segment[1]):
                    self.network.add_segment(where_put_segment[0], where_put_segment[1])
                    history.append(where_put_segment)
                else:
                    pass
        return np.array(history)

    def energy(self):
        pass

    def generate_position(self, present_position):
        where_to_go = rd.randrange(4)
        if where_to_go == 0:
            segment_place = [present_position[0] - 1, present_position[1]]
        elif where_to_go == 1:
            segment_place = [present_position[0], (present_position[1] + 1) % self.segment_count]
        elif where_to_go == 2:
            segment_place = [(present_position[0] + 1) % self.segment_count, present_position[1]]
        elif where_to_go == 3:
            segment_place = [present_position[0], present_position[1] - 1]
        else:
            raise ValueError
        return segment_place

    def where_put_segment(self):
        return [rd.randrange(self.segment_count), rd.randrange(self.segment_count)]


class Algorithm:
    def __init__(self, segment_count):
        self.segment_count = segment_count
        self.config = InitialConfig(segment_count).create_config()
        self.energy = 0

    def movement(self, step_number):
        for i in range(step_number):
            choose_segment = rd.randint(0, self.segment_count)
            if choose_segment == 0 or choose_segment == self.segment_count:
                self.ending_movement(choose_segment)
            else:
                self.config[choose_segment] = self.knee_movement(choose_segment)
        return self.config

    def knee_movement(self, segment):
        new_place = self.config[segment - 1] + self.config[(segment + 1) %
                                                           self.segment_count] - self.config[segment]
        if new_place in self.config:
            return self.config[segment]
        else:
            return new_place

    def ending_movement(self, segment):
        choose_movement_type = rd.randint(0, 1)
        if choose_movement_type == 0:
            return self.reptile(segment)
        else:
            return self.ending_rotation(segment)

    def reptile(self, segment): # modify newly created element
        if segment == 0:
            self.apply_movement_for_reptile(-1, -1)
        else:
            self.apply_movement_for_reptile(0, 1)

    def apply_movement_for_reptile(self, segment, roll):
        direction = rd.randint(0, 3)
        if direction == 0:
            if self.config[segment] + [0, 1] not in self.config:
                self.config = np.roll(self.config, roll, axis=0)
                self.config[segment] += [0, 1]
        elif direction == 1:
            if self.config[segment] + [1, 0] not in self.config:
                self.config = np.roll(self.config, roll, axis=0)
                self.config[segment] += [1, 0]
        elif direction == 2:
            if self.config[segment] + [-1, 0] not in self.config:
                self.config = np.roll(self.config, roll, axis=0)
                self.config[segment] += [-1, 0]
        elif direction == 3:
            if self.config[segment] + [0, -1] not in self.config:
                self.config = np.roll(self.config, roll, axis=0)
                self.config[segment] += [0, -1]

    def ending_rotation(self, segment):
        direction = rd.randint(0, 3)
        if segment == 0:
            if direction == 0:
                if self.config[1] + [0, 1] not in self.config:
                    self.config[0] = self.config[1] + [0, 1]
            elif direction == 1:
                if self.config[1] + [0, -1] not in self.config:
                    self.config[0] = self.config[1] + [0, -1]
            elif direction == 2:
                if self.config[1] + [-1, 0] not in self.config:
                    self.config[0] = self.config[1] + [-1, 0]
            elif direction == 3:
                if self.config[1] + [1, 0] not in self.config:
                    self.config[0] = self.config[1] + [1, 0]
        else:
            if direction == 0:
                if self.config[-2] + [0, 1] not in self.config:
                    self.config[-1] = self.config[1] + [0, 1]
            elif direction == 1:
                if self.config[-2] + [0, -1] not in self.config:
                    self.config[-1] = self.config[1] + [0, -1]
            elif direction == 2:
                if self.config[-2] + [-1, 0] not in self.config:
                    self.config[-1] = self.config[1] + [-1, 0]
            elif direction == 3:
                if self.config[-2] + [1, 0] not in self.config:
                    self.config[-1] = self.config[1] + [1, 0]

    def energy_change(self):
        pass


if __name__ == '__main__':
    pygame.init()
    parts_count = 30
    # q = InitialConfig(parts_count)
    q = Algorithm(parts_count)
    positions = q.movement(1000)
    counts = {}
    print(positions)
    #print(positions)
    #print("=" * 30)

    for pos in positions:
        # assert (0 <= pos[0] < parts_count) and (0 <= pos[1] < parts_count)
        a = tuple(pos)
        counts[a] = counts.get(a, 0) + 1

    display_size = (500, 500)
    assert display_size[0] == display_size[1]
    display = pygame.display.set_mode(display_size)

    part_size = display_size[0] / parts_count
    get_rect_coordinates = lambda pos: (pos[0] * part_size, pos[1] * part_size, part_size, part_size)
    get_color = lambda x: (0, 200, 0) if x == 1 else (200, 0, 0)

    display.fill((255, 255, 255))

    for pos, count in counts.items():
        #print("{}: {}".format(pos, count))
        pygame.draw.rect(
            display,
            get_color(count),
            get_rect_coordinates(pos),
            0)
        pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit()
        time.sleep(0.2)
