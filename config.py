from pytocl.car import State, Command

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
#    'z',
    'focused_distances_from_edge'
]
COMMAND_MASK = [True, True, False, True, False]
COMMAND_MASKED_PROPERTIES = [COMMAND_PROPERTIES[i] for i in range(len(COMMAND_PROPERTIES)) if COMMAND_MASK[i]]
STATE_VECTOR_SIZE = 23
COMMAND_VECTOR_SIZE = COMMAND_MASK.count(True)
STATE_MASK = {
    'angle',
    'speed_x',
    'speed_y',
    'distances_from_edge',
    'distance_from_center',
}
def state_to_dict(state):
    res = {}
    for prop in STATE_PROPERTIES:
        if prop in STATE_MASK:
            res[prop] = eval('state.' + prop)
    return res

def dict_to_vector(dict_in, properties, requires_grad):
    res = []
    for prop in properties:
        if type(dict_in[prop]) is tuple:
            for val in dict_in[prop]:
                res.append(val)
        else:
            res.append(dict_in[prop])
    return res

def state_to_vector(state):
    return dict_to_vector(state_to_dict(state), STATE_MASK, False)

def vector_to_command(vector):
    res = Command()
    res.accelerator = vector[0] 
    res.brake = vector[1] 
    res.steering = vector[2] 
    return res
