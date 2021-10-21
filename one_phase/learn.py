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
n_data = 1000000
n_residual = 4

data_shape = (280 + 324,)

def one_hot(arr):
    res = []
    for part in range(8):
        for place in range(8):
            if arr[place] == part:
                res.append(1.0)
            else:
                res.append(0.0)
    for part in range(3):
        for place in range(8, 16):
            if arr[place] == part:
                res.append(1.0)
            else:
                res.append(0.0)
    for part in range(12):
        for place in range(16, 28):
            if arr[place] == part:
                res.append(1.0)
            else:
                res.append(0.0)
    for part in range(2):
        for place in range(28, 40):
            if arr[place] == part:
                res.append(1.0)
            else:
                res.append(0.0)
    for dr in range(24):
        if arr[40] == dr:
            res.append(1.0)
        else:
            res.append(0.0)
    for color in range(6):
        for place in range(41, 95):
            if arr[place] == color:
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
    y = LeakyReLU(y)
    y = Dense(32)(y)
    y = Add()([y, sc])
    y = LeakyReLU(y)
y = Dense(1)(y)
model = Model(inputs=x, outputs=y)
model.summary()

data = []
labels = []

len_solutions = [0 for _ in range(20)]

with open('learn_data/data.txt', 'r') as f:
    raw_data = f.read().splitlines()

for _, datum in zip(trange(n_data), raw_data):
    #datum = f.readline()
    datum_int = [int(i) for i in datum.split()]
    label = datum_int[-1] - 10
    cube = datum_int[:-1]
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
