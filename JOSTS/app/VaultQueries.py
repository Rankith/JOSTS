from app.models import Element,ElementText,Video,UserNote
from django.db.models import Q

vals = Element.objects.filter(event="V").filter(value>=7.0).filter(value<8.0).update(range=7)