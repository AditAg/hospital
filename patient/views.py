from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from .forms import PatientForm
from django.contrib.auth.models import User
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection,transaction
import json
import re

# Create your views here.
months = {'1':'January','2':'February','3':'March','4':'April','5':'May','6':'June','7':'July','8':'August','9':'September','10':'October','11':'November','12':'December'}

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
def xyz(history,stri):
    for i in range(len(history)):
        sched = history[i]
        year = sched[stri].year
        month = months[str(sched[stri].month)]
        dt = sched[stri].day
        history[i]['year']=year
        history[i]['month']=month
        history[i]['dt']=dt
    return history
def index(request):
    if request.method=="POST":
        if request.POST.get('seen')=="True":
            notif_id=request.POST.get('id')
            cursor = connection.cursor()
            cursor.execute('START TRANSACTION;')
            cursor.execute('DELETE FROM Notifications WHERE notification_id = %s',[notif_id])
            cursor.execute('COMMIT;')
            cursor.close()
            response_data = {}
            return HttpResponse(json.dumps(response_data),content_type='application/json')

    template = loader.get_template('patient/patient_loggedin.html')
    if request.user.is_authenticated:
        cursor = connection.cursor()
        cursor.execute('SELECT * from Patients WHERE user_id=%s',[request.user.id])
        patient_details = dictfetchall(cursor)
        if len(patient_details)>=1:
            cursor.execute('SELECT * from Notifications where patient_id=%s',[patient_details[0]['patient_id']])
            notifications = dictfetchall(cursor)
            cursor.execute('SELECT * from Examination WHERE patient_id=%s AND ((examination_date>cast(now() as date)) OR (examination_date=cast(now() as date) AND (start_time>=(cast(now() as time)))))',[patient_details[0]['patient_id']])
            upcoming_examinations= dictfetchall(cursor)
            print(upcoming_examinations)
            cursor.execute('SELECT * from Examination WHERE patient_id=%s AND ((examination_date<cast(now() as date)) OR (examination_date=cast(now() as date) AND (start_time<(cast(now() as time)))))',[patient_details[0]['patient_id']])
            previous_examinations = dictfetchall(cursor)
            print(previous_examinations)
            cursor.execute('SELECT * from RegisteredAppointments WHERE patient_id=%s AND ((appointment_date<cast(now() as date)) OR ((appointment_date=cast(now() as date)) AND (appointment_time<(cast(now() as time)))))',[patient_details[0]['patient_id']])
            previous_appointments = dictfetchall(cursor)
            cursor.execute('SELECT * from RegisteredAppointments WHERE patient_id=%s AND ((appointment_date>cast(now() as date)) OR ((appointment_date=cast(now() as date)) AND (appointment_time>=(cast(now() as time)))))',[patient_details[0]['patient_id']])
            upcoming_appointments = dictfetchall(cursor)
            cursor.execute('SELECT * FROM DoctorSpeciality')
            specialities = dictfetchall(cursor)
            cursor.execute('SELECT * FROM Lab')
            labs = dictfetchall(cursor)
            print(labs)
            cursor.execute('SELECT * from Diseases')
            disease = dictfetchall(cursor)
            cursor.execute('SELECT * FROM History,Diseases WHERE patient_id=%s and History.disease=Diseases.disease_id',[patient_details[0]['patient_id']])
            history = dictfetchall(cursor)
            history = xyz(history,'start_date')
            for i in range(len(history)):
                sched = history[i]
                year = sched['end_date'].year
                month = months[str(sched['end_date'].month)]
                dt = sched['end_date'].day
                history[i]['end_year']=year
                history[i]['end_month'] = month
                history[i]['end_dt'] = dt
            previous_appointments = xyz(previous_appointments,'appointment_date')
            upcoming_appointments = xyz(upcoming_appointments,'appointment_date')
            previous_examinations = xyz(previous_examinations,'examination_date')
            upcoming_examinations = xyz(upcoming_examinations,'examination_date')
            context = {'patient':patient_details[0],'notifications':notifications,'upcoming_examinations':upcoming_examinations,
            'previous_examinations':previous_examinations,'upcoming_appointments':upcoming_appointments,
            'previous_appointments':previous_appointments,'specialities':specialities,'history':history,'lab':labs,'disease':disease,}
        else:
            return HttpResponse("<h2>You need to log in , first to access this page</h2>")
    else:
        return HttpResponse("<h2> You need to log in, first to access this page</h2>")
    return HttpResponse(template.render(context,request))


