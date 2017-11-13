from config import *
from utils.data import *

from disciples.mlp import MultiLayerPerceptron

if __name__ == '__main__':
    print("Testing MLP")
    train_states, train_commands = load_csv_file('resources/drive_data/full_data.csv')
    train_commands = apply_mask(train_commands, COMMAND_MASK)
    print("loaded", len(train_states), "data points.")
    mlp = MultiLayerPerceptron(iterations=100000, verbose=True)
    mlp.train(train_states, train_commands)
    prediction = mlp.predict([train_states[420]])
    print("prediction:", prediction, train_commands[420])
    mlp.save('mlp_driver_100k/')