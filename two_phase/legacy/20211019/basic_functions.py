'''
corner numbering
  0 1
   U
0 3 2 1
 L F R
7 4 5 6
   D
  7 6

edge numbering
       0
     3 U 1
       2
11 L 8 F 9 R 10
       4
     7 D 5
       6

sticker numbering
              U
           0  1  2
           3  4  5
           6  7  8
    L         F         R         B
36 37 38   9 10 11  18 19 20  27 28 29
39 40 41  12 13 14  21 22 23  30 31 32
42 43 44  15 16 17  24 25 26  33 34 35
              D
          45 46 47
          48 49 50
          51 52 53

color numbering
white: 0
green: 1
red: 2
blue: 3
orange: 4
yellow: 5

rotation:
U F number
w g 0
o g 1
y g 2
r g 3
w r 4
g r 5
y r 6
b r 7
w b 8
r b 9
y b 10
o b 11
w o 12
b o 13
y o 14
g o 15
b w 16
o w 17
g w 18
r w 19
g y 20
o y 21
b y 22
r y 23

rotated face
R 0 (0-2)
L 1 (3-5)
U 2 (6-8)
D 3 (9-11)
F 4 (12-14)
B 5 (15-17)
'''


#                   0    1     2     3    4     5     6    7     8     9    10    11    12   13    14    15   16    17
twists_notation = ["R", "R2", "R'", "L", "L2", "L'", "U", "U2", "U'", "D", "D2", "D'", "F", "F2", "F'", "B", "B2", "B'"]

fac = [1]
for i in range(1, 13):
    fac.append(fac[-1] * i)

corner_move_parts = [
    (1, 6, 5, 2), # R
    (3, 4, 7, 0), # L
    (0, 1, 2, 3), # U
    (4, 5, 6, 7), # D
    (2, 5, 4, 3), # F
    (0, 7, 6, 1)  # B
]
co_plus = (2, 1, 2, 1)
edge_move_parts = [
    (1, 10, 5, 9), # R
    (3, 8, 7, 11), # L
    (0, 1, 2, 3),  # U
    (4, 5, 6, 7),  # D
    (2, 9, 4, 8),  # F
    (0, 11, 6, 10) # B
]
eo_changes = [
    (), # R
    (), # L
    (),# U
    (),  # D
    (2, 9, 4, 8),  # F
    (0, 11, 6, 10) # B
]

corner_places = [(0, 36, 29), (2, 27, 20), (8, 18, 11), (6, 9, 38), (45, 44, 15), (47, 17, 24), (53, 26, 33), (51, 35, 42)]
corner_colors = [(0, 4, 3),   (0, 3, 2),   (0, 2, 1),   (0, 1, 4),  (5, 4, 1),    (5, 1, 2),    (5, 2, 3),    (5, 3, 4)   ]
edge_places = [(1, 28), (5, 19), (7, 10), (3, 37), (46, 16), (50, 25), (52, 34), (48, 43), (12, 41), (14, 21), (30, 23), (32, 39)]
edge_colors = [(0, 3),  (0, 2),  (0, 1),  (0, 4),  (5, 1),   (5, 2),   (5, 3),   (5, 4),   (1, 4),   (1, 2),   (3, 2),   (3, 4)  ]

'''
sticker numbering
              U
           0  1  2
           3  4  5
           6  7  8
    L         F         R         B
36 37 38   9 10 11  18 19 20  27 28 29
39 40 41  12 13 14  21 22 23  30 31 32
42 43 44  15 16 17  24 25 26  33 34 35
              D
          45 46 47
          48 49 50
          51 52 53
'''

sticker_moves = [
    [(5, 30, 50, 14), (19, 23, 25, 21), (2, 33, 47, 11), (27, 53, 17, 8), (20, 26, 24, 18)],    # R
    [(3, 12, 48, 32), (37, 41, 43, 39), (0, 9, 45, 35), (6, 15, 51, 29), (36, 38, 44, 42)],     # L
    [(28, 19, 10, 37), (1, 5, 7, 3), (29, 20, 11, 38), (27, 18, 9, 36), (0, 2, 8, 6)],          # U
    [(16, 25, 34, 43), (46, 50, 52, 48), (15, 24, 33, 42), (17, 26, 35, 44), (45, 47, 53, 51)], # D
    [(7, 21, 46, 41), (10, 14, 16, 12), (6, 18, 47, 44), (8, 24, 45, 38), (9, 11, 17, 15)],     # F
    [(1, 39, 52, 23), (28, 32, 34, 30), (2, 36, 51, 26), (0, 42, 53, 20), (27, 29, 35, 33)]     # B
]

