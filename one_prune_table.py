from basic_functions import *
from collections import deque
from tqdm import trange

inf = 1000

def table_phase0():
    print('start')
    trans = [[-1 for _ in range(14)] for _ in range(495)]
    with open('trans_table/trans_ep_phase0.txt', mode='r') as f:
        for i in range(495):
            for j in range(14):
                trans[i][j] = int(f.readline())
    solved = ep2idx_phase0(list(range(12)))
    table = [inf for _ in range(495)]
    que = deque([[solved, 0]])
    while que:
        idx, cost = que.popleft()
        cost += 1
        for twist_idx, twist in enumerate(candidate[0]):
            n_idx = trans[idx][twist_idx]
            if table[n_idx] > cost:
                table[n_idx] = cost
                que.append([n_idx, cost])
    with open('prune_table/prune_phase0_ep.txt', mode='w') as f:
        for elem in table:
            f.write(str(elem) + '\n')

    trans = [[-1 for _ in range(14)] for _ in range(2187)]
    with open('trans_table/trans_co.txt', mode='r') as f:
        for i in range(2187):
            for j in range(14):
                trans[i][j] = int(f.readline())
    solved = co2idx([0 for _ in range(8)])
    table = [inf for _ in range(2187)]
    que = deque([[solved, 0]])
    while que:
        idx, cost = que.popleft()
        cost += 1
        for twist_idx, twist in enumerate(candidate[0]):
            n_idx = trans[idx][twist_idx]
            if table[n_idx] > cost:
                table[n_idx] = cost
                que.append([n_idx, cost])
    with open('prune_table/prune_phase0_co.txt', mode='w') as f:
        for elem in table:
            f.write(str(elem) + '\n')
    
    trans = [[-1 for _ in range(14)] for _ in range(2048)]
    with open('trans_table/trans_eo.txt', mode='r') as f:
        for i in range(2048):
            for j in range(14):
                trans[i][j] = int(f.readline())
    solved = eo2idx([0 for _ in range(12)])
    table = [inf for _ in range(2048)]
    que = deque([[solved, 0]])
    while que:
        idx, cost = que.popleft()
        cost += 1
        for twist_idx, twist in enumerate(candidate[0]):
            n_idx = trans[idx][twist_idx]
            if table[n_idx] > cost:
                table[n_idx] = cost
                que.append([n_idx, cost])
    with open('prune_table/prune_phase0_eo.txt', mode='w') as f:
        for elem in table:
            f.write(str(elem) + '\n')

    print('phase0 done')


def table_phase1():
    print('start')
    trans_ep = [[-1 for _ in range(10)] for _ in range(24)]
    with open('trans_table/trans_ep_phase1_2.txt', mode='r') as f:
        for i in range(24):
            for j in range(10):
                trans_ep[i][j] = int(f.readline())
    trans = [[-1 for _ in range(10)] for _ in range(40320)]
    with open('trans_table/trans_cp.txt', mode='r') as f:
        for i in range(40320):
            for j in range(10):
                trans[i][j] = int(f.readline())
    print('initialized')
    table = [[inf for _ in range(40320)] for _ in range(24)]
    solved1 = ep2idx_phase1_2(list(range(12)))
    solved2 = cp2idx(list(range(8)))
    table[solved1][solved2]  = 0
    que = deque([[solved1, solved2, 0]])
    while que:
        idx1, idx2, cost = que.popleft()
        cost += 1
        for twist_idx, twist in enumerate(candidate[1]):
            n_idx1 = trans_ep[idx1][twist_idx]
            n_idx2 = trans[idx2][twist_idx]
            if table[n_idx1][n_idx2] > cost:
                table[n_idx1][n_idx2] = cost
                que.append([n_idx1, n_idx2, cost])
    with open('prune_table/prune_phase1_cp_ep.txt', mode='w') as f:
        for arr in table:
            for elem in arr:
                f.write(str(elem) + '\n')
    trans = [[-1 for _ in range(10)] for _ in range(40320)]
    with open('trans_table/trans_ep_phase1_1.txt', mode='r') as f:
        for i in range(40320):
            trans.append([])
            for j in range(10):
                trans[i][j] = int(f.readline())
    table = [[inf for _ in range(40320)] for _ in range(24)]
    solved1 = ep2idx_phase1_2(list(range(12)))
    solved2 = ep2idx_phase1_1(list(range(12)))
    table[solved1][solved2]  = 0
    que = deque([[solved1, solved2, 0]])
    while que:
        idx1, idx2, cost = que.popleft()
        cost += 1
        for twist_idx, twist in enumerate(candidate[1]):
            n_idx1 = trans_ep[idx1][twist_idx]
            n_idx2 = trans[idx2][twist_idx]
            if table[n_idx1][n_idx2] > cost:
                table[n_idx1][n_idx2] = cost
                que.append([n_idx1, n_idx2, cost])
    with open('prune_table/prune_phase1_ep_ep.txt', mode='w') as f:
        for arr in table:
            for elem in arr:
                f.write(str(elem) + '\n')
    print('phase1 done')


table_phase0()
#table_phase1()