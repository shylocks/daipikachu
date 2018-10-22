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
#                                           cname=station['cname'], stationid=station['v01301'])
#     return 1
import requests
r = requests.get(url='http://api.map.baidu.com/geocoder/v2/',
                 params={'location': '39.934,116.329', 'ak': '23D1VgIGjVSqoGqh4SWrAWE5IdgHNmby', 'output': 'json'})
result = r.json()
city = result['result']['addressComponent']['city']
print(city)
