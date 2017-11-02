from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth.models import User,Group
from django.db import connection,transaction

# Create your views here.
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def index(request):
    template = loader.get_template('mainpage\startpage.html')
    #if request.user.is_authenticated:
    #   return HttpResponse(template.render({},request))
    #cursor.execute('CREATE TABLE IF NOT EXISTS User(ID INT PRIMARY KEY,Username VARCHAR(100) NOT NULL UNIQUE,'
    #               'Password VARCHAR(100) NOT NULL UNIQUE, first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100), '
    #               'email  VARCHAR(100))')
    with connection.cursor() as cursor:
        cursor.execute('CREATE TABLE IF NOT EXISTS DoctorSpeciality(label varchar(10) primary key,speciality varchar(30) not null)')
        cursor.execute('CREATE TABLE IF NOT EXISTS Lab(lab_id INTEGER PRIMARY KEY AUTO_INCREMENT,lab_name VARCHAR(100),lab_open_time time, lab_close_time time,no_doctors INT DEFAULT 0,no_workers INT DEFAULT 0)')
        cursor.execute('CREATE TABLE IF NOT EXISTS Services(service_id INTEGER PRIMARY KEY AUTO_INCREMENT, service_name VARCHAR(100), service_details TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS Room(room_id INTEGER PRIMARY KEY AUTO_INCREMENT,Floor Int, Type VARCHAR(100), Cost_Per_Day FLOAT, room_details TEXT)')

        cursor.execute('INSERT INTO Lab(lab_name,lab_open_time,lab_close_time) SELECT * FROM ( SELECT "Operation Theatre","8:00","22:00") AS TMP'
                       ' WHERE NOT EXISTS(SELECT lab_name,lab_open_time,lab_close_time FROM Lab WHERE lab_id=1) LIMIT 1;')
        cursor.execute('INSERT INTO Lab(lab_name,lab_open_time,lab_close_time) SELECT * FROM ( SELECT "CT SCAN","10:00","22:00") AS TMP'
                       ' WHERE NOT EXISTS(SELECT lab_name,lab_open_time,lab_close_time FROM Lab WHERE lab_id=2) LIMIT 1;')
        cursor.execute('CREATE TABLE IF NOT EXISTS Doctor(doctor_id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT, user_id int NOT NULL, speciality varchar(10),'
                      'degree VARCHAR(30), Street_no VARCHAR(10), Street_Name VARCHAR(100),lab INT,'
                       'Apt_Number VARCHAR(10),City VARCHAR(20), State VARCHAR(20), Zip_code VARCHAR(10), Gender CHAR(1),Work_Duration VARCHAR(10),'
                       'Account_No VARCHAR(20) NOT NULL, foreign key(speciality) references DoctorSpeciality(label), '
                       'foreign key (user_id) REFERENCES auth_user(id),foreign key(lab) REFERENCES Lab(lab_id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS Doctor_Phone(doctor_id INT,contact VARCHAR(13),foreign key(doctor_id) references Doctor(doctor_id),primary key(doctor_id,contact))')
        cursor.execute('INSERT INTO DoctorSpeciality SELECT * FROM ( SELECT "GYN","Gynaeocologist") AS TMP'
                       ' WHERE NOT EXISTS(SELECT * FROM DoctorSpeciality WHERE label="GYN") LIMIT 1;')
        cursor.execute('INSERT INTO DoctorSpeciality SELECT * FROM ( SELECT "PAED","Padaetrician") AS TMP'
                       ' WHERE NOT EXISTS(SELECT * FROM DoctorSpeciality WHERE label="PAED") LIMIT 1;')
        cursor.execute('INSERT INTO DoctorSpeciality SELECT * FROM ( SELECT "PATH","Pathologist") AS TMP'
                        ' WHERE NOT EXISTS(SELECT * FROM DoctorSpeciality WHERE label="PATH") LIMIT 1;')
        cursor.execute('CREATE TABLE IF NOT EXISTS Unregistered_Patients(email varchar(100) primary key,'
                           'username varchar(100) not null, dob date, contact varchar(13),address varchar(100), street varchar(50),'
                           'city varchar(20),zip_code varchar(6))')
        cursor.execute('CREATE TABLE IF NOT EXISTS UnregisteredAppointments(appointment_id INTEGER primary key AUTO_INCREMENT,'
                           'patient varchar(100),appointment_date date,appointment_time time,department varchar(100), '
                            'appointment_purpose varchar(100),doctor_id int,foreign key(doctor_id) references Doctor(doctor_id),'
                            'foreign key(patient) references Unregistered_Patients(email))')
        cursor.execute('CREATE TABLE IF NOT EXISTS Patients(patient_id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT, user_id int NOT NULL, type varchar(10),'
                      'DOB date,BloodGroup Varchar(5),Job VARCHAR(20),Street_no VARCHAR(10), Street_Name VARCHAR(100),'
                       'Apt_Number VARCHAR(10),City VARCHAR(20), State VARCHAR(20), Zip_code VARCHAR(10), Gender CHAR(1),'
                       'Account_No VARCHAR(20) NOT NULL, foreign key (user_id) REFERENCES auth_user(id))')
        #AadharCardNo for Patient
        cursor.execute('CREATE TABLE IF NOT EXISTS Patient_Phone(patient_id INT,contact VARCHAR(13), foreign key(patient_id) references Patients(patient_id),primary key(patient_id,contact))')

        cursor.execute('CREATE TABLE IF NOT EXISTS room_booked(room_id INT, patient_id INT, foreign key(room_id) REFERENCES Room(room_id), foreign key(patient_id) REFERENCES Patients(patient_id),primary key(room_id,patient_id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS RegisteredAppointments(id INTEGER PRIMARY KEY AUTO_INCREMENT,patient_id INT, '
                       'appointment_date date,appointment_time time,department varchar(100),appointment_purpose varchar(100),'
                       'doctor_id int,foreign key(doctor_id) references Doctor(doctor_id),'
                            'foreign key(patient_id) references Patients(patient_id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS Appointments(id INTEGER PRIMARY KEY AUTO_INCREMENT, unregistered_id INTEGER, registered_id INTEGER, is_registered bool, foreign key(unregistered_id) references UnregisteredAppointments(appointment_id), '
                       'foreign key(registered_id) references RegisteredAppointments(id))')
        cursor.execute("create table if not exists Schedule(start_time time not null,end_time time not null, date date not null,day char(100),message char(200),doctor_id int,is_appointment boolean default 0,is_examination boolean default 0, appointment_id int, foreign key(appointment_id) references Appointments(id),foreign key(doctor_id) references Doctor(doctor_id),primary key(doctor_id,date,start_time,end_time))")
        cursor.execute("CREATE TABLE IF NOT EXISTS Notifications(notification_id INTEGER PRIMARY KEY AUTO_INCREMENT, notification_message TEXT,patient_id INT NOT NULL,FOREIGN KEY(patient_id) REFERENCES Patients(patient_id));")
        cursor.execute("CREATE TABLE IF NOT EXISTS Diseases(disease_id INTEGER PRIMARY KEY AUTO_INCREMENT, disease_name text)")
        cursor.execute("CREATE TABLE IF NOT EXISTS Examination(examination_date date NOT NULL, examination_type VARCHAR(100) NOT NULL,start_time time NOT NULL,end_time time NOT NULL, "
                       "patient_id int NOT NULL, doctor_id INT NOT NULL, disease int, Outcome text, Treatment text,lab int, is_done boolean, foreign key(lab) references Lab(lab_id), "
                       " foreign key(patient_id) references Patients(patient_id) "
                       ", foreign key(doctor_id) references Doctor(doctor_id),foreign key(disease) references Diseases(disease_id), PRIMARY KEY(examination_date,examination_type,start_time,end_time,patient_id,doctor_id))")
        
        cursor.execute('CREATE TABLE IF NOT EXISTS Managers(user_id INT, foreign key(user_id) REFERENCES auth_user(id),primary key(user_id))')
        #How to add constraint for schedule to be a foreign key of examination
        #How to create weak entity with another weak entity.
        cursor.execute("CREATE TABLE IF NOT EXISTS History(id INTEGER PRIMARY KEY AUTO_INCREMENT,disease INT NOT NULL, details TEXT, start_date date, end_date date, patient_id INT NOT NULL,"
                       "foreign key(disease) REFERENCES Diseases(disease_id), foreign key(patient_id) references Patients(patient_id) )")

        cursor.execute('CREATE TABLE IF NOT EXISTS Medicine(medicine_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,name VARCHAR(30) NOT NULL)')
        cursor.execute('CREATE TABLE IF NOT EXISTS Medicine_Details(Invoice_No VARCHAR(10) NOT NULL, medicine_name INT, Batch_No VARCHAR(10), Date_of_Manufacture date,Date_of_Expiry date, Price float NOT NULL,Quantity INT, foreign key(medicine_name) references Medicine(medicine_id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS Instrument(instrument_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT, instrument_name VARCHAR(50),cost_per_piece float NOT NULL, instrument_type VARCHAR(20))')
        cursor.execute('CREATE TABLE IF NOT EXISTS Purchase_Details(instrument_id INTEGER, date_of_purchase date,count_bought INT, place_of_purchase VARCHAR(100), foreign key(instrument_id) references Instrument(instrument_id),primary key(instrument_id,date_of_purchase,count_bought,place_of_purchase))')
        cursor.execute('CREATE TABLE IF NOT EXISTS Worker(worker_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT, worker_name VARCHAR(50),worker_type VARCHAR(10),salary float,date_of_joining date,qualifications VARCHAR(100),street_no varchar(10),street_name varchar(20),apt_number varchar(10),city varchar(20),state varchar(20),gender varchar(20),account_no varchar(20),work_duration varchar(20))')
        cursor.execute('CREATE TABLE IF NOT EXISTS Worker_Phone(worker_id INTEGER NOT NULL,phone VARCHAR(13),foreign key(worker_id) references Worker(worker_id), primary key(worker_id,phone))')
        cursor.execute('CREATE TABLE IF NOT EXISTS Bill(bill_no INTEGER PRIMARY KEY AUTO_INCREMENT,bill_date date,patient_id INT,doc_charges float DEFAULT 0.0,room_charges float DEFAULT 0.0,medicine_charges float DEFAULT 0.0,service_charges float DEFAULT 0.0,foreign key(patient_id) references Patients(patient_id))')


        cursor.execute('SELECT * from Schedule')
        d = cursor.fetchall()
        print(d)
        transaction.commit()
        cursor.execute('SELECT * from DoctorSpeciality')
        #specialities = DoctorSpeciality.objects.raw('SELECT * from doctor_DoctorSpeciality')
        specialities = dictfetchall(cursor)
        #specialities = cursor.fetchall()
        cursor.execute('SELECT * FROM Lab')
        lab_details = dictfetchall(cursor)
        cursor.execute('SELECT * from Services')
        service_details = dictfetchall(cursor)
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
        print(user_type)
        context={'specialities':specialities,'service_details':service_details,'lab_details':lab_details,'user_type':user_type,}
        print(specialities)
        return HttpResponse(template.render(context, request))

