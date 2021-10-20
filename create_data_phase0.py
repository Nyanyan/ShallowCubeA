from normal_solver import solver
from basic_functions import *
from tqdm import trange
from random import randint

n_data = 100000
data = []
labels = []
len_solutions = [0 for _ in range(20)]

def face(mov):
    return mov // 3

def axis(mov):
    return mov // 6

for _ in trange(n_data):
    n_move = randint(1, 20)
    cube = [i // 9 for i in range(54)]
    l_mov = -1000
    for _ in range(n_move):
        mov = randint(0, 17)
        while face(mov) == face(l_mov) or (axis(mov) == axis(l_mov) and mov < l_mov):
            mov = randint(0, 17)
        cube = move_sticker(cube, mov)
        l_mov = mov
    solution = solver(cube, 0)
    len_solutions[len(solution)] += 1
    with open('learn_data/phase0/data.txt', 'a') as f:
        f.write(''.join([str(i) for i in cube]))
        f.write(' ')
        f.write(str(len(solution)))
        f.write('\n')
