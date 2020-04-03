"""
Definition of models.
"""

from django.db import models
from django.conf import settings

# Create your models here.
class Disc(models.Model):
    display_name = models.CharField(max_length=10)
    folder_name = models.CharField(max_length=10)
    full_name = models.CharField(max_length=25,default='Womens')
    event_list = models.CharField(max_length=255,default='V,UB,BB,FX')
    vault_range_low = models.DecimalField(max_digits=3,default=7.0,decimal_places=1)
    vault_range_high = models.DecimalField(max_digits=3,default=10.1,decimal_places=1)
    def __str__(self):
       return self.display_name

class Video(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,null=True)
    event = models.CharField(max_length=2)
    file = models.CharField(max_length=255)
    fps = models.IntegerField(default=25)
    approved = models.BooleanField(default=False)
    approved_johanna = models.BooleanField(default=False)
    old_id = models.IntegerField(null=True,default=None)
    def __str__(self):
        return self.event + " " + self.file

class Element(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,null=True)
    event = models.CharField(max_length=2)
    str_grp = models.IntegerField(default=0)
    code_order = models.IntegerField(default=0)
    id_number = models.CharField(max_length=20)
    letter_value = models.CharField(max_length=2,default='',blank=True)
    value = models.DecimalField(max_digits=3,default='',blank=True,decimal_places=1)
    bonus = models.DecimalField(max_digits=3,default=0.0,blank=True,decimal_places=1)
    letter_value_9 = models.CharField(max_length=2,default='',blank=True)
    value_9 = models.DecimalField(max_digits=3,default=0.0,blank=True,decimal_places=1)
    bonus_9 = models.DecimalField(max_digits=3,default=0.0,blank=True,decimal_places=1)
    letter_value_8 = models.CharField(max_length=2,default='',blank=True)
    value_8 = models.DecimalField(max_digits=3,default=0.0,blank=True,decimal_places=1)
    bonus_8 = models.DecimalField(max_digits=3,default=0.0,blank=True,decimal_places=1)
    letter_value_67 = models.CharField(max_length=2,default='',blank=True)
    value_67 = models.DecimalField(max_digits=3,default=0.0,blank=True,decimal_places=1)
    bonus_67 = models.DecimalField(max_digits=3,default=0.0,blank=True,decimal_places=1)
    range = models.CharField(max_length=25,default='',blank=True)
    up_value_letter = models.CharField(max_length=2,default='',blank=True)
    down_value_letter = models.CharField(max_length=2,default='',blank=True)
    show_exercise_builder = models.BooleanField(default=False)
    old_id = models.IntegerField(null=True,default=None)

    def __str__(self):
        return self.event + " " + str(self.id_number)
    def image_url(self):
        return self.event.lower() + self.id_number.replace(".","")

class UnratedElement(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,null=True)
    event = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    old_id = models.IntegerField(null=True,default=None)

class VideoLink(models.Model):
    video = models.ForeignKey(Video,on_delete=models.CASCADE)
    element = models.ForeignKey(Element,on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    frame_jump = models.IntegerField(default=0)
    class Meta:
        ordering = ['order']

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
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,null=True)
    event = models.CharField(max_length=20,blank=True,default='')
    rule_id = models.CharField(max_length=30,blank=True,default='')
    section = models.CharField(max_length=30,blank=True,default='')
    rule_no = models.CharField(max_length=30,blank=True,default='')
    sub_rule = models.CharField(max_length=30,blank=True,default='')
    display_order = models.IntegerField(default=100)
    search_display = models.CharField(max_length=4,default='1')
    old_id = models.IntegerField(null=True,default=None)

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
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=255,blank=True,default='')
    label = models.CharField(max_length=255,blank=True,default='')
    event = models.CharField(max_length=2,blank=True,default='')

class SymbolDuplicate(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,null=True)
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

