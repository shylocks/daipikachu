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
import jieba
import jieba.posseg as psg
from bs4 import BeautifulSoup


# Create your views here.


def getGifData(request):
    s_datetime = request.GET.get("s_datetime")
    e_datetime = request.GET.get("e_datetime")
    duration = request.GET.get("duration")
    if not duration:
        duration = 0.5
    if not s_datetime:
        s_datetime = datetime.datetime.now().strftime('%Y%m%d')
    if not e_datetime:
        e_datetime = datetime.datetime.now().strftime('%Y%m%d')
    quality = request.GET.get("quality")
    if not quality:
        quality = 2
    datacode = request.GET.get("datacode")
    img_dict_list = []
    begin = datetime.date(int(s_datetime[0:4]), int(s_datetime[4:6]), int(s_datetime[6:8]))
    end = datetime.date(int(e_datetime[0:4]), int(e_datetime[4:6]), int(e_datetime[6:8]))
    d = begin
    delta = datetime.timedelta(days=1)
    while d <= end:
        d_datetime = d.strftime("%Y%m%d")
        if not datacode.find("FY2G") == -1:
            r = fy2g(datacode, d_datetime)
            for rr in r['data']:
                img_dict_list.append(rr)
        elif not datacode.find("FY4A") == -1:
            r = fy4a(datacode, d_datetime)
            for rr in r['data']:
                img_dict_list.append(rr)
        elif not datacode.find('nmc') == -1:
            nmc_code = datacode.split("[")
            r = nmc(nmc_code[1], nmc_code[2], d_datetime)
            for rr in r['data']:
                img_dict_list.append(rr)
        elif not datacode.find('DATUM') == -1:
            target = models.Datum.objects.filter(datacode=datacode).first()
            nmc_code = datacode.split("_")
            r = datum(nmc_code[1], nmc_code[2], nmc_code[3], int(target.type))
            for rr in r['data']:
                img_dict_list.append(rr)
        else:
            url = "http://data.cma.cn/weatherGis/web/bmd/VisDataDef/getVisData?d_datetime=" + d_datetime + "&datacode=" + datacode
            http = urllib3.PoolManager()
            r = http.request('GET', url)
            for rr in eval(r.data)['data']:
                img_dict_list.append(rr)
        d += delta
    print(img_dict_list)
    if not len(img_dict_list) == 0:
        frames = []
        tmp = io.imread(img_dict_list[0]['fileURL']).shape
        shape = (int(tmp[0] / int(quality)), int(tmp[1] / int(quality)))
        for img_dict in img_dict_list:
            frames.append(resize(io.imread(img_dict['fileURL']), shape))
        gif_dir = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        imageio.mimsave(gif_dir + ".gif", frames, 'GIF', duration=duration)
        return HttpResponse(open(gif_dir + ".gif", "rb").read(), content_type="image/gif")
    return HttpResponse("error")


def getItemData(request):
    name = request.GET.get("name")
    item_list = models.Items.objects.filter(grandfathername=name).all()
    data = {"status": 1, "data": {}}
    for item in item_list:
        if not item.fathername in data["data"].keys():
            data["data"][item.fathername] = []
        data["data"][item.fathername].append(
            {"name": item.name, "datacode": item.datacode, "imgUrl": item.datacode.replace("/", '')})
    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def getVisData(request):
    d_datetime = request.GET.get("d_datetime")
    datacode = request.GET.get("datacode")
    datacode = datacode.replace(" ", "+")
    print(datacode)
    if datacode.find("DATUM") == -1:
        data_type = models.Items.objects.filter(datacode=datacode).first().type
    else:
        data_type = models.Datum.objects.filter(datacode=datacode).first().type
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
        nmc_code = datacode.split("[")
        content = json.dumps(nmc(nmc_code[1], nmc_code[2], d_datetime), ensure_ascii=False)
        return HttpResponse(content, content_type='application/json; charset=utf-8')
    if not datacode.find("DATUM") == -1:
        target = models.Datum.objects.filter(datacode=datacode).first()
        nmc_code = datacode.split("_")
        content = json.dumps(datum(nmc_code[1], nmc_code[2], nmc_code[3], int(target.type)))
        return HttpResponse(content, content_type='application/json; charset=utf-8')
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
            data['selector'].append(t['v_SHIJIAN'][8:10] + ':' + t['v_SHIJIAN'][10:12])
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
                data['selector'].append(t[26:28])
    else:
        for i in range(24):
            data["data"].append({"id": i,
                                 "fileURL": "http://img.nsmc.org.cn/CLOUDIMAGE/FY2G/lan/" + datacode + d_datetime + "_" + str(
                                     i).zfill(2) + "00.jpg",
                                 "v_SHIJIAN": d_datetime + str(i).zfill(2) + "0000",
                                 "c_IYMDHMS": d_datetime + str(i).zfill(2) + "0000"})
            data['selector'].append(str(i).zfill(2) + ":00:00")
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
        data['selector'].append(ds['dataTime'][0:2] + ":" + ds['dataTime'][2:4])
    return data