def aboutus(request):
    cursor = connection.cursor()
    cursor.execute('SELECT * from Doctor')
    doctors = dictfetchall(cursor)
    doctor_details = []
    for i in range(len(doctors)):
        cursor.execute('SELECT * from auth_user WHERE id=%s',[doctors[i]['user_id']])
        user_details = dictfetchall(cursor)[0]
        z = doctors[i].update(user_details)
        cursor.execute('SELECT * from lab where lab_id=%s',[doctors[i]['lab']])
        lab_details = dictfetchall(cursor)[0]
        z = doctors[i].update(lab_details)
        cursor.execute('SELECT * from DoctorSpeciality where label=%s',[doctors[i]['speciality']])
        speciality_details = dictfetchall(cursor)[0]
        z = doctors[i].update(speciality_details)
        cursor.execute('SELECT * from Doctor_Phone where doctor_id=%s',[doctors[i]['doctor_id']])
        contact_details = dictfetchall(cursor)
        cc = {'contact':''}
        if(len(contact_details)!=0):
            cc['contact']+=contact_details[0]['contact']
        for j in range(1,len(contact_details)):
            cc['contact'] += str(',' + contact_details[j]['contact'])
        z = doctors[i].update(cc)
        doctor_details.append(doctors[i])
    cursor.execute('SELECT * FROM Lab')
    lab_details = dictfetchall(cursor)
    cursor.execute('SELECT * from Services')
    service_details = dictfetchall(cursor)
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

    context = {'doctors':doctor_details,'service_details':service_details,'lab_details':lab_details,'user_type':user_type,}
    return render(request, 'mainpage\\about-us.html', context)

