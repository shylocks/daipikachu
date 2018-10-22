from django.db import models

# Create your models here.


class Items(models.Model):
    name = models.CharField(max_length=255, verbose_name="名称")
    fathername = models.CharField(max_length=255, verbose_name="父级菜单")
    grandfathername = models.CharField(max_length=255, verbose_name="上级菜单")
    datacode = models.CharField(max_length=255, verbose_name="代码")


class Fy4h(models.Model):
    displaynamechn = models.CharField(max_length=255, verbose_name="名称")
    groupnamechn = models.CharField(max_length=255, verbose_name="组名称")
    serviceurl = models.CharField(max_length=255, verbose_name="服务地址")
    imagename = models.CharField(max_length=255, verbose_name="图片名称")
    maxlevel = models.CharField(max_length=255, verbose_name="最大区间")


class Datum(models.Model):
    name = models.CharField(max_length=255, verbose_name="名称")
    fathername = models.CharField(max_length=255, verbose_name="父级菜单")
    grandfathername = models.CharField(max_length=255, verbose_name="上级菜单")
    datacode = models.CharField(max_length=255, verbose_name="代码")
    type = models.CharField(max_length=255, verbose_name="数据类型")


class Charts(models.Model):
    stationid = models.CharField(max_length=255, verbose_name="观测站代码")
    datacode = models.CharField(max_length=255, verbose_name="代码")
    parms = models.TextField()
    data = models.TextField()


class Station(models.Model):
    provincecode = models.CharField(max_length=255, verbose_name="省份代码")
    provincename = models.CharField(max_length=255, verbose_name="省份名称发")
    stationid = models.CharField(max_length=255, verbose_name="观测站代码")
    cname = models.CharField(max_length=255, verbose_name="观测站名称")
