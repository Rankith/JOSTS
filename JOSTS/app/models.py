"""
Definition of models.
"""

from django.db import models

# Create your models here.
class Skill(models.Model):
    event = models.CharField(max_length=2)
    str_grp = models.IntegerField(default=0)
    code_order = models.IntegerField(default=0)
    id_number = models.IntegerField(default=0)
    def __str__(self):
        return self.event + " " + str(self.id_number)

class EnglishSkill(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.SET_NULL,null=True)
    language = models.CharField(max_length=2)
    text = models.CharField(max_length=400)
    def __str__(self):
        return self.skill.event + " " + self.text