class QuizResult(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    event = models.CharField(max_length=20,blank=True,default='')
    date_completed = models.DateField(null=True,default=None,blank=True)
    correct = models.IntegerField(default=0)
    wrong = models.IntegerField(default=0)
    def total(self):
        return self.correct + self.wrong
    def percent(self):
        return int(round(self.correct/(self.correct + self.wrong),2)*100)
    missed = models.ManyToManyField(Element)
    type = models.CharField(max_length=20,blank=True,default='')

class ActivityLog(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,null=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    action_type = models.CharField(max_length=50)
    action_detail = models.CharField(max_length=50,blank=True,null=True)
    action_item = models.CharField(max_length=50,blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class UnsubscribeFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    expensive = models.BooleanField(default=False)
    dont_need = models.BooleanField(default=False)
    different_features = models.BooleanField(default=False)
    low_quality = models.BooleanField(default=False)
    hard_to_use = models.BooleanField(default=False)
    other = models.BooleanField(default=False)
    other_details = models.TextField(blank=True,default='')

class Theme(models.Model):
    file = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    def __str__(self):
        return str(self.name)

DEFAULT_THEME_ID = 1
class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL,null=True, default=DEFAULT_THEME_ID)

class RuleLink(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,null=True)
    text = models.CharField(max_length=255)
    rule = models.ManyToManyField(Rule)
    category_name = models.CharField(max_length=40,blank=True,default='')
    category_order = models.IntegerField(default=0)
    deduction_amount = models.IntegerField(default=0)
    connected_elements = models.IntegerField(default=0)
    type = models.CharField(max_length=1,blank=True,default='')
    event = models.CharField(max_length=2,blank=True,default='')
    old_id = models.IntegerField(null=True,default=None)
    def __str__(self):
        return self.event + " " + self.text

class VideoNote(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE,null=True)
    rule_link = models.ForeignKey(RuleLink, on_delete=models.SET_NULL,null=True,blank=True)
    element_link = models.ForeignKey(Element, on_delete=models.SET_NULL,null=True,blank=True)
    unrated_link = models.ForeignKey(UnratedElement, on_delete=models.SET_NULL,null=True,blank=True)
    frame = models.IntegerField(default=0)
    skip_frame = models.BooleanField(default=False)
    color = models.CharField(max_length=12,blank=True,default='')
    event = models.CharField(max_length=2,blank=True,default='')
    cr = models.CharField(max_length=6,blank=True,default='')
    override_text = models.CharField(max_length=255,blank=True,default='')
    no_value_type = models.CharField(max_length=25,blank=True,default='')
    timestamp = models.DateTimeField(auto_now=True)
    class Meta:
       ordering = ['-video__id']

class VideoNoteTemp(models.Model):
    video = models.ForeignKey(Video, on_delete=models.SET_NULL,null=True)
    rule_link = models.ForeignKey(RuleLink, on_delete=models.SET_NULL,null=True,blank=True)
    element_link = models.ForeignKey(Element, on_delete=models.SET_NULL,null=True,blank=True)
    frame = models.IntegerField(default=0)
    skip_frame = models.BooleanField(default=False)
    color = models.CharField(max_length=12,blank=True,default='')
    event = models.CharField(max_length=2,blank=True,default='')
    cr = models.CharField(max_length=6,blank=True,default='')
    override_text = models.CharField(max_length=255,blank=True,default='')
    no_value_type = models.CharField(max_length=25,blank=True,default='')
    timestamp = models.DateTimeField(auto_now=True)

class PageTour(models.Model):
    url = models.CharField(max_length=255)
    file = models.CharField(max_length=255)
    def __str__(self):
        return self.url

class UserToursComplete(models.Model):
    page = models.ForeignKey(PageTour, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)

class VersionSettings(models.Model):
    name = models.CharField(max_length=30)
    rule_sub_header = models.CharField(max_length=30,blank=True,default='Section')
    drawing_prefix = models.CharField(max_length=5,blank=True,default='')
    use_level_slider = models.BooleanField(default=True)

class StructureGroup(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.CASCADE,null=True)
    event = models.CharField(max_length=2,blank=True,default='')
    group = models.IntegerField(default=0)
    name = models.CharField(max_length=50,blank=True,default='')

class CompetitionType(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=3)
    display_order = models.IntegerField(default=1)
    def __str__(self):
        return self.short_name + " " + self.disc.display_name

class Competition(models.Model):
    type = models.ForeignKey(CompetitionType, on_delete=models.SET_NULL,null=True)
    year = models.CharField(max_length=4)
    short_name = models.CharField(max_length=3,blank=True, default='')
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name + " " + self.type.disc.display_name

class CompetitionGroup(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=3)
    def __str__(self):
        return self.short_name + " " + self.competition.name + " " + self.competition.type.disc.display_name

class CompetitionVideo(models.Model):
    competition_group = models.ForeignKey(CompetitionGroup, on_delete=models.SET_NULL,null=True)
    video = models.ForeignKey(Video,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

class TCExample(models.Model):
    video = models.ForeignKey(Video,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=1)
    year = models.CharField(max_length=4)
    short_name = models.CharField(max_length=3)
    special_notes = models.TextField(blank=True,default='')

class JudgeInstruction(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,null=True)
    event = models.CharField(max_length=2)
    year = models.CharField(max_length=4)
    type = models.CharField(max_length=1)