from pytocl.driver import Driver
from pytocl.car import State, Command
import torch
import keyboard
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

        steering_intensity = 0.25

        command = Command()
        if keyboard.is_pressed("w"):
            command.accelerator = 1
        if keyboard.is_pressed("s"):
            command.brake = 1
        if keyboard.is_pressed("a"):
            command.steering = steering_intensity
        if keyboard.is_pressed("d"):
            command.steering = -steering_intensity


        self.epochCounter +=1

        acceleration = command.accelerator

        if acceleration > 0:
            if abs(carstate.distance_from_center) >= 1:
                # off track, reduced grip:
                acceleration = min(0.4, acceleration)

            command.accelerator = min(acceleration, 1)

            if carstate.rpm > 8000:
                command.gear = carstate.gear + 1

        # else:
        #     command.brake = min(-acceleration,)

        if carstate.rpm < 2500 & carstate.gear != 0:
            command.gear = carstate.gear - 1

        if not command.gear:
            command.gear = carstate.gear or 1


        #if self.epochCounter % 100 == 0:





        return command