def Login(request):
    next = request.GET.get('next', str('/home/'))
    with connection.cursor() as cursor:
        if next =='/home/':
            error=""
        else:
            error="Please LogIn First"
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            try:
                user = authenticate(username=username, password=password)
            except:
                return render(request, "mainpage\login.html",
                              {'redirect_to': "mainpage:index", 'error_message': 'Sorry provide correct details','error':error})

            if user is not None:
                if user.is_active:
                    login(request, user)
                    cursor.execute('SELECT * from Doctor where user_id=%s',[user.id])
                    doctor_object = dictfetchall(cursor)
                    if doctor_object is not None and len(doctor_object)>=1:
                        return redirect('doctor:index')

                    cursor.execute('SELECT * from Patients where user_id = %s',[user.id])
                    patient_object = dictfetchall(cursor)
                    #patient_object = Patient.objects.filter(user=request.user)
                    if patient_object is not None and len(patient_object)>=1:
                        return redirect('patient:index')
                    cursor.execute('SELECT * FROM Managers where user_id=%s',[user.id])
                    admin_object = dictfetchall(cursor)
                    if admin_object is not None and len(admin_object)>=1:
                        return redirect('manager:index')
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponse("Inactive User")
            else:
                return render(request, "mainpage\login.html",
                              {'redirect_to': "mainpage:index", 'error_message': 'Sorry provide correct details'})
        cursor.execute('SELECT * FROM Lab')
        lab_details = dictfetchall(cursor)
        cursor.execute('SELECT * from Services')
        service_details = dictfetchall(cursor)
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

        return render(request, "mainpage/login.html", {'redirect_to': next,'service_details':service_details,'lab_details':lab_details,'user_type':user_type,})

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


