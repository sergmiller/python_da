import os
import sys
import time
import copy
import random


class Life_model(object):
    '''
    0 - Free space
    1 - Victim
    2 - Predator
    3 - Wall
    '''

    dirs = ((0,1),(1,0),(-1,0),(0,-1))
    symbs = (' ', '.','@', '_')

    class Cell(object):
        def __init__(self, kind, t_hungry, t_rep_vict, t_rep_pred):
            self.kind = kind
            self.t_hungry = t_hungry
            self.t_rep_vict = t_rep_vict
            self.t_rep_pred = t_rep_pred
            self.t_to_dead = t_hungry
            self.change_kind(kind)

        def __backup_t_to_rep(self):
            self.t_to_rep = self.t_rep_vict if self.kind == 1 else self.t_rep_pred

        def change_kind(self, kind):
            self.kind = kind
            self.t_to_dead = self.t_hungry
            self.__backup_t_to_rep()

        def next(self):
            if self.kind in (1,2):
                if self.t_to_rep == -1:
                    self.__backup_t_to_rep()
                if self.t_to_rep:
                    self.t_to_rep -= 1

            if self.kind == 2:
                if self.t_to_dead > 0:
                    self.t_to_dead -= 1
                else:
                    self.change_kind(0)

        def symb(self):
            return Life_model.symbs[self.kind]



    def __init__(self, n = 10, m = 10, t = 10, p_vict_exist = 0.25,
    p_pred_exist = 0.25, p_wall_exist = 0.25, p_vict_move = 0.25, p_pred_move = 0.5,
    t_hungry = 3, t_rep_vict = 5, t_rep_pred = 5, visualize = 0):
        self.n = n
        self.m = m
        self.t = t
        self.p_vict_exist = p_vict_exist
        self.p_pred_exist = p_pred_exist
        self.p_wall_exist = p_wall_exist
        self.p_vict_move = p_vict_move
        self.p_pred_move = p_pred_move
        self.t_hungry = t_hungry
        self.t_rep_vict = t_rep_vict
        self.t_rep_pred = t_rep_pred
        self.visualize = visualize

        rnd_builder = gen_rnd_builder(p_vict_exist, p_pred_exist, p_wall_exist)

        self.field = [[
            Life_model.Cell(rnd_builder(), t_hungry, t_rep_vict, t_rep_pred)
        for j in range(m)]
        for i in range(n)]

    def __visualize(self, step):
        if self.visualize:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('step ' + str(step + 1))
            for i in range(self.n):
                print(' '.join([x.symb() for x in self.field[i]]))
            time.sleep(1)

    def __check(self,x,y):
        return -1 < x < self.n and -1 < y < self.m

    def run(self):
        self.__visualize(0)
        for step in range(self.t):
            for i in range(self.n):
                for j in range(self.m):
                    k = self.field[i][j].kind
                    if k in (1,2):
                        stats = [[],[]]  # stats for spaces and victims
                        for d in Life_model.dirs:
                            x = i + d[0]
                            y = j + d[1]
                            if self.__check(x,y):
                                kn = self.field[x][y].kind
                                if kn in (0,1):
                                    stats[kn].append((x,y))

                        if not self.field[i][j].t_to_rep and len(stats[0]):
                            _child = random.randint(0, len(stats[0]) - 1)
                            ch_x, ch_y = stats[0][_child][0], stats[0][_child][1]
                            self.field[ch_x][ch_y].change_kind(k)
                            self.field[i][j].t_to_rep = -1
                            stats[0].pop(_child)

                        if k == 1:
                            if random.random() < self.p_vict_move and len(stats[0]):
                                _move = random.randint(0, len(stats[0]) - 1)
                                mv_x, mv_y = stats[0][_move][0], stats[0][_move][1]
                                self.field[mv_x][mv_y] = copy.copy(self.field[i][j])
                                self.field[i][j].change_kind(0)
                        else:
                            if len(stats[1]):
                                _eat = random.randint(0, len(stats[1]) - 1)
                                eat_x, eat_y = stats[1][_eat][0], stats[1][_eat][1]
                                self.field[mv_x][mv_y] = copy.copy(self.field[i][j])
                                self.field[mv_x][mv_y].t_to_dead = self.t_hungry
                                self.field[i][j].change_kind(0)
                            else:
                                if random.random() < self.p_pred_move and len(stats[0]):
                                    _move = random.randint(0, len(stats[0]) - 1)
                                    mv_x, mv_y = stats[0][_move][0], stats[0][_move][1]
                                    self.field[mv_x][mv_y] = copy.copy(self.field[i][j])
                                    self.field[i][j].change_kind(0)
            for i in range(self.n):
                for j in range(self.m):
                    self.field[i][j].next()
            self.__visualize(step+1)

### TOOLS ###
def gen_rnd_builder(p1, p2, p3):
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
######

def main(kwargs):
    random.seed(1)
    life_model = Life_model(**convert_args(kwargs))
    life_model.run()

if __name__ == "__main__":
    kwargs = dict(x.split('=', 1) for x in sys.argv[1:])
    # try:
    main(kwargs)
    # except:
        # print('Something wrong')
