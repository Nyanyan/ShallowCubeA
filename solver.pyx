# distutils: language=c++
# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True

import cython
from libcpp.vector cimport vector
from libcpp cimport bool

from numpy import tanh
from time import time
from basic_functions import *

cdef idxes_init(int phase, cp, co, ep, eo):
    cdef int[3] res
    if phase == 0:
        res[0] = co2idx(co)
        res[1] = eo2idx(eo)
        res[2] = ep2idx_phase0(ep)
    else:
        res[0] = cp2idx(cp)
        res[1] = ep2idx_phase1_1(ep)
        res[2] = ep2idx_phase1_2(ep)
    return res

cdef int trans1(int phase, int idx1, int twist):
    if phase == 0:
        return trans_co[idx1][twist]
    else:
        return trans_cp[idx1][twist]

cdef int trans2(int phase, int idx2, int twist):
    if phase == 0:
        return trans_eo[idx2][twist]
    else:
        return trans_ep_phase1_1[idx2][twist]

cdef int trans3(int phase, int idx3, int twist):
    if phase == 0:
        return trans_ep_phase0[idx3][twist]
    else:
        return trans_ep_phase1_2[idx3][twist]
'''
cdef int distance(int phase, int idx1, int idx2, int idx3):
    if phase == 0:
        return max(prune_phase0_co_ep[idx3][idx1], prune_phase0_eo_ep[idx3][idx2])
    else:
        return max(prune_phase1_cp_ep[idx3][idx1], prune_phase1_ep_ep[idx3][idx2])
'''
cdef double[2] input_layer
cdef double[8] hidden1
cdef double[4] hidden2

cdef double leaky_relu(double x):
    return max(0.01 * x, x)

cdef int distance(int phase, int idx1, int idx2, int idx3):
    global input_layer, hidden1, hidden2
    cdef int i, j
    cdef double res, min_val
    if phase == 0:
        input_layer[0] = prune_phase0_co_ep[idx3][idx1]
        input_layer[1] = prune_phase0_eo_ep[idx3][idx2]
    else:
        input_layer[0] = prune_phase1_cp_ep[idx3][idx1]
        input_layer[1] = prune_phase1_ep_ep[idx3][idx2]
    min_val = max(input_layer[0], input_layer[1])
    if input_layer[0] == input_layer[1] or min_val < 10.0:
        return int(min_val)
    for i in range(2):
        input_layer[i] -= mean[phase][i]
        input_layer[i] /= std[phase][i]
    for i in range(8):
        hidden1[i] = bias1[phase][i]
        for j in range(2):
            hidden1[i] += dense1[phase][j][i] * input_layer[j]
        hidden1[i] = leaky_relu(hidden1[i])
    for i in range(4):
        hidden2[i] = bias2[phase][i]
        for j in range(8):
            hidden2[i] += dense2[phase][j][i] * hidden1[j]
        hidden2[i] = leaky_relu(hidden2[i])
    res = bias3[phase]
    for i in range(4):
        res += dense3[phase][i] * hidden2[i]
    res = tanh(res) * max_len[phase]
    return int(max(min_val, res))

cdef vector[vector[int]] phase_search(int phase, int idx1, int idx2, int idx3, int depth, int dis, int len_phase_solution):
    global phase_solution
    cdef vector[vector[int]] res
    if depth == 0:
        if dis == 0:
            res.push_back(phase_solution)
        return res
    elif dis == 0:
        return res
    cdef int l1_twist, l2_twist, twist_idx, twist, n_idx1, n_idx2, n_idx3, n_dis
    cdef vector[vector[int]] sol
    depth -= 1
    l1_twist = phase_solution[len_phase_solution - 1] if len_phase_solution >= 1 else -10
    l2_twist = phase_solution[len_phase_solution - 2] if len_phase_solution >= 2 else -10
    for twist_idx, twist in enumerate(candidate[phase]):
        if time() - strt_search > 0.2:
            return res
        if twist // 3 == l1_twist // 3: # don't turn same face twice
            continue
        if twist // 3 == l2_twist // 3 and twist // 6 == l1_twist // 6: # don't turn opposite face 3 times
            continue
        if twist // 6 == l1_twist // 6 and twist < l1_twist: # for example, permit R L but not L R
            continue
        n_idx1 = trans1(phase, idx1, twist_idx)
        n_idx2 = trans2(phase, idx2, twist_idx)
        n_idx3 = trans3(phase, idx3, twist_idx)
        n_dis = distance(phase, n_idx1, n_idx2, n_idx3)
        if n_dis > depth:
            continue
        phase_solution.push_back(twist)
        sol = phase_search(phase, n_idx1, n_idx2, n_idx3, depth, n_dis, len_phase_solution + 1)
        sol_size = sol.size()
        #if phase == 1 and sol_size: # only one solution needed
        #    return sol
        for idx in range(sol_size):
            res.push_back(sol[idx])
        if phase == 0 and res.size() > 50:
            return res
        phase_solution.pop_back()
    return res

