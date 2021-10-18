import tensorflow as tf
from tensorflow.keras.datasets import boston_housing
from tensorflow.keras.layers import Activation, Add, BatchNormalization, Conv2D, Dense, GlobalAveragePooling2D, Input, concatenate, Flatten, Dropout
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.callbacks import EarlyStopping, LearningRateScheduler, LambdaCallback
from tensorflow.keras.optimizers import Adam
#from keras.layers.advanced_activations import LeakyReLU
from tensorflow.keras.regularizers import l2
import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange
from random import random, randint, shuffle, sample
import subprocess
from math import exp

from basic_functions import *

n_data = 20000
val_ratio = 0.2
max_depth = 18
ln_moves = 10
move_translate = [1, 4, 6, 7, 8, 9, 10, 11, 13, 16]
n_epochs = 50
input_shape = (2,)

moves = list(range(ln_moves))
n_train_data = n_data
n_val_data = int(n_data * val_ratio)

train_data = []
train_labels = []
test_data = []
test_labels = []

solved_stickers = []
for i in range(6):
    solved_stickers.extend([i for _ in range(9)])
solved_cp, solved_co, solved_ep, solved_eo = sticker2arr(solved_stickers)
#solved = [co2idx(solved_co), eo2idx(solved_eo), ep2idx_phase0(solved_ep)]
solved = [cp2idx(solved_cp), ep2idx_phase1_1(solved_ep), ep2idx_phase1_2(solved_ep)]

def read_file(filename, a, b):
    res = []
    with open(filename, mode='r') as f:
        for idx in range(a):
            res.append([])
            for _ in range(b):
                res[idx].append(int(f.readline()))
    return res

def read_file_dim1(filename, a):
    res = []
    with open(filename, mode='r') as f:
        for idx in range(a):
            res.append(int(f.readline()))
    return res

trans_cp = read_file('trans_table/trans_cp.txt', 40320, ln_moves)
trans_ep_phase1_1 = read_file('trans_table/trans_ep_phase1_1.txt', 40320, ln_moves)
trans_ep_phase1_2 = read_file('trans_table/trans_ep_phase1_2.txt', 24, ln_moves)
prune_phase1_cp_ep = read_file('prune_table/prune_phase1_cp_ep.txt', 24, 40320)
prune_phase1_ep_ep = read_file('prune_table/prune_phase1_ep_ep.txt', 24, 40320)
#prune_phase0_co = read_file_dim1('prune_table/prune_phase0_co.txt', 2187)
#prune_phase0_eo = read_file_dim1('prune_table/prune_phase0_eo.txt', 2048)
#prune_phase0_ep = read_file_dim1('prune_table/prune_phase0_ep.txt', 495)
print('initialized')

def illegal_move(move, last_move):
    if last_move == -1:
        return False
    move = move_translate[move]
    last_move = move_translate[last_move]
    if move // 3 == last_move // 3 and move <= last_move:
        return True
    return False

def collect_data(num):
    all_data = []
    for _ in range(num):
        idxes = [i for i in solved]
        last_move = -1
        for i in range(1, max_depth + 1):
            move = randint(0, ln_moves - 1)
            while illegal_move(move, last_move):
                move = randint(0, ln_moves - 1)
            idxes = [trans_cp[idxes[0]][move], trans_ep_phase1_1[idxes[1]][move], trans_ep_phase1_2[idxes[2]][move]]
            all_data.append([[prune_phase1_cp_ep[idxes[2]][idxes[0]], prune_phase1_ep_ep[idxes[2]][idxes[1]]], i, [elem for elem in idxes]])
            last_move = move
    shuffle(all_data)
    res_data = np.array([i[0] for i in all_data])
    res_labels = np.array([i[1] for i in all_data])
    res_idxes = [i[2] for i in all_data]
    return res_data, res_labels, res_idxes

train_data, train_labels, train_idxes = collect_data(n_train_data)
mae = 0.0
for i, arr in enumerate(train_data):
    predicted = max(arr)
    mae += abs(train_labels[i] - predicted)
mae /= len(train_data)
print('mae calculated with max function', mae)
mean = train_data.mean(axis=0)
std = train_data.std(axis=0)
train_data = (train_data - mean) / std
train_labels = train_labels / max_depth
print(train_data.shape, train_labels.shape)

val_data, val_labels, val_idxes = collect_data(n_val_data)
val_data = (val_data - mean) / std
val_labels = val_labels / max_depth
print(val_data.shape, val_labels.shape)

def LeakyReLU(x):
    return tf.math.maximum(0.01 * x, x)

model = load_model('param/phase1_model.h5')
prediction = model.predict(train_data[0:10])
for i in range(10):
    print(train_idxes[i])
    print(train_data[i])
    print(prediction[i][0]* 18)
    print(train_labels[i] * 18)
    print('')
exit()

x = Input(shape=input_shape)
hidden = Dense(8)(x)
hidden = LeakyReLU(hidden)
hidden = Dense(4)(hidden)
hidden = LeakyReLU(hidden)
y = Dense(1)(hidden)
y = Activation('tanh', name='value')(y)

model = Model(inputs=[x], outputs=[y])
model.summary()
model.compile(loss='mse', optimizer='adam', metrics=['mae'])
print(model.evaluate(train_data, train_labels))
early_stop = EarlyStopping(monitor='val_loss', patience=10)
history = model.fit(train_data, train_labels, epochs=n_epochs, validation_data=(val_data, val_labels), callbacks=[early_stop])
with open('param/phase1_mean.txt', 'w') as f:
    for i in mean:
        f.write(str(i) + '\n')
with open('param/phase1_std.txt', 'w') as f:
    for i in std:
        f.write(str(i) + '\n')
model.save('param/phase1_model.h5')

for key in ['loss', 'val_loss']:
    plt.plot(history.history[key], label=key)
plt.xlabel('epoch')
plt.ylabel('loss')
plt.legend(loc='best')
plt.savefig('graph/phase1_loss.png')
plt.clf()

for key in ['mae', 'val_mae']:
    plt.plot(history.history[key], label=key)
plt.xlabel('epoch')
plt.ylabel('mae')
plt.legend(loc='best')
plt.savefig('graph/phase1_mae.png')
plt.clf()



