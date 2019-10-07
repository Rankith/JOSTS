"""
Definition of models.
"""

from django.db import models

# Create your models here.
class Video(models.Model):
    event = models.CharField(max_length=2)
    file = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)
    approved_johanna = models.BooleanField(default=False)
    def __str__(self):
        return self.event + " " + self.file

class Skill(models.Model):
    event = models.CharField(max_length=2)
    str_grp = models.IntegerField(default=0)
    code_order = models.IntegerField(default=0)
    id_number = models.IntegerField(default=0)
    letter_value = models.CharField(max_length=1,default='A')
    value = models.DecimalField(max_digits=3,default=0.1,decimal_places=1)
    range = models.CharField(max_length=25,default='',blank=True)
    show_exercise_builder = models.BooleanField(default=False)
    videos = models.ManyToManyField(Video,blank=True)
    video_jump = models.CharField(max_length=255,blank=True)
    def __str__(self):
        return self.event + " " + str(self.id_number)
    def image_url(self):
        return self.event + str(self.id_number)

class EnglishSkill(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.SET_NULL,null=True)
    language = models.CharField(max_length=2,default="EN")
    text = models.CharField(max_length=400)
    def __str__(self):
        return self.skill.event + " " + self.text
