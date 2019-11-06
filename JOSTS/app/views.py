"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest,JsonResponse
from app.models import Element,ElementText,Video,UserNote,Rule,RuleText,DrawnImage
from django.db.models import Q
from django.db.models import IntegerField
from django.db.models.functions import Cast
import re
from binascii import a2b_base64
from django.http import HttpResponse

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
    #elements = ElementText.objects.filter(language="EN")
    #vals = Element.objects.order_by('letter_value').values('letter_value').distinct()
    #groups = Element.objects.order_by('str_grp').values('str_grp').distinct()
    #Element.objects.filter(event="V").filter(letter_value='A').update(letter_value='')
    #Element.objects.filter(event="V").filter(letter_value_9='A').update(letter_value_9='')
    #Element.objects.filter(event="V").filter(letter_value_8='A').update(letter_value_8='')
    #Element.objects.filter(event="V").filter(letter_value_67='A').update(letter_value_67='')
    #Rule.objects.filter(section="Appendix 12").update(display_order=112,search_display='A12')
    #Rule.objects.filter(section="Appendix 7").update(display_order=107,search_display='A7')
    context = {
        'type':'element',
        'search_type':'element',
        'list_type':'element',
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
    vals = Element.objects.exclude(event="V").order_by('letter_value').values('letter_value').distinct()
    groups = Element.objects.order_by('str_grp').values('str_grp').distinct()
    ranges = Element.objects.order_by('range').values('range').exclude(range='').annotate(int_order=Cast('range',IntegerField())).order_by('int_order').distinct()
    groupDict = {}
    valueDict = {}
    #vvals = Element.objects.filter(event="V").filter(value__gte=7.0).filter(value__lt=8.0).update(range=7)
    #vvals = Element.objects.filter(event="V").filter(value__gte=8.0).filter(value__lt=9.0).update(range=8)
    #vvals = Element.objects.filter(event="V").filter(value__gte=9.0).filter(value__lt=10.0).update(range=9)
    #vvals = Element.objects.filter(event="V").filter(value__gte=10).update(range=10)
    Element.objects.filter(event="V").update(letter_value='')
    for group in groups:
        groupEvents = "search-" + " search-".join(str(events['event']) for events in Element.objects.filter(str_grp = group['str_grp']).order_by('event').values('event').distinct())
        groupDict[group['str_grp']] = groupEvents
    for value in vals:
        valueEvents = "search-" + " search-".join(str(events['event']) for events in Element.objects.filter(letter_value = value['letter_value']).order_by('event').values('event').distinct())
        valueDict[value['letter_value']] = valueEvents
    context = {
        'vals':vals,
        'groups': groups,
        'groupsEvents': groupDict,
        'valueEvents': valueDict,
        'events': ['FX','BB','UB','V'],
        'ranges': ranges,
        'type':'element',
        }
    return render(request, 'app/element_search.html',context=context)

def element_list(request):
    dget = dict(request.GET)
    query = Q(language="EN")
    for k,v in dget.items():
        innerQuery = Q()
        for i in v:
            kwargs = {'{0}'.format(k): i}
            innerQuery.add(Q(**kwargs), Q.OR)
        query.add(innerQuery,Q.AND)
    elements = ElementText.objects.filter(query).order_by('element__code_order')
   
    context = {
        'lang_elements': elements,
        'num_elements': str(len(elements)) + " Elements",
        }
    return render(request, 'app/element_list.html',context=context)


#RULES
def rules(request):
    context = {
        'type':'rule',
         'search_type':'rule',
        'list_type':'rule',
        }
    return render(request, 'app/elements_fixed.html',context=context)

def rule(request):
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

def rule_search(request):
    sections = Rule.objects.order_by('display_order','search_display','section').values('section','display_order','search_display').distinct()
    sectionDict = {}
    #for section in sections:
    #    sectionDict[section['section']] = section['search_];
    context = {
        'sections':sections,
        'sectionsDict': sectionDict,
        'type': 'rule',
        }
    return render(request, 'app/element_search.html',context=context)

def rule_list(request):
    dget = dict(request.GET)
    query = Q()
    for k,v in dget.items():
        innerQuery = Q()
        for i in v:
            kwargs = {'{0}'.format(k): i}
            innerQuery.add(Q(**kwargs), Q.OR)
        query.add(innerQuery,Q.AND)
    rules = RuleText.objects.filter(query).order_by('rule__display_order')
   
    context = {
        'rules': rules,
        'num_rules': str(len(rules)) + " Rules",
        }
    return render(request, 'app/rule_list.html',context=context)

#shorthand
def shorthand_training(request):
    context = {
        'type':'shorthand_trainer',
        'search_type':'element',
        'list_type':'element',
        }
    return render(request, 'app/elements_fixed.html',context=context)

def shorthand_trainer(request):
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
    return render(request, 'app/shorthand_trainer.html',context=context)

def save_record_image(request):
    d = DrawnImage(name='test', label='testl',event='fx')
    d.save()
    datauri = request.POST.get('data','')
    imgstr = re.search(r'base64,(.*)', datauri).group(1)
    binary_data = a2b_base64(imgstr)
    output = open('media/drawnimages/' + request.POST.get('disc','') + '/' + request.POST.get('event','') + '/' + request.POST.get('name','') + '.png', 'wb')
    output.write(binary_data)
    output.close()

    d = DrawnImage(name=request.POST.get('name','') + '.png', label=request.POST.get('label',''),event=request.POST.get('event',''))
    d.save()

    return HttpResponse(status=201)
    #canvasData = request.GET.get('data','').strip('data:image/png;base64,')
    #im = Image.open(canvasData)
    #im.save('test.png')