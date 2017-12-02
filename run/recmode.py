#! /usr/bin/env python3

import sys, os, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pytocl.main import main
from drivers.recmode import rec_mode_driver

MODEL_PATH = 'resources/models/mlp/'

if __name__ == '__main__':
    main(rec_mode_driver(MODEL_PATH))

