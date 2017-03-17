import os
import sys
import time
import copy
import random

class Life_model(object):
    '''
    ' ' - Free space(0)
    . - Victim(1)
    ^ - Predator(2)
    # - Wall(3)
    '''

    ###JUST FOR VISUAL STYLE###
    COLORS = ('', '0;32;40m', '0;31;40m','0;30;43m') #red, green, white
    DIRS = ((0,1),(1,0),(-1,0),(0,-1))
    CHANGE_COLOR = '\x1b['
    NORMAL_COLOR = CHANGE_COLOR + '0m'
    SYMBS = (' ', '@', '#', ' ')
    ######

    class Cell(object):
        def __init__(self, kind, t_hungry, t_rep_vict, t_rep_pred):
            self.kind = kind
            self.t_hungry = t_hungry
            self.t_rep_vict = t_rep_vict
            self.t_rep_pred = t_rep_pred
            self.t_to_dead = t_hungry
            self.change_kind(kind)
            self.used = 0

        def backup_t_to_rep(self):
            self.t_to_rep = self.t_rep_vict if self.kind == 1 else self.t_rep_pred

        def change_kind(self, kind):
            self.kind = kind
            self.t_to_dead = self.t_hungry
            self.backup_t_to_rep()

        def next(self):
            self.used = 0
            if self.kind in (1,2):
                if self.t_to_rep:
                    self.t_to_rep -= 1
            if self.kind == 2:
                if self.t_to_dead > 0:
                    self.t_to_dead -= 1
                else:
                    self.change_kind(0)

        def symb(self):
            if self.kind:
                return Life_model.CHANGE_COLOR + \
                Life_model.COLORS[self.kind] + \
                Life_model.SYMBS[self.kind] + \
                Life_model.NORMAL_COLOR
            return ' '

    def __init__(self, n = 10, m = 10, p_vict_exist = 0.25,
    p_pred_exist = 0.25, p_wall_exist = 0.25, p_vict_move = 0.25, p_pred_move = 0.5,
    t_hungry = 3, t_rep_vict = 5, t_rep_pred = 5, visualize = 0, vis_sleep_time = 0):
        self.n = n
        self.m = m
        self.p_vict_exist = p_vict_exist
        self.p_pred_exist = p_pred_exist
        self.p_wall_exist = p_wall_exist
        self.p_vict_move = p_vict_move
        self.p_pred_move = p_pred_move
        self.t_hungry = t_hungry
        self.t_rep_vict = t_rep_vict
        self.t_rep_pred = t_rep_pred
        self.visualize = visualize
        self.vis_sleep_time = vis_sleep_time
        self.step = 0
        self.alive = [0,0]

        rnd_builder = gen_rnd_builder(p_vict_exist, p_pred_exist, p_wall_exist)

        self.field = [[
            Life_model.Cell(rnd_builder(), t_hungry, t_rep_vict, t_rep_pred)
        for j in range(m)]
        for i in range(n)]

    def __visualize(self, step):
        if self.visualize:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('step: ' + str(step + 1))
            print('victims: ' + str(self.alive[0]))
            print('predators: ' + str(self.alive[1]))
            for i in range(self.n):
                print(''.join([x.symb() for x in self.field[i]]))
            time.sleep(self.vis_sleep_time)

    def __check(self,x,y):
        return -1 < x < self.n and -1 < y < self.m

    def __rnd_dir(self, px, py, stats):
        dir = random.randint(0, len(stats) - 1)
        x, y = stats[dir][0], stats[dir][1]
        stats.pop(dir)
        return x, y

    def __move(self, px, py, stats):
        mv_x, mv_y = self.__rnd_dir(px, py, stats)
        self.field[mv_x][mv_y] = copy.copy(self.field[px][py])
        self.field[px][py].change_kind(0)

    def __get_stats(self, px, py):
        stats = [[],[]]
        for d in Life_model.DIRS:
            x = px + d[0]
            y = py + d[1]
            if self.__check(x,y):
                k = self.field[x][y].kind
                if k <= 1:
                    stats[k].append((x,y))
        return stats

    def next(self):
            for i in range(self.n):
                for j in range(self.m):
                    if not self.field[i][j].used:
                        self.field[i][j].used = 1
                        k = self.field[i][j].kind
                        if k in (1,2):
                            stats = self.__get_stats(i,j)  # stats about free spaces and victims nearly

                            if not self.field[i][j].t_to_rep and len(stats[0]):  #random replication if free space exists
                                ch_x, ch_y = self.__rnd_dir(i,j,stats[0])
                                self.field[ch_x][ch_y].change_kind(k)
                                self.field[i][j].backup_t_to_rep()

                            if k == 2 and len(stats[1]):  # eat victim if can
                                self.field[i][j].t_to_dead = self.t_hungry
                                self.__move(i,j,stats[1])

                            if random.random() < self.p_vict_move and len(stats[0]):  # move to near free cell randomly
                                self.__move(i,j,stats[0])
            self.alive = [0,0]
            for i in range(self.n):
                for j in range(self.m):
                    self.field[i][j].next()
                    k = self.field[i][j].kind
                    if k in (1,2):
                        self.alive[k - 1] += 1

            self.__visualize(self.step)
            self.step += 1

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
    t = int(kwargs.pop('t',100))
    life_model = Life_model(**convert_args(kwargs))
    for step in range(t):
        life_model.next()

if __name__ == "__main__":
    kwargs = dict(x.split('=', 1) for x in sys.argv[1:])
    main(kwargs)
