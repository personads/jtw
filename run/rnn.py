#! /usr/bin/env python3

import sys, os, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pytocl.main import main
from drivers.rnn import RNNDriver

MODEL_PATH = 'resources/models/rnn/'

if __name__ == '__main__':
    main(RNNDriver(MODEL_PATH))
