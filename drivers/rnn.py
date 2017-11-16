from pytocl.driver import Driver
from pytocl.car import State, Command

from config import *
from utils.data import *
from disciples.rnn import RecurrentNeuralNetwork

class RNNDriver(Driver):

    def __init__(self, model_path, sequence_length=10, step=30):
        super().__init__()
        self.epoch = 0
        self.memory = [[0. for _ in range(STATE_VECTOR_SIZE)] for _ in range(sequence_length * step)]
        self.memory_step = step
        self.sequence_length = sequence_length
        self.jesus = RecurrentNeuralNetwork()
        self.jesus.restore(model_path)

    def update_memory(self, state):
        for i in range(1, len(memory)):
            self.memory[i-1] = self.memory[i]
        self.memory[-1] = state

    def get_state_sequence():
        res = []
        for i in range(self.sequence_length):
            res.append(self.memory[-(i*self.memory_step+1)])
        return res

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
        self.update_memory(carstate)
        state_sequence = self.get_state_sequence()
        command_vector = self.jesus.take_wheel(state_sequence)
        command = vector_to_command(command_vector)
        self.calc_gear(command, carstate)
        if self.epoch%100 == 0:
            print(command_vector)
        self.epoch += 1
        return command
