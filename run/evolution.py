from neat_parts.net import load_net, save_net, compute_sigma, Net
import subprocess
import pickle
import numpy as np
import random
import math


class Specie(object):
    """
    Class representing node in neural network

    Attributes:
        number (int): Human readable string describing the exception.
        layer (str): Layer to which node belongs to (inp, hid, out).
        value (float): Activation accumulated in the Node.
        history (float): Last value (if history_enabled set to True else 0).
        history_enabled (bool): Enable remembering last value of Node (for RNN).
        activation_function(lambda function): Function which applies activation to self.value when activation
        is called.
    """

    def __init__(self, alpha: Net):
        self.alpha = alpha
        self.individuals = []
        self.total_fitness = 0
        self.individuals.append(self.alpha)

    def evaluate(self):
        self.alpha = None
        for i in self.individuals:
            save_net(i, "/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/resources/neat_population_better_than_100/eval")
            subprocess.call("/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/train.sh")
            i.fitness = pickle.load(open("/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/resources/neat_population_better_than_100/result", "rb"))
            i.fitness /= len(self.individuals)
            self.total_fitness += i.fitness
            if self.alpha is None or self.alpha.fitness < i.fitness:
                self.alpha = i

    def add_individual(self, n: Net):
        self.individuals.append(n)

    def new_generation(self):
        if len(self.individuals) == 1:
            self.alpha = self.individuals[0]
        if len(self.individuals) >= 2 and len(self.individuals) < 5:
            self.alpha = self.individuals[np.random.randint(0, len(self.individuals))]
        if len(self.individuals) >= 5:
            self.alpha = self.individuals[np.random.randint(1, len(self.individuals))]
        self.individuals = [self.alpha]

    def kill_worst_part(self, part=0.05):
        sorter = [(x.fitness, x) for x in self.individuals]
        sorter.sort(key=lambda x: x[0])
        new_length = int(math.floor((1-part) * len(self.individuals)))
        if new_length == 0:
            new_length = 1
        self.individuals = [sorter[i][1] for i in range(new_length)]



class Evolution(object):
    """
    Class representing node in neural network

    Attributes:
        number (int): Human readable string describing the exception.
        layer (str): Layer to which node belongs to (inp, hid, out).
        value (float): Activation accumulated in the Node.
        history (float): Last value (if history_enabled set to True else 0).
        history_enabled (bool): Enable remembering last value of Node (for RNN).
        activation_function(lambda function): Function which applies activation to self.value when activation
        is called.
    """
    def __init__(self, nets, innovation_global, threshold=3.0):
        self.species_list = []
        self.innovation_global = innovation_global
        self.population_size = len(nets)
        self.threshold = threshold
        self.generation = 0
        self.best = []

        for n in nets:
            spec_pos = 0
            found = False
            while spec_pos < len(self.species_list):
                s: Specie = self.species_list[spec_pos]
                if compute_sigma(n, s.alpha) < threshold:
                    s.add_individual(n)
                    found = True
                    break
                else:
                    spec_pos += 1
            if not found:
                self.species_list.append(Specie(n))

    def generation_step(self):
        best_net: Net = None
        best_net_val = 0
        new_nets = []

        offspring_counts = np.zeros(len(self.species_list))
        total_fit = 0.1
        for specie in self.species_list:
            specie.evaluate()
            total_fit += specie.total_fitness
            specie.kill_worst_part()

        s = 0
        if len(offspring_counts) == 1:
            offspring_counts[0] = self.population_size
        else:
            for i in range(len(offspring_counts)):
                if i != len(offspring_counts)-1:
                    offspring_counts[i] = int(self.species_list[i].total_fitness / total_fit * self.population_size)
                    if offspring_counts[i] == 0:
                        offspring_counts[i] += 1
                    s += offspring_counts[i]
                else:
                    offspring_counts[i] = self.population_size - s

        for i in range(len(self.species_list)):
            specie = self.species_list[i]
            if specie.alpha.fitness * len(specie.individuals) > best_net_val:
                best_net = specie.alpha
                best_net_val = specie.alpha.fitness * len(specie.individuals)
            if len(specie.individuals) >= 5 and offspring_counts[i] > 0:
                new_nets.append(specie.alpha)
                offspring_counts[i] -= 1

            for j in range(int(offspring_counts[i]) - 1):
                if j < 0.75*(offspring_counts[i] + 1) and len(specie.individuals) >= 2:
                    pair = random.sample(range(len(specie.individuals)), 2)
                    new_net: Net = specie.individuals[pair[0]] + specie.individuals[pair[1]]
                else:
                    if len(specie.individuals) > 2:
                        new_net: Net = specie.individuals[np.random.randint(1, len(specie.individuals))]
                    else:
                        new_net: Net = specie.individuals[0]
                if np.random.rand() < 0.8:
                    new_net.mutation_weights()
                if np.random.rand() < 0.05:
                    new_net.mutation_add_node(self.innovation_global, self.innovation_global+1)
                    self.innovation_global += 2
                if np.random.rand() < 0.3:
                    new_net.mutation_add_edge(self.innovation_global)
                    self.innovation_global += 1
                new_nets.append(new_net)
            specie.new_generation()

        for n in new_nets:
            spec_pos = 0
            found = False
            while spec_pos < len(self.species_list):
                s: Specie = self.species_list[spec_pos]
                if compute_sigma(n, s.alpha) < self.threshold:
                    s.add_individual(n)
                    found = True
                    break
                else:
                    spec_pos += 1
            if not found:
                self.species_list.append(Specie(n))
        save_net(best_net,
                 "/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/resources/best_nets/gen"
                 + str(self.generation))
        self.best.append(best_net_val)
        self.generation += 1
        np.savetxt("generations.txt", np.array(self.best))


if __name__ == '__main__':
    nets = []
    for i in range(500):
        net = load_net("/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/resources/neat_population_better_than_100/net" + str(i))
        nets.append(net)
    evol = Evolution(nets, 46, 4.0)
    for i in range(1000):
        evol.generation_step()
        print(len(evol.species_list))