cdef vector[int] robotize(vector[int] arr, int idx, int direction, bool rotated):
    cdef int twist_ax, twist_face, twist_direction, twist_arm, i, sol_size, res_size
    cdef vector[int] res
    res_size = 1000
    if idx == len(arr):
        return res
    twist_ax = arr[idx] // 6
    twist_face = arr[idx] // 3
    twist_direction = arr[idx] % 3
    if can_rotate[direction][twist_ax]:
        sol = robotize(arr, idx + 1, direction, False)
        sol_size = sol.size()
        if sol_size and sol[0] == -1:
            res.push_back(-1)
            return res
        res.push_back(actual_face[direction].index(twist_face) * 3 + twist_direction)
        for i in range(sol_size):
            res.push_back(sol[i])
    else:
        if rotated:
            res.push_back(-1)
            return res
        for rotation in range(12, 14):
            n_direction = move_dir(direction, rotation)
            twist_arm = actual_face[n_direction].index(twist_face) * 3 + twist_direction
            sol = robotize(arr, idx + 1, n_direction, True)
            sol_size = sol.size()
            if sol_size and sol[0] == -1:
                continue
            if res_size > sol_size + 2:
                res = []
                res.push_back(rotation)
                res.push_back(twist_arm)
                for i in range(sol_size):
                    res.push_back(sol[i])
    return res


def solver(stickers):
    global phase_solution, strt_search
    min_phase0_depth = 0
    res = []
    l = 27
    max_phase0_depth = 15
    break_flag = False
    
    s_cp, s_co, s_ep, s_eo = sticker2arr(stickers)
    if s_cp.count(-1) == 1 and len((set(range(8)) - set(s_cp))) == 1:
        s_cp[s_cp.index(-1)] = list(set(range(8)) - set(s_cp))[0]
    if s_ep.count(-1) == 1 and len((set(range(12)) - set(s_ep))) == 1:
        s_ep[s_ep.index(-1)] = list(set(range(12)) - set(s_ep))[0]
    if s_co.count(-1) == 1:
        s_co[s_co.index(-1)] = (3 - (sum(s_co) + 1) % 3) % 3
    if s_eo.count(-1) == 1:
        s_eo[s_eo.index(-1)] = (2 - (sum(s_eo) + 1) % 2) % 2
    print(s_cp, s_ep)
    if -1 in s_cp or -1 in s_co or -1 in s_ep or -1 in s_eo:
        raise Exception('Error')
    '''
    s_cp = list(range(8))
    s_co = [0 for _ in range(8)]
    s_ep = list(range(12))
    s_eo = [0 for _ in range(12)]
    from random import randint
    for _ in range(40):
        twist = randint(0, 17)
        s_cp = move_cp(s_cp, twist)
        s_co = move_co(s_co, twist)
        s_ep = move_ep(s_ep, twist)
        s_eo = move_eo(s_eo, twist)
    '''
    while True:
        search_lst = [[s_cp, s_co, s_ep, s_eo, []]]
        n_search_lst = []
        for phase in range(2):
            for cp, co, ep, eo, last_solution in search_lst:
                idx1, idx2, idx3 = idxes_init(phase, cp, co, ep, eo)
                dis = distance(phase, idx1, idx2, idx3)
                if dis == 0:
                    n_search_lst.append([cp, co, ep, eo, last_solution])
                    continue
                phase_solution = []
                strt_depth = dis if phase == 1 else max(dis, min_phase0_depth)
                cnt = 0
                for depth in range(strt_depth, l - len(last_solution)):
                    strt_search = time()
                    sol = phase_search(phase, idx1, idx2, idx3, depth, dis, 0)
                    if sol.size():
                        cnt += 1
                        for solution in sol:
                            n_cp = [i for i in cp]
                            n_co = [i for i in co]
                            n_ep = [i for i in ep]
                            n_eo = [i for i in eo]
                            n_solution = [i for i in last_solution]
                            for twist in solution:
                                n_cp = move_cp(n_cp, twist)
                                n_co = move_co(n_co, twist)
                                n_ep = move_ep(n_ep, twist)
                                n_eo = move_eo(n_eo, twist)
                                n_solution.append(twist)
                            n_search_lst.append([n_cp, n_co, n_ep, n_eo, n_solution])
                            if phase == 1:
                                l = min(l, len(n_solution) + 1)
                        if phase == 0:
                            min_phase0_depth = depth + 1
                        if phase == 0 or (phase == 1 and cnt >= 2):
                            break
            search_lst = []
            for i, arrs in enumerate(n_search_lst):
                search_lst.append([])
                for j, arr in enumerate(arrs):
                    search_lst[i].append([])
                    for val in arr:
                        search_lst[i][j].append(val)
            n_search_lst = []
            print('max len', l, 'phase', phase, 'depth', depth, 'found solutions', len(search_lst))
            if phase == 0 and len(search_lst) == 0:
                break_flag = True
                break
        if search_lst:
            len_res = 1000
            res = []
            for _, _, _, _, res_candidate in search_lst:
                robotized_res_can = robotize(res_candidate, 0, 0, False)
                if robotized_res_can.size() < len_res:
                    res = list(robotized_res_can)
                    len_res = robotized_res_can.size()
        elif min_phase0_depth >= max_phase0_depth or break_flag:
            break
        #else:
        #min_phase0_depth += 1
    print('solution lengh', len(res), 'length for human', l - 1)
    return res

