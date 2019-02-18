def gen_trans(line, context):
    line = transvalue(line, 'AudioFilename',
                      lambda x: x.replace(".ogg", ".mp3"))
    line = transvalue(line, 'PreviewTime',
                      lambda x: speed_rate(x, context))
    return line


def meta_trans(line, context):
    line = transvalue(line, 'Version',
                      lambda x: x + " x{}".format(round(context['speed'], 2)),
                      lambda x: context['speed'] != 1.0)
    line = transvalue(line, 'BeatmapID', lambda x: 0)
    line = transvalue(line, 'BeatmapSetID', lambda x: -1)
    return line


def diff_trans(line, context):
    line = transvalue(line, 'HPDrainRate',
                      lambda x: context['HP'],
                      lambda x: 'HP' in context)
    line = transvalue(line, 'OverallDifficulty',
                      lambda x: context['OD'],
                      lambda x: 'OD' in context)
    return line


def time_trans(line, context):
    elements = line.split(',')
    if not context['keep_sv'] and '_processed' in context:
        return None
    elements[0] = speed_rate(elements[0], context)
    if float(elements[1]) > 0:
        elements[1] = speed_rate(elements[1], context)
    context['_processed'] = True
    return ','.join(elements)


def obj_trans(line, context):
    elements = line.split(',')
    elements[2] = speed_rate(elements[2], context)
    if elements[3] == '128':
        slices = elements[5].split(":")
        slices[0] = speed_rate(slices[0], context)
        elements[5] = ":".join(slices)
    return ','.join(elements)


translations = {'General': gen_trans,
                'Metadata': meta_trans,
                'Difficulty': diff_trans,
                'TimingPoints': time_trans,
                'HitObjects': obj_trans}


def transvalue(line, key, func, con=None):
    if line.startswith(key + ":"):
        old = line.replace(key + ":", "").strip()
        if con is None or con(old):
            return key + ": " + str(func(old))
    return line


def speed_rate(x, context) -> str:
    return str(int(float(x) / context['speed']))


def fosu_v14(in_file, out_file, od=None, hp=None, vol=None, keep_sv=True, speed=1.0):
    fin = open(in_file, 'r')
    fout = open(out_file, 'w')
    field = None
    context = {'OD': od, 'HP': hp, 'keep_sv': keep_sv, 'vol': vol, 'speed': speed}

    while True:
        line = fin.readline()
        if not line:
            break
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            field = line[1:-1]
        elif line != '' and field in translations:
            line = translations[field](line, context)

        if line is not None:
            fout.write(line + '\n')
            if line.startswith('osu file'):
                fout.write('// Powered by Mania-Lab\n')

    fin.close()
    fout.close()
