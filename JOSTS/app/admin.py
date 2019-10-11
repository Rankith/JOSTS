from django.contrib import admin
from app.models import Element, ElementText, Video

class ElementAdmin(admin.ModelAdmin):
    list_display = ('id_number','str_grp','code_order','event','letter_value','value')

admin.site.register(Element,ElementAdmin)
admin.site.register(ElementText)
admin.site.register(Video)