def search(request):
    data = {'status': -1}
    name = request.GET.get("name")
    if name:
        data['status'] = 1
        data['data'] = []
        item_query_list = []
        item_query_list.append(models.Datum.objects.filter(grandfathername__contains=name).all())
        item_query_list.append(models.Datum.objects.filter(fathername__contains=name).all())
        item_query_list.append(models.Datum.objects.filter(name__contains=name).all())
        item_query_list.append(models.Items.objects.filter(grandfathername__contains=name).all())
        item_query_list.append(models.Items.objects.filter(fathername__contains=name).all())
        item_query_list.append(models.Items.objects.filter(name__contains=name).all())
        datacode_list = []
        for item_list in item_query_list:
            for item in item_list:
                if item.datacode not in datacode_list:
                    data['data'].append(
                        {'grandfather': item.grandfathername, 'fathername': item.fathername, 'name': item.name,
                         'datacode': item.datacode})

    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def getDatumItem(request):
    name = request.GET.get("name")
    data = {"status": 1, "data": []}
    if not name:
        item_list = models.Datum.objects.all()
        for item in item_list:
            if item.fathername not in data['data']:
                data['data'].append(item.fathername)
    else:
        item_list = models.Datum.objects.filter(fathername__contains=name)
        for item in item_list:
            data["data"].append({"name": item.name,
                                 "datacode": item.datacode, "type": item.type})
    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def nmc(nmc_code, datacode, d_datetime):
    url = "http://www.nmc.cn/publish/" + nmc_code + "/" + datacode
    print(url)
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    html = r.data.decode()
    pat = re.compile('img_path:\'(.*?)\',html_path', re.S)
    ds_list = pat.findall(html)
    pat = re.compile('ymd:\'(.*?)\'}\)', re.S)
    selector_list = pat.findall(html)
    data = {'maxdate': datetime.datetime.now().strftime('%Y%m%d'), "data": [], "dataType": 1, 'selector': []}
    for i, ds in enumerate(ds_list):
        data["data"].append({"id": i, "fileURL": "http://image.nmc.cn" + ds[0:ds.find('?')],
                             "v_SHIJIAN": d_datetime + ds[78:82],
                             "c_IYMDHMS": d_datetime + ds[78:82]})
        data['selector'].append(selector_list[i][9:])
    datacode = 'nmc[' + nmc_code + '[' + datacode
    data['iconURL'] = 'https://www.shylocks.ml/static/' + datacode.replace('/', '') + '.png'
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
        for i in range(12):
            data["data"].append(
                {"id": i,
                 "fileURL": surl + c_type + burl + mon + "-" + c_type + "-" + idx + "-" + str(i + 1).zfill(2) + ".png",
                 "v_SHIJIAN": "",
                 "c_IYMDHMS": ""})
            data['dataType'] = 1
        data['selector'] = [str(w + 1).zfill(2) + "月" for w in range(12)]

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


