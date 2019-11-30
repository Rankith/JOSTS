"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpRequest,JsonResponse
from app.models import Element,ElementText,Video,UserNote,Rule,RuleText,DrawnImage,SymbolDuplicate,SubscriptionTest,Subscription
from django.db.models import Q
from django.db.models import IntegerField
from django.db.models.functions import Cast
import re
from binascii import a2b_base64
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, SubscriptionForm
from django.contrib.auth import authenticate, login
import stripe
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

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

def subscription_check(user):
    #standard subscription
    if Subscription.objects.filter(user=user.id,expires__gte = datetime.today()).count() > 0:
        return True
    #super user
    if user.is_superuser or user.is_staff:
        return True
    #free account
    if Subscription.objects.filter(user=user.id,free=True).count() > 0:
        return True
    return False


def subscription_cancel(request):
    stripe.api_key = settings.STRIPE_API_KEY
    sub_response = None
    
    try:
        sub_response = stripe.Subscription.delete(request.GET.get('sub'))
    except:
        return redirect('/subscriptions/')

    Subscription.objects.filter(subscription_id=request.GET.get('sub')).update(cancelled=True)
    return redirect('/subscriptions/')

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_API_KEY
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
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
        #invoice payment for subscription

        session = event['data']['object']
        line = session['lines']['data'][0]
        sub_end = line['period']['end']
        sub_paid = event['created']
        sub_id = line['subscription']
        interval = line['plan']['interval'].title()
        customer_id=session['customer']
        charge_id = session['charge']

        #sub_id='sub_GGsgPUtrAbpIAo'
        #customer_id='cus_GGsgPUtrAbpIAo'
        #interval='month'

        #now update customers default payment method to wahtever was just used
        try:
            charge = stripe.Charge.retrieve(charge_id)
            stripe.Customer.modify(customer_id,invoice_settings={'default_payment_method':charge["payment_method"]})
        except:
            chargefail = True

        sub_end = datetime.fromtimestamp(sub_end)
        sub_paid = datetime.fromtimestamp(sub_paid)

        #first check if there is an existing one
        sub = Subscription.objects.filter(customer_id=customer_id,subscription_id=sub_id)
        subuse = '';
        if len(sub) > 0:
            subuse = sub[0]
        else:
            #find empty customer
            sub = Subscription.objects.filter(customer_id=customer_id,subscription_id='')
            if len(sub) > 0:
                subuse = sub[0]
            else:
                #make a new one
                sub = Subscription.objects.filter(customer_id=customer_id)
                subuse = Subscription(user=sub[0].user,customer_id=customer_id)
        subuse.expires = sub_end
        subuse.interval=interval
        subuse.subscription_id=sub_id
        subuse.last_payment=sub_paid
        subuse.save()
       
        #handle_checkout_session(session)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fulfill the purchase...
        #handle_checkout_session(session)

    return HttpResponse(status=200)

@login_required(login_url='/login/')
def subscriptions(request):
    sub = Subscription.objects.filter(user=request.user.id,expires__gte = datetime.today())
    live_subscriptions = Subscription.objects.filter(user=request.user.id,expires__gte = datetime.today(),cancelled=False).count()
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            stripe.api_key = settings.STRIPE_API_KEY
            cust = Subscription.objects.filter(user=request.user.id).values("customer_id")
            session = stripe.checkout.Session.create(
                customer=cust[0]["customer_id"],
                payment_method_types=['card'],
                subscription_data={
                    'items': [{
                    'plan': form.cleaned_data.get('subscription'),
                    }],
                    'trial_from_plan':'true',
                },
                success_url=request.build_absolute_uri("/") + 'subscriptions/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri("/") + 'subscriptions/',
            )
            return render(request, 'app/subscriptions.html', {'form': form,'checkout_session_id': session.id,'subscriptions':sub,'stripe_public_key':settings.STRIPE_PUBLIC_KEY,'live_subs':  live_subscriptions})
    else:
        form = SubscriptionForm()
    return render(request, 'app/subscriptions.html', {'form': form,'subscriptions':sub,'stripe_public_key':settings.STRIPE_PUBLIC_KEY,'live_subs':  live_subscriptions})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            #now create the stripe customer
            stripe.api_key = settings.STRIPE_API_KEY
            customer = stripe.Customer.create(
                email=form.cleaned_data.get('email'))
            sub = Subscription(user=user,customer_id=customer.id)
            sub.save()
            return redirect('/subscriptions')
    else:
        form = SignUpForm()
    return render(request, 'app/signup.html', {'form': form})

@login_required(login_url='/login/')
@user_passes_test(subscription_check,login_url='/subscriptions/')
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
@user_passes_test(subscription_check,login_url='/subscriptions/')
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
@user_passes_test(subscription_check,login_url='/subscriptions/')
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
@user_passes_test(subscription_check,login_url='/subscriptions/')
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
@user_passes_test(subscription_check,login_url='/subscriptions/')
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