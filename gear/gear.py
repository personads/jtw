import numpy as np
import subprocess


POPULATION_SIZE = 100
GEAR_DIR = "../resources/gear"
GENERATIONS = 200


def create_population(size=100):
    pop = []
    for i in range(size):
        pop.append(np.random.randint(10000, size=5))
    return np.array(pop)


def save_vec(id, vec):
    np.save(GEAR_DIR + "/" + str(id), vec)


def save_population(population):
    for i in range(len(population)):
        save_vec(i, population[i])


def test_population(population):
    result = []
    for i in range(len(population)):
        print("For Max:", i)
        np.save(GEAR_DIR + "/active", population[i])
        subprocess.call("/home/kuro/Projects/ComputationalIntelligence/torcs-client/JesusTakeTheWheel/train.sh")
        with open(GEAR_DIR + '/result.txt') as f:
            for line in f:
                result.append(float(line))
    return np.array(result)


def recombination(vec1, vec2, fitness1, fitness2):
    vec3 = np.array(vec1)
    vec4 = np.array(vec1)
    prob = fitness1 / (fitness1 + fitness2)

    for i in range(len(vec1)):
        res1 = 0
        res2 = 0
        for j in range(14):
            a1 = np.random.uniform()
            a2 = np.random.uniform()

            if a1 < prob:
                bit = vec1[i] & (1 << j)
                res1 = res1 | bit
            else:
                bit = vec2[i] & (1 << j)
                res1 = res1 | bit

            if a2 < prob:
                bit = vec1[i] & (1 << j)
                res2 = res2 | bit
            else:
                bit = vec2[i] & (1 << j)
                res2 = res2 | bit
        vec3[i] = res1
        vec4[i] = res2
    return vec3, vec4


def recombination2(vec1, vec2):
    vec3 = np.array(vec1)
    vec4 = np.array(vec1)
    for i in range(len(vec1)):
        boundary = np.random.randint(13)
        a1 = vec1[i] % (2 ** (boundary+1))
        a2 = vec1[i] - (vec1[i] % (2 ** (boundary+1)))
        b1 = vec2[i] % (2 ** (boundary+1))
        b2 = vec2[i] - (vec2[i] % (2 ** (boundary + 1)))
        vec3[i] = a1 + b2
        vec4[i] = b1 + a2
    return vec3, vec4


def mutation_double(vec1, mutation_prob=0.2, span=300):
    for i in range(len(vec1)):
        add = np.random.uniform(-span, span)
        vec1[i] += add if vec1[i] + add > 0 and vec1[i] + add < 10000 else -add

def recombination_double(vec1, vec2):
    split = np.random.randint(0, len(vec1)-1)
    vec3 = np.concatenate((vec1[:split+1], vec2[split+1:]), axis=0)
    vec4 = np.concatenate((vec2[:split + 1], vec1[split + 1:]), axis=0)
    return vec3, vec4


def mutation(vec1, mutation_prob=0.1):
    for i in range(len(vec1)):
        num = vec1[i]
        for j in range(14):
            a = np.random.rand()
            if a <= mutation_prob:
                num = num ^ (1 << j)
        vec1[i] = num


def get_parents(population, fitness, parents=POPULATION_SIZE*0.2):
    total = np.sum(fitness)
    probs = fitness/total
    total = 1.0
    result = set()
    for par in range(int(parents)):
        val = np.random.uniform(0, total)
        cumulative = 0
        new_parent = None
        index = 0
        while True:
            if index in result:
                index += 1
                continue
            if cumulative + probs[index] >= val:
                new_parent = index
                total -= probs[index]
                break
            else:
                cumulative += probs[index]
                index += 1
        result.add(new_parent)
    return result


def survival(population, fitness, size=100):
    a = fitness.argsort()
    res = fitness[a]
    pop = population[a]
    res = res[::-1]
    pop = pop[::-1]
    res = res[:size]
    pop = pop[:size]
    return pop, res


if __name__ == '__main__':
    #Global values
    best_indiv = None
    best_value = 0
    best_values = []

    #Init
    population = create_population(POPULATION_SIZE)
    fitness = test_population(population)

    for gen in range(GENERATIONS):
        parents = get_parents(population, fitness)
        parents = list(parents)
        for i in range(0, len(parents), 2):
            child1, child2 = recombination_double(population[parents[i]], population[parents[i+1]])
            population = np.append(population, [child1, child2], axis=0)
        for i in range(len(population)):
            mutation_double(vec1=population[i], span=2000)
        fitness = test_population(population)
        population, fitness = survival(population, fitness, POPULATION_SIZE)

        best_values.append(fitness[0])
        np.savetxt("evolution.txt", best_values)

        np.savetxt("population.txt", population)
        np.savetxt("fitness.txt", fitness)
        if fitness[0] > best_value:
            best_value = fitness[0]
            best_indiv = population[0]
            f = open("bestval.txt", 'w')
            f.write(str(best_value))
            f.close()

            np.savetxt("best_indiv.txt", best_indiv)
    # index = np.argmax(fitness)
    # print(population[index], fitness[index])

