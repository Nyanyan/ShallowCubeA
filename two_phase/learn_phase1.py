import tensorflow as tf
from tensorflow.keras.datasets import boston_housing
from tensorflow.keras.layers import Activation, Add, BatchNormalization, Conv2D, Dense, GlobalAveragePooling2D, Input, concatenate, Flatten, Dropout
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.callbacks import EarlyStopping, LearningRateScheduler, LambdaCallback
from tensorflow.keras.optimizers import Adam
#from keras.layers.advanced_activations import LeakyReLU
from tensorflow.keras.regularizers import l2
from tensorflow.keras.utils import plot_model
import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange
from basic_functions import *
from random import randint


n_epochs = 200
test_ratio = 0.15
n_data = 1012000
n_residual = 2

data_shape = (182,)
min_move = 1
max_move = 12
n_moves = 10

move_candidate = [1, 4, 6, 7, 8, 9, 10, 11, 13, 16]

edges = [1, 3, 5, 7, 10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34, 37, 39, 41, 43, 46, 48, 50, 52]

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
n_co = 2187
n_cp = 40320
n_ep_phase0 = 495
n_ep_phase1_0 = 40320
n_ep_phase1_1 = 24
n_eo = 2048

with open("param/prune_phase1_ep_cp.txt", "r") as f:
    prune_phase1_ep_cp = []
    for i in range(n_ep_phase1_1):
        prune_phase1_ep_cp.append([])
        for j in range(n_cp):
            prune_phase1_ep_cp[i].append(float(f.readline()))

with open("param/prune_phase1_ep_ep.txt", "r") as f:
    prune_phase1_ep_ep = []
    for i in range(n_ep_phase1_1):
        prune_phase1_ep_ep.append([])
        for j in range(n_ep_phase1_0):
            prune_phase1_ep_ep[i].append(float(f.readline()))


def one_hot(arr):
    res = []
    for color in [0, 5]:
        for i in range(0, 9):
            if arr[i] == color:
                res.append(1.0)
            else:
                res.append(0.0)
        for i in range(45, 54):
            if arr[i] == color:
                res.append(1.0)
            else:
                res.append(0.0)
    for color in [1, 2, 3, 4]:
        for i in range(9, 45):
            if arr[i] == color:
                res.append(1.0)
            else:
                res.append(0.0)
    cp, co, ep, eo = sticker2arr(arr)
    idx0 = cp2idx(co)
    idx1 = ep2idx_phase1_1(ep)
    idx2 = ep2idx_phase1_2(ep)
    res.append(prune_phase1_ep_cp[idx2][idx0])
    res.append(prune_phase1_ep_ep[idx2][idx1])
    return res

def face(mov):
    return mov // 3

def axis(mov):
    return mov // 6

def LeakyReLU(x):
    return tf.math.maximum(0.01 * x, x)



x = Input(shape=data_shape)
y = Dense(32)(x)
y = LeakyReLU(y)
y = Dense(32)(y)
y = LeakyReLU(y)
for _ in range(n_residual):
    sc = y
    y = Dense(32)(y)
    y = Add()([y, sc])
    y = LeakyReLU(y)
y = Dense(1)(y)
model = Model(inputs=x, outputs=y)
model.summary()

data = []
labels = []

len_solutions = [0 for _ in range(20)]

with open('learn_data/phase1/all_data.txt', 'r') as f:
    for _ in trange(n_data):
        cube_str, label = f.readline().split()
        label = int(label)
        cube = [int(i) for i in cube_str]
        data.append(one_hot(cube))
        labels.append(label)
        len_solutions[label] += 1

print(len_solutions)

data = np.array(data)
labels = np.array(labels)

n_test = int(n_data * test_ratio)
n_train = n_data - n_test

train_data = data[0:n_train]
train_labels = labels[0:n_train]
test_data = data[n_train:n_data]
test_labels = labels[n_train:n_data]

print('train', train_data.shape, train_labels.shape)
print('test', test_data.shape, test_labels.shape)


model.compile(loss='mse', optimizer='adam', metrics='mae')
print(model.evaluate(test_data, test_labels))
early_stop = EarlyStopping(monitor='val_loss', patience=5)
history = model.fit(train_data, train_labels, epochs=n_epochs, validation_data=(test_data, test_labels), callbacks=[early_stop])
model.save('param/phase1.h5')

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
