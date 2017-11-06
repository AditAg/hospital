from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from .forms import DoctorForm
from django.contrib.auth.models import User
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection,transaction
import json
from datetime import datetime,timedelta
import re
import smtplib

# Create your views here.
#def index(request,doctor_id):
    #if(request.user)
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

def convert_date(date):
    p = date.split(' ')
    month = p[0][:-1]
    date = p[1][:-1]
    year = p[2]
    m = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sept':'09','Oct':'10','Nov':'11','Dec':'12'}
    month = m[month]
    return str(year + '-' + month + '-' + date)

def convert_time(time):
    if(time=="noon"):
        return str("12:00")
    t = time.split(' ')
    d = t[0].split(':')
    if(len(d)==1):
        t[0] = t[0] + ':00'

    if(t[1]=="a.m."):
        return t[0]
    else:
        d = t[0].split(':')
        d[0] = str(int(d[0]) + 12)
        return str(d[0]+':'+t[1])
        
months = {'1':'January','2':'February','3':'March','4':'April','5':'May','6':'June','7':'July','8':'August','9':'September','10':'October','11':'November','12':'December'}
def index(request):
    if(request.method=="POST"):
        if(request.user.is_authenticated):
            with connection.cursor() as cursor:

                cursor.execute('SELECT * from doctor WHERE user_id=%s',[request.user.id])
                doctor_details = dictfetchall(cursor)
                if(len(doctor_details)==1):
                    start_time = request.POST.get('start_time')
                    end_time = request.POST.get('end_time')
                    examination_date = request.POST.get('examination_date')
                    Outcome = request.POST.get('Outcome')
                    Treatment = request.POST.get('Treatment')
                    start_time = convert_time(str(start_time))
                    end_time = convert_time(str(end_time))
                    examination_date = convert_date(str(examination_date))
                    cursor.execute('START TRANSACTION;')
                    cursor.execute('UPDATE examination SET Outcome=%s, Treatment=%s,is_done=%s WHERE examination_date=%s and start_time=%s and end_time=%s and doctor_id=%s',[Outcome,Treatment,'1',examination_date,start_time,end_time,doctor_details[0]['doctor_id']])
                    cursor.execute('COMMIT;')
                    response_data={}
                    return HttpResponse(json.dumps(response_data),content_type='application/json')
                else:
                    response_data={}
                    return HttpResponse(json.dumps(response_data),content_type='application/json')
        else:
            status = 500
            response_data={}
            response = HttpResponse(json.dumps(response_data),content_type='application/json')
            response.status_code=status
            return response

    template = loader.get_template('doctor/doctor_loggedin.html')
    with connection.cursor() as cursor:
        if request.user.is_authenticated:
            cursor.execute('SELECT * from doctor where user_id = %s',[request.user.id])
            doctor_details = dictfetchall(cursor)
            if len(doctor_details)>=1:
                cursor.execute('SELECT * from schedule WHERE doctor_id=%s',[doctor_details[0]['doctor_id']])
                schedule = dictfetchall(cursor)
                for i in range(len(schedule)):
                    sched = schedule[i]
                    year = sched['date'].year
                    month = months[str(sched['date'].month)]
                    dt = sched['date'].day
                    schedule[i]['year']=year
                    schedule[i]['month']=month
                    schedule[i]['dt']=dt
                now = datetime.now()
                now2 = datetime.now() + timedelta(days=2)
                year = now.year
                month = now.month
                day = now.day
                cursor.execute('SELECT * FROM examination,diseases,patients,auth_user WHERE doctor_id=%s and examination.disease = diseases.disease_id and examination.patient_id=patients.patient_id and patients.user_id = auth_user.id and ((examination.examination_date < cast(now() as date)) OR ((examination.examination_date=cast(now() as date)) AND (examination.start_time<cast(now() as time))))',[doctor_details[0]['doctor_id']])
                examinations = dictfetchall(cursor)
                cursor.execute('SELECT * FROM examination,diseases,patients,auth_user WHERE doctor_id=%s and examination.disease = diseases.disease_id and examination.patient_id=patients.patient_id and patients.user_id = auth_user.id and ((examination.examination_date >cast(now() as date)) OR (examination.examination_date = cast(now() as date) AND examination.start_time>=cast(now() as time)))',[doctor_details[0]['doctor_id']])
                upcoming_examinations = dictfetchall(cursor)
                cursor.execute('SELECT * from schedule WHERE doctor_id=%s and is_appointment=true and date >= cast(now() as date) and date<= cast((now() + interval 2 day) as date)',[doctor_details[0]['doctor_id']])
                appts = dictfetchall(cursor)
                appts = xyz(appts,'date')
                upcoming_examinations = xyz(upcoming_examinations,'examination_date')
                examinations = xyz(examinations,'examination_date')
                exams = []
                for i in range(len(examinations)):
                    exams.append((i,examinations[i]))
                cursor.execute('SELECT DISTINCT patient_id from examination WHERE doctor_id=%s and is_done=1 and (examination_date<cast(now() as date) or (examination_date=cast(now() as date) and start_time<cast(now() as time)))',[doctor_details[0]['doctor_id']])
                patients = dictfetchall(cursor)
                patient_det = []
                for i in patients:
                    cursor.execute('SELECT * from patients,auth_user WHERE patient_id=%s and patients.user_id=auth_user.id',[i['patient_id']])
                    pp = dictfetchall(cursor)
                    patient_det.append(pp[0])
                context = {'patients':patient_det,'doctor':doctor_details[0],'schedule':schedule,'appointments':appts,'examinations':exams,'upcoming_examinations':upcoming_examinations,}
            else:
                return HttpResponse("<h2>You need to log in as a doctor, first to access this page</h2>")
        else:
            return HttpResponse("<h2> You need to log in as a doctor, first to access this page</h2>")
        return render(request,'doctor/doctor_loggedin.html',context)


