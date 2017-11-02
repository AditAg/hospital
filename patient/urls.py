from django.conf.urls import url
from . import views

app_name='patient'
urlpatterns=[
    #url(r'^(<patient_id>[0-9]+)/$',views.index,name='index'),
    #url(r'^register/$',views.patient_register,name='patient_register'),
    #Book Appointment
    url(r'^home/$', views.index,name='index'),
    url(r'^register/$',views.PatientFormView.as_view(), name='patient_register'),
    url(r'^bookappointment/$',views.book,name='bookappointment'),
    url(r'^logout/$',views.Logout,name='logout'),
    url(r'^appointmentdetails/(?P<appointment_id>[0-9]+)/$',views.appointmentdetails,name='appointmentdetails'),
    url(r'^examinationdetails/(?P<examination_id>[0-9]+)/$',views.examinationdetails,name='examinationdetails'),
    url(r'^details/$',views.changedetails,name='change'),
    url(r'^requestexamination/$',views.request_examination, name='requestexamination'),
    url(r'^enterhistory/$',views.enterhistory,name='enterhistory'),
    url(r'^showbills/$',views.showbills,name='showbills'),
]