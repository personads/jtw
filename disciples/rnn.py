'''
    Recurrent Neural Network (class)
'''
import sys

import tensorflow as tf

from config import *
from disciples.tf_disciple import TensorFlowDisciple

class RecurrentNeuralNetwork(TensorFlowDisciple):
    '''
    Recurrent Neural Network based classifier
    '''

    def __init__(self, iterations=200000, hidden_size=100, layer_count=3, dropout_prob=0.5, learning_rate=0.1, tf_session=None, verbose=False):
        '''
        Constructor of RecurrentNeuralNetwork
        '''
        # init tensorflow classifier
        TensorFlowDisciple.__init__(self, iterations, tf_session, verbose)
        # init tensorflow variables
        # -- init model
        self.hidden_size = hidden_size
        self.layer_count = layer_count
        self.dropout_prob = dropout_prob
        self.learning_rate = learning_rate
        # --- construct model
        self.tf_input = tf.placeholder(tf.float32, [None, 1, STATE_VECTOR_SIZE])
        # --- define multi-layer rnn with gru and dropout
        self.tf_rnn_cell = tf.contrib.rnn.GRUCell(num_units=self.hidden_size)
        self.tf_rnn_dropout = tf.contrib.rnn.DropoutWrapper(self.tf_rnn_cell, output_keep_prob=self.dropout_prob)
        self.tf_rnn = tf.contrib.rnn.MultiRNNCell([self.tf_rnn_cell] * self.layer_count)
        self.tf_rnn_out, self.tf_rnn_state = tf.nn.dynamic_rnn(
            self.tf_rnn_cell,
            self.tf_input,
            dtype=tf.float32,
            sequence_length=self._get_seq_len(self.tf_input)
        )
        self.tf_rnn_out = self.tf_rnn_out[:,0,:]
        # --- output layer
        self.tf_var_wa = tf.Variable(tf.truncated_normal([self.hidden_size, 1], stddev=0.1))
        self.tf_var_ba = tf.Variable(tf.constant(0.1, shape=[1]))
        self.tf_var_acc = tf.sigmoid(tf.matmul(self.tf_rnn_out, self.tf_var_wa) + self.tf_var_ba)
        self.tf_var_wb = tf.Variable(tf.truncated_normal([self.hidden_size, 1], stddev=0.1))
        self.tf_var_bb = tf.Variable(tf.constant(0.1, shape=[1]))
        self.tf_var_brake = tf.sigmoid(tf.matmul(self.tf_rnn_out, self.tf_var_wb) + self.tf_var_bb)
        self.tf_var_ws = tf.Variable(tf.truncated_normal([self.hidden_size, 1], stddev=0.1))
        self.tf_var_bs = tf.Variable(tf.constant(0.1, shape=[1]))
        self.tf_var_steer = tf.tanh(tf.matmul(self.tf_rnn_out, self.tf_var_ws) + self.tf_var_bs)
        self.tf_model = tf.concat([self.tf_var_acc, self.tf_var_brake, self.tf_var_steer], axis=1)
        # -- init loss and optimizer
        self.tf_truth = tf.placeholder(tf.float32, [None, COMMAND_VECTOR_SIZE])
        self.tf_loss = tf.reduce_mean(tf.squared_difference(self.tf_model, self.tf_truth))
        self.tf_train_step = tf.train.AdagradOptimizer(self.learning_rate).minimize(self.tf_loss)
        # -- init session
        self.tf_session = tf_session if tf_session else tf.Session()
        self.tf_session.run(tf.global_variables_initializer())

    def _get_seq_len(self, sequence):
        res = tf.ones([tf.shape(sequence)[0]])
        return tf.cast(res, tf.int32)

    def _convert_to_sequences(self, data):
        res = []
        for point in data:
            res.append([point])
        return res

    def train(self, train_in, train_out, batch_size=400):
        '''
        Train the MLP on given data
        '''
        if self.verbose: print("training Recurrent Neural Network...")
        train_in = self._convert_to_sequences(train_in)
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
        pred_in = self._convert_to_sequences(pred_in)
        res = self.tf_session.run(self.tf_model, feed_dict={self.tf_input: pred_in})
        return res

    def take_wheel(self, state):
        return self.predict([state])[0]

