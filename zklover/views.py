from django.shortcuts import *
from django.http import JsonResponse
# Create your views here.


def api(request):
    print(request.GET.urlencode())
    return JsonResponse({"msg": "ok!"})
