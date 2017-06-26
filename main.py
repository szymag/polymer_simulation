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

    def is_active(self, segment):
        return self.network[segment[0], segment[1]] == State.active.value

    def is_stuck(self, segment):
        # The segment will be surrounded by another segment if True
        neighbours = [list(map(lambda x: x % self.size, map(sum,
            zip(segment, move)))) for move in InitialConfig.moves]
        return all(map(self.is_active, neighbours))

    def return_network(self):
        return self.network


class InitialConfig:
    moves = ((-1, 0), (0, 1), (1, 0), (0, -1))

    def __init__(self, segment_count):
        self.segment_count = segment_count
        self.network = Network(segment_count)
        self.failed_count = 0
        self.reset()

    def reset(self):
        segment = self.random_segment()
        self.history = [segment]
        self.network.add(segment)

    def backtrack(self):
        steps = min(5, len(self.history))

        for previous_segment in self.history[-steps:]:
            self.network.remove(previous_segment)
        del self.history[-steps:]

        if len(self.history) == 0:
            self.reset()

    def step(self):
        try:
            segment = rd.choice(self.get_next_segments())
            self.network.add(segment)
            self.history.append(segment)
            return True
        except IndexError:
            return False

    def create_config(self):
        while len(self.history) != self.segment_count:
            success = self.step()
            if not success:
                self.failed_count += 1

                if self.failed_count < 10:
                    self.backtrack()
                else:
                    self.failed_count = 0
                    self.reset()

        return np.array(self.history)

    def energy(self):
        tmp = self.network.network
        return np.sum(tmp * np.roll(tmp, 1, axis=0) +\
               tmp * np.roll(tmp, -1, axis=0) +\
               tmp * np.transpose(np.roll(np.transpose(tmp), 1, axis=0)) +\
               tmp * np.transpose(np.roll(np.transpose(tmp), -1, axis=0))) / 2

    def get_next_segments(self):
        fit_to_network_size = lambda x: x % self.segment_count
        possible_positions = [list(map(fit_to_network_size,
                                       map(sum, zip(self.history[-1], move)))) for move in self.moves]
        return list(filter(lambda x: not self.network.is_active(x), possible_positions))

    def random_segment(self):
        return [rd.randrange(self.segment_count), rd.randrange(self.segment_count)]


class Algorithm:
    def __init__(self, segment_count):
        self.segment_count = segment_count
        self.init = InitialConfig(segment_count)
        self.config = self.init.create_config()
        self.tmp =self.config
        self.energy = self.init.energy()

    def movement(self, step_number):
        for i in range(step_number):
            segment = rd.randint(2, self.segment_count-2)
            if segment == 0 or segment == self.segment_count:
                self.ending_movement(segment)
            else:
                self.knee_movement(segment)

        return self.config

    def knee_movement(self, segment):
        new_place = (self.config[segment - 1] + self.config[(segment + 1) %
                    self.segment_count] - self.config[segment] + [self.segment_count, self.segment_count])%self.segment_count
        if np.equal(new_place, self.config).all(axis=1).any():
            pass
        else:
            self.config[segment] = new_place

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
       # print(self.config)
        tmp_network = Network(self.segment_count)
        for i in self.config:
            tmp_network.add(i)
        net = tmp_network.network
        return np.sum(net * np.roll(net, 1, axis=0) + \
                      net * np.roll(net, -1, axis=0) + \
                      net * np.transpose(np.roll(np.transpose(net), 1, axis=0)) + \
                      net * np.transpose(np.roll(np.transpose(net), -1, axis=0))) / 2


if __name__ == '__main__':
    pygame.init()
    parts_count = 50
    q = InitialConfig(parts_count)
    q = Algorithm(parts_count)
    positions = q.movement(3000)
    #positions = q.create_config()
    counts = {}
    #print(q.energy())
    print(positions)
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
