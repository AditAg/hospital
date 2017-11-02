from django.conf.urls import include, url
from . import views

app_name = 'services'

urlpatterns=[
    url(r'^$',views.allservices,name='allservices'),
    url(r'(?P<lab_id>[0-9]+)/$',views.lab_details, name = 'lab_details'),
    url(r'rooms/$',views.rooms,name='rooms'),

]