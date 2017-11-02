from django.conf.urls import url
from . import views

app_name = 'doctor'
urlpatterns = [
    #url(r'^(?P<doctor_id>[0-9]+)/$',views.index,name='index'),
    url(r'^home/$', views.index, name='index'),
    url(r'^register/$', views.DoctorFormView.as_view(), name='doctor_register'),
    url(r'^logout/$',views.Logout,name='logout'),
    url(r'^set_schedule/$',views.Set,name = 'set'),
    url(r'^set2/$',views.set_2,name="set_2"),
    url(r'^check/$',views.check,name='check'),
    url(r'^cancel/$',views.cancel,name='cancel'),
    url(r'^checkappointment/(?P<appointment_id>[0-9]+)/$',views.appointment_details,name='appointmentdetails'),
    #check_appointments
    #specify_schedule
    #See reports of patients
]
