'''
    Multi-Layer Perceptron (class)
'''
import sys

import tensorflow as tf

from config import *
from disciples.tf_disciple import TensorFlowDisciple

class MultiLayerPerceptron(TensorFlowDisciple):
    '''
    Multi-Layer Perceptron based classifier
    '''

    def __init__(self, iterations=200000, num_layers=1, hidden_size=150, learning_rate=0.05, tf_session=None, verbose=False):
        '''
        Constructor of MultiLayerPerceptronClassifier
        '''
        # init tensorflow classifier
        TensorFlowDisciple.__init__(self, iterations, tf_session, verbose)
        # init tensorflow variables
        # -- init model
        self.num_layers = max(1, num_layers)
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        self.tf_input = tf.placeholder(tf.float32, [None, STATE_VECTOR_SIZE])
        self.tf_var_wi = tf.Variable(tf.truncated_normal([STATE_VECTOR_SIZE, self.hidden_size], stddev=0.1))
        self.tf_var_bi = tf.Variable(tf.constant(0.1, shape=[self.hidden_size]))
        self.tf_layer_in = tf.tanh(tf.matmul(self.tf_input, self.tf_var_wi) + self.tf_var_bi)
        self.tf_hidden = self.tf_layer_in
        for _ in range(num_layers-1):
            self.tf_hidden = self._create_hidden_layer(self.tf_hidden)
        self.tf_var_wo = tf.Variable(tf.truncated_normal([self.hidden_size, COMMAND_VECTOR_SIZE], stddev=0.1))
        self.tf_var_bo = tf.Variable(tf.constant(0.1, shape=[COMMAND_VECTOR_SIZE]))
        self.tf_layer_out = tf.tanh(tf.matmul(self.tf_hidden, self.tf_var_wo) + self.tf_var_bo)
        self.tf_model = self.tf_layer_out
        # -- init loss and optimizer
        self.tf_truth = tf.placeholder(tf.float32, [None, COMMAND_VECTOR_SIZE])
        self.tf_loss = tf.reduce_mean(tf.squared_difference(self.tf_model, self.tf_truth))
        self.tf_train_step = tf.train.AdagradOptimizer(self.learning_rate).minimize(self.tf_loss)
        # -- init session
        self.tf_session = tf_session if tf_session else tf.Session()
        self.tf_session.run(tf.global_variables_initializer())
        if self.verbose: print("initialised Multi-Layer Perceptron with", self.num_layers, "hidden layers")

    def _create_hidden_layer(self, input_layer):
        tf_var_w = tf.Variable(tf.truncated_normal([self.hidden_size, self.hidden_size], stddev=0.1))
        tf_var_b = tf.Variable(tf.constant(0.1, shape=[self.hidden_size]))
        tf_layer = tf.tanh(tf.matmul(input_layer, tf_var_w) + tf_var_b)
        return tf_layer

    def train(self, train_in, train_out, batch_size=400):
        '''
        Train the MLP on given data
        '''
        if self.verbose: print("training Multi-Layer Perceptron...")
        self.seek = 0
        cur_loss = 42. # init loss
        for train_i in range(self.iterations):
            if self.verbose:
                sys.stdout.write('\riteration: %d of %d (%f loss)' % (train_i+1, self.iterations, cur_loss))
                if train_i%1000 == 0: cur_loss = self.tf_session.run(self.tf_loss, feed_dict={self.tf_input: train_in, self.tf_truth: train_out})
                sys.stdout.flush()
            # create batch
            cur_train_in, cur_train_out = self._create_next_batch(train_in, train_out, batch_size)
            # run training step
            self.tf_session.run(self.tf_train_step, feed_dict={self.tf_input: cur_train_in, self.tf_truth: cur_train_out})
        if self.verbose: sys.stdout.write('\rtraining complete (%d iterations, %f loss)'%(self.iterations, cur_loss) + (' ' * len(str(self.iterations)) + '\n'))

    def predict(self, pred_in):
        if self.verbose: print("predicting classes...")
        res = self.tf_session.run(self.tf_model, feed_dict={self.tf_input: pred_in})
        return res

    def take_wheel(self, state):
        return self.predict([state])[0]

