#from django.db import models
#from django import forms
#from django.contrib.auth.models import User
#from django.contrib import admin
# Create your models here.
#class Doctor(models.Model):
#    username = models.CharField(max_length=100,unique=True)
#    password = models.CharField(max_length=128)
#    name = models.CharField(max_length=100)
#    specialization = models.CharField(max_length=100)
'''class DoctorSpeciality(models.Model):
    speciality = models.CharField(max_length=30)
    label = models.CharField(max_length=10,primary_key=True)
    def __unicode__(self):
        return self.speciality

    def __str__(self):
        return self.speciality

    class Meta:
        verbose_name_plural = 'Doctors specialties'

class DoctorSpecialityAdmin(admin.ModelAdmin):
    search_fields = ('speciality', )




class Doctor(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    is_doctor = models.BooleanField(default=True)
    speciality = models.ForeignKey(DoctorSpeciality,default="Other")
    specialization = models.CharField(max_length=100)
    certification_CHOICES = (
        ('A', 'American Board'),
        ('B', 'Bachelor'),
    )
    certification = models.CharField(max_length=30, choices=certification_CHOICES)

    def __unicode__(self):
        return self.user.first_name + ' ' + self.user.last_name
    '''
