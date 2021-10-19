from basic_functions import *
import numpy as np
from tensorflow.keras.models import Model, load_model
from time import time
from heapq import heappush, heappop

model_phase0 = load_model('param/phase0.h5')
model_phase1 = load_model('param/phase1.h5')

c_predict = 1.0

edges = [1, 3, 5, 7, 10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34, 37, 39, 41, 43, 46, 48, 50, 52]
phase1_move_candidate = [1, 4, 6, 7, 8, 9, 10, 11, 13, 16]

def one_hot_phase0(arr):
    res = []
    for i in range(54):
        if arr[i] == 0 or arr[i] == 5:
            res.append(1.0)
        else:
            res.append(0.0)
    for i in edges:
        if arr[i] == 1 or arr[i] == 3:
            res.append(1.0)
        else:
            res.append(0.0)
    return res

def one_hot_phase1(arr):
    res = []
    for color in [0, 5]:
        for i in range(0, 9):
            if arr[i] == color:
                res.append(1.0)
            else:
                res.append(0.0)
        for i in range(45, 54):
            if arr[i] == color:
                res.append(1.0)
            else:
                res.append(0.0)
    for color in [1, 2, 3, 4]:
        for i in range(9, 45):
            if arr[i] == color:
                res.append(1.0)
            else:
                res.append(0.0)
    return res

def face(mov):
    return mov // 3

def axis(mov):
    return mov // 6

