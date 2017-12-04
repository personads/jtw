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

    def __init__(self, iterations=200000, hidden_size=100, layer_count=3, dropout_prob=0.0, sequence_length=5, learning_rate=0.1, tf_session=None, verbose=False):
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
        self.sequence_length = sequence_length
        self.learning_rate = learning_rate
        # --- construct model
        self.tf_input = tf.placeholder(tf.float32, [None, self.sequence_length, STATE_VECTOR_SIZE])
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
        # self.tf_rnn_out = self._get_seq_last(self.tf_rnn_out, self._get_seq_len(self.tf_input))
        self.tf_rnn_out = self._get_seq_last(self.tf_rnn_out)
        # --- output layer
        self.tf_var_w2 = tf.Variable(tf.truncated_normal([self.hidden_size, COMMAND_VECTOR_SIZE], stddev=0.1))
        self.tf_var_b2 = tf.Variable(tf.constant(0.1, shape=[COMMAND_VECTOR_SIZE]))
        self.tf_layer2 = tf.tanh(tf.matmul(self.tf_rnn_out, self.tf_var_w2) + self.tf_var_b2)
        self.tf_model = self.tf_layer2
        # -- init loss and optimizer
        self.tf_truth = tf.placeholder(tf.float32, [None, COMMAND_VECTOR_SIZE])
        self.tf_loss = tf.reduce_mean(tf.squared_difference(self.tf_model, self.tf_truth))
        self.tf_train_step = tf.train.AdagradOptimizer(self.learning_rate).minimize(self.tf_loss)
        # -- init session
        self.tf_session = tf_session if tf_session else tf.Session()
        self.tf_session.run(tf.global_variables_initializer())

    # def _get_seq_len(self, sequence):
    #     seq_binary = tf.sign(tf.reduce_max(tf.abs(sequence), axis=2)) # 1 if content, 0 if padding
    #     res = tf.reduce_sum(seq_binary, axis=1) # sum length of content
    #     return tf.cast(res, tf.int32)

    # def _get_seq_last(self, output, lengths):
    #     res = None
    #     batch_size = tf.shape(output)[0]
    #     indices = tf.range(0, batch_size) * self.sequence_length + (lengths - 1) # determine cutoff indices
    #     states = tf.reshape(output, [-1, self.hidden_size]) # flatten to sequence
    #     res = tf.gather(states, indices)
    #     return res

    def _get_seq_len(self, sequence):
        res = tf.fill([tf.shape(sequence)[0]], self.sequence_length)
        return res

    def _get_seq_last(self, output):
        return output[:,self.sequence_length-1,:]

    def train(self, train_in, train_out, batch_size=2000):
        '''
        Train the RNN on given data
        '''
        if self.verbose: print("training Recurrent Neural Network...")
        self.seek = 0
        cur_loss = 42. # init loss
        for train_i in range(self.iterations):
            if self.verbose:
                sys.stdout.write('\riteration: %d of %d (%f loss)' % (train_i+1, self.iterations, cur_loss))
                if train_i%10000 == 9999: cur_loss = self.tf_session.run(self.tf_loss, feed_dict={self.tf_input: train_in, self.tf_truth: train_out})
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

