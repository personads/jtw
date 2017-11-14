def load_csv_file(path):
    res_states, res_commands = [], []
    with open(path, 'r') as fop:
        for line in fop:
            line_parts = [float(part.replace('"', '')) for part in line.strip().split(',')]
            res_states.append(line_parts[:-5])
            res_commands.append(line_parts[-5:])
    return res_states, res_commands

def load_csv_file_dirty(path):
    res_states, res_commands = [], []
    with open(path, 'r') as fop:
        for line in fop:
            line_parts = [float(part.replace('"', '')) for part in line.strip().split(',')]

            ffilter = []
            for i in range(len(line_parts)-5):
                if i == 0 or i == 46 or i == 47 or  (i >= 49 and i <= 67) or i == 73:
                    ffilter.append(line_parts[i])
            res_states.append(ffilter)
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