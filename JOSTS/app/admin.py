from django.contrib import admin
from app.models import Element, ElementText, Video, UserNote

class ElementAdmin(admin.ModelAdmin):
    list_display = ('id_number','str_grp','code_order','event','letter_value','value')
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ('user','element','note')

admin.site.register(Element,ElementAdmin)
admin.site.register(ElementText)
admin.site.register(Video)
admin.site.register(UserNote,UserNoteAdmin)