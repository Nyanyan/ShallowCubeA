from basic_functions import *
import subprocess
from time import time
from random import randrange

solver = subprocess.Popen('./solver.out'.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None)

num = 10
avg_ln = 0
avg_tim = 0

for _ in range(10):
    state = [i // 9 for i in range(54)]

    for _ in range(30):
        twist = randrange(0, 18)
        state = move_sticker(state, twist)
    
    print(state)

    strt = time()
    solver.stdin.write((' '.join([str(i) for i in state]) + '\n').encode('utf-8'))
    solver.stdin.flush()
    ln = int(solver.stdout.readline())
    avg_ln += ln
    elapsed = time() - strt
    avg_tim += elapsed

print('avg_len', avg_ln / num)
print('avg_tim', avg_tim / num)