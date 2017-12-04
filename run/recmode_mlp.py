#! /usr/bin/env python3

import sys, os, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pytocl.main import main
from drivers.jesus import recmode_mlp

MODEL_PATH = 'resources/models/BEST_ONE_MLP/'

if __name__ == '__main__':
    main(recmode_mlp(MODEL_PATH))