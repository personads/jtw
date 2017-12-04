#! /usr/bin/env python3

import sys, os, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pytocl.main import main
from drivers.elm import ELMDriver

MODEL_PATH = 'resources/models/Link to elm_driver_reg/'

if __name__ == '__main__':
    main(ELMDriver(MODEL_PATH))
