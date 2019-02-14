from django.http import *
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

import app.utils as utils
from app.converter import mc_osu
from app.models import ConvModel


# Create your views here.

# api/upload: post
# (map: file) -> {
#     code: 1/0,
#     msg: id/error
# }
@require_http_methods(["POST"])
def convert_map(request):
    response = {}
    conv = ConvModel()
    try:
        obj = request.FILES.get("map")
        in_suffix = obj.name.split(".")[-1]
        name = obj.name.split(".")[0]
        # get id
        conv.save()
        conv.in_file = name + "." + in_suffix
        in_name = conv.get_absolute(conv.in_file)
        with open(in_name, 'wb') as f:
            for line in obj.chunks():
                f.write(line)
        if in_suffix == 'mc':
            out_suffix = "osu"
            conv.out_file = name + "." + out_suffix
            out_name = conv.get_absolute(conv.out_file)
            source = utils.read_file(in_name)
            # TODO: OD/HP/SV/VOL
            re = mc_osu.mc_osu_v14(source)
            if re[1]:
                utils.write_file(re[0], out_name)
            else:
                raise re[0]
            conv.result = True
        else:
            # TODO: osz
            raise Exception("谱面格式(%s)未被支持" % in_suffix)
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
    print(model)
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