solved_phase0 = one_hot_phase0([i // 9 for i in range(54)])
solved_phase1 = one_hot_phase1([i // 9 for i in range(54)])

print(solved_phase0)
print(solved_phase1)

def distance_phase0(arrs):
    res = [i[0] for i in model_phase0.predict(np.array(arrs))]
    for i, arr in enumerate(arrs):
        if arr == solved_phase0:
            res[i] = 0.0
    return res

def distance_phase1(arrs):
    res = [i[0] for i in model_phase1.predict(np.array(arrs))]
    for i, arr in enumerate(arrs):
        if arr == solved_phase1:
            res[i] = 0.0
    return res


def distance(cp, co, ep, eo, dr):
    mx = max(prune_cp[cp], prune_co_eo[co * 1024 * 24 + eo * 24 + dr], prune_ep[ep])
    #mn = min(prune_cp[cp], prune_co_eo[co * 1024 * 24 + eo * 24 + dr], prune_ep[ep])
    return mx

def transform(cp, co, ep, eo, dr, twist):
    return trans_cp[cp][twist], trans_co[co][twist], trans_ep[ep][twist], trans_eo[eo][twist], move_dir(dr, twist)

def phase0(stickers):
    res = []
    que = []
    print('raw', stickers)
    print('input', one_hot_phase0(stickers))
    dis = distance_phase0([one_hot_phase0(stickers)])[0]
    if dis == 0:
        return[]
    print(dis)
    heappush(que, [0 + c_predict * dis, stickers, []])
    while que:
        elems = []
        predict_data = []
        for _ in range(200):
            if que:
                dis, st, sol = heappop(que)
                for mov in range(18):
                    if sol and face(sol[-1]) == face(mov):
                        continue
                    if sol and axis(sol[-1]) == axis(mov) and mov < sol[-1]:
                        continue
                    nst = move_sticker(st, mov)
                    nsol = [i for i in sol]
                    nsol.append(mov)
                    elems.append([nst, nsol])
                    predict_data.append(one_hot_phase0(nst))
        predictions = distance_phase0(predict_data)
        for i, nf in enumerate(predictions):
            if nf == 0:
                return [elems[i][1]]
            ndis = len(elems[i][1]) + c_predict * nf
            heappush(que, [ndis, elems[i][0], elems[i][1]])

def phase1(stickers):
    res = []
    que = []
    print('raw', stickers)
    print('input', one_hot_phase1(stickers))
    dis = distance_phase1([one_hot_phase1(stickers)])[0]
    if dis == 0:
        return []
    print(dis)
    heappush(que, [0 + c_predict * dis, stickers, []])
    while que:
        #print(len(que))
        elems = []
        predict_data = []
        for _ in range(200):
            if que:
                dis, st, sol = heappop(que)
                for mov in phase1_move_candidate:
                    if sol and face(sol[-1]) == face(mov):
                        continue
                    if sol and axis(sol[-1]) == axis(mov) and mov < sol[-1]:
                        continue
                    nst = move_sticker(st, mov)
                    nsol = [i for i in sol]
                    nsol.append(mov)
                    elems.append([nst, nsol])
                    predict_data.append(one_hot_phase1(nst))
        predictions = distance_phase1(predict_data)
        for i, nf in enumerate(predictions):
            if nf == 0:
                return [elems[i][1]]
            ndis = len(elems[i][1]) + c_predict * nf
            heappush(que, [ndis, elems[i][0], elems[i][1]])

def solver(stickers):
    global phase_solution
    res = []
    l = 30
    phase_solution = []
    solutions = phase0(stickers)
    for solution in solutions:
        print(*[twists_notation[i] for i in solution])
        for twist in solution:
            stickers = move_sticker(stickers, twist)
        res.extend(solution)
    print(stickers)
    solutions = phase1(stickers)
    for solution in solutions:
        print(*[twists_notation[i] for i in solution])
        for twist in solution:
            stickers = move_sticker(stickers, twist)
        res.extend(solution)
    print(stickers)
    return res
'''
trans_cp = []
with open('trans/trans_cp.csv', mode='r') as f:
    for idx in range(40320):
        trans_cp.append([int(i) for i in f.readline().replace('\n', '').split(',')])
trans_co = []
with open('trans/trans_co.csv', mode='r') as f:
    for idx in range(2187):
        trans_co.append([int(i) for i in f.readline().replace('\n', '').split(',')])
#trans_ep = [[0 for _ in range(18)]]
trans_ep = np.zeros((19958400, 18), dtype=int)
with open('trans/trans_ep.csv', mode='r') as f:
    for idx in range(19958400):
        if idx % 200000 == 0:
            print('ep', idx / 19958400 * 100)
        trans_ep[idx] = [int(i) for i in f.readline().replace('\n', '').split(',')]
trans_eo = []
with open('trans/trans_eo.csv', mode='r') as f:
    for idx in range(1024):
        trans_eo.append([int(i) for i in f.readline().replace('\n', '').split(',')])

prune_cp = []
with open('prune/prune_cp.csv', mode='r') as f:
    prune_cp = [int(i) for i in f.readline().replace('\n', '').split(',')]
prune_co_eo = []
with open('prune/prune_co_eo.csv', mode='r') as f:
    prune_co_eo = [int(i) for i in f.readline().replace('\n', '').split(',')]
#prune_ep = [0]
prune_ep = []
with open('prune/prune_ep.csv', mode='r') as f:
    prune_ep = [int(i) for i in f.readline().replace('\n', '').split(',')]
'''
print('initialized')

phase_solution = []

w, g, r, b, o, y = range(6)
'''
#scramble R Dw R' Fw F D L' Dw2 F2 R2
state = [
    g, w, w, g, b, r, b, y, g, 
    w, r, o, b, r, b, o, o, b, 
    y, w, r, r, y, g, y, w, g, 
    b, b, y, y, o, o, o, o, r, 
    r, r, o, b, w, y, g, g, b, 
    y, y, r, w, g, o, w, g, w
]
strt = time()
solver(state)
elapsed = time() - strt
print('time', elapsed, 'sec')

# scramble: L B2 L2 D2 B L2 F' U2 R2 U2 F2 R2 U' F L2 B' D U2 R U2 x y'
state = [
    y, w, g, g, g, y, o, b, g, 
    b, r, w, b, o, g, o, o, o, 
    o, o, r, w, y, r, y, w, b, 
    w, b, r, y, r, b, r, o, y, 
    g, y, w, y, w, o, r, r, y, 
    g, w, b, g, b, r, b, g, w
]
'''
# scramble: L B2 L2 D2 B L2 F' U2 R2 U2 F2 R2 U' F L2 B' D U2 R U2
state = [
    y, r, r, o, w, y, w, y, g,
    o, g, y, b, g, w, g, y, g,
    r, b, y, b, r, o, w, y, r,
    b, g, g, g, b, w, w, r, b,
    o, b, b, o, o, r, o, g, w,
    o, o, r, w, y, r, y, w, b
]

state = [i // 9 for i in range(54)]

for notation in "L B2 L2 D2 B L2 F' U2 R2 U2 F2 R2 U' F L2 B' D U2 R U2".split():
    twist = twists_notation.index(notation)
    state = move_sticker(state, twist)
    #print(notation, twist, state)
print(state)

strt = time()
solution = solver(state)
print(*[twists_notation[i] for i in solution])
elapsed = time() - strt
print('time', elapsed, 'sec')