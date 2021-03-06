import enum
import numpy as np
import random as rd
import pygame
import pygame.locals
import sys
import time
from math import sqrt

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

    def energy(self):
        total_en = 4 * self.size
        tmp = self.return_network()
        return total_en - np.sum(tmp * np.roll(tmp, 1, axis=0) +\
               tmp * np.roll(tmp, -1, axis=0) +\
               tmp * np.transpose(np.roll(np.transpose(tmp), 1, axis=0)) +\
               tmp * np.transpose(np.roll(np.transpose(tmp), -1, axis=0)))

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
        print(tmp)
        return np.sum(tmp * np.roll(tmp, 1, axis=0) +\
               tmp * np.roll(tmp, -1, axis=0) +\
               tmp * np.transpose(np.roll(np.transpose(tmp), 1, axis=0)) +\
               tmp * np.transpose(np.roll(np.transpose(tmp), -1, axis=0)))


    def get_next_segments(self):
        fit_to_network_size = lambda x: x % self.segment_count
        possible_positions = [list(map(fit_to_network_size,
                                       map(sum, zip(self.history[-1], move)))) for move in self.moves]
        return list(filter(lambda x: not self.network.is_active(x), possible_positions))

    def random_segment(self):
        return [rd.randrange(self.segment_count), rd.randrange(self.segment_count)]

    def energy(self):
        return self.network.energy()

class Algorithm:
    def __init__(self, segment_count):
        self.segment_count = segment_count
        self.init = InitialConfig(segment_count)
        self.config = self.init.create_config()
        self.tmp =self.config
        self.energy = self.init.energy()

    def movement(self, step_number):
        for _ in range(step_number):
            segment = rd.randrange(self.segment_count)
            new_place = self.config[segment]
            if segment == 0 or segment == self.segment_count-1:
                how_move = rd.randint(0,1)
                if how_move == 1:
                    new_place = self.ending_rotation(segment)
                    delta_energy = self.energy_change(self.config[segment], new_place)
                else:
                    self.new_config = self.reptile(segment)
                    delta_energy = self.energy_change(self.config[0], self.new_config[0]) +\
                    self.energy_change(self.config[-1], self.new_config[-1])
            else:
                new_place = self.knee_movement(segment)
                delta_energy = self.energy_change(self.config[segment], new_place)
            self.config[segment] = new_place
            self.energy -= delta_energy
            print("\rCurrent radius: {:>5}".format(self.radius()), end='')
            yield self.config

    def knee_movement(self, segment):
        new_place = (self.config[segment - 1] + self.config[(segment + 1) %
                    self.segment_count] - self.config[segment] + [self.segment_count, self.segment_count])%self.segment_count
        if not np.equal(new_place, self.config).all(axis=1).any():
            return new_place
        else:
            return self.config[segment]

    def reptile(self, segment):
        if segment == 0:
            return self.apply_movement_for_reptile(0, -1, -1)
        else:
            return self.apply_movement_for_reptile(-1, 1, 0)

    def apply_movement_for_reptile(self, segment, roll, to_move):
        #print(np.roll(self.config, roll, axis=0))

        new_config = np.roll(self.config, roll, axis=0)
        new_config[segment] = self.config[to_move]

        if not np.equal(new_config[segment], self.config).all(axis=1).any():
            return new_config
        else:
            return self.config

    def ending_rotation(self, segment):
        new_place = self.config[segment]
        if segment == 0:
            # we check if position is OK for previous segment
            index = 1
        else:
            index = -2
        move = rd.choice([[0, 1], [0, -1], [-1, 0], [1, 0]])
        if not np.equal((self.config[index] + move) % self.segment_count, self.config).all(axis=1).any():
            new_place = (self.config[index] + move) % self.segment_count

        return new_place

    def energy_change(self, before, after):
        neighbour = [[0, 1], [0, -1], [-1, 0], [1, 0]]
        e_old = len([(before+i)% self.segment_count for i in neighbour
                    if not np.equal(np.array((before+i)% self.segment_count), self.config).all(axis=1).any()])
        e_new = len([(after+i)% self.segment_count for i in neighbour
                    if not np.equal(np.array((after+i)% self.segment_count), self.config).all(axis=1).any()])
        return e_new - e_old

    def radius(self):
        return sqrt(np.sum(((self.config[-1] - self.config[0]) % self.segment_count)**2))


def draw_configuration(display, positions, part_size):
    background_color = (255, 255, 255)
    valid_position_color = (0, 200, 0)
    invalid_position_color = (200, 0, 0)
    border_weight = 0

    get_rect_coordinates = lambda pos: (pos[0] * part_size, pos[1] * part_size, part_size, part_size)
    get_color = lambda x: valid_position_color if x == 1 else invalid_position_color

    counts = {}
    for position in map(tuple, positions):
        counts[position] = counts.get(position, 0) + 1

    display.fill(background_color)

    for pos, count in counts.items():
        coord = get_rect_coordinates(pos)
        pygame.draw.rect(
            display,
            get_color(count),
            get_rect_coordinates(pos),
            border_weight)

    pygame.display.update()


if __name__ == '__main__':
    parts_count = 25
    part_size = 30
    moves_count = 3000
    sleep_delay_seconds = 0.01

    pygame.init()

    algorithm = Algorithm(parts_count)

    display_size = (part_size * parts_count, part_size * parts_count)
    display = pygame.display.set_mode(display_size)

    positions = algorithm.movement(moves_count)
    last_position = next(positions)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit()
        draw_configuration(display, last_position, part_size)
        try:
            last = next(positions)
        except StopIteration:
            pass
        time.sleep(sleep_delay_seconds)
