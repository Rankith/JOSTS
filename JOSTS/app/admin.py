from django.contrib import admin
from app.models import Skill, EnglishSkill, Video

class SkillAdmin(admin.ModelAdmin):
    list_display = ('id_number','str_grp','code_order','event','letter_value','value')

admin.site.register(Skill,SkillAdmin)
admin.site.register(EnglishSkill)
admin.site.register(Video)