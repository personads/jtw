#! /usr/bin/env python3
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pytocl.main import main
from drivers.manual import ManualDriver

if __name__ == '__main__':
    # get going
    main(ManualDriver())
