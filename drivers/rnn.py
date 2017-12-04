from pytocl.driver import Driver
from pytocl.car import State, Command

from config import *
from utils.data import *
from disciples.rnn import RecurrentNeuralNetwork

class RNNDriver(Driver):

    def __init__(self, model_path, sequence_length=5, step=1):
        super().__init__()
        self.epoch = 0
        self.memory = [[0. for _ in range(STATE_VECTOR_SIZE)] for _ in range(sequence_length * step)]
        self.memory_step = step
        self.sequence_length = sequence_length
        self.jesus = RecurrentNeuralNetwork()
        self.jesus.restore(model_path)
        self.expected_gear = 0
        self.max_gear = 6

    def update_memory(self, state):
        for i in range(1, len(self.memory)):
            self.memory[i-1] = self.memory[i]
        self.memory[-1] = state

    def get_state_sequence(self):
        res = []
        for i in range(self.sequence_length):
            res.append(self.memory[-(i*self.memory_step+1)])
        return res

    def calc_gear(self, command, carstate):
        if carstate.rpm > 7000 and carstate.gear < self.max_gear:
            self.expected_gear = carstate.gear + 1

        if carstate.rpm < 3000 and carstate.gear != 0:
            self.expected_gear = carstate.gear - 1

        if carstate.gear != self.expected_gear:
            command.gear = self.expected_gear
            # print("attempting gear change from", carstate.gear, "to", self.expected_gear)
        if not command.gear:
            command.gear = carstate.gear or 1

    def drive(self, carstate: State) -> Command:
        command = Command()
        current_state = state_to_vector(carstate)
        self.update_memory(current_state)
        state_sequence = self.get_state_sequence()
        command_vector = self.jesus.take_wheel(state_sequence)
        command = vector_to_command(command_vector)
        self.calc_gear(command, carstate)
        if self.epoch%100 == 0:
            print(carstate.race_position)
        self.epoch += 1
        return command
