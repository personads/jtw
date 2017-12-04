'''
    Extreme Learning Machine (Class)
'''
import sys

import tensorflow as tf
import numpy as np

from config import *
from disciples.tf_disciple import TensorFlowDisciple

class ExtremeLearningMachine(TensorFlowDisciple):
    '''
    Extreme Learning Machine based classifier
    Type: Single hidden layer feedforward networks (SLFNs) with
          random hidden nodes
    '''

    def __init__(self, iterations=200000, hidden_size=400, learning_rate=0.1, tf_session=None, verbose=False):
        '''
        Constructor of ExtremeLearningMachine based classifier
        '''
        # init tensorflow classifier
        TensorFlowDisciple.__init__(self, iterations, tf_session, verbose)
        # init tensorflow variables
        # -- init model
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        self.tf_input = tf.placeholder(tf.float32, [None, STATE_VECTOR_SIZE])

        # hidden layer parameters, remain fixed, initialize with some part of training data ?
        self.tf_b_acc = tf.constant(0.1, shape=[1])
        self.tf_b_steer = tf.constant(0.1, shape=[1])

        self.tf_a_acc = tf.Variable(tf.random_uniform([STATE_VECTOR_SIZE, self.hidden_size], -1,1), trainable=False)
        self.tf_a_steer = tf.Variable(tf.random_uniform([STATE_VECTOR_SIZE, self.hidden_size], -1,2), trainable=False)

        self.tf_layer_1_acc = tf.sigmoid(tf.matmul(self.tf_input, self.tf_a_acc) + self.tf_b_acc)
        self.tf_layer_1_steer = tf.tanh(tf.matmul(self.tf_input, self.tf_a_steer) + self.tf_b_steer)

        # Network Parameters
        self.tf_beta_acc = tf.Variable(tf.random_normal([self.hidden_size, 1], stddev=0.1))
        self.tf_beta_steer = tf.Variable(tf.random_normal([self.hidden_size, 1], stddev=0.1))

        self.output_acc = tf.matmul(self.tf_layer_1_acc, self.tf_beta_acc)
        self.output_steer = tf.matmul(self.tf_layer_1_steer, self.tf_beta_steer)

        # Model
        self.tf_predict = tf.concat([self.output_acc, self.output_steer], axis=1)

        # -- init loss and optimizer
        self.tf_target = tf.placeholder(tf.float32, [None, COMMAND_VECTOR_SIZE])
        self.regularizer = tf.matmul(tf.transpose(tf.concat([self.tf_beta_acc, self.tf_beta_steer],axis=0)), tf.concat([self.tf_beta_acc, self.tf_beta_steer], axis=0))
        self.tf_loss = tf.reduce_mean(tf.squared_difference(self.tf_predict, self.tf_target)) + 0.1 * self.regularizer
        self.tf_train_step = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(self.tf_loss)
        # -- init session
        self.tf_session = tf_session if tf_session else tf.Session()
        self.tf_session.run(tf.global_variables_initializer())

    def train(self, train_in, train_out, batch_size=400):
        '''
        Train the ELM on given data
        '''
        if self.verbose: print("training Extreme Learning Machine...")
        self.seek = 0
        cur_loss = 42. # init loss
        for train_i in range(self.iterations):
            if self.verbose:
                sys.stdout.write('\riteration: %d of %d (%f loss)' % (train_i+1, self.iterations, cur_loss))
                if train_i%1000 == 0: cur_loss = self.tf_session.run(self.tf_loss, feed_dict={self.tf_input: train_in, self.tf_target: train_out})
                sys.stdout.flush()
            # create batch
            cur_train_in, cur_train_out = self._create_next_batch(train_in, train_out, batch_size)
            # run training step
            self.tf_session.run(self.tf_train_step, feed_dict={self.tf_input: cur_train_in, self.tf_target: cur_train_out})
        if self.verbose: sys.stdout.write('\rtraining complete (%d iterations, %f loss)'%(self.iterations, cur_loss) + (' ' * len(str(self.iterations)) + '\n'))

    def predict(self, pred_in):
        if self.verbose: print("predicting classes...")
        res = self.tf_session.run(self.tf_predict, feed_dict={self.tf_input: pred_in})
        return res

    def take_wheel(self, state):
        return self.predict([state])[0]
