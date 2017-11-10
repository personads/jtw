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