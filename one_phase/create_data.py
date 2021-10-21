from basic_functions import *
from tqdm import trange
from random import randint

n_data = 1000000
data = []
labels = []
len_solutions = [0 for _ in range(20)]

def face(mov):
    return mov // 3

def axis(mov):
    return mov // 6

data = []

for _ in trange(n_data):
    n_move = randint(10, 18)
    stickers = [i // 9 for i in range(54)]
    cp, co, ep, eo, dr = sticker2arr(stickers)
    l_mov = -1000
    for _ in range(n_move):
        mov = randint(0, 17)
        while face(mov) == face(l_mov) or (axis(mov) == axis(l_mov) and mov < l_mov):
            mov = randint(0, 17)
        stickers = move_sticker(stickers, mov)
        cp = move_cp(cp, mov)
        co = move_co(co, mov)
        ep = move_ep(ep, mov)
        eo = move_eo(eo, mov)
        dr = move_dir(dr, mov)
        l_mov = mov
    arr = [i for i in cp]
    arr.extend([i for i in co])
    arr.extend([i for i in ep])
    arr.extend([i for i in eo])
    arr.append(dr)
    arr.extend([i for i in stickers])
    data.append([arr, n_move])

with open('learn_data/data.txt', 'w') as f:
    for arr, n_mmove in data:
        f.write(' '.join([str(i) for i in arr]))
        f.write(' ')
        f.write(str(n_move))
        f.write('\n')
