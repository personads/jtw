#! /usr/bin/env python3

from pytocl.main import main
from drivers.mlp import MLPDriver

if __name__ == '__main__':
    main(MLPDriver())
