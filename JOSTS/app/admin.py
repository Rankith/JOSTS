from django.contrib import admin
from app.models import Element, ElementText, Video, UserNote, Rule, RuleText
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class ElementAdmin(ImportExportModelAdmin): 
#class ElementAdmin(admin.ModelAdmin): 
    list_display = ('id_number','str_grp','code_order','event','letter_value','value','id')
    list_filter = ('event','str_grp','letter_value','range')
    search_fields = ('id_number',)#comment if importing
    list_editable = ('str_grp','code_order','event','letter_value','value')#comment if importing
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ('user','element','note')
class ElementTextAdmin(ImportExportModelAdmin): 
#class ElementTextAdmin(admin.ModelAdmin):
    list_display = ('element','language','id_number_text','text','short_text','named','additional_info','hold_text')
    list_filter = ('element__event','element__str_grp','element__letter_value','element__range')
    search_fields = ('text','short_text','named') #comment if importing
    list_editable = ('language','id_number_text','text','short_text','named','additional_info','hold_text') #comment if importing

class RuleAdmin(ImportExportModelAdmin): 
    list_display = ('id','rule_id','event','section','rule_no','sub_rule')
    list_filter = ('event',)
    list_editable = ('event','section','rule_no','sub_rule')

class RuleTextAdmin(ImportExportModelAdmin):
    list_display = ('rule','cue','response','additional_info','rule_description','specific_deduction','cat0','cat1','cat2','cat3','cat4')
    list_filter = ('rule__event','rule__section')
    list_editable = ('cue','response','additional_info','rule_description','specific_deduction','cat0','cat1','cat2','cat3','cat4')
    list_search = ('cue','response','additional_info','rule_description')



admin.site.register(Element,ElementAdmin)
admin.site.register(ElementText,ElementTextAdmin)
admin.site.register(Rule,RuleAdmin)
admin.site.register(RuleText,RuleTextAdmin)
admin.site.register(Video)
admin.site.register(UserNote,UserNoteAdmin)