def sticker2arr(stickers):
    cp = [-1 for _ in range(8)]
    co = [-1 for _ in range(8)]
    for place in range(8):
        part_color = [stickers[i] for i in corner_places[place]]
        for part in range(8):
            for dr in range(3):
                cnt = 0
                for sticker in range(3):
                    if part_color[sticker] != -1 and part_color[sticker] != corner_colors[part][(sticker - dr) % 3]:
                        break
                    if part_color[sticker] == -1:
                        cnt += 1
                else:
                    if cnt <= 1:
                        cp[place] = part
                        co[place] = dr
                        break
            else:
                continue
            break
    ep = [-1 for _ in range(12)]
    eo = [-1 for _ in range(12)]
    for place in range(12):
        part_color = [stickers[i] for i in edge_places[place]]
        for part in range(12):
            for dr in range(2):
                for sticker in range(2):
                    if part_color[sticker] != edge_colors[part][(sticker - dr) % 2]:
                        break
                else:
                    ep[place] = part
                    eo[place] = dr
                    break
            else:
                continue
            break
    return cp, co, ep, eo

def sticker2numbering(stickers):
    res = list(range(54))
    for place in range(8):
        part_color = [stickers[i] for i in corner_places[place]]
        for part in range(8):
            for dr in range(3):
                cnt = 0
                for sticker in range(3):
                    if part_color[sticker] != -1 and part_color[sticker] != corner_colors[part][(sticker - dr) % 3]:
                        break
                    if part_color[sticker] == -1:
                        cnt += 1
                else:
                    if cnt <= 1:
                        for i in range(3):
                            res[corner_places[place][i]] = corner_places[part][(i - dr) % 3]
                        break
            else:
                continue
            break
    for place in range(12):
        part_color = [stickers[i] for i in edge_places[place]]
        for part in range(12):
            for dr in range(2):
                for sticker in range(2):
                    if part_color[sticker] != edge_colors[part][(sticker - dr) % 2]:
                        break
                else:
                    for i in range(2):
                        res[edge_places[place][i]] = edge_places[part][(i - dr) % 2]
                    break
            else:
                continue
            break
    return res

def reverse(twist):
    res = twist
    if twist % 3 == 0:
        res = twist + 2
    elif twist % 3 == 2:
        res = twist - 2
    return res

def move_sticker(stickers, mov):
    face = mov // 3
    num = mov % 3 + 1
    arr = [i for i in stickers]
    n_arr = [i for i in arr]
    for _ in range(num):
        for mov_arr in sticker_moves[face]:
            for i in range(4):
                n_arr[mov_arr[(i + 1) % 4]] = arr[mov_arr[i]]
        arr = [i for i in n_arr]
    return arr

