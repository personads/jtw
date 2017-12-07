from __future__ import print_function
import sys, os, argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
from pytocl.main import main
from drivers.gear import GearDriver

if __name__ == '__main__':
    population = np.array([6350, 9050, 9200, 9350, 9400])
    downshift = np.array([5775, 6775, 7200, 7500, 7900])
    np.save("../resources/gear/active", population)
    main(GearDriver())