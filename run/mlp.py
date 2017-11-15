#! /usr/bin/env python3

import sys, os, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pytocl.main import main
from drivers.mlp import MLPDriver

if __name__ == '__main__':
    # argument parsing
    arg_parser = argparse.ArgumentParser(description='Jesus Take the Wheel (MLP)')
    arg_parser.add_argument('model_path', help='path to model folder')
    args = arg_parser.parse_args()
    # get going
    main(MLPDriver(args.model_path))