def print_sticker(arr):
    colors = 'wgrboy'
    for face in range(6):
        for row in range(3):
            for col in range(3):
                idx = face * 9 + row * 3 + col
                print(colors[arr[idx] // 9], end='')
            print('')
        print('')

def move_cp(cp, twist):
    twist_type = twist // 3
    twist_amount = twist % 3 + 1
    res = [i for i in cp]
    for _ in range(twist_amount):
        n_res = [i for i in res]
        for i in range(4):
            n_res[corner_move_parts[twist_type][(i + 1) % 4]] = res[corner_move_parts[twist_type][i]]
        res = n_res
    return res

def move_co(co, twist):
    twist_type = twist // 3
    twist_amount = twist % 3 + 1
    res = [i for i in co]
    flip_flag = twist_type != 2 and twist_type != 3 and twist_amount != 2
    for _ in range(twist_amount):
        n_res = [i for i in res]
        for i in range(4):
            n_res[corner_move_parts[twist_type][(i + 1) % 4]] = res[corner_move_parts[twist_type][i]]
            if flip_flag:
                n_res[corner_move_parts[twist_type][(i + 1) % 4]] += co_plus[i]
                n_res[corner_move_parts[twist_type][(i + 1) % 4]] %= 3
        res = n_res
    return res

def move_ep(ep, twist):
    twist_type = twist // 3
    twist_amount = twist % 3 + 1
    res = [i for i in ep]
    for _ in range(twist_amount):
        n_res = [i for i in res]
        for i in range(4):
            n_res[edge_move_parts[twist_type][(i + 1) % 4]] = res[edge_move_parts[twist_type][i]]
        res = n_res
    return res

def move_eo(eo, twist):
    twist_type = twist // 3
    twist_amount = twist % 3 + 1
    res = [i for i in eo]
    for _ in range(twist_amount):
        n_res = [i for i in res]
        for i in range(4):
            n_res[edge_move_parts[twist_type][(i + 1) % 4]] = res[edge_move_parts[twist_type][i]]
        for i in range(len(eo_changes[twist_type])):
            n_res[eo_changes[twist_type][i]] = 1 - n_res[eo_changes[twist_type][i]]
        res = n_res
    return res

def cmb(n, r):
    return fac[n] // fac[r] // fac[n - r]

def cp2idx(cp): # 40320
    res = 0
    for i in range(8):
        cnt = cp[i]
        for j in cp[:i]:
            if j < cp[i]:
                cnt -= 1
        res += fac[7 - i] * cnt
    return res

def idx2cp(idx):
    res = [-1 for _ in range(8)]
    for i in range(8):
        candidate = idx // fac[7 - i]
        marked = [True for _ in range(i)]
        for _ in range(8):
            for j, k in enumerate(res[:i]):
                if k <= candidate and marked[j]:
                    candidate += 1
                    marked[j] = False
        res[i] = candidate
        idx %= fac[7 - i]
    return res

def co2idx(co): # 2187
    res = 0
    for i in range(7):
        res *= 3
        res += co[i]
    return res

def idx2co(idx):
    res = [0 for _ in range(8)]
    for i in reversed(range(7)):
        res[i] = idx % 3
        idx //= 3
    res[7] = (3 - sum(res) % 3) % 3
    return res

def ep2idx(ep): # 19958400
    res = 0
    ii = 0
    for i in range(1, 12):
        if 1 <= ep[i] < 10:
            cnt = ep[i] - 1
            for j in ep[1:i]:
                if j < ep[i]:
                    cnt -= 1
            res += fac[8 - ii] * cnt
            ii += 1
    res *= 55
    targets = set(range(1, 10))
    cnt = 9
    for i in range(1, 12):
        if ep[i] in targets:
            res += cmb(11 - i, cnt)
            cnt -= 1
    return res

def idx2ep(idx):
    idx1 = idx // 55
    ep9 = [-1 for _ in range(9)]
    for i in range(9):
        candidate = idx1 // fac[8 - i] + 1
        marked = [True for _ in range(i)]
        for _ in range(9):
            for j, k in enumerate(ep9[:i]):
                if k <= candidate and marked[j]:
                    candidate += 1
                    marked[j] = False
        ep9[i] = candidate
        idx1 %= fac[8 - i]
    idx2 = idx % 55
    res = [10 for _ in range(12)]
    res[0] = 0
    target = -1
    cnt = 9
    j = 0
    for i in range(1, 12):
        tmp = cmb(11 - i, cnt)
        if idx2 >= tmp:
            res[i] = ep9[j]
            idx2 -= tmp
            cnt -= 1
            j += 1
            if cnt == 0:
                break
    return res


def eo2idx(eo): # 1024
    res = 0
    for i in eo[1:11]:
        res *= 2
        res += i
    return res

def idx2eo(idx):
    res = [0 for _ in range(12)]
    for i in reversed(range(1, 11)):
        res[i] = idx % 2
        idx //= 2
    res[11] = sum(res) % 2
    return res

'''
ep = list(range(12))
eo = [0 for _ in range(12)]
cp = list(range(8))
co = [0 for _ in range(8)]
sticker = list(range(54))
for notation in "R U R' U'".split():
    twist = twists_notation.index(notation)
    print(twist)
    sticker = move_sticker(sticker, twist)
    print_sticker(sticker)
'''