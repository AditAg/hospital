from django.shortcuts import render
from django.db import connection,transaction

# Create your views here.
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def allservices(request):
	cursor = connection.cursor()
	cursor.execute('SELECT * FROM Lab')
	lab_details = dictfetchall(cursor)
	cursor.execute('SELECT * from Services')
	service_details = dictfetchall(cursor)
	print(lab_details,service_details)
	context = {'labs':lab_details,'services':service_details}
	return render(request,'services\services.html',context)

def lab_details(request,lab_id):
	cursor = connection.cursor()
	cursor.execute('SELECT * from Lab where lab_id=%s',[lab_id])
	lab_details = dictfetchall(cursor)
	print(lab_details)
	context = {'lab': lab_details[0],}
	return render(request,'services\lab_details.html',context)

def rooms(request):
	cursor = connection.cursor()
	cursor.execute('SELECT DISTINCT Type from Room')
	types = dictfetchall(cursor)
	context={'types':types,}
	return render(request,'services\services.html',context)