from pytocl.driver import Driver
from pytocl.car import State, Command
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class SteeringNN(nn.Module):
    def __init__(self, sensors, first):
        super().__init__()
        self.linear1 = nn.Linear(sensors,first)
        #self.linear2 = nn.Linear(first,second)
        self.optimizer = optim.SGD(self.parameters(), lr=0.01)

    def forward(self, x):
        x = self.linear1(x)

    def update(self, true, calc):
        loss = nn.MSELoss()
        output = loss(true,calc)
        output.backward()
        self.optimizer.step()

    def save(self):
        self.save_state_dict('mytraining.pt')





class MyDriver(Driver):
    # Override the `drive` method to create your own driver

    def __init__(self):
        super().__init__()
        self.epochCounter = 0
        self.model = SteeringNN(19,1)

    def drive(self, carstate: State) -> Command:
        # Interesting stuff
        command = Command()
        if carstate.speed_x < 15 :
            command.accelerator = 1.0

        command.gear = self.calcGear(command,carstate)
        self.epochCounter +=1





        #if self.epochCounter % 100 == 0:





        return command




    def calcGear(self, command, carstate: State):
        if carstate.rpm > 8000 and command.accelerator > 0:
            return carstate.gear + 1
        if carstate.rpm < 2500 and command.accelerator == 0:
            return carstate.gear - 1
        return carstate.gear
    