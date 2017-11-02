from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.contrib.auth.models import User
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection,transaction
import json
from datetime import datetime,timedelta
import re

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def index(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			context={'manager_details':x,}
			return render(request,'manager/startpage.html',context)
	else:
		return redirect('mainpage:index')

def view_doctors(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			cursor.execute('SELECT * from Doctor,auth_user,DoctorSpeciality,Lab where Doctor.lab=Lab.lab_id and Doctor.user_id = auth_user.id and Doctor.speciality = DoctorSpeciality.label')
			doctor_details = dictfetchall(cursor)
			for i in range(len(doctor_details)):

				cursor.execute('SELECT * from Doctor_Phone where doctor_id=%s',[doctor_details[i]['doctor_id']])
				contact_details = dictfetchall(cursor)
				cc = {'contact':''}
				if(len(contact_details)!=0):
					cc['contact']+=contact_details[0]['contact'] 	
				for j in range(1,len(contact_details)):
					cc['contact'] += str(',' + contact_details[j]['contact'])
					z = doctor_details[i].update(cc)
			print(doctor_details)
			context={"doctor_details":doctor_details,}
			return render(request,'manager/view_doctors.html',context)
	else:
		return redirect('mainpage:index')

def view_patients(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			cursor.execute('SELECT * from Patients,auth_user where Patients.user_id = auth_user.id')
			patient_details = dictfetchall(cursor)
			for i in range(len(patient_details)):

				cursor.execute('SELECT * from Patient_Phone where patient_id=%s',[patient_details[i]['patient_id']])
				contact_details = dictfetchall(cursor)
				cc = {'contact':''}
				if(len(contact_details)!=0):
					cc['contact']+=contact_details[0]['contact'] 	
				for j in range(1,len(contact_details)):
					cc['contact'] += str(',' + contact_details[j]['contact'])
					z = patient_details[i].update(cc)
			print(patient_details)
			context={'patient_details':patient_details,}
			return render(request,'manager/view_patients.html',context)
	else:
		return redirect('mainpage:index')

def convert_date2(date):
    p = date.split('-')
    if(len(p)==1):
    	return p
    year=p[0]
    month = p[1]
    dt = p[2]
    m = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sept':'09','Oct':'10','Nov':'11','Dec':'12'}
    return str(dt + '-' + month + '-' + year)

def view_workers(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
		if(request.method=='POST'):
			if(request.POST.get('workerid')):
				with connection.cursor() as cursor:
					worker_id = request.POST.get('workerid')
					cursor.execute('START TRANSACTION;')
					cursor.execute('DELETE FROM Worker_Phone WHERE worker_id=%s',[worker_id])
					cursor.execute('DELETE FROM Worker where worker_id=%s',[worker_id])
					cursor.execute('COMMIT;')
					response_data={}
					return HttpResponse(json.dumps(response_data),content_type='application/json')
			with connection.cursor() as cursor:
				worker_id = request.POST.get('worker_id')
				worker_name = request.POST.get('worker_name')
				worker_type = request.POST.get('worker_type')
				salary = request.POST.get('salary')
				date_of_joining = request.POST.get('date_of_joining')
				print(date_of_joining)
				qualifications = request.POST.get('qualifications')
				street_no = request.POST.get('street_no')
				street_name = request.POST.get('street_name')
				apt_number = request.POST.get('apt_number')
				city = request.POST.get('city')
				state = request.POST.get('state')
				gender = request.POST.get('gender')
				account_no = request.POST.get('account_no')
				work_duration = request.POST.get('work_duration')
				contact = request.POST.get('contact')
				cursor.execute('START TRANSACTION;')
				cursor.execute('UPDATE Worker SET worker_name=%s,worker_type=%s,salary=%s,date_of_joining=%s,qualifications=%s,street_no=%s,street_name=%s,apt_number=%s,city=%s,state=%s,gender=%s,account_no=%s,work_duration=%s WHERE worker_id=%s',[worker_name,worker_type,salary,date_of_joining,qualifications,street_no,street_name,apt_number,city,state,gender,account_no,work_duration,worker_id])
				cursor.execute('COMMIT;')
			response_data={}
			return HttpResponse(json.dumps(response_data),content_type='application/json')

		else:
			with connection.cursor() as cursor:
				cursor.execute('SELECT * from Worker')
				worker_details = dictfetchall(cursor)
				for i in range(len(worker_details)):
					cursor.execute('SELECT * from Worker_Phone WHERE worker_id=%s',[worker_details[i]['worker_id']])
					contact_details = dictfetchall(cursor)
					cc={'contact':''}
					if(len(contact_details)!=0):
						cc['contact']+= contact_details[0]['phone']
					for j in range(1,len(contact_details)):
						cc['contact'] += str(',' + contact_details[j]['phone'])
					z = worker_details[i].update(cc) 
					# date = convert_date2(str(worker_details[i]['date_of_joining']))
					# cc = {'date':date}
					# z = worker_details[i].update(cc)
				context={'worker_details':worker_details,}
				return render(request,'manager/view_workers.html',context)
	else:
		return redirect('mainpage:index')

def view_inventory(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			cursor.execute('SELECT * from Instrument')
			instruments = dictfetchall(cursor)
			context={'instruments':instruments,}
			return render(request,'manager/view_instruments.html',context)
	else:
		return redirect('mainpage:index')

def view_purchasedetails(request,instrument_id):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			cursor.execute('SELECT * from Purchase_Details WHERE instrument_id=%s',[instrument_id])
			instruments = dictfetchall(cursor)
			context={'instruments':instruments,'instrument_id':instrument_id,}
			return render(request,'manager/view_purchasedetails.html',context)
	else:
		return redirect('mainpage:index')
def view_medicines(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			cursor.execute('SELECT * from Medicine')
			medicines = dictfetchall(cursor)
			context={'medicines':medicines,}
			return render(request,'manager/view_medicines.html',context)
	else:
		return redirect('mainpage:index')
def view_medicinedetails(request,medicine_id):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			cursor.execute('SELECT * from Medicine_Details WHERE medicine_name=%s',[medicine_id])
			medicines = dictfetchall(cursor)
			context={'medicines':medicines,'medicine_id':medicine_id,}
			return render(request,'manager/view_medicinedetails.html',context)
	else:
		return redirect('mainpage:index')
def add_medicinedetails(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			if(request.method=="POST"):
				invoice_no = request.POST.get('invoice_no')
				print(invoice_no)
				medicine = request.POST.get('medicine')
				batch_no = request.POST.get('batch_no')
				date_of_manufacture = request.POST.get('date_of_manufacture')
				date_of_expiry = request.POST.get('date_of_expiry')
				price = request.POST.get('price')
				quantity = request.POST.get('quantity')
				cursor.execute('SELECT * from Medicine_Details WHERE Invoice_No=%s',[invoice_no])
				det = dictfetchall(cursor)
				if(len(det)==0 and invoice_no is not None and invoice_no!=''):
					cursor.execute('START TRANSACTION;')
					cursor.execute('INSERT INTO Medicine_Details VALUES(%s,%s,%s,%s,%s,%s,%s)',[invoice_no,medicine,batch_no,date_of_manufacture,date_of_expiry,price,quantity])
					cursor.execute('COMMIT;')
					return redirect('manager:viewmedicines')
				else:
					cursor.execute('SELECT * from Medicine')
					medicines=dictfetchall(cursor)
					context={'medicines':medicines,'error_message':'Sorry the invoice no. is invalid'}
					return render(request,'manager/add_medicinedetails.html',context)

			else:
				cursor.execute('SELECT * from Medicine')
				medicines=dictfetchall(cursor)
				context={'medicines':medicines,}
				return render(request,'manager/add_medicinedetails.html',context)
	else:
		return redirect('mainpage:index')

def add_medicine(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			if(request.method=="POST"):
				medicine_name = request.POST.get('medicine_name')
				other_details = request.POST.get('other_details')
				cursor.execute('START TRANSACTION;')
				cursor.execute('INSERT INTO Medicine(name) VALUES(%s)',[medicine_name])
				cursor.execute('COMMIT;')
				return redirect('manager:viewmedicines')
				
			else:
				context={}
				return render(request,'manager/add_medicine.html',context)
	else:
		return redirect('mainpage:index')

def add_purchasedetails(request,instrument_id):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			if(request.method=="POST"):
				instru_id = request.POST.get('instrument_id')
				print(instru_id)
				date_of_purchase = request.POST.get('date_of_purchase')
				count_bought = request.POST.get('count_bought')
				place_of_purchase = request.POST.get('place_of_purchase')
				cursor.execute('SELECT * from Purchase_Details WHERE instrument_id=%s and date_of_purchase=%s and count_bought=%s and place_of_purchase=%s',[instrument_id,date_of_purchase,count_bought,place_of_purchase])
				det = dictfetchall(cursor)
				if(len(det)==0):
					cursor.execute('START TRANSACTION;')
					cursor.execute('INSERT INTO Purchase_Details VALUES(%s,%s,%s,%s)',[instrument_id,date_of_purchase,count_bought,place_of_purchase])
					cursor.execute('COMMIT;')
					return redirect('manager:viewinstruments')
				else:
					context={'instrument_id':instrument_id,'error_message':"Sorry the entry isn't valid"}
					return render(request,'manager/add_purchasedetails.html',context)

			else:
				context={'instrument_id':instrument_id,}
				return render(request,'manager/add_purchasedetails.html',context)
	else:
		return redirect('mainpage:index')

def add_instrument(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			if(request.method=="POST"):
				instrument_name = request.POST.get('instrument_name')
				cost_per_piece = request.POST.get('cost_per_piece')
				instrument_type = request.POST.get('instrument_type')
				
				cursor.execute('START TRANSACTION;')
				cursor.execute('INSERT INTO Instrument(instrument_name,cost_per_piece,instrument_type) VALUES(%s,%s,%s)',[instrument_name,cost_per_piece,instrument_type])
				cursor.execute('COMMIT;')
				return redirect('manager:viewinstruments')
				
			else:
				context={}
				return render(request,'manager/add_instrument.html',context)
	else:
		return redirect('mainpage:index')

def add_worker(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			if(request.method=="POST"):
				worker_name = request.POST.get('worker_name')
				worker_type = request.POST.get('worker_type')
				salary = request.POST.get('salary')
				date_of_joining = request.POST.get('date_of_joining')
				qualifications = request.POST.get('qualifications')
				street_no = request.POST.get('street_no')
				street_name = request.POST.get('street_name')
				apt_number = request.POST.get('apt_number')
				city = request.POST.get('city')
				state = request.POST.get('state')
				gender = request.POST.get('gender')
				account_no = request.POST.get('account_no')
				work_duration = request.POST.get('work_duration')
				contact = request.POST.get('contact')
				contacts = re.findall(r"[0-9]+",contact)
				final_contacts=set()
				for i in contacts:
					if(len(i)==11 and i[0]=='0'):
						final_contacts.add(i[1:])
					elif (len(i)==10):
						final_contacts.add(i)
					elif (len(i)==13 and i[0]=='+'):
						final_contacts.add(i[3:])

				cursor.execute('START TRANSACTION;')
				cursor.execute('INSERT INTO Worker(worker_name,worker_type,salary,date_of_joining,qualifications,street_no,street_name,apt_number,city,state,gender,account_no,work_duration) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[worker_name,worker_type,salary,date_of_joining,qualifications,street_no,street_name,apt_number,city,state,gender,account_no,work_duration])
				cursor.execute('SELECT LAST_INSERT_ID();')
				id_dd = dictfetchall(cursor)
				for i in final_contacts:
					cursor.execute('INSERT INTO Worker_Phone VALUES(%s,%s)',[id_dd[0]['LAST_INSERT_ID()'],i])
				cursor.execute('COMMIT;')
				return redirect('manager:viewworkers')
				
			else:
				context={}
				return render(request,'manager/add_worker.html',context)
	else:
		return redirect('mainpage:index')
def view_rooms(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			cursor.execute('SELECT * from Room')
			rooms = dictfetchall(cursor)
			context={'rooms':rooms,}
			return render(request,'manager/view_rooms.html',context)
	else:
		return redirect('mainpage:index')
def addroom(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			if(request.method=="POST"):
				Floor = request.POST.get('Floor')
				Type = request.POST.get('Type')
				Cost_Per_Day = request.POST.get('Cost_Per_Day')
				room_details = request.POST.get('room_details')
				cursor.execute('START TRANSACTION;')
				cursor.execute('INSERT INTO Room(Floor,Type,Cost_Per_Day,room_details) VALUES(%s,%s,%s,%s)',[Floor,Type,Cost_Per_Day,room_details])
				cursor.execute('COMMIT;')
				return redirect('manager:viewrooms')
				
			else:
				context={}
				return render(request,'manager/add_room.html',context)
	else:
		return redirect('mainpage:index')

def view_labs(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			cursor.execute('SELECT * from Lab')
			labs = dictfetchall(cursor)
			context={'labs':labs,}
			return render(request,'manager/view_labs.html',context)
	else:
		return redirect('mainpage:index')
def addlab(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			if(request.method=="POST"):
				lab_name = request.POST.get('lab_name')
				o = request.POST.get('lab_open_time')
				c = request.POST.get('lab_close_time')
				d = request.POST.get('lab_description')
				cursor.execute('START TRANSACTION;')
				cursor.execute('INSERT INTO Lab(lab_name,lab_open_time,lab_close_time,lab_description) VALUES(%s,%s,%s,%s)',[lab_name,o,c,d])
				cursor.execute('COMMIT;')
				return redirect('manager:viewlabs')
				
			else:
				context={}
				return render(request,'manager/add_lab.html',context)
	else:
		return redirect('mainpage:index')

def view_bills(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
		if(request.method=='POST'):
			if(request.POST.get('billno')):
				with connection.cursor() as cursor:
					bill_no = request.POST.get('billno')
					cursor.execute('START TRANSACTION;')
					cursor.execute('DELETE FROM Bill where bill_no=%s',[bill_no])
					cursor.execute('COMMIT;')
				response_data={}
				return HttpResponse(json.dumps(response_data),content_type='application/json')
			else:
				with connection.cursor() as cursor:
					bill_no = request.POST.get('bill_no')
					bill_date = request.POST.get('bill_date')
					doc_charges = request.POST.get('doc_charges')
					room_charges = request.POST.get('room_charges')
					medicine_charges = request.POST.get('medicine_charges')
					service_charges = request.POST.get('service_charges')
					patient_id = request.POST.get('patient_id')
					cursor.execute('START TRANSACTION;')
					cursor.execute('UPDATE Bill SET patient_id=%s,bill_date=%s,doc_charges=%s,room_charges=%s,medicine_charges=%s,service_charges=%s WHERE bill_no=%s',[patient_id,bill_date,doc_charges,room_charges,medicine_charges,service_charges,bill_no])
					cursor.execute('COMMIT;')
				response_data={}
				return HttpResponse(json.dumps(response_data),content_type='application/json')

		else:
			with connection.cursor() as cursor:
				cursor.execute('SELECT * from Bill')
				bills = dictfetchall(cursor)
				context={'bills':bills,}
				return render(request,'manager/view_bills.html',context)
	else:
		return redirect('mainpage:index')


def addbill(request):
	if(request.user.is_authenticated):
		with connection.cursor() as cursor:
			cursor.execute('SELECT * from Managers where user_id=%s',[request.user.id])
			x = dictfetchall(cursor)
			if(len(x)==0):
				return redirect('mainpage:index')
			if(request.method=="POST"):
				patient_id = request.POST.get('patient_id')
				bill_date = request.POST.get('bill_date')
				doc_charges = request.POST.get('doc_charges')
				if(not doc_charges):
					doc_charges=0
				room_charges = request.POST.get('room_charges')
				if(not room_charges):
					room_charges=0
				medicine_charges = request.POST.get('medicine_charges')
				if(not medicine_charges):
					medicine_charges=0
				service_charges = request.POST.get('service_charges')
				if(not service_charges):
					service_charges=0
				cursor.execute('START TRANSACTION;')
				cursor.execute('INSERT INTO Bill(patient_id,bill_date,doc_charges,room_charges,medicine_charges,service_charges) VALUES(%s,%s,%s,%s,%s,%s)',[patient_id,bill_date,doc_charges,room_charges,medicine_charges,service_charges])
				cursor.execute('COMMIT;')
				return redirect('manager:viewbills')
				
			else:
				cursor.execute('SELECT * from Patients,auth_user WHERE Patients.user_id=auth_user.id')
				patients=dictfetchall(cursor)
				context={'patients':patients,}
				return render(request,'manager/add_bill.html',context)
	else:
		return redirect('mainpage:index')