import enum
import numpy as np
import random as rd
import pygame
import pygame.locals
import sys
import time

class State(enum.Enum):
    inactive = 0
    active = 1

class Network:
    def __init__(self, size):
        self.network = np.zeros((size, size))
        self.size = size

    def add(self, segment):
        self.network[segment[0], segment[1]] = State.active.value

    def remove(self, segment):
        self.network[segment[0], segment[1]] = State.inactive.value

    def check_if_segment(self, segment):
        return self.network[segment[0], segment[1]] == State.active.value

    def is_stuck(self, segment):
        # The segment will be surrounded by another segment if True
        neighbours = [list(map(lambda x: x % self.size, map(sum,
            zip(segment, move)))) for move in InitialConfig.moves]
        return all(map(self.check_if_segment, neighbours))

    def return_network(self):
        return self.network


class InitialConfig:
    moves = ((-1, 0), (0, 1), (1, 0), (0, -1))

    def __init__(self, segment_count):
        self.segment_count = segment_count
        self.network = Network(segment_count)

    def create_config(self):
        failed_count = 0
        segment = self.where_put_segment()
        history = [segment]
        self.network.add(segment)
        while len(history) != self.segment_count:
            if self.network.is_stuck(history[-1]):
                failed_count += 1
                if failed_count < 10:
                    try:
                        for i in range(5):
                            self.network.remove(history[-1])
                            del history[-1]
                            if len(history) == 0:
                                segment = self.where_put_segment()
                                history.append(segment)
                    except:
                        segment = self.where_put_segment()
                        history.append(segment)
                        self.network.add(segment)
                else:
                    failed_count = 0
                    segment = self.where_put_segment()
                    history = [segment]
                    self.network.add(segment)
            else:
                segment = self.generate_position(history[-1])
                if not self.network.check_if_segment(segment):
                    self.network.add(segment)
                    history.append(segment)
        return np.array(history)

    def energy(self):
        pass

    def generate_position(self, present_position):
        move = self.moves[rd.randrange(len(self.moves))]
        position_after_move = map(sum, zip(present_position, move))

        fit_to_network_size = lambda x: x % self.segment_count
        return list(map(fit_to_network_size, position_after_move))

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
