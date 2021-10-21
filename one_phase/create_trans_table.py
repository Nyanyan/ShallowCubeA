import numpy as np
from collections import deque
from basic_functions import *
from time import time
from tqdm import trange


n_moves = 18
n_cp = 40320
n_co = 2187
n_ep = 19958400
n_eo = 1024
n_dr = 24

trans_cp = np.full((n_cp, n_moves), -1)
trans_co = np.full((n_co, n_moves), -1)
trans_ep = np.full((n_ep, n_moves), -1)
trans_eo = np.full((n_eo, n_moves), -1)
trans_dr = np.full((n_dr, n_moves), -1)



for idx in trange(n_cp):
    arr = idx2cp(idx)
    for mov in range(n_moves):
        n_idx = cp2idx(move_cp(arr, mov))
        trans_cp[idx][mov] = n_idx
with open('param/trans_cp.txt', 'w') as f:
    for i in range(n_cp):
        for j in range(n_moves):
            f.write(str(trans_cp[i][j]) + '\n')


for idx in trange(n_co):
    arr = idx2co(idx)
    for mov in range(n_moves):
        n_idx = co2idx(move_co(arr, mov))
        trans_co[idx][mov] = n_idx
with open('param/trans_co.txt', 'w') as f:
    for i in range(n_co):
        for j in range(n_moves):
            f.write(str(trans_co[i][j]) + '\n')


for idx in trange(n_ep):
    arr = idx2ep(idx)
    for mov in range(n_moves):
        n_idx = ep2idx(move_ep(arr, mov))
        trans_ep[idx][mov] = n_idx
with open('param/trans_ep.txt', 'w') as f:
    for i in range(n_ep):
        for j in range(n_moves):
            f.write(str(trans_ep[i][j]) + '\n')


for idx in trange(n_eo):
    arr = idx2eo(idx)
    for mov in range(n_moves):
        n_idx = eo2idx(move_eo(arr, mov))
        trans_eo[idx][mov] = n_idx
with open('param/trans_eo.txt', 'w') as f:
    for i in range(n_eo):
        for j in range(n_moves):
            f.write(str(trans_eo[i][j]) + '\n')


for idx in trange(n_dr):
    arr = idx
    for mov in range(n_moves):
        n_idx = move_dir(arr, mov)
        trans_dr[idx][mov] = n_idx
with open('param/trans_dr.txt', 'w') as f:
    for i in range(n_dr):
        for j in range(n_moves):
            f.write(str(trans_dr[i][j]) + '\n')
