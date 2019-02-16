import json
import bisect
from app.utils import Comparable
from app import utils
from django.template import loader


class BpmStamp(Comparable):

    def __init__(self, time, bpm, beat):
        Comparable.__init__(self, beat)
        self.bpm = bpm
        self.time = time

    def translate(self, context):
        return ",".join(list(map(lambda x: str(int(x)), [
            0 if self.time == 0 else self.time - context['offset'],
            60000 / self.bpm, 4, 2, 1, context['vol'], 1, 0])))


class NoteStamp(Comparable):

    def __init__(self, beat, end, bpm_list, column):
        Comparable.__init__(self, beat)
        self.beat = beat
        self.end = end
        self.time = beat2time_context(beat, bpm_list)
        if end is not None:
            self.endtime = beat2time_context(end, bpm_list)
        self.column = column

    def translate(self, context):
        return ",".join(list(map(lambda x: str(int(x)), [
            (self.column * 2 + 1) * 64, 192, self.time - context['offset'],
            1 if self.end is None else 128, 0,
            0 if self.end is None else self.endtime - context['offset']
        ]))) + ":0:0:0:0:"


def mc_osu_v14(mc: str, od=8, hp=7, vol=70, keep_sv=True):
    try:
        context = {'OD': od, 'HP': hp, 'keep_sv': keep_sv, 'vol': vol}
        mc_json = json.loads(mc)
        gen_parse(mc_json, context)
        meta_parse(mc_json, context)
        time_parse(mc_json, context)
        obj_parse(mc_json, context)
        translate(context)
        return str(loader.render_to_string('osu_v14.osu', context)), True
    except Exception as e:
        return e, False

def fmc_osu_v14(in_file, out_file, od=8, hp=7, vol=70, keep_sv=True):
    source = utils.read_file(in_file)
    re = mc_osu_v14(source, od, hp, vol, keep_sv)
    if re[1]:
        utils.write_file(re[0], out_file)
    else:
        raise re[0]


def translate(context):
    bpm_list = context['bpm_list'] if context['keep_sv'] else context['bpm_list'][0]
    note_list = context['note_list']
    context['TP'] = "\n".join(list(map(lambda b: b.translate(context), bpm_list)))
    context['HO'] = "\n".join(list(map(lambda n: n.translate(context), note_list)))


def gen_parse(mc: dict, context: dict):
    notes = mc['note']
    for i in range(len(notes) - 1, -1, -1):
        if 'sound' in notes[i]:
            file = notes[i]['sound']
            suffix = file.rsplit(".", 1)[-1]
            name = file.rsplit(".", 1)[0]
            if suffix == 'ogg':
                file = name + ".mp3"
            context['audio'] = file
            context['offset'] = notes[i]['offset']
            break
    if 'audio' not in context:
        raise AttributeError('sound not found')


def meta_parse(mc: dict, context: dict):
    meta = mc['meta']
    context['title'] = meta['song']['title']
    context['artist'] = meta['song']['artist']
    context['creator'] = meta['creator']
    context['version'] = meta['version']
    context['column'] = meta['mode_ext']['column']
    context['bg'] = meta['background']


def time_parse(mc: dict, context: dict):
    bpm_list = []
    mc_time = sorted(mc['time'], key=lambda x: beat_parser(x['beat']))  # ensure order
    for i in range(0, len(mc_time)):
        t = mc_time[i]
        beat = beat_parser(t['beat'])
        bpm = t['bpm']
        if i == 0:
            bpm_list.append(BpmStamp(0, bpm, beat))
        else:
            time = beat2time(beat, bpm_list[-1])
            bpm_list.append(BpmStamp(time, bpm, beat))
    context['bpm_list'] = bpm_list


def obj_parse(mc: dict, context: dict):
    note_list = []
    bpm_list = context['bpm_list']
    mc_note = sorted(mc['note'], key=lambda x: beat_parser(x['beat']))  # ensure order
    for i in mc_note:
        if "column" not in i:
            continue
        beat = beat_parser(i['beat'])
        end = None if 'endbeat' not in i else beat_parser(i['endbeat'])
        column = i['column']
        note_list.append(NoteStamp(beat, end, bpm_list, column))
    context['note_list'] = note_list


def beat_parser(beat: list):
    return beat[0] + beat[1] / beat[2] + 1


def beat2time_context(beat: float, bpm_list):
    position = bisect.bisect_right(bpm_list, beat) - 1
    return beat2time(beat, bpm_list[position])


def beat2time(beat, last_stamp: BpmStamp):
    return (beat - last_stamp.value) * 60000 / last_stamp.bpm + last_stamp.time
