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

    def __init__(self, iterations=200000, hidden_size=100, learning_rate=0.1, tf_session=None, verbose=False):
        '''
        Constructor of MultiLayerPerceptronClassifier
        '''
        # init tensorflow classifier
        TensorFlowDisciple.__init__(self, iterations, tf_session, verbose)
        # init tensorflow variables
        # -- init model
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        self.tf_input = tf.placeholder(tf.float32, [None, STATE_VECTOR_SIZE])
        self.tf_var_w1 = tf.Variable(tf.truncated_normal([STATE_VECTOR_SIZE, self.hidden_size], stddev=0.1))
        self.tf_var_b1 = tf.Variable(tf.constant(0.1, shape=[self.hidden_size]))
        self.tf_layer1 = tf.sigmoid(tf.matmul(self.tf_input, self.tf_var_w1) + self.tf_var_b1)
        self.tf_var_w2 = tf.Variable(tf.truncated_normal([self.hidden_size, COMMAND_VECTOR_SIZE], stddev=0.1))
        self.tf_var_b2 = tf.Variable(tf.constant(0.1, shape=[COMMAND_VECTOR_SIZE]))
        self.tf_layer2 = tf.matmul(self.tf_layer1, self.tf_var_w2) + self.tf_var_b2
        self.tf_model = self.tf_layer2
        # -- init loss and optimizer
        self.tf_truth = tf.placeholder(tf.float32, [None, COMMAND_VECTOR_SIZE])
        self.tf_loss = tf.reduce_mean(tf.squared_difference(self.tf_model, self.tf_truth))
        self.tf_train_step = tf.train.AdagradOptimizer(self.learning_rate).minimize(self.tf_loss)
        # -- init session
        self.tf_session = tf_session if tf_session else tf.Session()
        self.tf_session.run(tf.global_variables_initializer())

    def train(self, train_in, train_out, batch_size=100):
        '''
        Train the MLP on given data

        The training data must be a list of dicts with each containing the feature keys and their values for one data point.
        E.g. [{'feature-0': value}]

        Keyword arguments:
            training_data (list): training data points
            batch_size (int): size of training data batches
        '''
        if self.verbose: print("training Multi-Layer Perceptron...")
        self.seek = 0
        cur_loss = 42.
        for train_i in range(self.iterations):
            if self.verbose:
                sys.stdout.write('\riteration: %d of %d (%f loss)' % (train_i+1, self.iterations, cur_loss))
                if train_i%500 == 0: cur_loss = self.tf_session.run(self.tf_loss, feed_dict={self.tf_input: train_in, self.tf_truth: train_out})
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
