"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest,JsonResponse
from app.models import Element,ElementText,Video,UserNote

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )


def elements(request):
    elements = ElementText.objects.filter(language="EN")
    vals = Element.objects.order_by('letter_value').values('letter_value').distinct()
    groups = Element.objects.order_by('str_grp').values('str_grp').distinct()
    context = {
        'lang_elements': elements,
        'vals':vals,
        'groups': groups,
        'events': ['FX','BB','UB','V']
        }
    return render(request, 'app/elements_fixed.html',context=context)

def element(request):
    idIn = request.GET.get('id')
    element = ElementText.objects.filter(id=idIn)
    userNote = UserNote.objects.filter(user=request.user.id,element=idIn)
    if (len(userNote) > 0):
        userNote = userNote[0].note;
    else:
        userNote = '';
    context = {
        'lang_elements': element[0],
        'user_note': userNote,
        }
    return render(request, 'app/element.html',context=context)

def update_user_note(request):
    elementIn = request.GET.get('element')
    noteIn = request.GET.get('note')
    elementInstance = Element.objects.get(pk=elementIn)
    note, created = UserNote.objects.update_or_create(
        user=request.user.id,element=elementIn,
        defaults={'user': request.user,'element':elementInstance,'note':noteIn},
    )
    resp = {'updated':True}
    return JsonResponse(resp)

def element_search(request):
    idIn = request.GET.get('disc')
    vals = Element.objects.order_by('letter_value').distinct('letter_value')
    groups = Element.objects.order_by('str_grp').distinct('str_grp')
    context = {
        'vals':vals,
        'groups': groups,
        }
    return render(request, 'app/element_search.html',context=context)

def element_list(request):
    elements = ElementText.objects.filter(**request.GET)
   
    context = {
        'lang_elements': elements,
        }
    return render(request, 'app/element_list.html',context=context)