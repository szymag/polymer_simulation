import numpy as np
import random as rd
import pygame
import pygame.locals
import sys
import time

class Segment:
    def __init__(self, x, y):
        self.coordinate = (x, y)
        # self.previous_segment = prev_neigh
        # self.next_segment = next_neigh


class Network:
    def __init__(self, size):
        self.network = np.zeros((size, size))

    def add_segment(self, coord_1, coord_2):
        value = 1
        self.network[coord_1, coord_2] = 1

    def del_segment(self, coord_1, coord_2):
        self.network[coord_1, coord_2] = 0

    def check_if_segment(self, coord_1, coord_2):
        if self.network[coord_1, coord_2] == 1:
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
        where_put_segment = (rd.randint(0, self.segment_count - 1), rd.randint(0, self.segment_count - 1))
        history.append(where_put_segment)
        self.network.add_segment(where_put_segment[0], where_put_segment[1])
        while len(history) != self.segment_count:
            print(len(history))
            if self.network.check_if_segment(history[-1][0], history[-1][1] - 1) and \
                self.network.check_if_segment(history[-1][0] - 1, history[-1][1]) and \
                self.network.check_if_segment((history[-1][0] + 1) % self.segment_count, history[-1][1]) and \
                    self.network.check_if_segment(history[-1][0], (history[-1][1] + 1) % self.segment_count):
                failed_count += 1
                if failed_count < 10:
                    try:
                        for i in range(5):
                            self.network.del_segment(history[-1][0], history[-1][1])
                            del history[-1]
                            if len(history) == 0:
                                where_put_segment = (
                                rd.randint(0, self.segment_count - 1), rd.randint(0, self.segment_count - 1))
                                history.append(where_put_segment)
                    except:
                        where_put_segment = (rd.randint(0, self.segment_count - 1), rd.randint(0, self.segment_count - 1))
                        history.append(where_put_segment)
                        self.network.add_segment(where_put_segment[0], where_put_segment[1])
                else:
                    failed_count = 0
                    history = []
                    where_put_segment = (rd.randint(0, self.segment_count - 1), rd.randint(0, self.segment_count - 1))
                    history.append(where_put_segment)
                    self.network.add_segment(where_put_segment[0], where_put_segment[1])
            else:
                where_put_segment = self.generate_position(history[-1])
                if not self.network.check_if_segment(where_put_segment[0], where_put_segment[1]):
                    self.network.add_segment(where_put_segment[0], where_put_segment[1])
                    history.append(where_put_segment)
                else:
                    pass
        return history

    def generate_position(self, present_position):
        where_to_go = rd.randint(0, 3)
        if where_to_go == 0:
            segment_place = (present_position[0] - 1, present_position[1])
        elif where_to_go == 1:
            segment_place = (present_position[0], (present_position[1] + 1) % self.segment_count)
        elif where_to_go == 2:
            segment_place = ((present_position[0] + 1) % self.segment_count, present_position[1])
        elif where_to_go == 3:
            segment_place = (present_position[0], present_position[1] - 1)
        else:
            raise ValueError
        return segment_place


class Algorithm:
    def __init__(self):
        pass


if __name__ == '__main__':
    pygame.init()
    parts_count = 500
    q = InitialConfig(parts_count)
    positions = q.create_config()
    counts = {}

    print(positions)
    print("=" * 30)

    for pos in positions:
        # assert (0 <= pos[0] < parts_count) and (0 <= pos[1] < parts_count)
        counts[pos] = counts.get(pos, 0) + 1

    display_size = (500, 500)
    assert display_size[0] == display_size[1]
    display = pygame.display.set_mode(display_size)

    part_size = display_size[0] / parts_count
    get_rect_coordinates = lambda pos: (pos[0] * part_size, pos[1] * part_size, part_size, part_size)
    get_color = lambda x: (0, 200, 0) if x == 1 else (200, 0, 0)

    display.fill((255, 255, 255))

    for pos, count in counts.items():
        print("{}: {}".format(pos, count))
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