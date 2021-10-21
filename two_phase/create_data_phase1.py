from normal_solver import solver
from basic_functions import *
from tqdm import trange
from random import randint

move_candidate = [1, 4, 6, 7, 8, 9, 10, 11, 13, 16]

n_data = 100000
data = []
labels = []
len_solutions = [0 for _ in range(20)]

def face(mov):
    return mov // 3

def axis(mov):
    return mov // 6

for _ in trange(n_data):
    n_move = randint(1, 30)
    cube = [i // 9 for i in range(54)]
    l_mov = -1000
    for _ in range(n_move):
        mov = move_candidate[randint(0, 9)]
        while face(mov) == face(l_mov) or (axis(mov) == axis(l_mov) and mov < l_mov):
            mov = move_candidate[randint(0, 9)]
        cube = move_sticker(cube, mov)
        l_mov = mov
    solution = solver(cube, 1)
    len_solutions[len(solution)] += 1
    with open('learn_data/phase1/data9.txt', 'a') as f:
        f.write(''.join([str(i) for i in cube]))
        f.write(' ')
        f.write(str(len(solution)))
        f.write('\n')
