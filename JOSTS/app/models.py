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
    letter_value = models.CharField(max_length=2,default='',blank=True)
    value = models.DecimalField(max_digits=3,default='',blank=True,decimal_places=1)
    letter_value_9 = models.CharField(max_length=2,default='',blank=True)
    value_9 = models.DecimalField(max_digits=3,default='',blank=True,decimal_places=1)
    letter_value_8 = models.CharField(max_length=2,default='',blank=True)
    value_8 = models.DecimalField(max_digits=3,default='',blank=True,decimal_places=1)
    letter_value_67 = models.CharField(max_length=2,default='',blank=True)
    value_67 = models.DecimalField(max_digits=3,default='',blank=True,decimal_places=1)
    range = models.CharField(max_length=25,default='',blank=True)
    show_exercise_builder = models.BooleanField(default=False)
    videos = models.ManyToManyField(Video,blank=True)
    video_jump = models.CharField(max_length=255,blank=True)
    def __str__(self):
        return self.event + " " + str(self.id_number)
    def image_url(self):
        return self.event.lower() + self.id_number.replace(".","")

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

class Rule(models.Model):
    event = models.CharField(max_length=20,blank=True,default='')
    rule_id = models.CharField(max_length=30,blank=True,default='')
    section = models.CharField(max_length=30,blank=True,default='')
    rule_no = models.CharField(max_length=30,blank=True,default='')
    sub_rule = models.CharField(max_length=30,blank=True,default='')
    display_order = models.IntegerField(default=100)
    search_display = models.CharField(max_length=4,default='1')
    def __str__(self):
        return str(self.id)

class RuleText(models.Model):
    rule = models.ForeignKey(Rule, on_delete=models.SET_NULL,null=True)
    cue = models.TextField(blank=True,default='')
    response = models.TextField(blank=True,default='')
    additional_info = models.CharField(max_length=400,blank=True,default='')
    rule_description = models.CharField(max_length=400,blank=True,default='')
    specific_deduction = models.CharField(max_length=400,blank=True,default='')
    chapter_text = models.CharField(max_length=255,blank=True,default='')
    section_text = models.CharField(max_length=255,blank=True,default='')
    cat0 = models.CharField(max_length=30,blank=True,default='')
    cat1 = models.CharField(max_length=30,blank=True,default='')
    cat2 = models.CharField(max_length=30,blank=True,default='')
    cat3 = models.CharField(max_length=30,blank=True,default='')
    cat4 = models.CharField(max_length=30,blank=True,default='')

class DrawnImage(models.Model):
    name = models.CharField(max_length=255,blank=True,default='')
    label = models.CharField(max_length=255,blank=True,default='')
    event = models.CharField(max_length=2,blank=True,default='')

class SymbolDuplicate(models.Model):
    symbol = models.CharField(max_length=255,blank=True,default='')
    replace_with = models.CharField(max_length=255,blank=True,default='')
    event = models.CharField(max_length=2,blank=True,default='')

class SubscriptionTest(models.Model):
    stripe_sent = models.TextField(blank=True,default='')
    type = models.CharField(max_length=255,blank=True,default='')

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    customer_id = models.CharField(blank=True,default='',max_length=255)
    subscription_id = models.CharField(blank=True,default='',max_length=255)
    last_payment = models.DateField(null=True,default=None,blank=True)
    expires = models.DateField(null=True,default=None,blank=True)
    type = models.CharField(max_length=255,blank=True,default='')
    interval = models.CharField(max_length=15,blank=True,default='')
    cancelled = models.BooleanField(default=False)
    free = models.BooleanField(default=False)

class SubscriptionSetup(models.Model):
    display_text = models.CharField(max_length=255,blank=True,default='')
    stripe_plan_id = models.CharField(max_length=255,blank=True,default='')
    type = models.CharField(max_length=10,blank=True,default='')
    interval = models.CharField(max_length=10,blank=True,default='')
    def __str__(self):
       return str(self.display_text)