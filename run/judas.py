#! /usr/bin/env python3
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pytocl.main import main
from drivers.judas import Judas

if __name__ == '__main__':
    main(Judas())
