'''
    TensorFlow Disciple (superclass)
'''

import tensorflow as tf

class TensorFlowDisciple:
    '''
    Superclass for TensorFlow-based classifiers
    '''

    def __init__(self, iterations=10000, tf_session=None, verbose=False):
        # add session
        self.tf_session = tf_session
        # init other
        self.iterations = iterations
        self.seek = 0
        self.verbose = verbose

    def _create_next_batch(self, data, classes, batch_size):
        res_data = []
        res_classes = []
        seek_end = min(self.seek+batch_size, len(data)) # seek to next batch or end
        res_data, res_classes = data[self.seek:seek_end], classes[self.seek:seek_end]
        self.seek = seek_end if seek_end < len(data) else 0 # seek to last end or start
        if len(res_data) < batch_size: # check if batch was cutoff early
            res_data += data[:(batch_size-len(res_data))]
            res_classes += classes[:(batch_size-len(res_classes))]
            self.seek = batch_size-len(res_data) # seek to last end
        return res_data, res_classes

    def save(self, path):
        tf_saver = tf.train.Saver()
        tf_saver_out = tf_saver.save(self.tf_session, path)
        if self.verbose: print("saved model to '" + str(tf_saver_out) + "'")

    def restore(self, path):
        tf_saver = tf.train.Saver()
        tf_saver.restore(self.tf_session, path)
        if self.verbose: print("restored model from '" + str(path) + "'")

    def reset(self):
        tf.reset_default_graph()

    def close(self):
        self.tf_session.close()
