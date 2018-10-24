# from django.test import TestCase
#
# # Create your tests here.
# import urllib3
# import re
# from . import models
# import json
#
#
# def getDatumData():
#     station_list = models.Station.objects.all()
#     for i, station in enumerate(station_list):
#         print(i)
#         datacode_list = [w.datacode for w in models.Datum.objects.filter(datacode__contains="charts").all()]
#         for datacode in datacode_list:
#             d_datacode = datacode.split("-")[1]
#             http = urllib3.PoolManager()
#             url = "http://data.cma.cn/weatherGis/web/dataservice/AppData/list?id=" + d_datacode + "&stationID=" + station.stationid
#             r = http.request("GET", url)
#             models.Charts.objects.create(stationid=station.stationid, datacode=datacode, data=r.data.decode('utf-8'))
#
# def getStationCode():
#     http = urllib3.PoolManager()
#     url = "http://data.cma.cn/weatherGis/web/dmd/chinaprovincedic/provincelist"
#     r = http.request("GET", url)
#     province_list = json.loads(r.data.decode('utf-8'))
#     for province in province_list:
#         print(province)
#         url = "http://data.cma.cn/weatherGis/web/bmd/stationinfo/getStationSurf?provincecode=" + province[
#             'provincecode']
#         print(url)
#         r = http.request("GET", url)
#         station_list = json.loads(r.data.decode('utf-8'))
#         for station in station_list:
#             models.Station.objects.create(provincecode=province['provincecode'], provincename=province['provincename'],
#                              cname=station['cname'], stationid=station['v01301'])
# #station_list = models.Station.objects.all()
#     data_code_list = [
#         '{"xseries":{"V04002": "月份"}, "yseries":{"V12011": "累年各月极端最高天气", "V12012": "累年各月极端最低天气"},"x":"月","y":"温度值(℃)"}',
#         '{"xseries":{"V04002": "月份"}, "yseries":{"V12001_701": "累年各月平均气温", "V12011_701": "累年各月平均最高气温", "V12012_701": "累年各月平均最低气温"} ,"x":"月","y":"温度值(℃)"}',
#         '{"xseries":{"V04002": "月份"}, "yseries":{"V13306_701": "降水量值"},"x":"月","y":"降水量值(mm)"}',
#         '{"xseries":{"V04002": "月份"}, "yseries":{"V13060_MAX": "最大降水量值"},"x":"月","y":"降水量值(mm)"}',
#         '{"xseries":{"V04002": "月份"}, "yseries":{"V10004_701": "气压值"},"x":"月","y":"气压值(hPa)"}',
#         '{"xseries":{"V04002": "月份"}, "yseries":{"V13003_701":"累年各月平均相对湿度"},"x":"月","y":"湿度值(%)"}']
#     for station in station_list:
#         print(station.id)
#         data_list = models.Charts.objects.filter(stationid=station.stationid).all()
#         for i, data in enumerate(data_list):
#             models.Charts.objects.filter(id=data.id).update(parms=data_code_list[i])

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
filename = 'data.raw'
with open(filename,'w') as f:
    for i in range(255):
        for j in range(255):
            f.write(str((i+j)/512)+' ')
        f.write('\n')
#plt.imshow(s,cmap='gray')
#plt.show()

