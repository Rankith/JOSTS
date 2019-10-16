from django.contrib import admin
from app.models import Element, ElementText, Video, UserNote 
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class ElementAdmin(ImportExportModelAdmin):
    list_display = ('id_number','str_grp','code_order','event','letter_value','value','id')
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ('user','element','note')
class ElementTextAdmin(ImportExportModelAdmin):
    list_display = ('element','language','text','short_text','named','additional_info')

class ElementResource(resources.ModelResource):
    class Meta:
        model = Element

admin.site.register(Element,ElementAdmin)
admin.site.register(ElementText,ElementTextAdmin)
admin.site.register(Video)
admin.site.register(UserNote,UserNoteAdmin)