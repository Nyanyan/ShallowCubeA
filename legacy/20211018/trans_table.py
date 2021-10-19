from basic_functions import *
from tqdm import trange

def cp_table():
    table = [[-1 for _ in range(10)] for _ in range(40320)]
    for idx in trange(40320):
        cp = idx2cp(idx)
        for twist_idx, twist in enumerate(candidate[1]):
            n_cp = move_cp(cp, twist)
            n_idx = cp2idx(n_cp)
            table[idx][twist_idx] = n_idx
    with open('trans_table/trans_cp.txt', mode='w') as f:
        for arr in table:
            for elem in arr:
                f.write(str(elem) + '\n')
    print('done')

def co_table():
    table = [[-1 for _ in range(14)] for _ in range(2187)]
    for idx in trange(2187):
        co = idx2co(idx)
        for twist_idx, twist in enumerate(candidate[0]):
            n_co = move_co(co, twist)
            n_idx = co2idx(n_co)
            table[idx][twist_idx] = n_idx
    with open('trans_table/trans_co.txt', mode='w') as f:
        for arr in table:
            for elem in arr:
                f.write(str(elem) + '\n')
    print('done')

def ep_table_phase0():
    table = [[-1 for _ in range(14)] for _ in range(495)]
    for idx in trange(495):
        ep = idx2ep_phase0(idx)
        for twist_idx, twist in enumerate(candidate[0]):
            n_ep = move_ep(ep, twist)
            n_idx = ep2idx_phase0(n_ep)
            table[idx][twist_idx] = n_idx
    with open('trans_table/trans_ep_phase0.txt', mode='w') as f:
        for arr in table:
            for elem in arr:
                f.write(str(elem) + '\n')
    print('done')

def ep_table_phase1_1():
    table = [[-1 for _ in range(10)] for _ in range(40320)]
    for idx in trange(40320):
        ep = idx2ep_phase1_1(idx)
        for twist_idx, twist in enumerate(candidate[1]):
            n_ep = move_ep(ep, twist)
            n_idx = ep2idx_phase1_1(n_ep)
            table[idx][twist_idx] = n_idx
    with open('trans_table/trans_ep_phase1_1.txt', mode='w') as f:
        for arr in table:
            for elem in arr:
                f.write(str(elem) + '\n')
    print('done')

def ep_table_phase1_2():
    table = [[-1 for _ in range(10)] for _ in range(24)]
    for idx in trange(24):
        ep = idx2ep_phase1_2(idx)
        for twist_idx, twist in enumerate(candidate[1]):
            n_ep = move_ep(ep, twist)
            n_idx = ep2idx_phase1_2(n_ep)
            table[idx][twist_idx] = n_idx
    with open('trans_table/trans_ep_phase1_2.txt', mode='w') as f:
        for arr in table:
            for elem in arr:
                f.write(str(elem) + '\n')
    print('done')

def eo_table():
    table = [[-1 for _ in range(14)] for _ in range(2048)]
    for idx in trange(2048):
        eo = idx2eo(idx)
        for twist_idx, twist in enumerate(candidate[0]):
            n_eo = move_eo(eo, twist)
            n_idx = eo2idx(n_eo)
            table[idx][twist_idx] = n_idx
    with open('trans_table/trans_eo.txt', mode='w') as f:
        for arr in table:
            for elem in arr:
                f.write(str(elem) + '\n')
    print('done')

cp_table()
co_table()
ep_table_phase0()
ep_table_phase1_1()
ep_table_phase1_2()
eo_table()