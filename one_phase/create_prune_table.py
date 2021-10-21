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

with open('param/trans_cp.txt', 'r') as f:
    for i in trange(n_cp):
        for j in range(n_moves):
            trans_cp[i][j] = int(f.readline())
with open('param/trans_co.txt', 'r') as f:
    for i in trange(n_co):
        for j in range(n_moves):
            trans_co[i][j] = int(f.readline())
with open('param/trans_ep.txt', 'r') as f:
    for i in trange(n_ep):
        for j in range(n_moves):
            trans_ep[i][j] = int(f.readline())
with open('param/trans_eo.txt', 'r') as f:
    for i in trange(n_eo):
        for j in range(n_moves):
            trans_eo[i][j] = int(f.readline())
with open('param/trans_dr.txt', 'r') as f:
    for i in trange(n_dr):
        for j in range(n_moves):
            trans_dr[i][j] = int(f.readline())

prune_cp_eo = np.full((n_cp, n_eo), 1000)
prune_co_eo_dr = np.full((n_co, n_eo, n_dr), 1000)
prune_ep = np.full(n_ep, 1000)
prune_cp_dr = np.full((n_cp, n_dr), 1000)

solved_cp = list(range(8))
solved_co = [0 for _ in range(8)]
solved_ep = list(range(12))
solved_eo = [0 for _ in range(12)]
solved_dr = 0

que = deque([[cp2idx(solved_cp), eo2idx(solved_eo), 0]])
strt = time()
former_time = time()
pushed = 0
n_elems = n_cp * n_eo
while que:
    if time() - former_time > 0.1:
        former_time = time()
        elapsed = time() - strt
        ratio = pushed / n_elems
        print('\r', round(100 * ratio, 3), 'persent completed;', 'elapsed', int(elapsed), 'sec;', 'ET', int(elapsed / ratio - elapsed), 'sec;', 'len que', len(que), end='                  ')
    cp_idx, eo_idx, num = que.popleft()
    if prune_cp_eo[cp_idx][eo_idx] > num:
        prune_cp_eo[cp_idx][eo_idx] = num
        pushed += 1
        for mov in range(18):
            n_cp_idx = trans_cp[cp_idx][mov]
            n_eo_idx = trans_eo[eo_idx][mov]
            if prune_cp_eo[n_cp_idx][n_eo_idx] > num + 1:
                que.append([n_cp_idx, n_eo_idx, num + 1])
print('')
print('writing')
with open('param/prune_cp_eo.txt', 'w') as f:
    for i in range(n_cp):
        for j in range(n_eo):
            f.write(str(prune_cp_eo[i][j]) + '\n')
print('done')

que = deque([[co2idx(solved_co), eo2idx(solved_eo), solved_dr, 0]])
strt = time()
former_time = time()
pushed = 0
n_elems = n_co * n_eo * n_dr
while que:
    if time() - former_time > 0.1:
        former_time = time()
        elapsed = time() - strt
        ratio = pushed / n_elems
        print('\r', round(100 * ratio, 3), 'persent completed;', 'elapsed', int(elapsed), 'sec;', 'ET', int(elapsed / ratio - elapsed), 'sec;', 'len que', len(que), end='                  ')
    co_idx, eo_idx, dr_idx, num = que.popleft()
    if prune_co_eo_dr[co_idx][eo_idx][dr_idx] > num:
        prune_co_eo_dr[co_idx][eo_idx][dr_idx] = num
        pushed += 1
        for mov in range(18):
            n_co_idx = trans_co[co_idx][mov]
            n_eo_idx = trans_eo[eo_idx][mov]
            n_dr_idx = trans_dr[dr_idx][mov]
            if prune_co_eo_dr[n_co_idx][n_eo_idx][n_dr_idx] > num + 1:
                que.append([n_co_idx, n_eo_idx, n_dr_idx, num + 1])
print('')
print('writing')
with open('param/prune_co_eo_dr.txt', 'w') as f:
    for i in range(n_co):
        for j in range(n_eo):
            for k in range(n_dr):
                f.write(str(prune_co_eo_dr[i][j][k]) + '\n')
print('done')

que = deque([[ep2idx(solved_ep), 0]])
strt = time()
former_time = time()
pushed = 0
n_elems = n_ep
while que:
    if time() - former_time > 0.1:
        former_time = time()
        elapsed = time() - strt
        ratio = pushed / n_elems
        print('\r', round(100 * ratio, 3), 'persent completed;', 'elapsed', int(elapsed), 'sec;', 'ET', int(elapsed / ratio - elapsed), 'sec;', 'len que', len(que), end='                  ')
    ep_idx, num = que.popleft()
    if prune_ep[ep_idx] > num:
        prune_ep[ep_idx] = num
        pushed += 1
        for mov in range(18):
            n_ep_idx = trans_ep[ep_idx][mov]
            if prune_ep[n_ep_idx] > num + 1:
                que.append([n_ep_idx, num + 1])
print('')
print('writing')
with open('param/prune_ep.txt', 'w') as f:
    for i in range(n_ep):
        f.write(str(prune_ep[i]) + '\n')
print('done')

que = deque([[cp2idx(solved_cp), solved_dr, 0]])
strt = time()
former_time = time()
pushed = 0
n_elems = n_cp * n_eo
while que:
    if time() - former_time > 0.1:
        former_time = time()
        elapsed = time() - strt
        ratio = pushed / n_elems
        print('\r', round(100 * ratio, 3), 'persent completed;', 'elapsed', int(elapsed), 'sec;', 'ET', int(elapsed / ratio - elapsed), 'sec;', 'len que', len(que), end='                  ')
    cp_idx, dr_idx, num = que.popleft()
    if prune_cp_dr[cp_idx][dr_idx] > num:
        prune_cp_dr[cp_idx][dr_idx] = num
        pushed += 1
        for mov in range(18):
            n_cp_idx = trans_cp[cp_idx][mov]
            n_dr_idx = trans_dr[dr_idx][mov]
            if prune_cp_dr[n_cp_idx][n_dr_idx] > num + 1:
                que.append([n_cp_idx, n_dr_idx, num + 1])
print('')
print('writing')
with open('param/prune_cp_dr.txt', 'w') as f:
    for i in range(n_cp):
        for j in range(n_dr):
            f.write(str(prune_cp_dr[i][j]) + '\n')
print('done')