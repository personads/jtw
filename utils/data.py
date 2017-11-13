def load_csv_file(path):
    res_states, res_commands = [], []
    with open(path, 'r') as fop:
        for line in fop:
            line_parts = [float(part.replace('"', '')) for part in line.strip().split(',')]
            res_states.append(line_parts[:-5])
            res_commands.append(line_parts[-5:])
    return res_states, res_commands

def apply_mask(data, mask):
    res = []
    for d in data:
        cur_res = []
        for i in range(len(mask)):
            if mask[i]:
                cur_res.append(d[i])
        res.append(cur_res)
    return res