def Logout(request):
    logout(request)
    return HttpResponseRedirect("/home/")

def register(request):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Lab')
    lab_details = dictfetchall(cursor)
    cursor.execute('SELECT * from Services')
    service_details = dictfetchall(cursor)
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

    context={'service_details':service_details,'lab_details':lab_details,'user_type':user_type,}
    return render(request,'mainpage\\register_choose.html',context)

def check(request):
    if request.method== 'POST':
        choice=request.POST['type']
        if(choice=='doctor'):
            return HttpResponseRedirect("/doctor/register/")
        else:
            return HttpResponseRedirect("/patient/register/")


def book_appointment(request):
    print("HI")
    if request.method=="POST":
        username = request.POST.get("Username")
        email = request.POST.get("email")
        DOB = request.POST.get("dob")
        contact = request.POST.get("contact")
        appointment_date = request.POST.get("appointment_date")
        appointment_time = request.POST.get("appointment_time")
        department = request.POST.get("department")
        address = request.POST.get("Address")
        street = request.POST.get("Street")
        city = request.POST.get("City")
        zip_code = request.POST.get("Zipcode")
        appointment_purpose = request.POST.get("Appointment_Purpose")
        with connection.cursor() as cursor2:
            cursor2.execute('SELECT * from Unregistered_Patients where email = %s',[email])
            user = dictfetchall(cursor2)
            if len(user)>=1:
                return HttpResponse("Please <a href = '{% mainpage:login' %}' >logIn</a> to book more appointments, you\'ve already booked an appointment with this mail id before")

            else:
                print(department.strip())
                cursor2.execute('SELECT speciality from Doctor')
                print(cursor2.fetchall())
                cursor2.execute('SELECT doctor_id from Doctor where speciality = %s',[department.strip()])
                docs = cursor2.fetchall()
                print(type(appointment_time))
                print(docs)
                for i in docs:
                    #cursor2.execute('SELECT * from Schedule where doctor_id = %s and date= %s and ((start_time<=%s and end_time>=time(%s) and start_time!=end_time)'
                    #                'or (start_time>=time(%s) and start_time<=() ))',[i,appointment_date,appointment_time,appointment_time,appointment_time,appointment_time])
                    cursor2.execute('SELECT * from Schedule where doctor_id = %s and date= %s and ((start_time<=%s and end_time>%s and start_time!=end_time)'
                                    'or (start_time>=%s and start_time<%s))',[i[0],appointment_date,appointment_time,appointment_time,appointment_time,add(appointment_time,15)])

                    pc = cursor2.fetchall()
                    if len(pc)==0:
                        cursor2.execute('START TRANSACTION;')
                        cursor2.execute('Insert into Unregistered_Patients values(%s,%s,%s,%s,%s,%s,%s,%s)',[email,username,DOB,contact,address,street,city,zip_code])
                        cursor2.execute('INSERT INTO UnregisteredAppointments(patient,appointment_date,'
                               'appointment_time,department,appointment_purpose,doctor_id) VALUES(%s,%s,%s,%s,%s,%s)',
                                        [email,appointment_date,appointment_time,department,appointment_purpose,i[0]])
                        cursor2.execute('SELECT appointment_id from UnregisteredAppointments WHERE patient=%s',[email])
                        d = dictfetchall(cursor2)
                        cursor2.execute('INSERT INTO Appointments(unregistered_id,is_registered) VALUES (%s,%s)',[d[0]['appointment_id'],"0"])
                        cursor2.execute('SELECT LAST_INSERT_ID();')
                        d =dictfetchall(cursor2)
                        print(d)
                        print(d[0])
                        cursor2.execute('INSERT INTO Schedule(start_time,end_time,date,message,doctor_id,is_appointment,appointment_id) VALUES(%s,%s,%s,%s,%s,%s,%s)',[appointment_time,add(appointment_time,30),appointment_date,appointment_purpose,i[0],'1',d[0]['LAST_INSERT_ID()']])
                        cursor2.execute('SELECT * from auth_user,Doctor where doctor_id = %s and Doctor.user_id = auth_user.id',[i[0]])
                        name = dictfetchall(cursor2)
                        cursor2.execute('COMMIT;')
                        print(name)
                        #cursor2.execute('SELECT user_id from Doctor where doctor_id = %s',[i])
                        #id = cursor2.fetchall()
                        #cursor2.execute('SELECT username from auth_user where id = %s',[id])
                        #name = cursor2.fetchall()
                        return render(request,'mainpage/Thank_you.html',{'appointment_time':appointment_time,'name':name[0]})
                for i in docs:
                    cursor.execute('SELECT MIN(start_time) FROM Schedule WHERE doctor_id=%s and date=%s and (start_time>=%s and start_time<=%s)',[i[0],appointment_date,appointment_time,add(appointment_time,15)])
                    r = dictfetchall(cursor)
                    cursor2.execute('SELECT * from Schedule where doctor_id = %s and date = %s and start_time=%s and (start_time >=%s and '
                                'NOT EXISTS(SELECT * from Schedule where doctor_id = %s and date = %s and (end_time>=%s and end_time <=%s)))'
                                ,[i[0],appointment_date,r[0]['MIN(start_time)'],add(appointment_time,-15),i[0],appointment_date,add(appointment_time,-15),r[0]['MIN(start_time)']])
                        
                    pc = dictfetchall(cursor2)
                    if len(pc)>=1:
                        schedule = pc[0]
                        print(schedule)
                        if str(schedule['end_time'])>=appointment_time:
                            cursor2.execute('START TRANSACTION;')
                            cursor2.execute('Insert into Unregistered_Patients values(%s,%s,%s,%s,%s,%s,%s,%s)',[email,username,DOB,contact,address,street,city,zip_code])
                            cursor2.execute('INSERT INTO UnregisteredAppointments(patient,appointment_date,'
                               'appointment_time,department,appointment_purpose,doctor_id) VALUES(%s,%s,%s,%s,%s,%s)',
                                        [email,appointment_date,add(schedule['start_time'],-15),department,appointment_purpose,i[0]])
                            cursor2.execute('SELECT appointment_id from UnregisteredAppointments WHERE patient=%s',[email])
                            d = dictfetchall(cursor2)
                            cursor2.execute('INSERT INTO Appointments(unregistered_id,is_registered) VALUES (%s,%s)',[d[0]['appointment_id'],"0"])
                            cursor2.execute('SELECT LAST_INSERT_ID();')
                            d =dictfetchall(cursor2)
                            cursor2.execute('INSERT INTO Schedule(start_time,end_time,date,message,doctor_id,is_appointment,appointment_id) VALUES(%s,%s,%s,%s,%s,%s,%s)',[add(schedule['start_time'],-15),schedule['start_time'],appointment_date,appointment_purpose,i[0],'1',d[0]['LAST_INSERT_ID()']])

                            transaction.commit()
                            cursor2.execute('SELECT username from auth_user,Doctor where doctor_id = %s and Doctor.user_id = auth_user.id',[i[0]])
                            name = cursor2.fetchall()
                            cursor2.execute('COMMIT;')
                            #cursor2.execute('SELECT user_id from Doctor where doctor_id = %s',[i])
                            #id = cursor2.fetchall()
                            #cursor2.execute('SELECT username from auth_user where id = %s',[id])
                            #name = cursor2.fetchall()
                            return HttpResponse("Thank you your appointment has been booked at 15 minute before " + str(schedule['start_time']) + " with doctor <a href = '{% url 'mainpage:aboutus' %}'>" + name[0][0] + "</a>. Return to the <a href = {% url 'mainpage:index' %}> Homepage here</a>.")
                    cursor2.execute('SELECT MAX(end_time) FROM Schedule WHERE doctor_id = %s and date = %s and (start_time<=%s and end_time>%s)',[i[0],appointment_date,appointment_time,appointment_time])
                    r = dictfetchall(cursor)
                    cursor2.execute('SELECT * from Schedule where doctor_id = %s and date = %s and end_time=%s and (start_time<=%s and end_time>%s and end_time<=%s and NOT EXISTS(SELECT * FROM Schedule where doctor_id = %s and date = %s and start_time>=%s and start_time<=%s))',
                                        [i[0],appointment_date,r[0]['MAX(end_time)'],appointment_time,appointment_time,add(appointment_time,15),i[0],appointment_date,r[0]['MAX(end_time)'],add(r[0]['MAX(end_time)'],15)])
                    pc = dictfetchall(cursor2)
                    if len(pc)>=1:
                        schedule = pc[0]
                        if str(schedule['end_time'])>=appointment_time:
                            cursor2.execute('START TRANSACTION;')
                            cursor2.execute('Insert into Unregistered_Patients values(%s,%s,%s,%s,%s,%s,%s,%s)',[email,username,DOB,contact,address,street,city,zip_code])
                            cursor2.execute('INSERT INTO UnregisteredAppointments(patient,appointment_date,'
                               'appointment_time,department,appointment_purpose,doctor_id) VALUES(%s,%s,%s,%s,%s,%s)',
                                        [email,appointment_date,schedule['end_time'],department,appointment_purpose,i[0]])
                            cursor2.execute('SELECT appointment_id from UnregisteredAppointments WHERE patient=%s',[email])
                            d = dictfetchall(cursor2)
                            cursor2.execute('INSERT INTO Appointments(unregistered_id,is_registered) VALUES (%s,%s)',[d[0]['appointment_id'],'0'])
                            d =dictfetchall(cursor2)
                            print(d)
                            cursor2.execute('INSERT INTO Schedule(start_time,end_time,date,message,doctor_id,is_appointment,appointment_id) VALUES(%s,%s,%s,%s,%s,%s,%s)',[schedule['end_time'],add(schedule['end_time'],15),appointment_date,appointment_purpose,i[0],'1',d[0]['LAST_INSERT_ID()']])
                            transaction.commit()
                            cursor2.execute('SELECT username from auth_user,Doctor where doctor_id = %s and Doctor.user_id = auth_user.id',[i[0]])
                            name = cursor2.fetchall()
                            cursor2.execute('COMMIT;')
                            #cursor2.execute('SELECT user_id from Doctor where doctor_id = %s',[i])
                            #id = cursor2.fetchall()
                            #cursor2.execute('SELECT username from auth_user where id = %s',[id])
                            #name = cursor2.fetchall()
                            return HttpResponse("Thank you your appointment has been booked at " + str(schedule['end_time']) + " with doctor <a href = '{% url 'mainpage:aboutus' %}'>" + name[0][0] + "</a>. Return to the <a href = {% url 'mainpage:index' %}> Homepage here</a>.")

                return HttpResponse("Sorry no possible timeslot available as per your choice. Please book again for some other day.")
    else:
        return redirect('mainpage:index')

#cast(DATEADD(MINUTE,15,%s)as time)
def doctordetails(request,doctor_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM Doctor,auth_user,Lab where Doctor.lab=Lab.lab_id and Doctor.doctor_id=%s and Doctor.user_id=auth_user.id',[doctor_id])
        doctor_dets = dictfetchall(cursor)
    if(len(doctor_dets)==0):
        return redirect('mainpage:index')
    if(len(doctor_dets)==1):
        return render(request,'mainpage/doctor_detail.html',{'i':doctor_dets[0],})
