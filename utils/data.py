from config import *

def load_csv_file(path):
    res_states, res_commands = [], []
    with open(path, 'r') as fop:
        for line in fop:
            line_parts = [float(part.replace('"', '')) for part in line.strip().split(',')]
            res_states.append(line_parts[:-5]) # append state information up to command
            res_commands.append(line_parts[-5:]) # append command information of length 5
    return res_states, res_commands

def state_to_dict(state, apply_mask=True):
    '''
    Returns dict with masked state properties
    '''
    res = {}
    for prop in STATE_PROPERTIES:
        if (prop not in STATE_MASK) and apply_mask:
            continue
        res[prop] = eval('state.' + prop)
    return res

def dict_to_vector(dict_in, properties):
    res = []
    for prop in properties:
        if type(dict_in[prop]) is tuple:
            for val in dict_in[prop]:
                res.append(val)
        else:
            res.append(dict_in[prop])
    return res

def state_to_vector(state, apply_mask=True):
    properties = STATE_MASK if apply_mask else STATE_PROPERTIES
    return dict_to_vector(state_to_dict(state, apply_mask), properties)

def vector_to_command(vector):
    res = Command()
    res.accelerator = vector[0] if vector[0] > 0. else 0.
    res.brake = -1. * vector[0] if vector[0] < 0. else 0.
    res.steering = vector[1] 
    return res

def condense_command_vector(vector):
    res = [0., 0.]
    res[0] = vector[0] - vector[1] # accelaration - brake
    res[1] = vector[2] # steering
    return res

def condense_command_vectors(vectors):
    return [condense_command_vector(v) for v in vectors]

def apply_mask_to_vectors(data, properties, mask):
    res = []
    for data_point in data:
        cur_res = []
        i = 0
        for prop in properties:
            if prop in mask:
                cur_res += data_point[i:i+properties[prop]]
            i += properties[prop]
        res.append(cur_res)
    return res

def states_to_sequences(states, sequence_length, step):
    res = []
    for i in range(len(states)):
        cur_res = [[0. for _ in range(STATE_VECTOR_SIZE)] for _ in range(sequence_length)]
        for j in range(sequence_length):
            if i - step*j < 0:
                break
            cur_res[-(j+1)] = states[i - step*j]
        res.append(cur_res)
    return res