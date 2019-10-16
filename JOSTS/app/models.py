"""
Definition of models.
"""

from django.db import models
from django.conf import settings

# Create your models here.
class Video(models.Model):
    event = models.CharField(max_length=2)
    file = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)
    approved_johanna = models.BooleanField(default=False)
    def __str__(self):
        return self.event + " " + self.file

class Element(models.Model):
    event = models.CharField(max_length=2)
    str_grp = models.IntegerField(default=0)
    code_order = models.IntegerField(default=0)
    id_number = models.CharField(max_length=20)
    letter_value = models.CharField(max_length=1,default='A')
    value = models.DecimalField(max_digits=3,default=0.1,decimal_places=1)
    letter_value_9 = models.CharField(max_length=1,default='A')
    value_9 = models.DecimalField(max_digits=3,default=0.1,decimal_places=1)
    letter_value_8 = models.CharField(max_length=1,default='A')
    value_8 = models.DecimalField(max_digits=3,default=0.1,decimal_places=1)
    letter_value_67 = models.CharField(max_length=1,default='A')
    value_67 = models.DecimalField(max_digits=3,default=0.1,decimal_places=1)
    range = models.CharField(max_length=25,default='',blank=True)
    show_exercise_builder = models.BooleanField(default=False)
    videos = models.ManyToManyField(Video,blank=True)
    video_jump = models.CharField(max_length=255,blank=True)
    def __str__(self):
        return self.event + " " + str(self.id_number)
    def image_url(self):
        return self.event + self.id_number.replace(".","")

class ElementText(models.Model):
    element = models.ForeignKey(Element, on_delete=models.SET_NULL,null=True)
    language = models.CharField(max_length=2,default="EN")
    text = models.CharField(max_length=400,blank=True,default='')
    short_text = models.CharField(max_length=50,blank=True,default='')
    named = models.CharField(max_length=50,blank=True,default='')
    additional_info = models.CharField(max_length=400,blank=True,default='')
    id_number_text = models.CharField(max_length=50,blank=True,default='')
    hold_text = models.CharField(max_length=50,blank=True,default='')
    def __str__(self):
        return self.element.event + " " + self.text

class UserNote(models.Model):
    element = models.ForeignKey(Element, on_delete=models.SET_NULL,null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    note = models.CharField(max_length=400,blank=True,default='')