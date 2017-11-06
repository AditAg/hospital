from django import forms
#from hospital.mainpage.models import Doctor
#from .models import Doctor,DoctorSpeciality
from django.db import connection

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class DoctorForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    username = forms.CharField(max_length=200)
    email = forms.CharField(max_length=200)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    with connection.cursor() as cursor:
        cursor.execute('SELECT * from doctorspeciality')
        doctor_specialities = dictfetchall(cursor)
    specialities=[]
    for obj in doctor_specialities:
        specialities.append((obj['label'],obj['speciality']))
    specialdd = tuple(specialities)
    speciality = forms.ChoiceField(choices=specialdd,required=True)
    degree = forms.CharField(max_length=30)
    with connection.cursor() as cursor:
        cursor.execute('SELECT * from Lab')
        doctor_lab = dictfetchall(cursor)
    labs=[]
    for obj in doctor_lab:
        labs.append((obj['lab_id'],obj['lab_name']))
    labs.append(("0","None"))
    labd = tuple(labs)
    lab = forms.ChoiceField(choices=labd,required=True)
    Street_no = forms.CharField(max_length=10, required=True)
    Street_Name = forms.CharField(max_length=100,required=True)
    Apt_number = forms.CharField(max_length=10)
    City = forms.CharField(max_length=10,required=True)
    State = forms.CharField(max_length=20)
    Zip_code = forms.CharField(max_length=10)
    Gender = forms.ChoiceField(choices = (('M','M'),('F','F')),required=True)
    Work_Duration = forms.CharField(max_length=10)
    Account_No = forms.CharField(max_length=15,required=True)
    contact = forms.CharField(max_length=100,required=True)


    #class Meta:
    #    model = Doctor
    #    fields = ['username','email','password','first_name','last_name','specialityD','specialization','certification']
        #widgets = {
        #    'name': forms.TextInput(attrs={'placeholder': 'What\'s your name?'}),
        #    'email': forms.TextInput(attrs={'placeholder': 'john@example.com'}),
        #    'gist': forms.TextInput(attrs={'placeholder': 'In a few words, I\'m looking for/to...'}),
        #    'expire': forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'})
        #}

