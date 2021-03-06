"""daipikachu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from zklover import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/getVisData', views.getVisData),
    path('api/getGifData', views.getGifData),
    path('api/getItemData', views.getItemData),
    path('api/getDatumItem', views.getDatumItem),
    path('api/getProvinceItem', views.getProvinceList),
    path('api/getStationItem', views.getStationList),
    path('api/getForecastInfo', views.getForecastInfo),
    path('api/getChartsData', views.getChartsData),
    path('api/getCharts', views.getCharts),
    path('api/search',views.search),
    path('api/robot',views.robot),
    path('api/news',views.news),
    path('', views.homepage),
    path('test',views.test)
]
