from django.shortcuts import *
from django.http import JsonResponse
import urllib3
import datetime
import imageio
from skimage import io
from skimage.transform import resize
from . import models
import re
import json
from . import weather


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
        nmc_code = datacode.split("*")
        r = nmc(nmc_code[1], nmc_code[2], d_datetime)
        img_dict_list = r['data']
    elif not datacode.find('DATUM') == -1:
        target = models.Datum.objects.filter(datacode=datacode).first()
        nmc_code = datacode.split("*")
        r = datum(nmc_code[1], nmc_code[2], nmc_code[3], int(target.type))
        img_dict_list = r['data']
    else:
        url = "http://data.cma.cn/weatherGis/web/bmd/VisDataDef/getVisData?d_datetime=" + d_datetime + "&datacode=" + datacode
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        img_dict_list = eval(r.data)['data']
    print(img_dict_list)
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
    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def getVisData(request):
    d_datetime = request.GET.get("d_datetime")
    datacode = request.GET.get("datacode")
    data_type = models.Items.objects.filter(datacode=datacode).first().type
    if not d_datetime:
        if data_type == 1:
            d_datetime = datetime.datetime.now().strftime('%Y%m%d')
        else:
            d_datetime = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    if not datacode.find("FY2G") == -1:
        return JsonResponse(fy2g(datacode, d_datetime))
    if not datacode.find("FY4A") == -1:
        return JsonResponse(fy4a(datacode, d_datetime))
    if not datacode.find("nmc") == -1:
        nmc_code = datacode.split("*")
        content = json.dumps(nmc(nmc_code[1], nmc_code[2], d_datetime), ensure_ascii=False)
        return HttpResponse(content, content_type='application/json; charset=utf-8')
    if not datacode.find("DATUM") == -1:
        target = models.Datum.objects.filter(datacode=datacode).first()
        nmc_code = datacode.split("_")
        return JsonResponse(datum(nmc_code[1], nmc_code[2], nmc_code[3], int(target.type)))
    url = "http://data.cma.cn/weatherGis/web/bmd/VisDataDef/getVisData?d_datetime=" + d_datetime + "&datacode=" + datacode
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    data = eval(r.data.decode())
    data_type = models.Items.objects.filter(datacode=datacode).first().type
    data['dataType'] = data_type
    if data_type == 1:
        data_list = data['data']
        data['selector'] = []
        for t in data_list:
            data['selector'].append(t['v_SHIJIAN'][8:12])
    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def fy2g(datacode, d_datetime):
    url = "http://www.nsmc.org.cn/NSMC/datalist/fy2g/fy2g_lan.txt"
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    image_path_list = bytes.decode(r.data).split(",\r\n")
    data = {'maxdate': datetime.datetime.now().strftime('%Y%m%d'), "data": [], "dataType": 1, 'selector': []}
    if d_datetime == datetime.datetime.now().strftime('%Y%m%d'):
        for id, t in enumerate(image_path_list):
            if not t.find(datacode + d_datetime) == -1:
                data["data"].append({"id": id, "fileURL": "http://img.nsmc.org.cn/CLOUDIMAGE/FY2G/lan/" + t,
                                     "v_SHIJIAN": d_datetime + t[26:30] + "00",
                                     "c_IYMDHMS": d_datetime + t[26:30] + "00"})
                data['selector'].append(t[26:30])
    else:
        for i in range(24):
            data["data"].append({"id": i,
                                 "fileURL": "http://img.nsmc.org.cn/CLOUDIMAGE/FY2G/lan/" + datacode + d_datetime + "_" + str(
                                     i).zfill(2) + "00.jpg",
                                 "v_SHIJIAN": d_datetime + str(i).zfill(2) + "0000",
                                 "c_IYMDHMS": d_datetime + str(i).zfill(2) + "0000"})
            data['selector'].append(str(i).zfill(2) + "0000")
    return data


def fy4a(datacode, d_datetime):
    target = models.Fy4h.objects.filter(imagename=datacode).first()
    url = "http://fy4.nsmc.org.cn/nsmc/v1/nsmc/image/animation/datatime/filesys?dataCode=" + target.imagename + \
          "&hourRange=" + target.maxlevel
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    ds_list = eval(r.data.decode())['ds']
    today = datetime.datetime.now().strftime('%Y%m%d')
    data = {'maxdate': datetime.datetime.now().strftime('%Y%m%d'), "data": [], "dataType": 1, 'selector': []}
    for id, ds in enumerate(ds_list):
        r = http.request('GET',
                         target.serviceurl + "&DATE=" + ds['dataDate'] + "&TIME=" + ds['dataTime'] + "&&ENDTIME=" + ds[
                             'endTime'] + "&", redirect=False)
        data["data"].append({"id": id, "fileURL": r.get_redirect_location().replace(today, d_datetime),
                             "v_SHIJIAN": d_datetime + ds['dataTime'],
                             "c_IYMDHMS": d_datetime + ds['dataTime']})
        data['selector'].append(ds['dataTime'][0:4])
    return data


