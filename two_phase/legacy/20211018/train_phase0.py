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
max_depth = 12
ln_moves = 14
move_translate = [0, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 17]
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
solved = [co2idx(solved_co), eo2idx(solved_eo), ep2idx_phase0(solved_ep)]
#solved_phase1 = [cp2idx(solved_cp), ep2idx_phase1_1(solved_ep), ep2idx_phase1_2(solved_ep)]

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

trans_co = read_file('trans_table/trans_co.txt', 2187, ln_moves)
trans_eo = read_file('trans_table/trans_eo.txt', 2048, ln_moves)
trans_ep_phase0 = read_file('trans_table/trans_ep_phase0.txt', 495, ln_moves)
prune_phase0_co_ep = read_file('prune_table/prune_phase0_co_ep.txt', 495, 2187)
prune_phase0_eo_ep = read_file('prune_table/prune_phase0_eo_ep.txt', 495, 2048)
prune_phase0_co = read_file_dim1('prune_table/prune_phase0_co.txt', 2187)
prune_phase0_eo = read_file_dim1('prune_table/prune_phase0_eo.txt', 2048)
prune_phase0_ep = read_file_dim1('prune_table/prune_phase0_ep.txt', 495)
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
            idxes = [trans_co[idxes[0]][move], trans_eo[idxes[1]][move], trans_ep_phase0[idxes[2]][move]]
            all_data.append([[prune_phase0_co_ep[idxes[2]][idxes[0]], prune_phase0_eo_ep[idxes[2]][idxes[1]]], i])
            #all_data.append([[prune_phase0_co[idxes[0]], prune_phase0_eo[idxes[1]], prune_phase0_ep[idxes[2]]], i])
            #all_data.append([[prune_phase0_co[idxes[0]], prune_phase0_eo[idxes[1]], prune_phase0_ep[idxes[2]], prune_phase0_co_ep[idxes[2]][idxes[0]], prune_phase0_eo_ep[idxes[2]][idxes[1]]], i])
            last_move = move
    shuffle(all_data)
    res_data = np.array([i[0] for i in all_data])
    res_labels = np.array([i[1] for i in all_data])
    return res_data, res_labels

train_data, train_labels = collect_data(n_train_data)
mae = 0.0
for i, arr in enumerate(train_data):
    predicted = max(arr)
    mae += abs(train_labels[i] - predicted)
mae /= len(train_data)
print('mae calculated with max function', mae)
mean = train_data.mean(axis=0)
std = train_data.std(axis=0)
train_data = (train_data - mean) / std
train_labels = train_labels / ln_moves
print(train_data.shape, train_labels.shape)

val_data, val_labels = collect_data(n_val_data)
val_data = (val_data - mean) / std
val_labels = val_labels / ln_moves
print(val_data.shape, val_labels.shape)

def LeakyReLU(x):
    return tf.math.maximum(0.01 * x, x)

x = Input(shape=input_shape)
hidden = Dense(32)(x)
hidden = LeakyReLU(hidden)
for _ in range(1):
    hidden = Dense(16)(hidden)
    hidden = LeakyReLU(hidden)
y = Dense(1)(hidden)
y = Activation('tanh', name='value')(y)

model = Model(inputs=[x], outputs=[y])
model.summary()
model.compile(loss='mse', optimizer='adam', metrics=['mae'])
print(model.evaluate(train_data, train_labels))
early_stop = EarlyStopping(monitor='val_loss', patience=10)
history = model.fit(train_data, train_labels, epochs=n_epochs, validation_data=(val_data, val_labels), callbacks=[early_stop])
with open('param/mean.txt', 'w') as f:
    for i in mean:
        f.write(str(i) + '\n')
with open('param/std.txt', 'w') as f:
    for i in std:
        f.write(str(i) + '\n')
model.save('param/model.h5')

for key in ['loss', 'val_loss']:
    plt.plot(history.history[key], label=key)
plt.xlabel('epoch')
plt.ylabel('loss')
plt.legend(loc='best')
plt.savefig('graph/loss.png')
plt.clf()

for key in ['mae', 'val_mae']:
    plt.plot(history.history[key], label=key)
plt.xlabel('epoch')
plt.ylabel('mae')
plt.legend(loc='best')
plt.savefig('graph/mae.png')
plt.clf()



