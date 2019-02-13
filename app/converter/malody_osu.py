import json
from django.template import loader


def mc_osu_v14(mc: str, od=8, hp=7, keep_sv=True) -> (str, bool):
    try:
        context = {}
        mc_json = json.loads(mc)
        gen_parse(mc_json, context)
        meta_parse(mc_json, context)
        diff_parse(od, hp, context)
        event_parse(mc_json, context)
        time_parse(mc_json, context, keep_sv)
        obj_parse(mc_json, context)

        return str(loader.render_to_string('osu_v14.osu', context)), True

    except Exception as e:
        return str(e), False


def gen_parse(mc: dict, context: dict):
    notes = mc['note']
    for i in range(len(notes) - 1, -1, -1):
        if 'sound' in notes[i]:
            context['audio'] = notes[i]['sound']
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


def diff_parse(od, hp, context: dict):
    context['OD'] = od
    context['HP'] = hp


def event_parse(mc: dict, context: dict):
    pass

def time_parse(mc: dict, context: dict, keep_sv):
    pass


def obj_parse(mc: dict, context: dict):
    pass
