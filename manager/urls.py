from django.conf.urls import url
from . import views

app_name = 'manager'
urlpatterns = [
	url(r'^home/$',views.index,name='index'),
	url(r'^doctors/$',views.view_doctors, name='viewdoctors'),
	url(r'^patients/$',views.view_patients,name='viewpatients'),
	url(r'^workers/$',views.view_workers,name='viewworkers'),
	url(r'^inventory/$',views.view_inventory,name='viewinstruments'),
	url(r'^medicines/$',views.view_medicines,name='viewmedicines'),
	url(r'^addmedicines/$',views.add_medicinedetails,name='addmedicines'),
	url(r'^addmedicine/$',views.add_medicine,name='addmedicine'),
	url(r'^addpurchasedetails/(?P<instrument_id>[0-9]+)/$',views.add_purchasedetails,name='addpurchasedetails'),
	url(r'^addinstrument/$',views.add_instrument,name='addinstrument'),
	url(r'^purchasedetails/(?P<instrument_id>[0-9]+)/$',views.view_purchasedetails,name='purchasedetails'),
	url(r'^medicinedetails/(?P<medicine_id>[0-9]+)/$',views.view_medicinedetails,name='medicinedetails'),
	url(r'^addworker/$',views.add_worker,name='addworker'),
	url(r'^rooms/$',views.view_rooms,name='viewrooms'),
	url(r'^addroom/$',views.addroom,name='addroom'),
	url(r'^labs/$',views.view_labs,name='viewlabs'),
	url(r'^addlab/$',views.addlab,name='addlab'),
	url(r'^bills/$',views.view_bills,name='viewbills'),
	url(r'^addbill/$',views.addbill,name='addbill'),
]
