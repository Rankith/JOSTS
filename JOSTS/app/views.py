"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpRequest,JsonResponse
from app.models import Element,ElementText,Video,UserNote,Rule,RuleText,DrawnImage,SymbolDuplicate,SubscriptionTest
from django.db.models import Q
from django.db.models import IntegerField
from django.db.models.functions import Cast
import re
from binascii import a2b_base64
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, SubscriptionForm
from django.contrib.auth import authenticate, login
import stripe
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = 'sk_test_aHg8DgoSqtGog1R8gr7qt6jt00Cei8nZ3t'
    endpoint_secret = 'whsec_cLJSpiDXS58u5XJbbqbvpWKCSUQT7KU3'
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    st = SubscriptionTest(type=event['type'], stripe_sent = str(event['data']['object']))
    st.save()
    # Handle the checkout.session.completed event
    if event['type'] == 'invoice.payment_succeeded':
        session = event['data']['object']
        #handle_checkout_session(session)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fulfill the purchase...
        #handle_checkout_session(session)

    return HttpResponse(status=200)

@login_required(login_url='/login/')
def subscriptions(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            stripe.api_key = 'sk_test_aHg8DgoSqtGog1R8gr7qt6jt00Cei8nZ3t'
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                subscription_data={
                    'items': [{
                    'plan': form.cleaned_data.get('subscription'),
                    }],
                },
                success_url=request.build_absolute_uri("/") + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(),
            )
            return render(request, 'app/subscriptions.html', {'form': form,'checkout_session_id': session.id})
    else:
        form = SubscriptionForm()
    return render(request, 'app/subscriptions.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('/subscriptions')
    else:
        form = SignUpForm()
    return render(request, 'app/signup.html', {'form': form})

@login_required(login_url='/login/')
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
    display = dget['display'][0]
    del dget['display']
    search = dget['search'][0]
    search = search.replace("1/2","½")
    search = search.replace("1/4","¼")
    del dget['search']
    query = Q(language="EN")
    for k,v in dget.items():
        innerQuery = Q()
        for i in v:
            kwargs = {'{0}'.format(k): i}
            innerQuery.add(Q(**kwargs), Q.OR)
        query.add(innerQuery,Q.AND)
    elements = ElementText.objects.filter(query).order_by('element__code_order')
    if search != "":
        elements = elements.filter(element__usernote__note__icontains=search) | elements.filter(text__icontains=search) | elements.filter(short_text__icontains=search) | elements.filter(named__icontains=search) | elements.filter(additional_info__icontains=search)
    context = {
        'lang_elements': elements,
        'num_elements': str(len(elements)) + " Elements",
        'display': display,
        }
    return render(request, 'app/element_list.html',context=context)


#RULES
@login_required(login_url='/login/')
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
    search = dget['search'][0]
    search = search.replace("1/2","½")
    search = search.replace("1/4","¼")
    del dget['search']
    query = Q()
    for k,v in dget.items():
        innerQuery = Q()
        for i in v:
            kwargs = {'{0}'.format(k): i}
            innerQuery.add(Q(**kwargs), Q.OR)
        query.add(innerQuery,Q.AND)
    rules = RuleText.objects.filter(query).order_by('rule__display_order')
    if search != "":
        rules = rules.filter(cue__icontains=search) | rules.filter(response__icontains=search) | rules.filter(rule_description__icontains=search) | rules.filter(specific_deduction__icontains=search) | rules.filter(additional_info__icontains=search)
    context = {
        'rules': rules,
        'num_rules': str(len(rules)) + " Rules",
        }
    return render(request, 'app/rule_list.html',context=context)

#shorthand
@login_required(login_url='/login/')
def shorthand_training(request):
    #DrawnImage.objects.filter(label__contains='bb').update(event='bb')
    #dupes = SymbolDuplicate.objects.all()
    #for dupe in dupes:
        #DrawnImage.objects.filter(label=dupe.symbol).update(label=dupe.replace_with)
    Element.objects.filter(event="V").filter(value__gte=7.0).filter(value__lt=8.0).update(range=7)
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
    count = DrawnImage.objects.filter(label=element[0].element.image_url()).count()
    symbol_duplicates = SymbolDuplicate.objects.filter(event__iexact=element[0].element.event)
    if (len(userNote) > 0):
        userNote = userNote[0].note;
    else:
        userNote = '';
    context = {
        'lang_elements': element[0],
        'user_note': userNote,
        'count' : count,
        'symbol_duplicates' : symbol_duplicates
        }
    return render(request, 'app/shorthand_trainer.html',context=context)

def save_record_image(request):
    datauri = request.POST.get('data','')
    imgstr = re.search(r'base64,(.*)', datauri).group(1)
    binary_data = a2b_base64(imgstr)
    label_save = request.POST.get('label','')
    output = open('/' + settings.MEDIA_ROOT + '/drawnimages/' + request.POST.get('disc','') + '/' + request.POST.get('event','') + '/' + request.POST.get('name','') + '.png', 'wb')
    output.write(binary_data)
    output.close()
    replace_with = SymbolDuplicate.objects.filter(event=request.POST.get('event',''),symbol=request.POST.get('label',''))
    if (len(replace_with) != 0):
        label_save = replace_with[0].replace_with
    d = DrawnImage(name=request.POST.get('name','') + '.png', label=label_save,event=request.POST.get('event',''))
    d.save()

    count = DrawnImage.objects.filter(label=request.POST.get('label','')).count()

    return HttpResponse(count)
    #canvasData = request.GET.get('data','').strip('data:image/png;base64,')
    #im = Image.open(canvasData)
    #im.save('test.png')

@login_required(login_url='/login/')
def shorthand_lookup(request):
    context = {
        'type':'element',
        'search_type':'element',
        'list_type':'shorthand',
        }
    return render(request, 'app/shorthand_lookup.html',context=context)

def element_for_shorthand(request):
    idIn = request.GET.get('id')
    eventIn = request.GET.get('event')
    element = ElementText.objects.filter(element__id_number=idIn).filter(element__event=eventIn)
    context = {
        'lang_elements': element[0],
        }
    return render(request, 'app/element_for_shorthand.html',context=context)

def shorthand_search(request):
    vals ={}
    groups = {}
    ranges = {}
    groupDict = {}
    valueDict = {}
    #vvals = Element.objects.filter(event="V").filter(value__gte=7.0).filter(value__lt=8.0).update(range=7)
    #vvals = Element.objects.filter(event="V").filter(value__gte=8.0).filter(value__lt=9.0).update(range=8)
    #vvals = Element.objects.filter(event="V").filter(value__gte=9.0).filter(value__lt=10.0).update(range=9)
    #vvals = Element.objects.filter(event="V").filter(value__gte=10).update(range=10)

    context = {
        'vals':vals,
        'groups': groups,
        'groupsEvents': groupDict,
        'valueEvents': valueDict,
        'events': ['FX','BB','UB','V'],
        'ranges': ranges,
        'type':'shorthand',
        }
    return render(request, 'app/element_search.html',context=context)

def element_lookup(request):
    eventIn = request.GET.get('event')
    if (eventIn == "V"):
        vals = Element.objects.order_by('element__range').values('element__range').exclude(range='').annotate(int_order=Cast('element__range',IntegerField())).order_by('int_order').distinct()
    else:
        vals = Element.objects.filter(event=eventIn).order_by('letter_value').values('letter_value').distinct()   
    groups = Element.objects.filter(event=eventIn).order_by('str_grp').values('str_grp').distinct()
    elements = ElementText.objects.filter(element__event=eventIn,language="EN").order_by('element__str_grp','element__letter_value','element__code_order')
    context = {
        'vals':vals,
        'groups': groups,
        'elements': elements,
        'event':eventIn,
        }
    return render(request, 'app/element_lookup.html',context=context)

#Quiz
@login_required(login_url='/login/')
def quiz_shorthand(request):
    context = {
        'type':'shorthand',
        }
    return render(request, 'app/quiz_base.html',context=context)

def quiz_setup(request):
    context = {
        'events': ['FX','BB','UB','V'],
        }
    return render(request, 'app/quiz_setup.html',context=context)

def quiz(request):
    elements = ElementText.objects.filter(element__event=request.GET.get('event')).order_by('?')
    context = {
        'events': ['FX','BB','UB','V'],
        'lang_elements': elements,
        }
    return render(request, 'app/quiz.html',context=context)