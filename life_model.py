import os
import sys
import time
from copy import copy
from enum import IntEnum
import random

DEFAULT_GENERATION_TIME = 100


class LifeModel(object):
    '''
    ' ' - Free space(0)
    '@' - Victim(1)
    '#' - Predator(2)
    '_' - Wall(3)
    '''

    class CellType(IntEnum):
        FREE_SPACE = 0
        VICTIM = 1
        PREDATOR = 2
        WALL = 3

    # constants
    STATS_IMPORTANT_CELLS_TYPES = [CellType.FREE_SPACE, CellType.VICTIM]
    LIVING_CELLS_TYPES = [CellType.VICTIM, CellType.PREDATOR]
    DEFAULT_LIFE_COUNTER = {CellType.VICTIM: 0, CellType.PREDATOR: 0}
    LEFT_SUITABLE_INDEX = 0

    # JUST FOR VISUAL STYLE
    COLORS = ('', '0;32;40m', '0;31;40m', '0;30;43m')  # red, green, yellow
    DIRECTIONS = ((0, 1), (1, 0), (-1, 0), (0, -1))
    CHANGE_COLOR = '\x1b['
    NORMAL_COLOR = CHANGE_COLOR + '0m'
    CELL_VISUALIZATION_SYMBOL = (' ', '@', '#', ' ')

    class Cell(object):
        def __init__(
            self, cell_type, time_to_death,
                time_to_reproduction_victims, time_to_reproduction_predators):
            self.cell_type = cell_type
            self.time_to_death = time_to_death
            self.time_to_reproduction_victims = time_to_reproduction_victims
            self.time_to_reproduction_predators = time_to_reproduction_predators
            self.time_to_death = time_to_death
            self.change_cell_type(cell_type)
            self.used = False

        def reset_time_to_reproduction(self):
            self.time_to_reproduction = self.time_to_reproduction_victims\
                if self.cell_type == LifeModel.CellType.VICTIM else\
                self.time_to_reproduction_predators

        def change_cell_type(self, cell_type):
            self.cell_type = cell_type
            self.time_to_death = self.time_to_death
            self.reset_time_to_reproduction()

        def update_cell_state(self):
            self.used = False
            if self.cell_type in LifeModel.LIVING_CELLS_TYPES:
                if self.time_to_reproduction:
                    self.time_to_reproduction -= 1
            if self.cell_type == LifeModel.CellType.PREDATOR:
                if self.time_to_death:
                    self.time_to_death -= 1
                else:
                    self.change_cell_type(LifeModel.CellType.FREE_SPACE)

        def visualize_cell(self):
            if self.cell_type:
                return LifeModel.CHANGE_COLOR + LifeModel.COLORS[self.cell_type] +\
                    LifeModel.CELL_VISUALIZATION_SYMBOL[self.cell_type] + LifeModel.NORMAL_COLOR
            return ' '

    def __init__(
            self, row_number=10, column_number=10, probability_victim_cell=0.25,
            probability_predator_cell=0.25, probability_wall_cell=0.25,
            probability_victim_move=0.25, probability_predator_move=0.5, time_to_death=3,
            time_to_reproduction_victims=5, time_to_reproduction_predators=5,
            visualize=0, visualisation_pause=0, random_state=None):
        self.row_number = row_number
        self.column_number = column_number
        self.probability_victim_cell = probability_victim_cell
        self.probability_predator_cell = probability_predator_cell
        self.probability_wall_cell = probability_wall_cell
        self.probability_victim_move = probability_victim_move
        self.probability_predator_move = probability_predator_move
        self.time_to_death = time_to_death
        self.time_to_reproduction_victims = time_to_reproduction_victims
        self.time_to_reproduction_predators = time_to_reproduction_predators
        self.visualize = visualize
        self.visualisation_pause = visualisation_pause
        self.life_counter = LifeModel.DEFAULT_LIFE_COUNTER
        self.step = 0

        if random_state is not None:
            random.seed(random_state)

        special_random_cell_generator = gen_special_random_cell_generator(
            probability_victim_cell,
            probability_predator_cell,
            probability_wall_cell)

        self.field = [[
            LifeModel.Cell(
                special_random_cell_generator(),
                time_to_death,
                time_to_reproduction_victims,
                time_to_reproduction_predators)
            for column in range(column_number)]
            for row in range(row_number)]

    def __visualize(self, step):
        if self.visualize:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('step: ' + str(step + 1))
            print('victims: ' + str(self.life_counter[LifeModel.CellType.VICTIM]))
            print('predators: ' + str(self.life_counter[LifeModel.CellType.PREDATOR]))
            for row in range(self.row_number):
                print(''.join([x.visualize_cell() for x in self.field[row]]))
            time.sleep(self.visualisation_pause)

    def __check_inside_field(self, row, column):
        return 0 <= row < self.row_number and 0 <= column < self.column_number

    def __choose_random_direction(self, available_directions):
        direction = random.randint(LifeModel.LEFT_SUITABLE_INDEX, len(available_directions) - 1)
        row, column = available_directions[direction][0], available_directions[direction][1]
        available_directions.pop(direction)
        return row, column

    def __move_from(self, row, column, available_directions):
        to_row, to_column = self.__choose_random_direction(available_directions)
        self.field[to_row][to_column] = copy(self.field[row][column])
        self.field[row][column].change_cell_type(0)

    def __get_stats(self, row, column):
        stats = [[], []]
        for direction in LifeModel.DIRECTIONS:
            neighbor_x = row + direction[0]
            neighbor_y = column + direction[1]
            if self.__check_inside_field(neighbor_x, neighbor_y):
                current_cell_type = self.field[neighbor_x][neighbor_y].cell_type
                if current_cell_type in LifeModel.STATS_IMPORTANT_CELLS_TYPES:
                    stats[current_cell_type].append((neighbor_x, neighbor_y))
        return stats

    def __update_field_state(self):
        self.life_counter = copy(LifeModel.DEFAULT_LIFE_COUNTER)
        for row in range(self.row_number):
            for column in range(self.column_number):
                self.field[row][column].update_cell_state()
                current_cell_type = self.field[row][column].cell_type
                if current_cell_type in LifeModel.LIVING_CELLS_TYPES:
                    self.life_counter[current_cell_type] += 1

    def generate_next_turn(self):
        for row in range(self.row_number):
            for column in range(self.column_number):
                current_cell = self.field[row][column]
                if not current_cell.used:
                    current_cell.used = True
                    current_cell_type = current_cell.cell_type
                    if current_cell_type in LifeModel.LIVING_CELLS_TYPES:
                        stats = self.__get_stats(row, column)
                        '''stats about free spaces and victims nearly'''

                        if not current_cell.time_to_reproduction and\
                                len(stats[LifeModel.CellType.FREE_SPACE]):
                            '''random replication if free space exists'''
                            copy_to_x, copy_to_y = self.__choose_random_direction(
                                                        stats[LifeModel.CellType.FREE_SPACE])
                            self.field[copy_to_x][copy_to_y].change_cell_type(current_cell_type)
                            current_cell.reset_time_to_reproduction()

                        if current_cell_type == LifeModel.CellType.PREDATOR and\
                                len(stats[LifeModel.CellType.VICTIM]):
                            '''eat victim if can'''
                            current_cell.time_to_death = self.time_to_death
                            self.__move_from(row, column, stats[LifeModel.CellType.VICTIM])

                        if len(stats[LifeModel.CellType.FREE_SPACE]):
                            random_outcome = random.random()
                            if (current_cell_type == LifeModel.CellType.VICTIM and
                                random_outcome < self.probability_victim_move) or\
                                    (current_cell_type == LifeModel.CellType.PREDATOR and
                                        random_outcome < self.probability_predator_move):
                                '''move to near free cell randomly'''
                                self.__move_from(row, column, stats[LifeModel.CellType.FREE_SPACE])

        self.__update_field_state()
        self.__visualize(self.step)
        self.step += 1


# TOOLS
def gen_special_random_cell_generator(p1, p2, p3):
    if p1 + p2 + p3 > 1:
        raise Exception('Incorrect probabilities: p1 + p2 + p3 > 1\n')

    def f():
        x = random.random()
        if x < p1:
            return 1
        if x < p1 + p2:
            return 2
        if x < p1 + p2 + p3:
            return 3
        return 0
    return f


def str_to_numb(x):
    try:
        return int(x)
    except ValueError:
        return float(x)


def convert_args(kwargs):
    for key in kwargs:
        kwargs[key] = str_to_numb(kwargs[key])
    return kwargs


def main(kwargs):
    t = int(kwargs.pop('t', DEFAULT_GENERATION_TIME))
    life_model = LifeModel(**convert_args(kwargs))
    for step in range(t):
        life_model.generate_next_turn()


if __name__ == "__main__":
    kwargs = dict(x.split('=', 1) for x in sys.argv[1:])
    main(kwargs)
