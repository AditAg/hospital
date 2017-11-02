from django.conf.urls import include,url
from . import views

app_name = 'mainpage'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^AboutUs/',views.aboutus, name = 'aboutus'),
    url(r'^login/$',views.Login,name='login'),
    url(r'^logout/$',views.Logout,name='logout'),
    url(r'^register/$',views.register,name='register'),
    url(r'^check_registration/$',views.check,name='check_registration'),
    url(r'^bookappointment/$',views.book_appointment,name='bookappointment'),
    #url('^appointment_details/id',views.appointment_details,name='appointmentdetails'),
    url(r'^doctordetails/(?P<doctor_id>[0-9]+)/$',views.doctordetails,name='doctordetails'),
]

