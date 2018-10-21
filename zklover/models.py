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