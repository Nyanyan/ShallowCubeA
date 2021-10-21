from basic_functions import *
import subprocess
from time import time
from random import randrange
from tqdm import trange

err = subprocess.DEVNULL
#err = None

solver = subprocess.Popen('./solver.out'.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err)

all_num = 50

avg_ln = 0
num = 0

for t in trange(all_num):
    state = [i // 9 for i in range(54)]

    for _ in range(100):
        twist = randrange(0, 18)
        state = move_sticker(state, twist)

    solver.stdin.write((' '.join([str(i) for i in state]) + '\n').encode('utf-8'))
    solver.stdin.flush()
    ln = int(solver.stdout.readline())
    #print(t, ln, state)
    if ln != 0:
        avg_ln += ln
        num += 1
solver.kill()

print('found', num, 'solutions', num / all_num * 100, 'persent')
print('avg_len', avg_ln / num, 'moves')