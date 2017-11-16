#! /usr/bin/env python3

import sys, os, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pytocl.main import main
from drivers.mlp import MLPDriver

MODEL_PATH = '/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/resources/models/mlp/'

if __name__ == '__main__':
    main(MLPDriver(MODEL_PATH))
