from django.test import TestCase

# Create your tests here.
import urllib3
import re

datacode = "dongbei"
url = "http://www.nmc.cn/publish/radar/" + datacode + ".html"
http = urllib3.PoolManager()
r = http.request("GET", url)
html = r.data.decode()
pat = re.compile('img_path:\'(.*?)\',html_path', re.S)
tmp = pat.findall(html)
print(tmp)
