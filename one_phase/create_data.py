from basic_functions import *
from tqdm import trange
from random import randint
import numpy as np

n_data = 1000000
data = []
labels = []
len_solutions = [0 for _ in range(20)]

def face(mov):
    return mov // 3

def axis(mov):
    return mov // 6

data = []

prune_cp_eo = np.zeros((40320, 1024))
prune_co_eo_dr = np.zeros((2187, 1024, 24))
prune_ep = np.zeros(19958400)
prune_cp_dr = np.zeros((40320, 24))

with open('param/prune_cp_eo.txt', mode='r') as f:
    elems = f.read().splitlines()
    print(len(elems))
    idx = 0
    for i in trange(40320):
        for j in range(1024):
            prune_cp_eo[i][j] = float(elems[idx])
            idx += 1
#print(max([max(i) for i in prune_cp_eo]))
with open('param/prune_co_eo_dr.txt', mode='r') as f:
    elems = f.read().splitlines()
    print(len(elems))
    idx = 0
    for i in trange(2187):
        for j in range(1024):
            for k in range(24):
                prune_co_eo_dr[i][j][k] = float(elems[idx])
                idx += 1
#print(max([max([max(j) for j in i]) for i in prune_co_eo_dr]))
with open('param/prune_ep.txt', mode='r') as f:
    elems = f.read().splitlines()
    print(len(elems))
    idx = 0
    for i in trange(19958400):
        prune_ep[i] = float(elems[idx])
        idx += 1
#print(max(prune_ep))
with open('param/prune_cp_dr.txt', mode='r') as f:
    elems = f.read().splitlines()
    print(len(elems))
    idx = 0
    for i in trange(40320):
        for j in range(24):
            prune_cp_dr[i][j] = float(elems[idx])
            idx += 1
#print(max([max(i) for i in prune_cp_dr]))

for _ in trange(n_data):
    n_move = randint(5, 18)
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
    cp_idx = cp2idx(cp)
    co_idx = co2idx(co)
    ep_idx = ep2idx(ep)
    eo_idx = eo2idx(eo)
    dr_idx = dr
    arr.append(prune_cp_eo[cp_idx][eo_idx])
    arr.append(prune_co_eo_dr[co_idx][eo_idx][dr_idx])
    arr.append(prune_ep[ep_idx])
    arr.append(prune_cp_dr[cp_idx][dr_idx])
    if max(prune_cp_eo[cp_idx][eo_idx], prune_co_eo_dr[co_idx][eo_idx][dr_idx], prune_ep[ep_idx], prune_cp_dr[cp_idx][dr_idx]) > n_move:
        print('what??')
    data.append([arr, n_move])

with open('learn_data/data.txt', 'a') as f:
    for arr, n_move in data:
        f.write(' '.join([str(i) for i in arr]))
        f.write(' ')
        f.write(str(n_move))
        f.write('\n')