def add(time,min):
    time = str(time)
    if(time=="noon"):
        time="12:00"
    l = time.split(':')
    hh = int(l[0])
    mm = int(l[1])
    if(min>0):
        mm = mm + min
        if mm >= 60:
            if hh==24:
                hh = 1
            else:
                hh = hh+1
            mm = mm - 60
    elif min<0:
        mm = mm + min
        if mm<0:
            if hh == 1:
                hh = 24
            else:
                hh = hh - 1
            mm = mm + 60
    return (str(hh) + ':' + str(mm))

class PatientFormView(View):
    form_class = PatientForm
    template_name = 'patient/registration_form.html'

    #display blank form
    def get(self,request):
        form = self.form_class(None)
        user_type=-1
        if(request.user.is_authenticated):
            cursor.execute('SELECT * FROM Doctor where user_id=%s',[request.user.id])
            is_doc = dictfetchall(cursor)
            if(len(is_doc)==0):
                cursor.execute('SELECT * from Patients where user_id=%s',[request.user.id])
                is_pat = dictfetchall(cursor)
                if(len(is_pat)==0):
                    user_type=2
                else:
                    user_type=1
            else:
                user_type=0
        return render(request,self.template_name,{'form':form,'user_type':user_type})

    #process form data
    def post(self,request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cursor = connection.cursor()
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            first_name=form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            type = form.cleaned_data['type']
            DOB = form.cleaned_data['DOB']
            contact_no = form.cleaned_data['contact_no']
            BloodGroup = form.cleaned_data['BloodGroup']
            AadharCard_No = form.cleaned_data['AadharCard_No']
            Job = form.cleaned_data['Job']
            Street_no = form.cleaned_data['Street_no']
            Street_Name = form.cleaned_data['Street_Name']
            Apt_Number = form.cleaned_data['Apt_number']
            City = form.cleaned_data['City']
            State = form.cleaned_data['State']
            Zip_code = form.cleaned_data['Zip_code']
            Gender = form.cleaned_data['Gender']
            Account_No = form.cleaned_data['Account_No']
            contacts = re.findall(r"[0-9]+",contact_no)
            final_contacts=set()
            for i in contacts:
                if(len(i)==11 and i[0]=='0'):
                    final_contacts.add(i[1:])

                elif (len(i)==10):
                    final_contacts.add(i)
                elif (len(i)==13 and i[0]=='+'):
                    final_contacts.add(i[3:])
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(username=username, email=email, password=password,first_name=first_name,last_name=last_name)
                cursor.execute('INSERT INTO Patients(user_id,type,DOB,BloodGroup,AadharCard_No,Job,Street_no,Street_Name,Apt_Number,City,State,Zip_code,'
                               'Gender,Account_No) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[user.id,type,DOB,BloodGroup,AadharCard_No,Job,Street_no,Street_Name,Apt_Number,City,State,Zip_code,Gender,Account_No])
                transaction.commit()
                user.save()
                cursor.execute('SELECT LAST_INSERT_ID();')
                val = dictfetchall(cursor)
                for i in final_contacts:
                    #check for duplicates and don't insert otherwise
                    #if i.
                    cursor.execute('INSERT INTO Patient_Phone VALUES(%s,%s)',[val[0]['LAST_INSERT_ID()'],i])
                #returns Doctor objects if credentials are correct
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('patient:index')
        form = self.form_class(None)
        return render(request,self.template_name,{'form':form,'error_message':"Sorry the username is taken"})

def Logout(request):
    logout(request)
    return HttpResponseRedirect('/home/')

def book(request):
    print("HI")
    if(request.user.is_authenticated):
        with connection.cursor() as cursor:
            cursor.execute('SELECT * from Patients WHERE user_id = %s',[request.user.id])
            patient_details = dictfetchall(cursor)
            if(len(patient_details)==1):
                if request.method=="POST":
                    appointment_date = request.POST.get("appointment_date")
                    appointment_time = request.POST.get("appointment_time")
                    department = request.POST.get("department")
                    appointment_purpose = request.POST.get("Appointment_Purpose")
                    comments = request.POST.get("comments")
                    cursor.execute('SELECT doctor_id from Doctor where speciality = %s',[department.strip()])
                    docs = cursor.fetchall()
                    for i in docs:
                        cursor.execute('SELECT * from Schedule where doctor_id = %s and date= %s and ((start_time<=%s and end_time>%s and start_time!=end_time) or (start_time>=%s and start_time<%s))',[i[0],appointment_date,appointment_time,appointment_time,appointment_time,add(appointment_time,15)])
                        pc = cursor.fetchall()
                        if len(pc)==0:
                            cursor.execute('START TRANSACTION;')
                            cursor.execute('INSERT INTO RegisteredAppointments(patient_id,appointment_date,'
                                   'appointment_time,department,appointment_purpose,doctor_id) VALUES(%s,%s,%s,%s,%s,%s)',
                                            [patient_details[0]['patient_id'],appointment_date,appointment_time,department,appointment_purpose,i[0]])
                            cursor.execute('SELECT LAST_INSERT_ID();')
                            d = dictfetchall(cursor)
                            cursor.execute('INSERT INTO Appointments(registered_id,is_registered) VALUES (%s,%s)',[d[0]['LAST_INSERT_ID()'],'1'])
                            cursor.execute('SELECT LAST_INSERT_ID();')
                            d =dictfetchall(cursor)
                            cursor.execute('INSERT INTO Schedule(start_time,end_time,date,message,doctor_id,is_appointment,appointment_id) VALUES(%s,%s,%s,%s,%s,%s,%s)',[appointment_time,add(appointment_time,30),appointment_date,appointment_purpose,i[0],'1',d[0]['LAST_INSERT_ID()']])
                            cursor.execute('SELECT username,doctor_id from auth_user,Doctor where doctor_id = %s and Doctor.user_id = auth_user.id',[i[0]])
                            name = dictfetchall(cursor)
                            cursor.execute('COMMIT;')
                            #cursor2.execute('SELECT user_id from Doctor where doctor_id = %s',[i])
                            #id = cursor2.fetchall()
                            #cursor2.execute('SELECT username from auth_user where id = %s',[id])
                            #name = cursor2.fetchall()
                            return render(request,'mainpage/Thank_you.html',{'appointment_time':appointment_time,'name':name[0]})
                    for i in docs:
                        cursor.execute('SELECT MIN(start_time) FROM Schedule WHERE doctor_id=%s and date=%s and (start_time>=%s and start_time<=%s)',[i[0],appointment_date,appointment_time,add(appointment_time,15)])
                        r = dictfetchall(cursor)
                        print(r)
                        cursor.execute('SELECT * from Schedule where doctor_id = %s and date = %s and start_time=%s and (start_time >=%s and '
                                        'NOT EXISTS(SELECT * from Schedule where doctor_id = %s and date = %s and (end_time>=%s and end_time <=%s)))'
                                        ,[i[0],appointment_date,r[0]['MIN(start_time)'],add(appointment_time,-15),i[0],appointment_date,add(appointment_time,-15),r[0]['MIN(start_time)']])
                        pc = dictfetchall(cursor)
                        if len(pc)>=1:
                            schedule = pc[0]
                            print(schedule)
                            if str(schedule['end_time'])>=appointment_time:
                                cursor.execute('START TRANSACTION;')
                                cursor.execute('INSERT INTO RegisteredAppointments(patient_id,appointment_date,'
                                   'appointment_time,department,appointment_purpose,doctor_id) VALUES(%s,%s,%s,%s,%s,%s)',
                                            [patient_details[0]['patient_id'],appointment_date,add(schedule['start_time'],-15),department,appointment_purpose,i[0]])
                                cursor.execute('SELECT LAST_INSERT_ID();')
                                d = dictfetchall(cursor)
                                cursor.execute('INSERT INTO Appointments(registered_id,is_registered) VALUES (%s,%s)',[d[0]['LAST_INSERT_ID()'],'1'])
                                cursor.execute('SELECT LAST_INSERT_ID();')
                                d =dictfetchall(cursor)
                                cursor.execute('INSERT INTO Schedule(start_time,end_time,date,message,doctor_id,is_appointment,appointment_id) VALUES(%s,%s,%s,%s,%s,%s,%s)',[add(schedule['start_time'],-15),schedule['start_time'],appointment_date,appointment_purpose,i[0],'1',d[0]['LAST_INSERT_ID()']])

                                transaction.commit()
                                cursor.execute('SELECT username from auth_user,Doctor where doctor_id = %s and Doctor.user_id = auth_user.id',[i[0]])
                                name = cursor2.fetchall()
                                cursor.execute('COMMIT;')
                                #cursor2.execute('SELECT user_id from Doctor where doctor_id = %s',[i])
                                #id = cursor2.fetchall()
                                #cursor2.execute('SELECT username from auth_user where id = %s',[id])
                                #name = cursor2.fetchall()
                                return HttpResponse("Thank you your appointment has been booked at 15 minute before " + str(schedule['start_time']) + " with doctor <a href =   > Homepage here</a>.")
                        cursor.execute('SELECT MAX(end_time) FROM Schedule WHERE doctor_id = %s and date = %s and (start_time<=%s and end_time>%s)',[i[0],appointment_date,appointment_time,appointment_time])
                        r = dictfetchall(cursor)
                        cursor.execute('SELECT * from Schedule where doctor_id = %s and date = %s and end_time=%s and (start_time<=%s and end_time>%s and end_time<=%s and NOT EXISTS(SELECT * FROM Schedule where doctor_id = %s and date = %s and start_time>=%s and start_time<=%s))',
                                        [i[0],appointment_date,r[0]['MAX(end_time)'],appointment_time,appointment_time,add(appointment_time,15),i[0],appointment_date,r[0]['MAX(end_time)'],add(r[0]['MAX(end_time)'],15)])
                        pc = dictfetchall(cursor)
                        if len(pc)>=1:
                            schedule = pc[0]
                            if str(schedule['end_time'])>=appointment_time:
                                cursor.execute('START TRANSACTION;')
                                cursor.execute('INSERT INTO RegisteredAppointments(patient_id,appointment_date,'
                                   'appointment_time,department,appointment_purpose,doctor_id) VALUES(%s,%s,%s,%s,%s,%s)',
                                            [patient_details[0]['patient_id'],appointment_date,schedule['end_time'],department,appointment_purpose,i[0]])
                                cursor.execute('SELECT LAST_INSERT_ID();')
                                d = dictfetchall(cursor)
                                cursor.execute('INSERT INTO Appointments(registered_id,is_registered) VALUES (%s,%s)',[d[0]['LAST_INSERT_ID()'],'1'])
                                cursor.execute('SELECT LAST_INSERT_ID();')
                                d = dictfetchall(cursor)
                                print(d)
                                cursor.execute('INSERT INTO Schedule(start_time,end_time,date,message,doctor_id,is_appointment,appointment_id) VALUES(%s,%s,%s,%s,%s,%s,%s)',[schedule['end_time'],add(schedule['end_time'],15),appointment_date,appointment_purpose,i[0],'1',d[0]['LAST_INSERT_ID()']])
                                transaction.commit()
                                cursor.execute('SELECT username from auth_user,Doctor where doctor_id = %s and Doctor.user_id = auth_user.id',[i[0]])
                                name = cursor.fetchall()
                                cursor.execute('COMMIT;')
                                #cursor2.execute('SELECT user_id from Doctor where doctor_id = %s',[i])
                                #id = cursor2.fetchall()
                                #cursor2.execute('SELECT username from auth_user where id = %s',[id])
                                #name = cursor2.fetchall()
                                return HttpResponse("Thank you your appointment has been booked at " + str(schedule['end_time']) + " with doctor <a href = '{% url 'mainpage:aboutus' %}'>" + name[0][0] + "</a>. Return to the <a href = {% url 'mainpage:index' %}> Homepage here</a>.")

                    return HttpResponse("Sorry no possible timeslot available as per your choice. Please book again for some other day.")
                else:
                    return redirect('patient:index')
            else:
                return HttpResponse("Sorry you need to be logged in as a patient to book an appointment here. Go to <a href='{% url 'mainpage:index' %}'> Homepage</a>.")
    else:
        return redirect('mainpage:index')

def appointmentdetails(request,appointment_id):
    return HttpResponse("Under construction")

def examinationdetails(request,examination_id):
    return HttpResponse("Under construction")   

def changedetails(request):
    if request.method=='GET':
        if(request.user.is_authenticated):
            with connection.cursor() as cursor:
                cursor.execute('SELECT type,DOB,BloodGroup,Job,Street_no,Street_Name,Apt_Number,City,State,Zip_code,Gender,Account_No,first_name,last_name,email,password FROM Patients,auth_user WHERE user_id=%s and Patients.user_id=auth_user.id',[request.user.id])
                patient_details = dictfetchall(cursor)
                pat_det = []
                for i in range(len(patient_details[0])):
                    pat_det.append((i,patient_details[0].keys()[i],patient_details[0].values()[i]))
                context={'patient_details':pat_det,}
                return render(request,'patient/change_details.html',context)
        else:
            return HttpResponse("Log In as Patient First")
    else:
        fields=["type","DOB","BloodGroup","Job","Street_no","Street_Name","Apt_Number","City","State","Zip_code","Gender","Account_No","first_name","last_name","email","password"]
        for i in fields:
            if(request.POST.get(i)):
                val = request.POST.get(i)
                with connection.cursor() as cursor:
                    cursor.execute('SELECT * from Patients WHERE user_id=%s',[request.user.id])
                    patient_details = dictfetchall(cursor)
                    if(len(patient_details)==1):
                        cursor.execute('START TRANSACTION;')
                        try:
                            if(i=="first_name"):
                                cursor.execute('UPDATE auth_user SET first_name=%s WHERE id=%s',[val,request.user.id])
                            elif(i=="last_name"):
                                cursor.execute('UPDATE auth_user SET last_name=%s WHERE id=%s',[val,request.user.id])
                            elif(i=="email"):
                                cursor.execute('UPDATE auth_user SET email_name=%s WHERE id=%s',[val,request.user.id])
                            elif(i=="password"):
                                cursor.execute('UPDATE auth_user SET password=%s WHERE id=%s',[val,request.user.id])
                            elif(i=="type"):
                                cursor.execute('UPDATE Patients SET type=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            elif(i=="DOB"):
                                cursor.execute('UPDATE Patients SET DOB=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            elif(i=="BloodGroup"):
                                cursor.execute('UPDATE Patients SET BloodGroup=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            elif(i=="Job"):
                                cursor.execute('UPDATE Patients SET Job=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            elif(i=="Street_no"):       
                                cursor.execute('UPDATE Patients SET Street_no=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            elif(i=="Street_Name"):
                                cursor.execute('UPDATE Patients SET Street_Name=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            elif(i=="Apt_Number"):
                                cursor.execute('UPDATE Patients SET Apt_Number=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            elif(i=="City"):
                                cursor.execute('UPDATE Patients SET City=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            elif(i=="State"):
                                cursor.execute('UPDATE Patients SET State=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            elif(i=="Zip_code"):
                                cursor.execute('UPDATE Patients SET Zip_code=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            elif(i=="Gender"):
                                cursor.execute('UPDATE Patients SET Gender=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            elif(i=="Account_No"):
                                cursor.execute('UPDATE Patients SET Account_No=%s WHERE patient_id=%s',[val,patient_details[0]['patient_id']])
                            else:
                                status = 500
                                response_data={}
                                response = HttpResponse(json.dumps(reponse_data),content_type='application/json')
                                response.status_code=status
                                return response
                        except:
                            status = 500
                            response_data={}
                            response = HttpResponse(json.dumps(reponse_data),content_type='application/json')
                            response.status_code=status
                            return response
                        
                        #cursor.execute('UPDATE Patients SET %s=%s WHERE patient_id=%s',[i,val,patient_details[0]['patient_id']])
                        cursor.execute('COMMIT;')
                        response_data={}
                        return HttpResponse(json.dumps(response_data),content_type='application/json')
                    else:
                        status = 500
                        response_data={}
                        response = HttpResponse(json.dumps(response_data),content_type='application/json')
                        response.status_code=status
                        return response

def request_examination(request):
    print("HI")
    if(request.user.is_authenticated):
        with connection.cursor() as cursor:
            cursor.execute('SELECT * from Patients WHERE user_id = %s',[request.user.id])
            patient_details = dictfetchall(cursor)
            if(len(patient_details)==1):
                if request.method=="POST":
                    appointment_date = request.POST.get("examination_date")
                    appointment_time = request.POST.get("examination_time")
                    lab = request.POST.get("lab")
                    print(appointment_date,appointment_time)
                    examination_purpose = request.POST.get("Examination_Purpose")
                    examination_type = request.POST.get("Examination_Type")
                    disease = request.POST.get("disease")
                    cursor.execute('SELECT doctor_id from Doctor where lab = %s',[lab])
                    docs = cursor.fetchall()
                    print(docs)
                    for i in docs:
                        cursor.execute('SELECT * from Schedule where doctor_id = %s and date= %s and ((start_time<=%s and end_time>%s and start_time!=end_time) or (start_time>=%s and start_time<%s))',[i[0],appointment_date,appointment_time,appointment_time,appointment_time,add(appointment_time,15)])
                        pc = cursor.fetchall()
                        if len(pc)==0:
                            cursor.execute('START TRANSACTION;')
                            cursor.execute('INSERT INTO Examination(patient_id,examination_date,disease,'
                                   'start_time,end_time,lab,examination_type,doctor_id,is_done) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                                            [patient_details[0]['patient_id'],appointment_date,disease,appointment_time,add(appointment_time,30),lab,examination_type,i[0],'0'])
                            cursor.execute('INSERT INTO Schedule(start_time,end_time,date,message,doctor_id,is_appointment,is_examination) VALUES(%s,%s,%s,%s,%s,%s,%s)',[appointment_time,add(appointment_time,30),appointment_date,"Examination Purpose"+ examination_purpose,i[0],'0','1'])
                            cursor.execute('SELECT username,doctor_id from auth_user,Doctor where doctor_id = %s and Doctor.user_id = auth_user.id',[i[0]])
                            name = dictfetchall(cursor)
                            cursor.execute('COMMIT;')
                            #cursor2.execute('SELECT user_id from Doctor where doctor_id = %s',[i])
                            #id = cursor2.fetchall()
                            #cursor2.execute('SELECT username from auth_user where id = %s',[id])
                            #name = cursor2.fetchall()
                            return render(request,'mainpage/Thank_you.html',{'appointment_time':appointment_time,'name':name[0]})
                    for i in docs:
                        cursor.execute('SELECT MIN(start_time) FROM Schedule WHERE doctor_id=%s and date=%s and (start_time>=%s and start_time<=%s)',[i[0],appointment_date,appointment_time,add(appointment_time,15)])
                        r = dictfetchall(cursor)
                        cursor.execute('SELECT * from Schedule where doctor_id = %s and date = %s and start_time=%s and (start_time >=%s and '
                                        'NOT EXISTS(SELECT * from Schedule where doctor_id = %s and date = %s and (end_time>=%s and end_time <=%s)))'
                                        ,[i[0],appointment_date,r[0]['MIN(start_time)'],add(appointment_time,-15),i[0],appointment_date,add(appointment_time,-15),r[0]['MIN(start_time)']])
                        pc = dictfetchall(cursor)
                        if len(pc)>=1:
                            schedule = pc[0]
                            print(schedule)
                            if str(schedule['end_time'])>=appointment_time:
                                cursor.execute('START TRANSACTION;')
                                cursor.execute('INSERT INTO Examination(disease,patient_id,examination_date,'
                                   'start_time,end_time,lab,examination_type,doctor_id,is_done) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                                            [disease,patient_details[0]['patient_id'],appointment_date,add(schedule['start_time'],-15),schedule['start_time'],lab,examination_type,i[0],'0'])
                                cursor.execute('INSERT INTO Schedule(start_time,end_time,date,message,doctor_id,is_appointment,is_examination) VALUES(%s,%s,%s,%s,%s,%s,%s)',[add(schedule['start_time'],-15),schedule['start_time'],appointment_date,"Examination Purpose"+ examination_purpose,i[0],'0','1'])

                                cursor.execute('SELECT username from auth_user,Doctor where doctor_id = %s and Doctor.user_id = auth_user.id',[i[0]])
                                name = cursor.fetchall()
                                cursor.execute('COMMIT;')
                                #cursor2.execute('SELECT user_id from Doctor where doctor_id = %s',[i])
                                #id = cursor2.fetchall()
                                #cursor2.execute('SELECT username from auth_user where id = %s',[id])
                                #name = cursor2.fetchall()
                                return HttpResponse("Thank you your examination has been booked at 15 minute before " + str(schedule['start_time']) + " with doctor <a href =  "" > Homepage here</a>.")
                        cursor.execute('SELECT MAX(end_time) FROM Schedule WHERE doctor_id = %s and date = %s and (start_time<=%s and end_time>%s)',[i[0],appointment_date,appointment_time,appointment_time])
                        r = dictfetchall(cursor)
                        cursor.execute('SELECT * from Schedule where doctor_id = %s and date = %s and end_time=%s and (start_time<=%s and end_time>%s and end_time<=%s and NOT EXISTS(SELECT * FROM Schedule where doctor_id = %s and date = %s and start_time>=%s and start_time<=%s))',
                                        [i[0],appointment_date,r[0]['MAX(end_time)'],appointment_time,appointment_time,add(appointment_time,15),i[0],appointment_date,r[0]['MAX(end_time)'],add(r[0]['MAX(end_time)'],15)])
                        pc = dictfetchall(cursor)
                        if len(pc)>=1:
                            schedule = pc[0]
                            if str(schedule['end_time'])>=appointment_time:
                                cursor.execute('START TRANSACTION;')
                                print(appointment_date,appointment_time)
                                cursor.execute('INSERT INTO Examination(disease,patient_id,examination_date,'
                                   'start_time,end_time,lab,examination_type,doctor_id,is_done) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                                            [disease,patient_details[0]['patient_id'],appointment_date,schedule['end_time'],add(schedule['end_time'],15),lab,examination_type,i[0],'0'])
                                cursor.execute('INSERT INTO Schedule(start_time,end_time,date,message,doctor_id,is_appointment,is_examination) VALUES(%s,%s,%s,%s,%s,%s,%s)',[schedule['end_time'],add(schedule['end_time'],15),appointment_date,"Examination Purpose"+ examination_purpose,i[0],'0','1'])
                                cursor.execute('SELECT username from auth_user,Doctor where doctor_id = %s and Doctor.user_id = auth_user.id',[i[0]])
                                name = cursor.fetchall()
                                cursor.execute('COMMIT;')
                                #cursor2.execute('SELECT user_id from Doctor where doctor_id = %s',[i])
                                #id = cursor2.fetchall()
                                #cursor2.execute('SELECT username from auth_user where id = %s',[id])
                                #name = cursor2.fetchall()
                                return HttpResponse("Thank you your examination has been booked at " + str(schedule['end_time']) + " with doctor <a href = '{% url 'mainpage:aboutus' %}'>" + name[0][0] + "</a>. Return to the <a href = {% url 'mainpage:index' %}> Homepage here</a>.")

                    return HttpResponse("Sorry no possible timeslot available as per your choice. Please book again for some other day.")
                else:
                    return redirect('patient:index')
            else:
                return HttpResponse("Sorry you need to be logged in as a patient to book an appointment here. Go to <a href='{% url 'mainpage:index' %}'> Homepage</a>.")
    else:
        return redirect('mainpage:index')

def enterhistory(request):
    if(request.method=='GET'):
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Diseases')
            diseases = dictfetchall(cursor)
            context={'diseases':diseases,}
        return render(request,'patient/enterhistory.html',context)
    else:
        with connection.cursor() as cursor:
            disease = request.POST.get('disease')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            details = request.POST.get('details')
            cursor.execute('SELECT patient_id from Patients WHERE user_id=%s',[request.user.id])
            patient_id = dictfetchall(cursor)
            if(len(patient_id)==1):
                cursor.execute('START TRANSACTION;')
                cursor.execute('INSERT INTO History(disease,start_date,end_date,patient_id,details) VALUES(%s,%s,%s,%s,%s)',[disease,start_time,end_time,patient_id[0]['patient_id'],details])
                cursor.execute('COMMIT;')
                return redirect('patient:index')
            else:
                return redirect('mainpage:index')

def showbills(request):
    if(request.user.is_authenticated):
        with connection.cursor() as cursor:
            cursor.execute('SELECT * from Patients WHERE user_id=%s',[request.user.id])
            patients = dictfetchall(cursor)
            if(len(patients)==1):
                cursor.execute('SELECT * from Bill WHERE patient_id=%s',[patients[0]['patient_id']])
                bills = dictfetchall(cursor)
                context={'bills':bills,}
                return render(request,'patient/show_bills.html',context)
            else:
                return redirect('mainpage:index')

    else:
        return redirect('mainpage:index')

