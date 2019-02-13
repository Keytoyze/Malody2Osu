from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core import serializers
import requests
import json


# Create your views here.

@require_http_methods(["POST"])
def convert_map(request):
    response = {}
    render()
    try:
        response['msg'] = str(request.POST)#request.POST.get('s', 'null')
        response['error_num'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1
    return JsonResponse(response)