cdef vector[int] phase_solution = []
cdef double strt_search

cdef int[2187][14] trans_co
with open('trans_table/trans_co.txt', mode='r') as f:
    for idx1 in range(2187):
        for idx2 in range(14):
            trans_co[idx1][idx2] = int(f.readline())
cdef int[40320][10] trans_cp
with open('trans_table/trans_cp.txt', mode='r') as f:
    for idx1 in range(40320):
        for idx2 in range(10):
            trans_cp[idx1][idx2] = int(f.readline())
cdef int[2048][14] trans_eo
with open('trans_table/trans_eo.txt', mode='r') as f:
    for idx1 in range(2048):
        for idx2 in range(14):
            trans_eo[idx1][idx2] = int(f.readline())
cdef int[495][14] trans_ep_phase0
with open('trans_table/trans_ep_phase0.txt', mode='r') as f:
    for idx1 in range(495):
        for idx2 in range(14):
            trans_ep_phase0[idx1][idx2] = int(f.readline())
cdef int[40320][10] trans_ep_phase1_1
with open('trans_table/trans_ep_phase1_1.txt', mode='r') as f:
    for idx1 in range(40320):
        for idx2 in range(10):
            trans_ep_phase1_1[idx1][idx2] = int(f.readline())
cdef int[24][10] trans_ep_phase1_2
with open('trans_table/trans_ep_phase1_2.txt', mode='r') as f:
    for idx1 in range(24):
        for idx2 in range(10):
            trans_ep_phase1_2[idx1][idx2] = int(f.readline())

cdef int[495][2187] prune_phase0_co_ep
with open('prune_table/prune_phase0_co_ep.txt', mode='r') as f:
    for idx1 in range(495):
        for idx2 in range(2187):
            prune_phase0_co_ep[idx1][idx2] = int(f.readline())
cdef int[495][2048] prune_phase0_eo_ep
with open('prune_table/prune_phase0_eo_ep.txt', mode='r') as f:
    for idx1 in range(495):
        for idx2 in range(2048):
            prune_phase0_eo_ep[idx1][idx2] = int(f.readline())
cdef int[24][40320] prune_phase1_cp_ep
with open('prune_table/prune_phase1_cp_ep.txt', mode='r') as f:
    for idx1 in range(24):
        for idx2 in range(40320):
            prune_phase1_cp_ep[idx1][idx2] = int(f.readline())
cdef int[24][40320] prune_phase1_ep_ep
with open('prune_table/prune_phase1_ep_ep.txt', mode='r') as f:
    for idx1 in range(24):
        for idx2 in range(40320):
            prune_phase1_ep_ep[idx1][idx2] = int(f.readline())

cdef double[2][2][8] dense1
cdef double[2][8] bias1
cdef double[2][8][4] dense2
cdef double[2][4] bias2
cdef double[2][4] dense3
cdef double[2] bias3
cdef double[2][2] mean, std
cdef int[2] max_len = [12, 18]
for phase in range(2):
    with open('param/phase' + str(phase) + '.txt', mode='r') as f:
        for idx1 in range(2):
            for idx2 in range(8):
                dense1[phase][idx1][idx2] = float(f.readline())
        for idx1 in range(8):
            bias1[phase][idx1] = float(f.readline())
        for idx1 in range(8):
            for idx2 in range(4):
                dense2[phase][idx1][idx2] = float(f.readline())
        for idx1 in range(4):
            bias2[phase][idx1] = float(f.readline())
        for idx1 in range(4):
            dense3[phase][idx1] = float(f.readline())
        bias3[phase] = float(f.readline())
    with open('param/phase' + str(phase) + '_mean.txt', mode='r') as f:
        for idx1 in range(2):
            mean[phase][idx1] = float(f.readline())
    with open('param/phase' + str(phase) + '_std.txt', mode='r') as f:
        for idx1 in range(2):
            std[phase][idx1] = float(f.readline())

print('solver initialized')


''' TEST '''
def main():
    '''
    num = 100
    tim = []
    lns = []
    for i in range(num):
        strt = time()
        #ln = len(solver())
        tmp = solver()
        ln = len(tmp)
        end = time()
        tim.append(end - strt)
        lns.append(ln)
        print(tmp)
        print(i)
    print('avg tim', sum(tim) / num)
    print('max tim', max(tim))
    print('min tim', min(tim))
    print('avg len', sum(lns) / num)
    print('max len', max(lns))
    print('min len', min(lns))
    '''
    w, g, r, b, o, y = range(6)
    arr = [y, b, r, y, w, w, w, r, y, r, g, g, y, g, r, y, o, o, o, b, y, y, r, w, w, b, b, b, o, r, g, b, r, r, b, o, g, g, g, w, o, o, b, g, o, b, w, g, o, y, y, w, r, w] # R F2 R2 B2 L F2 R2 B2 R D2 L D' F U' B' R2 D2 F' U2 F'
    strt = time()
    tmp = solver(arr)
    print(len(tmp), tmp)
    print(time() - strt)
