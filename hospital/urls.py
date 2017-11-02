"""hospital URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^home/',include('mainpage.urls', namespace='mainpage')),
    url(r'^(/)?$',RedirectView.as_view(url='/home/')),
    url(r'^services/',include('services.urls',namespace='services')),
    url(r'^login/',RedirectView.as_view(url='/home/login/')),
    url(r'^doctor/',include('doctor.urls',namespace='doctor')),
    url(r'^patient/',include('patient.urls',namespace='patient')),
    url(r'^manager/',include('manager.urls',namespace='manager')),
]

#if settings.DEBUG:
#    urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
#    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
