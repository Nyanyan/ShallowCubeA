from basic_functions import *

state = [i // 9 for i in range(54)]

#scramble = "R Dw R' Fw F D L' Dw2 F2 R2 Fw' L2 D' R"
scramble = "R Dw R' Fw F D L' Dw2 F2 R2 Fw' L2"


print('scramble:', scramble)
for twist in scramble.split():
    state = move_sticker(state, twists_notation.index(twist))
print('state', state)
print(*state)