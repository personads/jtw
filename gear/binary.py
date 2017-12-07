import numpy as np
import subprocess


GEAR_DIR = "../resources/gear"

def binary():
    population = np.array([4500, 10000, 10000, 10000, 10000])

    high = 9000
    low = 3000
    low_fitness = 0
    high_fitness = 0

    population[0] = low
    np.save(GEAR_DIR + "/active", population)
    subprocess.call("/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/train.sh")
    with open(GEAR_DIR + '/result.txt') as f:
        for line in f:
            low_fitness = float(line)

    population[0] = high
    np.save(GEAR_DIR + "/active", population)
    subprocess.call("/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/train.sh")
    with open(GEAR_DIR + '/result.txt') as f:
        for line in f:
            high_fitness = float(line)

    while high != low:
        population[0] = (high + low) / 2
        np.save(GEAR_DIR + "/active", population)
        subprocess.call("/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/train.sh")
        result = 0
        with open(GEAR_DIR + '/result.txt') as f:
            for line in f:
                result = float(line)
        print(high, low, (high + low) / 2, result)
        if result > low_fitness:
            low_fitness = result
            low = (high + low) / 2
        else:
            high_fitness = result
            high = (high + low) / 2

def all():
    population = np.array([6350, 9050, 9200, 9350, 9400])
    high_val = 0
    high = 0
    for i in range(100):
        population[4] = 5000 + 50*i
        np.save(GEAR_DIR + "/active", population)
        subprocess.call("/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/train.sh")
        with open(GEAR_DIR + '/result.txt') as f:
            for line in f:
                var = float(line)

        if var > high_val:
            high_val = var
            high = population[4]
            print(high_val, high)
    print(high_val, high)

if __name__ == '__main__':
    all()
