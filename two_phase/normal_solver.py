from basic_functions import *

def idxes_init(phase, cp, co, ep, eo):
    if phase == 0:
        res1 = co2idx(co)
        res2 = eo2idx(eo)
        res3 = ep2idx_phase0(ep)
        return (res1, res2, res3)
    else:
        res1 = cp2idx(cp)
        res2 = ep2idx_phase1_1(ep)
        res3 = ep2idx_phase1_2(ep)
        return (res1, res2, res3)

def trans(phase, idxes, twist):
    if phase == 0:
        res1 = trans_co[idxes[0]][twist]
        res2 = trans_eo[idxes[1]][twist]
        res3 = trans_ep_phase0[idxes[2]][twist]
        return (res1, res2, res3)
    else:
        res1 = trans_cp[idxes[0]][twist]
        res2 = trans_ep_phase1_1[idxes[1]][twist]
        res3 = trans_ep_phase1_2[idxes[2]][twist]
        return (res1, res2, res3)

def distance(phase, idxes):
    if phase == 0:
        return max(prun_phase0_co_ep[idxes[2]][idxes[0]], prun_phase0_eo_ep[idxes[2]][idxes[1]])
    else:
        return max(prun_phase1_cp_ep[idxes[2]][idxes[0]], prun_phase1_ep_ep[idxes[2]][idxes[1]])

def phase_search(phase, idxes, depth, dis):
    global phase_solution
    if depth == 0:
        if dis == 0:
            return [[i for i in phase_solution]]
        else:
            return []
    elif dis == 0:
        return []
    res = []
    depth -= 1
    l1_twist = phase_solution[-1] if phase_solution else -10
    l2_twist = phase_solution[-2] if len(phase_solution) >= 2 else -10
    l1_twist_type = l1_twist // 3
    l2_twist_type = l2_twist // 3
    for twist_idx, twist in enumerate(candidate[phase]):
        if twist // 3 == l1_twist_type: # don't turn same face twice
            continue
        if twist // 3 == l2_twist_type and twist // 6 == l1_twist // 6: # don't turn opposite face 3 times
            continue
        n_idxes = trans(phase, idxes, twist_idx)
        n_dis = distance(phase, n_idxes)
        if n_dis > depth:
            continue
        phase_solution.append(twist)
        sol = phase_search(phase, n_idxes, depth, n_dis)
        if phase == 1 and sol: # only one solution needed
            return sol
        res.extend(sol)
        if len(res) > 50:
            return res
        phase_solution.pop()
    return res

def solver(stickers, phase):
    global phase_solution
    min_phase0_depth = 0
    res = []
    l = 27
    s_cp, s_co, s_ep, s_eo = sticker2arr(stickers)
    search_lst = [[s_cp, s_co, s_ep, s_eo, []]]
    n_search_lst = []
    for cp, co, ep, eo, last_solution in search_lst:
        idxes = idxes_init(phase, cp, co, ep, eo)
        dis = distance(phase, idxes)
        phase_solution = []
        strt_depth = dis if phase == 1 else max(dis, min_phase0_depth)
        for depth in range(strt_depth, l - len(last_solution)):
            sol = phase_search(phase, idxes, depth, dis)
            if sol:
                return sol[0]
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
                        l = min(l, len(n_solution))
                if phase == 0:
                    min_phase0_depth = depth + 1
                break
    search_lst = [[i for i in j] for j in n_search_lst]
    n_search_lst = []
    if search_lst:
        res = [i for i in search_lst[-1][4]]
    return res

phase_solution = []
trans_co = []
with open('normal_alg/trans_co.csv', mode='r') as f:
    for line in map(str.strip, f):
        trans_co.append([int(i) for i in line.replace('\n', '').split(',')])
trans_cp = []
with open('normal_alg/trans_cp.csv', mode='r') as f:
    for line in map(str.strip, f):
        trans_cp.append([int(i) for i in line.replace('\n', '').split(',')])
trans_eo = []
with open('normal_alg/trans_eo.csv', mode='r') as f:
    for line in map(str.strip, f):
        trans_eo.append([int(i) for i in line.replace('\n', '').split(',')])
trans_ep_phase0 = []
with open('normal_alg/trans_ep_phase0.csv', mode='r') as f:
    for line in map(str.strip, f):
        trans_ep_phase0.append([int(i) for i in line.replace('\n', '').split(',')])
trans_ep_phase1_1 = []
with open('normal_alg/trans_ep_phase1_1.csv', mode='r') as f:
    for line in map(str.strip, f):
        trans_ep_phase1_1.append([int(i) for i in line.replace('\n', '').split(',')])
trans_ep_phase1_2 = []
with open('normal_alg/trans_ep_phase1_2.csv', mode='r') as f:
    for line in map(str.strip, f):
        trans_ep_phase1_2.append([int(i) for i in line.replace('\n', '').split(',')])
prun_phase0_co_ep = []
with open('normal_alg/prun_phase0_co_ep.csv', mode='r') as f:
    for line in map(str.strip, f):
        prun_phase0_co_ep.append([int(i) for i in line.replace('\n', '').split(',')])
prun_phase0_eo_ep = []
with open('normal_alg/prun_phase0_eo_ep.csv', mode='r') as f:
    for line in map(str.strip, f):
        prun_phase0_eo_ep.append([int(i) for i in line.replace('\n', '').split(',')])
prun_phase1_cp_ep = []
with open('normal_alg/prun_phase1_cp_ep.csv', mode='r') as f:
    for line in map(str.strip, f):
        prun_phase1_cp_ep.append([int(i) for i in line.replace('\n', '').split(',')])
prun_phase1_ep_ep = []
with open('normal_alg/prun_phase1_ep_ep.csv', mode='r') as f:
    for line in map(str.strip, f):
        prun_phase1_ep_ep.append([int(i) for i in line.replace('\n', '').split(',')])
print('initialize done')
