import sys, os, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import *
from utils.data import *

from disciples.mlp import MultiLayerPerceptron

if __name__ == '__main__':
    # argument parsing
    arg_parser = argparse.ArgumentParser(description='Training of Multi-Layer Perceptron')
    arg_parser.add_argument('input_path', help='path to data file (csv)')
    arg_parser.add_argument('output_path', help='path to model output folder')
    arg_parser.add_argument('--iterations', type=int, default=200000, help='number of training iterations')
    args = arg_parser.parse_args()
    # training process
    print("Training Multi-Layer Perceptron...")
    train_states, train_commands = load_csv_file(args.input_path)
    train_states = apply_mask_to_vectors(train_states, STATE_PROPERTIES, STATE_MASK)
    train_commands = condense_command_vectors(apply_mask_to_vectors(train_commands, COMMAND_PROPERTIES, COMMAND_MASK))
    print("loaded", len(train_states), "data points.")
    # initialize model
    mlp = MultiLayerPerceptron(iterations=args.iterations, num_layers=2, verbose=True)
    mlp.train(train_states, train_commands)
    mlp.save(args.output_path)