class DoctorFormView(View):
    form_class = DoctorForm
    template_name = 'doctor/registration_form.html'
    cursor = connection.cursor()
    #display blank form
    def get(self,request):
        form = self.form_class(None)
        user_type=-1
        if(request.user.is_authenticated):
            cursor.execute('SELECT * FROM doctor where user_id=%s',[request.user.id])
            is_doc = dictfetchall(cursor)
            if(len(is_doc)==0):
                cursor.execute('SELECT * from patients where user_id=%s',[request.user.id])
                is_pat = dictfetchall(cursor)
                if(len(is_pat)==0):
                    user_type=2
                else:
                    user_type=1
            else:
                user_type=0
        return render(request,self.template_name,{'form':form,'user_type':user_type,})

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
            degree = form.cleaned_data['degree']
            Street_no = form.cleaned_data['Street_no']
            Street_Name = form.cleaned_data['Street_Name']
            Apt_number = form.cleaned_data['Apt_number']
            City = form.cleaned_data['City']
            State = form.cleaned_data['State']
            Zip_code = form.cleaned_data['Zip_code']
            Gender = form.cleaned_data['Gender']
            Work_Duration = form.cleaned_data['Work_Duration']
            Account_No = form.cleaned_data['Account_No']
            contact = form.cleaned_data['contact']
            contacts = re.findall(r"[0-9]+",contact)
            final_contacts=set()
            for i in contacts:
                if(len(i)==11 and i[0]=='0'):
                    final_contacts.add(i[1:])

                elif (len(i)==10):
                    final_contacts.add(i)
                elif (len(i)==13 and i[0]=='+'):
                    final_contacts.add(i[3:])

            #cursor.execute('SELECT * from DoctorSpeciality where label=form.cleaned_data['specialityD'])
            #speciality = DoctorSpeciality.objects.raw('SELECT * from doctor_DoctorSpeciality where label = %s',[form.cleaned_data['specailityD']])
            speciality = form.cleaned_data['speciality']
            lab = form.cleaned_data['lab']
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                cursor.execute('START TRANSACTION;')
                user = User.objects.create_user(username=username, email=email, password=password,first_name=first_name,last_name=last_name)
                #cursor.execute('INSERT INTO auth_user(username,email,password,first_name,last_name) VALUES (%s,%s,%s,%s,%s)',[username,email,password,first_name,last_name])
                #cursor.execute('SELECT * from auth_user where username=%s',[username])
                #user = dictfetchall(cursor)
                #obj = form.save(commit=False)
                #obj.user = user
                #obj.speciality = speciality
                #obj.save()
                if(lab=="0"):
                    cursor.execute('INSERT INTO doctor(user_id,speciality,degree,Street_no,Street_Name,Apt_Number,City,State,Zip_code,'
                               'Gender,Work_Duration,Account_No) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[user.id,speciality,degree,Street_no,Street_Name,Apt_number,City,State,Zip_code,Gender,Work_Duration,Account_No])
                else:
                    cursor.execute('INSERT INTO doctor(user_id,speciality,degree,Street_no,Street_Name,lab,Apt_Number,City,State,Zip_code,'
                               'Gender,Work_Duration,Account_No) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[user.id,speciality,degree,Street_no,Street_Name,lab,Apt_number,City,State,Zip_code,Gender,Work_Duration,Account_No])
                cursor.execute('SELECT LAST_INSERT_ID();')
                val = dictfetchall(cursor)
                for i in final_contacts:
                    #check for duplicates and don't insert otherwise
                    #if i.
                    cursor.execute('INSERT INTO doctor_phone VALUES(%s,%s)',[val[0]['LAST_INSERT_ID()'],i])
                user.save()
                transaction.commit()
                cursor.execute('COMMIT;')
                #returns Doctor objects if credentials are correct
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request,user)
                        #user2 = Doctor.objects.filter(user=request.user)
                        #return redirect('doctor:index', doctor_id=user.id)
                        return redirect('doctor:index')
        form = self.form_class(None)
        return render(request,self.template_name,{'form':form,'error_message':"Sorry the username is taken"})

def Logout(request):
    logout(request)
    return HttpResponseRedirect('/home/')

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def add(time,min):
    l = time.split(':')
    hh = int(l[0])
    mm = int(l[1])
    if(min>0):
        mm = mm + min
        if mm > 60:
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

def Set(request):
    if(request.user.is_authenticated):
        if request.method=='GET':
            return render(request,'doctor/set_schedule.html',{})

        if request.method == 'POST':
            cursor = connection.cursor()
            cursor.execute('SELECT * from doctor WHERE user_id= %s',[request.user.id])
            doctor = dictfetchall(cursor)
            if len(doctor)==1:
                date = request.POST['date']
                day = request.POST['day']
                start_time = request.POST['start_time']
                end_time = request.POST['end_time']
                action = request.POST['action']
                message = request.POST['message']
                with connection.cursor() as cursor:
                    if action=='book':
                        cursor.execute('SELECT * from schedule where doctor_id=%s and date= %s and ((start_time>=%s and start_time<%s) or (end_time<=%s and end_time>%s)) ',[doctor[0]['doctor_id'],date,start_time,end_time,end_time,start_time])
                        d = dictfetchall(cursor)
                        no = 0
                        appts_to_reschedule=[]
                        other_schedules=[]
                        cursor.execute('SELECT * from examination where examination_date=%s and doctor_id=%s and ((start_time>=%s and start_time<%s) or (end_time<=%s and end_time>%s))',[doctor[0]['doctor_id'],date,start_time,end_time,end_time,start_time])
                        examinations = dictfetchall(cursor)
                        examinations_to_reschedule=[]
                        for i in d:
                            if i['is_appointment']:
                                #app = Appointment.objects.filter(id = i['appointment_id'])
                                cursor.execute('SELECT * from appointments where id = %s',[i['appointment_id']])
                                app = dictfetchall(cursor)
                                for p in app:
                                    if(p['is_registered']==0):
                                        cursor.execute('START TRANSACTION;')
                                        cursor.execute('SELECT patient from unregisteredappointments where appointment_id = %s',[p['unregistered_id']])
                                        z = dictfetchall(cursor)
                                        email_id = z[0]['patient']
                                        cursor.execute('DELETE FROM schedule WHERE doctor_id = %s AND start_time = %s'
                                                       'AND end_time = %s AND date = %s',[doctor[0]['doctor_id'],i['start_time'],i['end_time'],i['date']])
                                        cursor.execute('DELETE FROM appointments where id = %s',[p['id']])
                                        cursor.execute('DELETE FROM unregisteredappointments where appointment_id = %s',[p['unregistered_id']])
                                        cursor.execute('DELETE FROM unregistered_patients WHERE email=%s',[z[0]['patient']])
                                        cursor.execute('COMMIT;')
                                        TO = z[0]['patient']
                                        server='smtp.gmail.com'
                                        port=587
                                        sender='adit.agarwal.cse15@itbhu.ac.in'
                                        passwd = 'adit123@#06A'
                                        print("Hello")
                                        try:
                                            smtpobj=smtplib.SMTP('smtp.gmail.com:587')
                                            print("Done")
                                            smtpobj.ehlo()
                                            print("Done")
                                            smtpobj.starttls()
                                            print("Done")
                                            smtpobj.login(sender,passwd)
                                            print("Successfully logged in")
                                            message = "Your appointment from" + i['start_time'] + " to " + i['end_time'] + "has been cancelled. Please submit again."
                                            smtpobj.sendmail(sender,TO,message)
                                        except:
                                            continue


                                        #Use smtplib to send a mail to the mail id email_id that your appointment has been cancelled
                                    else:
                                        cursor.execute('SELECT registered_id from appointments where id=%s',[p['id']])
                                        z = dictfetchall(cursor)
                                        cursor.execute('SELECT * from registeredappointments where id = %s',[z[0]['registered_id']])
                                        z = dictfetchall(cursor)
                                        cursor.execute('SELECT * from patients where patient_id=%s',[z[0]['patient_id']])
                                        z = dictfetchall(cursor)
                                        cursor.execute('COMMIT;')
                                        appts_to_reschedule.append((no,i,z))
                                        #appts_to_reschedule.append((no,i))
                                        no = no + 1
                                        #Javascript Popup Here and also asking time for rescheduling appointment and also send a mail.
                                        #Also option for cancelling current schedule setting.
                                        #return render(request,'doctor/simple.html',{'appointment':i,'patient_details': app['patient']})
                            elif i['is_examination']:
                                cursor.execute('SELECT * from examination WHERE doctor_id=%s and examination_date=%s and start_time=%s and end_time=%s',[doctor[0]['doctor_id'],i['date'],i['start_time'],i['end_time']])
                                exam = dictfetchall(cursor)[0]
                                cursor.execute('SELECT * from patients,auth_user WHERE patient_id=%s and patients.user_id = auth_user.id',[exam['patient_id']])
                                z=dictfetchall(cursor)
                                examinations_to_reschedule.append((no,exam,z))
                                no = no + 1


                            else:
                                other_schedules.append((no,i))
                                no = no + 1
                        if len(appts_to_reschedule)+len(other_schedules)+len(examinations_to_reschedule)==0:
                            cursor.execute('INSERT INTO schedule(start_time,end_time,date,day,message,doctor_id) VALUES(%s,%s,%s,%s,%s,%s)',[start_time,end_time,date,day,message,doctor[0]['doctor_id']])
                            return redirect('doctor:index')
                        return render(request,'doctor/simple.html',{'appts':appts_to_reschedule,'other_appts':other_schedules,'examinations':examinations_to_reschedule,'date':str(date),'day':str(day),'start_time':str(start_time),'end_time':str(end_time),'action':'book','message':str(message),"doctor_id":str(doctor[0]['doctor_id'])})
                    else:
                        cursor.execute('SELECT * from schedule where doctor_id=%s and date= %s and ((start_time>=%s and start_time<=%s) or (end_time<=%s and end_time>=%s)) ',[doctor[0]['doctor_id'],date,start_time,end_time,end_time,start_time])
                        d = dictfetchall(cursor)
                        for i in d:
                            cursor.execute('START TRANSACTION;')
                            if i['start_time']>=add(end_time,-5):

                                cursor.execute('UPDATE schedule SET start_time=%s where doctor_id = %s and date = %s and start_time = %s and'
                                               'end_time = %s',[end_time,doctor[0]['doctor_id'],i['date'],i['start_time'],i['end_time']])
                                if(i['is_appointment']):
                                    cursor.execute('SELECT * from appointments WHERE id=%s',i['appointment_id'])
                                    appt = dictfetchall(cursor)
                                    if(appt[0]['is_registered']):
                                        cursor.execute('UPDATE registeredappointments SET appointment_time=%s where id=%s',[end_time,appt[0]['registered_id']])
                                        #can send a notifcation here as well.
                                    else:
                                        cursor.execute('SELECT * from unregisteredappointments WHERE appointment_id=%s',[appt[0]['unregistered_id']])
                                        cursor.execute('UPDATE unregisteredappointments SET appointment_time=%s WHERE appointment_id=%s',[end_time,appt[0]['unregistered_id']])
                                        
                                elif(i['is_examination']):
                                    cursor.execute('UPDATE examination SET start_time=%s WHERE doctor_id = %s and examination_date = %s and start_time = %s and'
                                               'end_time = %s',[end_time,doctor[0]['doctor_id'],i['date'],i['start_time'],i['end_time']])

                            elif(i['end_time']<=add(start_time,5)):
                                cursor.execute('UPDATE schedule SET end_time=%s where doctor_id = %s and date = %s and start_time = %s and'
                                               'end_time = %s',[start_time,doctor[0]['doctor_id'],i['date'],i['start_time'],i['end_time']])
                                if(i['is_appointment']):
                                    cursor.execute('SELECT * from appointments WHERE id=%s',i['appointment_id'])
                                    appt = dictfetchall(cursor)
                                    if(appt[0]['is_registered']):
                                        cursor.execute('UPDATE registeredappointments SET appointment_time=%s where id=%s',[start_time,appt[0]['registered_id']])
                                        #can send a notifcation here as well.
                                    else:
                                        cursor.execute('SELECT * from unregisteredappointments WHERE appointment_id=%s',[appt[0]['unregistered_id']])
                                        cursor.execute('UPDATE unregisteredappointments SET appointment_time=%s WHERE appointment_id=%s',[start_time,appt[0]['unregistered_id']])
                                        #can send a mail here as well
                                elif(i['is_examination']):
                                    cursor.execute('UPDATE examination SET end_time=%s WHERE doctor_id = %s and examination_date = %s and start_time = %s and'
                                               'end_time = %s',[start_time,doctor[0]['doctor_id'],i['date'],i['start_time'],i['end_time']])

                            else:
                                if(i['is_appointment']):
                                    cursor.execute('SELECT * FROM appointments WHERE id = %s',i['appointment_id'])
                                    appt = dictfetchall(cursor)
                                    cursor.execute('DELETE FROM schedule where doctor_id=%s and date= %s and start_time = %s and end_time = %s',[doctor[0]['doctor_id'],i['date'],i['start_time'],i['end_time']])
                                    cursor.execute('DELETE FROM appointments where id=%s',i['appointment_id'])
                                    if(appt[0]['is_registered']):
                                        cursor.execute('SELECT * FROM registeredappointments WHERE id=%s',[appt[0]['registered_id']])
                                        register = dictfetchall(cursor)
                                        cursor.execute('SELECT * from patients where patient_id =%s',[register[0]['patient_id']])
                                        patient_details = dictfetchall(cursor)
                                        
                                        cursor.execute('DELETE FROM registeredappointments WHERE id=%s',[register[0]['id']])
                                        cursor.execute('SELECT doctor_id,username from doctor,auth_user WHERE doctor_id = %s and doctor.user_id = auth_user.id',[register[0]['doctor_id']])
                                        doctor_details = dictfetchall(cursor)
                                        notification_message = "Your appointment dated " + str(i['date']) + " from " + str(i['start_time']) + " to " + i['end_time'] + "with the doctor "  + doctor_details[0]['username'] + " has been cancelled as the doctor has some important work. Book an appointment again for some other time"
                                        cursor.execute('INSERT INTO notifications(notification_message,patient_id) VALUES(%s,%s)',[notification_message,patient_details[0]['patient_id']])
                                    else:
                                        cursor.execute('SELECT * FROM unregisteredappointments WHERE appointment_id=%s',[appt[0]['unregistered_id']])
                                        register = dictfetchall(cursor)
                                        cursor.execute('SELECT * from unregistered_patients where email =%s',[register[0]['patient']])
                                        patient_details = dictfetchall(cursor)
                                        cursor.execute('DELETE FROM unregisteredappointments WHERE appointment_id=%s',[register[0]['appointment_id']])
                                        TO = patient_details[0]['patient']
                                        server='smtp.gmail.com'
                                        port=587
                                        sender='adit.agarwal.cse15@itbhu.ac.in'
                                        passwd = 'adit123@#06A'
                                        print("Hello")
                                        try:
                                            smtpobj=smtplib.SMTP('smtp.gmail.com:587')
                                            print("Done")
                                            smtpobj.ehlo()
                                            print("Done")
                                            smtpobj.starttls()
                                            print("Done")
                                            smtpobj.login(sender,passwd)
                                            print("Successfully logged in")
                                            message = "Your appointment from" + i['start_time'] + " to " + i['end_time'] + "has been cancelled. Please submit again."
                                            smtpobj.sendmail(sender,TO,message)
                                        except:
                                            continue


                                    
                                elif(i['is_examination']):
                                    cursor.execute('SELECT * from examination where examination_date=%s and doctor_id=%s and start_time=%s and end_time=%s',[i['date'],i['doctor_id'],i['start_time'],i['end_time']])
                                    exams = dictfetchall(cursor)
                                    cursor.execute('SELECT * from patients where patient_id=%s',[exams[0]['patient_id']])
                                    patient_details = dictfetchall(cursor)
                                    cursor.execute('DELETE FROM examination where examination_date=%s and start_time=%s and end_time=%s and doctor_id=%s',[i['date'],i['start_time'],i['end_time'],i['doctor_id']])
                                    cursor.execute('SELECT doctor_id from doctor WHERE lab=%s and doctor_id!=%s',[exams['lab'],i['doctor_id']])
                                    doctors = dictfetchall(cursor)
                                    flag=0
                                    for doc in doctors:
                                        if flag==0:
                                            cursor.execute('SELECT * from schedule WHERE doctor_id=%s and date=%s and ((start_time>=%s and start_time<%s) or (end_time<=%s and end_time>%s))',[doc['doctor_id'],exams[0]['examination_date'],exams[0]['start_time'],exams[0]['end_time'],exams[0]['end_time'],exams[0]['start_time']])
                                            dd = dictfetchall(cursor)
                                            if(len(dd)==0):
                                                cursor.execute('INSERT INTO examination VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[exams[0]['examination_date'],exams[0]['examination_type'],exams[0]['start_time'],exams[0]['end_time'],exams[0]['patient_id'],doc['doctor_id'],exams[0]['disease'],exams[0]['Outcome'],exams[0]['Treatment'],exams[0]['Lab'],'0'])
                                                flag = 1
                                                cursor.execute('UPDATE schedule SET doctor_id=%s WHERE start_time=%s and end_time=%s and date=%s and doctor_id=%s',[doc['doctor_id'],exams[0]['start_time'],exams[0]['end_time'],exams[0]['date'],exams[0]['doctor_id']])
                                    if flag==0:
                                        cursor.execute('SELECT lab_name from lab WHERE lab_id=%s',[exams[0]['lab']])
                                        lab = dictfetchall(cursor)
                                        cursor.execute('DELETE FROM schedule WHERE doctor_id=%s and date=%s and start_time=%s and end_time=%s',[exams[0]['doctor_id'],exams[0]['examination_date'],exams[0]['start_time'],exams[0]['end_time']])
                                        message = "Your examination for " + exams[0]['examination_date'] + " from "+ exams[0]['start_time'] + " to " + exams[0]['end_time'] + " with lab " + lab[0]['lab_name'] + " has been cancelled as no doctor is available."
                                        cursor.execute('INSERT INTO notifications(notification_message,patient_id) VALUES(%s,%s)',[message,patient_details[0]['patient_id']])
                                else:
                                    cursor.execute('DELETE FROM schedule WHERE start_time=%s and end_time=%s and doctor_id=%s and date=%s',[i['start_time'],i['end_time'],i['doctor_id'],i['date']])
                            cursor.execute('COMMIT;')

                        return HttpResponse("Thank you the schedule has been set. Go to <a href='{% url 'doctor:index' %}'>Home</a> here.>")
            else:
                return HttpResponse("Sorry you need to be logged in as a doctor to set the schedule")



    else:
        return redirect('mainpage:home')

def set_2(request):
    if request.method=='POST':
        start_time = str(request.POST['start_time'])
        end_time = str(request.POST['end_time'])
        date = str(request.POST['date'])
        doctor_id = str(request.POST['doctor_id'])
        day = str(request.POST['day'])
        message = str(request.POST['message'])
        cursor = connection.cursor()
        cursor.execute("INSERT INTO schedule(start_time,end_time,date,doctor_id,day,message) VALUES(%s,%s,%s,%s,%s,%s)",[start_time,end_time,date,doctor_id,day,message])
        transaction.commit()
        request_data={}
        return HttpResponse(json.dumps(request_data),content_type='application/json')


def check(request):
    if request.method=='POST':
        start_time = str(request.POST["start_time"])
        end_time = str(request.POST["end_time"])
        date = str(request.POST["date"])
        starttime_old = request.POST["starttime_old"]
        endtime_old = request.POST["endtime_old"]
        date_old = request.POST["date_old"]
        doctor_id = str(request.POST["doctor_id"])
        endtime_old = convert_time(str(endtime_old))
        starttime_old = convert_time(str(starttime_old))
        date_old = convert_date(str(date_old))
        print(start_time,end_time,date,starttime_old,endtime_old,date_old,doctor_id)
        with connection.cursor() as cursor:
            cursor.execute('SELECT * from schedule where doctor_id=%s and date= %s and ((start_time>=%s and start_time<%s)'
                           ' or (end_time<=%s and end_time>%s))',[doctor_id,date,start_time,end_time,end_time,start_time])
            z = dictfetchall(cursor)
            print(z)
            if(len(z)==0):
                cursor.execute('SELECT * from schedule WHERE doctor_id=%s and date=%s and start_time=%s and end_time=%s',[doctor_id,date_old,starttime_old,endtime_old])
                i = dictfetchall(cursor)
                cursor.execute('SELECT doctor_id,username from doctor,auth_user WHERE doctor_id = %s and doctor.user_id = auth_user.id',[doctor_id])
                doctor_details = dictfetchall(cursor)
                print(i,doctor_details,)
                cursor.execute('UPDATE schedule SET start_time=%s,date=%s,end_time=%s WHERE doctor_id=%s and date=%s and start_time=%s and end_time=%s',[start_time,date,end_time,doctor_id,date_old,starttime_old,endtime_old])
                print("Hello")
                if i[0]['is_appointment']:
                    cursor.execute('SELECT * from appointments where id=%s',[i[0]['appointment_id']])
                    i = dictfetchall(cursor)
                    cursor.execute('UPDATE registeredappointments SET appointment_time=%s and appointment_date=%s WHERE id=%s',[start_time,date,i[0]['registered_id']])
                    cursor.execute('SELECT * from registeredappointments WHERE id=%s',[i[0]['registered_id']])
                    p = dictfetchall(cursor)
                    cursor.execute('SELECT * from patients where patient_id =%s',[p[0]['patient_id']])
                    patient_details = dictfetchall(cursor)
                    notification_message = "Your appointment dated " + date_old + " from " + starttime_old + " to " + endtime_old + "with the doctor <a href = '{% url 'mainpage:doctordetails' " + doctor_details[0]['doctor_id'] + " %}'> " + doctor_details[0]['username'] + "</a> has been rescheduled to " + date + "from " + start_time + "to " + end_time + " as the doctor has some important work."
                    cursor.execute('INSERT INTO notifications(notification_message,patient_id) VALUES(%s,%s)',[notification_message,patient_details[0]['patient_id']])
                    transaction.commit()

                elif i[0]['is_examination']:
                    
                    cursor.execute('SELECT patient_id FROM examination WHERE examination_date=%s and doctor_id=%s and start_time=%s and end_time=%s',[i[0]['date'],i[0]['doctor_id'],i[0]['start_time'],i[0]['end_time']])
                    p = dictfetchall(cursor)
                    cursor.execute('UPDATE examination SET examination_date=%s, start_time=%s,end_time=%s WHERE examination_date=%s and doctor_id=%s and start_time=%s and end_time=%s',[date,start_time,end_time,i[0]['date'],i[0]['doctor_id'],i[0]['start_time'],i[0]['end_time']])
                    cursor.execute('SELECT * from patients where patient_id =%s',[p[0]['patient_id']])
                    patient_details = dictfetchall(cursor)
                    notification_message = "Your examination dated " + date_old + " from " + starttime_old + " to " + endtime_old + "with the lab has been rescheduled to " + date + "from " + start_time + "to " + end_time + " as the doctor has some important work."
                    cursor.execute('INSERT INTO notifications(notification_message,patient_id) VALUES(%s,%s)',[notification_message,patient_details[0]['patient_id']])
                    transaction.commit()
                print("Hello")
                response_data={'clash':'0',}
                return HttpResponse(json.dumps(response_data),content_type='application/json')
            else:
                response_data={'clash':'1',}
                return HttpResponse(json.dumps(response_data),content_type='application/json')


def cancel(request):
    print("Hello")
    if request.method=='POST':
        start_time = str(request.POST['s'])
        end_time = str(request.POST['e'])
        date = str(request.POST['d'])
        doctor_id = str(request.POST['doctor_id'])
        print(start_time,end_time,date,doctor_id)
        date = convert_date(date)
        start_time = convert_time(start_time)
        end_time = convert_time(end_time)
        print(start_time,end_time,date,doctor_id)
        with connection.cursor() as cursor:
            cursor.execute('SELECT * from schedule WHERE doctor_id=%s and date=%s and start_time=%s and end_time=%s',[doctor_id,date,start_time,end_time])
            p = dictfetchall(cursor)
            if(p[0]['is_appointment']):
                cursor.execute('START TRANSACTION;')
                cursor.execute('SELECT * from appointments where id=%s',[p[0]['appointment_id']])
                i = dictfetchall(cursor)
                cursor.execute('SELECT * from registeredappointments WHERE id=%s',[i[0]['registered_id']])
                q = dictfetchall(cursor)
                cursor.execute('DELETE FROM schedule WHERE doctor_id=%s and date=%s and start_time=%s and end_time=%s',[doctor_id,date,start_time,end_time])
                cursor.execute('DELETE FROM appointments WHERE id = %s',[i[0]['id']])
                cursor.execute('DELETE FROM registeredappointments WHERE id=%s',[q[0]['id']])
                cursor.execute('SELECT * from patients where patient_id =%s',[q[0]['patient_id']])
                patient_details = dictfetchall(cursor)
                cursor.execute('SELECT * from auth_user where id=%s',[patient_details[0]['user_id']])
                i = dictfetchall(cursor)
                cursor.execute('SELECT doctor_id,username from doctor,auth_user WHERE doctor_id = %s and doctor.user_id = auth_user.id',[p[0]['doctor_id']])
                doctor_details = dictfetchall(cursor)
                notification_message = "Your appointment dated " + str(date) + " from " + str(start_time) + " to " + str(end_time) + "with the doctor " + str(doctor_details[0]['username']) + "has been cancelled as the doctor has some important work. Book an appointment again for some other time"
                print(notification_message)
                cursor.execute('INSERT INTO notifications(notification_message,patient_id) VALUES(%s,%s)',[notification_message,patient_details[0]['patient_id']])
                transaction.commit()
                cursor.execute('COMMIT;')
                emailid= i[0]['email']
                #send a mail to emailid that your appointment has been cancelled by the doctor as he is busy please book it again for some other time.
                response_data={}
                return HttpResponse(json.dumps(response_data),content_type='application/json')
            elif(p[0]['is_examination']):
                cursor.execute('SELECT doctor_id from doctor WHERE doctor_id!=%s and lab=ANY(SELECT lab from doctor WHERE doctor_id=%s) ',[doctor_id,doctor_id])
                doctors = dictfetchall(cursor)
                flag=0
                cursor.execute('START TRANSACTION;')
                cursor.execute('DELETE FROM schedule WHERE doctor_id=%s and date=%s and start_time=%s and end_time=%s',[doctor_id,date,start_time,end_time])
                for doc in doctors:
                     if flag==0:
                        cursor.execute('SELECT * from schedule WHERE doctor_id=%s and date=%s and ((start_time>=%s and start_time<%s) or (end_time<=%s and end_time>%s))',[doc['doctor_id'],p[0]['date'],p[0]['start_time'],p[0]['end_time'],p[0]['end_time'],p[0]['start_time']])
                        dd = dictfetchall(cursor)
                        if(len(dd)==0):
                            cursor.execute('UPDATE examination SET doctor_id=%s WHERE examination_date=%s and start_time=%s and end_time=%s and doctor_id=%s',[doc['doctor_id'],p[0]['date'],p[0]['start_time'],p[0]['end_time'],doctor_id])
                            flag = 1
                            cursor.execute('UPDATE schedule SET doctor_id=%s WHERE start_time=%s and end_time=%s and date=%s and doctor_id=%s',[doc['doctor_id'],p[0]['start_time'],p[0]['end_time'],p[0]['date'],doctor_id])
                if flag==0:
                    cursor.execute('SELECT patient_id from examination WHERE examination_date=%s and start_time=%s and end_time=%s and doctor_id=%s',[date,start_time,end_time,doctor_id])
                    patient_details=dictfetchall(cursor)
                    cursor.execute('DELETE FROM examination WHERE examination_date=%s and start_time=%s and end_time=%s and doctor_id=%s',[date,start_time,end_time,doctor_id])
                    cursor.execute('SELECT l.lab_name from doctor d,lab l where d.doctor_id=%s and d.lab=l.lab_id',[doctor_id])
                    lab = dictfetchall(cursor)
                    message = "Your examination for " + date + " from "+ start_time + " to " + end_time + " with lab " + lab[0]['lab_name'] + " has been cancelled as no doctor is available."
                    cursor.execute('INSERT INTO notifications(notification_message,patient_id) VALUES(%s,%s)',[message,patient_details[0]['patient_id']])
                    cursor.execute('COMMIT;')
                    cursor.execute('SELECT * from auth_user,patients WHERE patients.user_id=auth_user.id and patients.patient_id=%s',[patient_details[0]['patient_id']])
                    i = dictfetchall(cursor)
                    emailid= i[0]['email']
                    #send a mail to emailid that your appointment has been cancelled by the doctor as he is busy please book it again for some other time.
                    response_data={}
                    return HttpResponse(json.dumps(response_data),content_type='application/json')
                response_data={}
                return HttpResponse(json.dumps(response_data),content_type='application/json')
            else:
                cursor.execute('DELETE FROM schedule WHERE doctor_id=%s and date=%s and start_time=%s and end_time=%s',[doctor_id,date,start_time,end_time])
                transaction.commit()
                response_data={}
                return HttpResponse(json.dumps(response_data),content_type='application/json')


def appointment_details(request,appointment_id):
    if request.user.is_authenticated:
       with connection.cursor() as cursor:
           cursor.execute('SELECT * from appointments WHERE id=%s',[appointment_id])
           i = dictfetchall(cursor)
           print(i)
           if(i[0]['is_registered']==1):
               cursor.execute('SELECT * FROM registeredappointments a,patients p,auth_user u WHERE a.id=%s and a.patient_id=p.patient_id and p.user_id=u.id',[i[0]['registered_id']])
               appt_details = dictfetchall(cursor)
               transaction.commit()
               return render(request,'doctor/doctor_reg_appointments.html',{'appointment_details':appt_details[0],})
           else:
               cursor.execute('SELECT * FROM unregisteredappointments a,unregistered_patients p WHERE a.appointment_id=%s and a.patient=p.email',[i[0]['unregistered_id']])
               appt_details = dictfetchall(cursor)
               transaction.commit()
               return render(request,'doctor/doctor_unreg_appointments.html',{'appointment_details':appt_details[0],})
    else:
        return HttpResponse("Please login first")