def getDatumItem(request):
    name = request.GET.get("name")
    if not name:
        item_list = models.Datum.objects.all()
    else:
        item_list = models.Datum.objects.filter(name__contains=name)
    data = {"status": 1, "data": []}
    for item in item_list:
        data["data"].append({"grandfathername": item.grandfathername, "fathername": item.fathername, "name": item.name,
                             "datacode": item.datacode, "type": item.type})
    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def nmc(nmc_code, datacode, d_datetime):
    if not nmc_code.find('nwpc') == -1:
        url = "http://www.nmc.cn/publish/" + nmc_code + "/" + datacode + ".htm"
    else:
        url = "http://www.nmc.cn/publish/" + nmc_code + "/" + datacode + ".html"
    print(url)
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    html = r.data.decode()
    pat = re.compile('img_path:\'(.*?)\',html_path', re.S)
    ds_list = pat.findall(html)
    pat = re.compile('ymd:\'(.*?)\'}\)', re.S)
    selector_list = pat.findall(html)
    data = {'maxdate': datetime.datetime.now().strftime('%Y%m%d'), "data": [], "dataType": 1, 'selector' : []}
    for i, ds in enumerate(ds_list):
        data["data"].append({"id": i, "fileURL": "http://image.nmc.cn" + ds[0:ds.find('?')],
                             "v_SHIJIAN": d_datetime + ds[78:82],
                             "c_IYMDHMS": d_datetime + ds[78:82]})
        data['selector'].append(selector_list[i][9:])
    return data


def datum(c_type, mon, idx, d_type):
    surl = 'http://image.data.cma.cn/climateImage/'
    burl = '/SURF_CLI_CHN_MUL_MUT_19712000_ATLAS-'
    data = {'maxdate': datetime.datetime.now().strftime('%Y%m%d'), "data": []}
    if d_type == 2:
        data["data"].append({"id": 1, "fileURL": surl + c_type + burl + mon + "-" + c_type + "-" + idx + ".png",
                             "v_SHIJIAN": "",
                             "c_IYMDHMS": ""})
        data['dataType'] = 2
    else:
        for i in range(13):
            data["data"].append(
                {"id": i,
                 "fileURL": surl + c_type + burl + mon + "-" + c_type + "-" + idx + "-" + str(i).zfill(2) + ".png",
                 "v_SHIJIAN": "",
                 "c_IYMDHMS": ""})
            data['dataType'] = 1
        data['selector'] = [str(w).zfill(2) + "月" for w in range(13)]

    return data


def getProvinceList(request):
    http = urllib3.PoolManager()
    url = "http://data.cma.cn/weatherGis/web/dmd/chinaprovincedic/provincelist"
    r = http.request("GET", url)
    data = eval(r.data.decode())
    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def getStationList(request):
    provincecode = request.GET.get("provincecode")
    http = urllib3.PoolManager()
    url = "http://data.cma.cn/weatherGis/web/bmd/stationinfo/getStationSurf?provincecode=" + provincecode
    r = http.request("GET", url)
    data = eval(r.data.decode())
    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def getChartsData(request):
    stationId = request.GET.get("stationId")
    datacode = request.GET.get("datacode")
    if not stationId:
        stationId = models.Station.objects.filter(cname__contains="北京").first().stationid
    charts_data = models.Charts.objects.filter(stationid=stationId, datacode=datacode).first()
    data = {}
    if not charts_data:
        data['status'] = '-1'
    else:
        data['status'] = '1'
        data['parms'] = eval(charts_data.parms)
        data['data'] = eval(charts_data.data)
    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def homepage(request):
    return redirect("https://www.showdoc.cc/180958275778100")


def getForecastInfo(request):
    cityname = getCityName(request.GET.get("location"))
    if not models.Station.objects.filter(cname=cityname).first():
        stationId = models.Station.objects.filter(cname__contains="北京").first().stationid
    else:
        stationId = models.Station.objects.filter(cname__contains=cityname).first().stationid
    http = urllib3.PoolManager()
    url = "http://data.cma.cn/forecast/getForecastInfo?stationId=" + stationId
    r = http.request("GET", url)
    data = eval(r.data.decode())
    data['wind'] = weather.windDri(data['WIN_D']) + weather.windlevel(data['WIN_S'])
    data['weather'] = weather.wth[data['WEP']]
    data['WEP'] = "http://image.data.cma.cn/static/image/forecast/bigIcon/" + str(data['WEP']) + ".png"
    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def getCityName(location='39.934,116.329'):
    import requests
    r = requests.get(url='http://api.map.baidu.com/geocoder/v2/',
                     params={'location': location, 'ak': '23D1VgIGjVSqoGqh4SWrAWE5IdgHNmby', 'output': 'json'})
    result = r.json()
    if not result['result']['addressComponent']['city']:
        return '北京'
    else:
        return result['result']['addressComponent']['city']


def test(request):
    station_list = models.Station.objects.all()
    data_code_list = [
        '{"xseries":{"V04002": "月份"}, "yseries":{"V12011": "累年各月极端最高天气", "V12012": "累年各月极端最低天气"},"x":"月","y":"温度值(℃)"}',
        '{"xseries":{"V04002": "月份"}, "yseries":{"V12001_701": "累年各月平均气温", "V12011_701": "累年各月平均最高气温", "V12012_701": "累年各月平均最低气温"} ,"x":"月","y":"温度值(℃)"}',
        '{"xseries":{"V04002": "月份"}, "yseries":{"V13306_701": "降水量值"},"x":"月","y":"降水量值(mm)"}',
        '{"xseries":{"V04002": "月份"}, "yseries":{"V13060_MAX": "最大降水量值"},"x":"月","y":"降水量值(mm)"}',
        '{"xseries":{"V04002": "月份"}, "yseries":{"V10004_701": "气压值"},"x":"月","y":"气压值(hPa)"}',
        '{"xseries":{"V04002": "月份"}, "yseries":{"V13003_701":"累年各月平均相对湿度"},"x":"月","y":"湿度值(%)"}']
    for station in station_list:
        print(station.id)
        data_list = models.Charts.objects.filter(stationid=station.stationid).all()
        for i, data in enumerate(data_list):
            models.Charts.objects.filter(id=data.id).update(parms=data_code_list[i])
    return HttpResponse("ok")
