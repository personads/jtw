from torch.autograd import Variable

COMMAND_PROPERTIES = ['accelerator', 'brake', 'gear', 'steering', 'focus']
STATE_PROPERTIES = [
    'angle',
    'current_lap_time',
    'damage',
    'distance_from_start',
    'distance_raced',
    'fuel',
    'gear',
    'last_lap_time',
    'opponents',
    'race_position',
    'rpm',
    'speed_x',
    'speed_y',
    'speed_z',
    'distances_from_edge',
    'distance_from_center',
    'wheel_velocities',
    'z',
    'focused_distances_from_edge'
]

def state_to_dict(state):
    res = {}
    for prop in STATE_PROPERTIES:
        res[prop] = eval('state.'+prop)
    return res

def dict_to_vector(dict_in, properties, requires_grad):
    res = []
    for prop in properties:
        if type(dict_in[prop]) is tuple:
            for val in dict_in[prop]:
                res.append(val)
        else:
            res.append(dict_in[prop])
    return Variable(res, required_grad=requires_grad)

def state_to_vector(state):
    return dict_to_vector(state_to_dict(state), STATE_PROPERTIES, False)
