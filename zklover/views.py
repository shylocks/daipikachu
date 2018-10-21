from django.shortcuts import *
from django.http import JsonResponse
import urllib3
import datetime
import imageio
from skimage import io
from skimage.transform import resize
from . import models
import re


# Create your views here.


def getGifData(request):
    d_datetime = request.GET.get("d_datetime")
    if not d_datetime:
        d_datetime = datetime.datetime.now().strftime('%Y%m%d')
    quality = request.GET.get("quality")
    if not quality:
        quality = 2
    datacode = request.GET.get("datacode")
    if not datacode.find("FY2G") == -1:
        r = fy2g(datacode, d_datetime)
        img_dict_list = r['data']
    elif not datacode.find("FY4A") == -1:
        r = fy4a(datacode, d_datetime)
        img_dict_list = r['data']
    elif not datacode.find('nmc') == -1:
        nmc_code = datacode.split("_")
        r = nmc(nmc_code[1], nmc_code[2], d_datetime)
        img_dict_list = r['data']
    else:
        url = "http://data.cma.cn/weatherGis/web/bmd/VisDataDef/getVisData?d_datetime=" + d_datetime + "&datacode=" + datacode
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        img_dict_list = eval(r.data)['data']
    if not len(img_dict_list) == 0:
        frames = []
        tmp = io.imread(img_dict_list[0]['fileURL']).shape
        shape = (int(tmp[0] / int(quality)), int(tmp[1] / int(quality)))
        for img_dict in img_dict_list:
            frames.append(resize(io.imread(img_dict['fileURL']), shape))
        imageio.mimsave("1.gif", frames, 'GIF', duration=0.5)
        return HttpResponse(open("1.gif", "rb").read(), content_type="image/gif")
    return HttpResponse("error")


def getItemData(request):
    name = request.GET.get("name")
    item_list = models.Items.objects.filter(grandfathername=name).all()
    data = {"status": 1, "data": []}
    for item in item_list:
        print(type(item.fathername), item.fathername)
        data["data"].append({"fathername": item.fathername, "name": item.name, "datacode": item.datacode})
    return JsonResponse(data)


def getVisData(request):
    d_datetime = request.GET.get("d_datetime")
    if not d_datetime:
        d_datetime = datetime.datetime.now().strftime('%Y%m%d')
    datacode = request.GET.get("datacode")
    if not datacode.find("FY2G") == -1:
        return JsonResponse(fy2g(datacode, d_datetime))
    if not datacode.find("FY4A") == -1:
        return JsonResponse(fy4a(datacode, d_datetime))
    if not datacode.find("nmc") == -1:
        nmc_code = datacode.split("_")
        return JsonResponse(nmc(nmc_code[1], nmc_code[2], d_datetime))
    url = "http://data.cma.cn/weatherGis/web/bmd/VisDataDef/getVisData?d_datetime=" + d_datetime + "&datacode=" + datacode
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    return JsonResponse(eval(r.data))


def fy2g(datacode, d_datetime):
    url = "http://www.nsmc.org.cn/NSMC/datalist/fy2g/fy2g_lan.txt"
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    image_path_list = bytes.decode(r.data).split(",\r\n")
    data = {'maxdate': datetime.datetime.now().strftime('%Y%m%d'), "data": []}
    for id, t in enumerate(image_path_list):
        if not t.find(datacode + d_datetime) == -1:
            data["data"].append({"id": id, "fileURL": "http://img.nsmc.org.cn/CLOUDIMAGE/FY2G/lan/" + t,
                                 "v_SHIJIAN": d_datetime + t[26:30] + "00",
                                 "c_IYMDHMS": d_datetime + t[26:30] + "00"})
    return data


def fy4a(datacode, d_datetime):
    target = models.Fy4h.objects.filter(imagename=datacode).first()
    url = "http://fy4.nsmc.org.cn/nsmc/v1/nsmc/image/animation/datatime/filesys?dataCode=" + target.imagename + \
          "&hourRange=" + target.maxlevel
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    ds_list = eval(r.data.decode())['ds']
    data = {'maxdate': datetime.datetime.now().strftime('%Y%m%d'), "data": []}
    for id, ds in enumerate(ds_list):
        r = http.request('GET',
                         target.serviceurl + "&DATE=" + ds['dataDate'] + "&TIME=" + ds['dataTime'] + "&&ENDTIME=" + ds[
                             'endTime'] + "&", redirect=False)
        data["data"].append({"id": id, "fileURL": r.get_redirect_location(),
                             "v_SHIJIAN": d_datetime + ds['dataTime'],
                             "c_IYMDHMS": d_datetime + ds['dataTime']})
    return data


def nmc(nmc_code, datacode, d_datetime):
    url = "http://www.nmc.cn/publish/" + nmc_code + "/" + datacode + ".html"
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    html = r.data.decode()
    pat = re.compile('img_path:\'(.*?)\',html_path', re.S)
    ds_list = pat.findall(html)
    data = {'maxdate': datetime.datetime.now().strftime('%Y%m%d'), "data": []}
    for id, ds in enumerate(ds_list):
        data["data"].append({"id": id, "fileURL": "http://image.nmc.cn" + ds[0:91],
                             "v_SHIJIAN": d_datetime + ds[78:82],
                             "c_IYMDHMS": d_datetime + ds[78:82]})
    return data
