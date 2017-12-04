from __future__ import print_function
import sys, os, argparse
import os
import neat
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pytocl.main import main
from drivers.neat import NeatDriver

MODEL_PATH = '/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/resources/neat_population_better_than_100/eval'

if __name__ == '__main__':
    main(NeatDriver(MODEL_PATH))
