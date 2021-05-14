import keras
from keras.engine.saving import load_model
from keras.engine.training import Model
from keras.layers import Input, Conv2D, Flatten, Dense
from keras.regularizers import l2
from keras.optimizers import Adam
from keras import backend as K

import numpy as np

import pickle


class PolicyValueNet:
    def __init__(self, row: int, col: int, actions: list, model_file=None):
        """
        :param actions: all actions list
        """
        self.row = row
        self.col = col
        self.actions = actions
        self.l2_const = 1e-4  # coef of l2 penalty
        if model_file:
            self.model = load_model(model_file)
        else:
            self.policy_net, self.value_net, self.model = self.create_model()

    def create_model(self):
        in_x = conv_net = Input((5, self.row, self.col))

        conv_net = Conv2D(filters=32, kernel_size=(3, 3), padding="same", data_format="channels_first",
                          activation="relu", kernel_regularizer=l2(self.l2_const))(conv_net)
        conv_net = Conv2D(filters=64, kernel_size=(3, 3), padding="same", data_format="channels_first",
                          activation="relu", kernel_regularizer=l2(self.l2_const))(conv_net)
        conv_net = Conv2D(filters=128, kernel_size=(3, 3), padding="same", data_format="channels_first",
                          activation="relu", kernel_regularizer=l2(self.l2_const))(conv_net)

        self.conv_net = conv_net

        # policy net
        policy_net = Conv2D(filters=4, kernel_size=(1, 1), activation="relu", data_format="channels_first",
                            kernel_regularizer=l2(self.l2_const))(conv_net)
        policy_net = Flatten()(policy_net)
        if len(self.actions) <= 200:
            policy_net = Dense(len(self.actions), activation="softmax",
                               kernel_regularizer=l2(self.l2_const))(policy_net)
        else:
            policy_net = Dense(1024, activation="relu",
                               kernel_regularizer=l2(self.l2_const))(policy_net)
            policy_net = Dense(len(self.actions), activation="softmax",
                               kernel_regularizer=l2(self.l2_const))(policy_net)

        # value net
        value_net = Conv2D(filters=2, kernel_size=(1, 1), activation="relu", data_format="channels_first",
                           kernel_regularizer=l2(self.l2_const))(conv_net)
        value_net = Flatten()(value_net)
        value_net = Dense(64, kernel_regularizer=l2(self.l2_const))(value_net)
        value_net = Dense(1, activation="tanh", kernel_regularizer=l2(self.l2_const))(value_net)

        model = Model(in_x, [policy_net, value_net])

        return policy_net, value_net, model


if __name__ == '__main__':
    model = PolicyValueNet(14, 14, list(range(4672)))
    model.model.save("primitive model")
