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

n_epochs = 50
test_ratio = 0.15
n_data = 100000
n_residual = 2

data_shape = (78,)
min_move = 1
max_move = 12
n_moves = 18

def one_hot(arr):
    res = []
    for i in range(54):
        if arr[i] == 0 or arr[i] == 5:
            res.append(1.0)
        else:
            res.append(0.0)
    for i in (1, 3, 5, 7, 10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34, 37, 39, 41, 43, 46, 48, 50, 52):
        if arr[i] == 1 or arr[i] == 3:
            res.append(1.0)
        else:
            res.append(0.0)
    return res

def face(mov):
    return mov // 3

def axis(mov):
    return mov // 6

def LeakyReLU(x):
    return tf.math.maximum(0.01 * x, x)



x = Input(shape=data_shape)
y = Dense(64)(x)
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

for _ in trange(n_data):
    n_move = randint(min_move, max_move)
    cube = [i // 9 for i in range(54)]
    l_mov = -1000
    for _ in range(n_move):
        mov = randint(0, n_moves - 1)
        while face(mov) == face(l_mov) or (axis(mov) == axis(l_mov) and mov < l_mov):
            mov = randint(0, n_moves - 1)
        cube = move_sticker(cube, mov)
        l_mov = mov
    data.append(one_hot(cube))
    labels.append(n_move)

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
model.save('param/phase0.h5')

for key in ['loss', 'val_loss']:
    plt.plot(history.history[key], label=key)
plt.xlabel('epoch')
plt.ylabel('loss')
plt.legend(loc='best')
plt.savefig('graph/phase0_loss.png')
plt.clf()

for key in ['mae', 'val_mae']:
    plt.plot(history.history[key], label=key)
plt.xlabel('epoch')
plt.ylabel('mae')
plt.legend(loc='best')
plt.savefig('graph/phase0_mae.png')
plt.clf()