def getCharts(request):
    stationId = request.GET.get("stationId")
    datacode = request.GET.get("datacode")
    if not stationId:
        stationId = models.Station.objects.filter(cname__contains="北京").first().stationid
    charts_data = models.Charts.objects.filter(stationid=stationId, datacode=datacode).first()
    data = {'status': '', 'series': [], 'yAxis': {}, 'categories': ''}
    if not charts_data:
        data = {'status': '-1'}
    else:
        data = {'status': '1', 'series': [], 'yAxis': {}, 'categories': ''}
        for key, value in eval(charts_data.parms)['yseries'].items():
            data_list = []
            for d in eval(charts_data.data):
                data_list.append(d[key])
            data['series'].append({'name': value, 'data': data_list})
            data['yAxis'] = {
                'title': eval(charts_data.parms)['y']
            }
            data['categories'] = [str(i + 1) + '月' for i in range(12)]
    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def homepage(request):
    return redirect("https://www.showdoc.cc/180958275778100")


def getForecastInfo(request):
    cityname = getCityName(request.GET.get("location"))
    cityname = cityname[:cityname.find("市")]
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


def robot(request):
    data = {'status': -1}
    docs_list = models.Docs.objects.all()
    for docs in docs_list:
        jieba.add_word(docs.name)
    s = request.GET.get("message")
    res_list = psg.cut(s)
    print([(x.word, x.flag) for x in psg.cut(s)])
    word_list = [x.word for x in res_list if x.flag == 'x']
    if len(word_list):
        key = docs_list.filter(name=word_list[0]).first()
        if key:
            data = {'status': 1, 'name': key.name, 'content': ['聪明的大咖找到啦~\n' + key.name + ',' + key.content]}
    else:
        res_list = psg.cut(s)
        word_list = [x.word for x in res_list if x.flag.startswith('n')]
        if len(word_list):
            key = docs_list.filter(name=word_list[0]).first()
            if key:
                if key.father.startswith('m'):
                    data = {'status': 2, 'name': key.name,
                            'content': ['你找的是不是' + key.name + '?\n' + key.name + ',' + key.content]}
                    if docs_list.filter(father=key.name).first():
                        hint = "关于" + key.name + '你可能还想知道:\n'
                        for keys in docs_list.filter(father=key.name).all():
                            hint = hint + keys.name + '\n'
                        data['content'].append(hint)
                else:
                    data = {'status': 1, 'name': key.name, 'content': ['聪明的大咖找到啦~\n' + key.name + ',' + key.content]}
            else:
                key = docs_list.filter(father__contains=word_list[0]).first()
                if key:
                    if docs_list.filter(father__contains=key.father[4:]).first():
                        data = {'status': 3, 'name': key.father[5:],
                                'content': ['你说的是不是' + key.father[5:] + '?\n该条目下包含：\n']}
                        tmp = ""
                        for i, d in enumerate(docs_list.filter(father__contains=key.father[4:]).all()):
                            tmp = tmp + str(i + 1) + '. ' + d.name + '\n'
                        data['content'].append(tmp)
                else:
                    key = docs_list.filter(name__contains=word_list[0]).first()
                    if key:
                        data = {'status': 4, 'name': key.name,
                                'content': ['你说的是不是' + key.name + '?\n' + key.name + ',' + key.content]}
                        if docs_list.filter(father=key.name).first():
                            hint = "关于" + key.name + '你可能还想知道:\n'
                            for keys in docs_list.filter(father=key.name).all():
                                hint = hint + keys.name + '\n'
                            data['content'].append(hint)
    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def news(request):
    http = urllib3.PoolManager()
    url = "http://data.cma.cn/article/getList/cateId/3.html"
    r = http.request("get", url)
    bs = BeautifulSoup(r.data.decode().replace('<img src="/static/images/newIcon.png" class="newIcon">', ''),
                       "html.parser")
    data = {'status': 1, 'data': []}
    for w in bs.find_all("li", style="list-style:none"):
        tmp_list = [x.word for x in psg.cut(w.a.string) if x.flag == 'n']
        if not len(tmp_list):
            tmp = '资讯'
        else:
            flag = 1
            for key in tmp_list:
                if len(key) == 2:
                    tmp = key
                    flag = 0
                    break
            if flag:
                tmp = '资讯'
        data['data'].append({'key': tmp, 'title': w.a.string})

    content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(content, content_type='application/json; charset=utf-8')


def test(request):
    item_list = models.Docs.objects.all()
    f = open('userdict.txt', 'w')
    for item in item_list:
        f.write(item.name + " 1\n")
    f.close()
    return HttpResponse("ok")
