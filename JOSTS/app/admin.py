from django.contrib import admin
from app.models import Element, ElementText, Video, UserNote 
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class ElementAdmin(ImportExportModelAdmin): 
#class ElementAdmin(admin.ModelAdmin): 
    list_display = ('id_number','str_grp','code_order','event','letter_value','value','id')
    list_filter = ('event','str_grp','letter_value','range')
    #search_fields = ('id_number')#comment if importing
    #list_editable = ('id_number','str_grp','code_order','event','letter_value','value')#comment if importing
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ('user','element','note')
class ElementTextAdmin(ImportExportModelAdmin): 
#class ElementTextAdmin(admin.ModelAdmin):
    list_display = ('element','language','id_number_text','text','short_text','named','additional_info','hold_text')
    list_filter = ('element__event','element__str_grp','element__letter_value','element__range')
    #search_fields = ('text','short_text','named') #comment if importing
    #list_editable = ('element','language','id_number_text','text','short_text','named','additional_info','hold_text') #comment if importing

class ElementResource(resources.ModelResource):
    class Meta:
        model = Element

admin.site.register(Element,ElementAdmin)
admin.site.register(ElementText,ElementTextAdmin)
admin.site.register(Video)
admin.site.register(UserNote,UserNoteAdmin)