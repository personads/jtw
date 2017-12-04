import sys, os, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pytocl.driver import Driver
from pytocl.car import State, Command

from config import *
from utils.data import *
from disciples.elm import ExtremeLearningMachine


class ELMDriver(Driver):

    def __init__(self, model_path):
        super().__init__()
        self.epoch = 0
        self.jesus = ExtremeLearningMachine()
        self.jesus.restore(model_path)

    def calc_gear(self, command, carstate):
        acceleration = command.accelerator
        if acceleration > 0:
            if carstate.rpm > 8000:
                command.gear = carstate.gear + 1
        if carstate.rpm < 2500 and carstate.gear != 0:
            command.gear = carstate.gear - 1
        if not command.gear:
            command.gear = carstate.gear or 1

    def drive(self, carstate: State) -> Command:
        command = Command()
        current_state = state_to_vector(carstate)
        command_vector = self.jesus.take_wheel(current_state)
        command = vector_to_command(command_vector)
        self.calc_gear(command, carstate)
        if self.epoch%100 == 0:
            print(command_vector)
        self.epoch += 1
        return command

if __name__ == '__main__':
    # argument parsing
    arg_parser = argparse.ArgumentParser(description='Training of Recurrent Neural Network')
    arg_parser.add_argument('input_path', help='path to data file (csv)')
    arg_parser.add_argument('output_path', help='path to model output folder')
    arg_parser.add_argument('--iterations', type=int, default=20000, help='number of training iterations (default: 20000)')
    args = arg_parser.parse_args()
    # training process
    print("Training Extreme Learning Machine...")
    train_states, train_commands = load_csv_file(args.input_path)
    train_states = apply_mask_to_vectors(train_states, STATE_PROPERTIES, STATE_MASK)
    train_commands = apply_mask_to_vectors(train_commands, COMMAND_PROPERTIES, COMMAND_MASK)
    print("loaded", len(train_states), "data points.")
    # initialize model
    print('initialize model')
    elm = ExtremeLearningMachine(iterations=args.iterations, verbose=True)
    print('Training')
    elm.train(train_states, train_commands)
    elm.save(args.output_path)