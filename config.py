from collections import OrderedDict

from pytocl.car import State, Command

# properties in OrderedDict('name': length) format
COMMAND_PROPERTIES = OrderedDict([('accelerator', 1), ('brake', 1), ('gear', 1), ('steering', 1), ('focus', 1)])
STATE_PROPERTIES = OrderedDict([
    ('angle', 1),
    ('current_lap_time', 1),
    ('damage', 1),
    ('distance_from_start', 1),
    ('distance_raced', 1),
    ('fuel', 1),
    ('gear', 1),
    ('last_lap_time', 1),
    ('opponents', 36),
    ('race_position', 1),
    ('rpm', 1),
    ('speed_x', 1),
    ('speed_y', 1),
    ('speed_z', 1),
    ('distances_from_edge', 19),
    ('focused_distances_from_edge', 5),
    ('distance_from_center', 1),
    ('wheel_velocities', 4)
#    ('z', 1)
])
# names of properties to keep
COMMAND_MASK = ['accelerator', 'brake', 'steering']
STATE_MASK = [
    'angle',
    'speed_x',
    'speed_y',
    'speed_z',
    'distances_from_edge',
    'distance_from_center'
]
# length of input and output vectors
STATE_VECTOR_SIZE = sum([STATE_PROPERTIES[prop] for prop in STATE_MASK])
# COMMAND_VECTOR_SIZE = sum([COMMAND_PROPERTIES[prop] for prop in COMMAND_MASK])
COMMAND_VECTOR_SIZE = 2
