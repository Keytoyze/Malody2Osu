from django.http import *
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from app.converter import mc_osu, osz, osu
from app.models import ConvModel


# Create your views here.

# api/upload: post
# {"map":file, "od"(0-10), "hp"(0-10), "sv"(on/none), "vol"(0-100), "speed"(0.5-2.0)}
# -> {
#     code: 1/0,
#     msg: id/error
# }
@require_http_methods(["POST"])
def convert_map(request):
    response = {}
    conv = ConvModel()
    try:
        obj = request.FILES.get("map")
        print(request.POST)
        in_suffix = obj.name.split(".")[-1]
        name = obj.name.split(".")[0]
        # get id
        conv.save()
        conv.in_file = name + "." + in_suffix
        in_name = conv.get_absolute(conv.in_file)

        od = request.POST.get('od')
        hp = request.POST.get('hp')
        sv = request.POST.get('sv') == 'on'
        vol = request.POST.get('vol')
        speed = float(request.POST.get('speed', 1.0))

        with open(in_name, 'wb') as f:
            for line in obj.chunks():
                f.write(line)

        if in_suffix == 'mc' or in_suffix == 'osu':
            out_suffix = "osu"
            conv.out_file = name + "." + out_suffix
            out_name = conv.get_absolute(conv.out_file)
            if in_suffix == 'mc':
                mc_osu.fmc_osu_v14(in_name, out_name, od=od, hp=hp, vol=vol, keep_sv=sv,
                                   speed=speed)
            else:
                osu.fosu_v14(in_name, out_name, od=od, hp=hp, vol=vol, keep_sv=sv, speed=speed)

        elif in_suffix == 'zip' or in_suffix == 'mcz' or in_suffix == 'osz':
            out_suffix = "osz"
            conv.out_file = name + "." + out_suffix
            out_name = conv.get_absolute(conv.out_file)
            osz.zip_osz_v14(in_name, out_name, od=od, hp=hp, vol=vol, keep_sv=sv, speed=speed)

        else:
            raise Exception("谱面格式(%s)未被支持" % in_suffix)

        conv.result = True
        conv.save()
        response['msg'] = conv.conv_id
        response['code'] = 1
    except Exception as e:
        conv.result = False
        conv.save()
        response['msg'] = str(e)
        response['code'] = 0
    return JsonResponse(response)


# api/download: get
# {id} -> {
# }
@require_http_methods(["GET"])
def download(request):
    conv_id = request.GET['id']
    model = ConvModel.objects.get(conv_id=conv_id)
    if model is None or model.result is None or not model.result:
        return HttpResponseForbidden()
    file = open(model.get_absolute(model.out_file), 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % model.out_file
    return response


@require_http_methods(["GET"])
def index(request):
    return render(request, "index.html")
