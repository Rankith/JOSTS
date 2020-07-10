"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpRequest,JsonResponse
from app.models import Element,ElementText,Video,UserNote,Rule,RuleText,DrawnImage,SymbolDuplicate,SubscriptionTest,Subscription,SubscriptionSetup,QuizResult, \
    ActivityLog,UserSettings,Theme,PageTour,UserToursComplete,RuleLink,VideoNote,VideoNoteTemp,VideoLink,Disc,UnratedElement,VersionSettings,StructureGroup, \
    Competition,CompetitionType,CompetitionGroup,CompetitionVideo,TCExample,JudgeInstruction,CoachInstruction,CoachEnvironment,CoachMethodology,CoachVideoLine,CoachVideoLink, \
    CoachFundamentalCategory, CoachFundamentalSection, CoachFundamentalSlide, CoachFundamentalAnswer, CoachFundamentalUserProgress, CoachFundamentalUserAnswer, CoachFundamentalUserQuiz,CoachUserNote, \
    AcroBalance
    
from django.db.models import Q
from django.db.models import IntegerField
from django.db.models.functions import Cast
import re
from binascii import a2b_base64
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, SubscriptionForm,UnsubscribeFeedbackForm,SettingsForm,LoginForm,ContactForm
from django.contrib.auth import authenticate, login
import stripe
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json
import mysql.connector
from django.db.models import Value
from django.db.models.functions import Replace,Left
from django.db.models import Count,Max
from django.core.mail import send_mail

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
    return render(request,'app/about.html')

def log_activity(request,action_type,action_detail,action_item):
    AL = ActivityLog(disc_id=request.session.get('disc',1),actor=request.user,action_type=action_type,action_detail=action_detail,action_item=action_item)
    AL.save()

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
    return redirect('/unsubscribe_feedback/')

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
            if (len(cust) == 0):
                customer = stripe.Customer.create(
                email=request.user.email)
                sub = Subscription(user=request.user,customer_id=customer.id)
                sub.save()
                cust = Subscription.objects.filter(user=request.user.id).values("customer_id")
            session = stripe.checkout.Session.create(
                customer=cust[0]["customer_id"],
                payment_method_types=['card'],
                subscription_data={
                    'items': [{
                    'plan': form.cleaned_data.get('subscription').stripe_plan_id,
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
            cust = sub.customer_id
            session = stripe.checkout.Session.create(
                customer=cust,
                payment_method_types=['card'],
                subscription_data={
                    'items': [{
                    'plan': form.cleaned_data.get('subscription').stripe_plan_id,
                    }],
                    'trial_from_plan':'true',
                },
                success_url=request.build_absolute_uri("/") + 'subscriptions/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri("/") + 'subscriptions/',
            )
            return render(request, 'app/signup.html', {'form': form,'checkout_session_id': session.id,'subscriptions':sub,'stripe_public_key':settings.STRIPE_PUBLIC_KEY})
    else:
        form = SignUpForm()
    return render(request, 'app/signup.html', {'form': form})

def loginview(request):
    if request.method == 'POST':
        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            raw_password = login_form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=raw_password)
            login(request, user)
            request.session['disc'] = login_form.cleaned_data.get('disc').id;
            request.session['disc_path'] = login_form.cleaned_data.get('disc').folder_name;
            request.session['disc_full_name'] = login_form.cleaned_data.get('disc').full_name;
            request.session['disc_events'] = login_form.cleaned_data.get('disc').event_list;
            request.session['version_name'] = VersionSettings.objects.first().name
            disc = Disc.objects.get(pk=login_form.cleaned_data.get('disc').id)
            request.session['exclude_screens'] = disc.exclude_screens
            request.session['discs'] = list(Disc.objects.filter(show_login=True).values_list("display_name",flat=True))
            return redirect('elements')
    else:
        login_form = LoginForm()

    context = {
        'form': login_form,
        'main_title': VersionSettings.objects.first().name
    }
    return render(request, 'app/login.html', context)

@login_required(login_url='/login/')
def user_settings(request):
    u_settings = UserSettings.objects.filter(user=request.user.id)
    if len(u_settings) == 0:
        u_settings = UserSettings(user=request.user)
    else:
        u_settings = u_settings.first()
    form = SettingsForm
    if request.method == 'POST':
        form = SettingsForm(request.POST,instance=u_settings)
        if form.is_valid():
            form.save()
            return render(request, 'app/user_settings.html', {'form': form})
    else:
        form = SettingsForm(instance=u_settings)
    return render(request, 'app/user_settings.html', {'form': form})

def unsubscribe_feedback(request):
    if request.method == 'POST':
        form = UnsubscribeFeedbackForm(request.POST)
        if form.is_valid():
            uf = form.save(commit=False)
            uf.user = request.user
            uf.save()
            
            return redirect('/subscriptions/')
    else:
        form = UnsubscribeFeedbackForm()
    return render(request, 'app/unsubscribe_feedback.html', {'form': form})

@login_required(login_url='/login/')
@user_passes_test(subscription_check,login_url='/subscriptions/')
def elements(request):
    #AcroBalance.objects.filter(bottom_interface_point='2B',event='B').update(category='1')
    #AcroBalance.objects.filter(bottom_interface_point='SA-H',event='B').update(category='2')
    #AcroBalance.objects.filter(bottom_interface_point='2F',event='B').update(category='3')
    #AcroBalance.objects.filter(bottom_interface_point='2FW',event='B').update(category='3')
    #AcroBalance.objects.filter(bottom_interface_point='2FEW',event='B').update(category='3')
    #AcroBalance.objects.filter(top_interface_point='25F',event='B').update(category='4')
    #AcroBalance.objects.filter(bottom_interface_point='SA',event='B').update(category='5')
    #AcroBalance.objects.filter(top_interface_point='25A',event='B').update(category='6')
    #AcroBalance.objects.filter(bottom_interface_point='1B',event='B').update(category='7')
    #AcroBalance.objects.filter(bottom_interface_point='SAN',event='B').update(category='8')
    #AcroBalance.objects.filter(bottom_interface_point='H',event='B').update(category='9')
    #AcroBalance.objects.filter(bottom_interface_point='1SA',event='B').update(category='10')
    #AcroBalance.objects.filter(top_interface_point='26',event='B').update(category='11')
    #AcroBalance.objects.filter(bottom_interface_point='1F',event='B').update(category='12')
    #elements = ElementText.objects.filter(language="EN")
    #vals = Element.objects.order_by('letter_value').values('letter_value').distinct()
    #groups = Element.objects.order_by('str_grp').values('str_grp').distinct()
    #Element.objects.filter(event="V").filter(letter_value='A').update(letter_value='')
    #Element.objects.filter(event="V").filter(letter_value_9='A').update(letter_value_9='')
    #Element.objects.filter(event="V").filter(letter_value_8='A').update(letter_value_8='')
    #Element.objects.filter(event="V").filter(letter_value_67='A').update(letter_value_67='')
    #Rule.objects.filter(section="Appendix 12").update(display_order=112,search_display='A12')
    #Rule.objects.filter(section="Appendix 7").update(display_order=107,search_display='A7')

    #Element.objects.filter(disc__isnull=True).update(disc=1)
    #Rule.objects.filter(disc__isnull=True).update(disc=1)
    #Video.objects.filter(disc__isnull=True).update(disc=1)
    #DrawnImage.objects.filter(disc__isnull=True).update(disc=1)
    #SymbolDuplicate.objects.filter(disc__isnull=True).update(disc=1)
    #QuizResult.objects.filter(disc__isnull=True).update(disc=1)
    #ActivityLog.objects.filter(disc__isnull=True).update(disc=1)
    #RuleLink.objects.filter(type="E").update(pause_time='indef')
    context = {
        'type':'element',
        'search_type':'element',
        'list_type':'element',
        }
    return render(request, 'app/elements_fixed.html',context=context)

def element(request):
    idIn = request.GET.get('id')
    value_display = request.GET.get('value_display')
    element = ElementText.objects.filter(id=idIn)
    userNote = UserNote.objects.filter(user=request.user.id,element=idIn)
    if (len(userNote) > 0):
        userNote = userNote[0].note;
    else:
        userNote = '';
    if request.session.get('disc_path') == 'aer':
        image_sex = 'M'
    else:
        image_sex = ''
    context = {
        'lang_elements': element[0],
        'user_note': userNote,
        'val_display': value_display,
        'image_sex':image_sex,
        }
    #activity log
    log_activity(request,'Elements','View',str(element[0].element))
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
    #activity log
    log_activity(request,'Elements','Update User Note',str(elementInstance))
    return JsonResponse(resp)

def element_search(request):
    if request.session.get('disc_path') == 'tra':
        #trampoline so get different stuff
        twists = Element.objects.filter(disc=request.session.get('disc',1)).order_by('tramp_twists').values_list('tramp_twists',flat=True).distinct()
        flips = Element.objects.filter(disc=request.session.get('disc',1))#.order_by('tramp_flips').values_list('tramp_flips',flat=True).distinct()
        flips = flips.filter(event="TU") | flips.filter(event="DM")
        flips = flips.order_by('tramp_flips').values_list('tramp_flips',flat=True).distinct()
        events=request.session.get('disc_events','V,UB,BB,FX').split(",")
        positions = 'feet,front,back'.split(",")
        twistsDict = {}
        for twist in twists:
            if twist == 0:
                t = "0"
            elif twist % 2 != 0:
                t = str(int(twist)) + "/2"
            else:
                t = str(int(twist/2)) + "/1"
            twistsDict[twist] = t
        context = {
            'twists':twists,
            'flips': flips,
            'events': events,
            'search_type':'element',
            'value_low':0,
            'value_high':6,
            'positions':positions,
            'twistsDict': twistsDict
            }
        return render(request, 'app/element_search_tramp.html',context=context)
    elif request.session.get('disc_path') == 'acro':
        cats = AcroBalance.objects.filter(event="B").exclude(category='B').exclude(category='M').extra({'category':"CAST(category as UNGISNED)"}).order_by('category').values_list('category',flat=True).distinct()

        events=request.session.get('disc_events','V,UB,BB,FX').split(",")
        context = {
            'categories':cats,
            'events': events,
            'search_type':'element',
            }
        return render(request, 'app/element_search_acro.html',context=context)
    elif request.session.get('disc_path') == 'aer':
        vals = Element.objects.filter(disc=request.session.get('disc',1)).exclude(event="V").order_by('value').values('value').distinct()
        groups = Element.objects.filter(disc=request.session.get('disc',1)).order_by('skill_grp').values('skill_grp').distinct()
        ranges = Element.objects.filter(disc=request.session.get('disc',1)).order_by('range').values('range').exclude(range='').annotate(int_order=Cast('range',IntegerField())).order_by('int_order').distinct()
        groupDict = {}
        valueDict = {}
        #Video.objects.filter(id__in=TCExample.objects.all().values_list('video__id')).update(approved_liason=True,approved_final=True,approved_sts=True)

        events=request.session.get('disc_events','V,UB,BB,FX').split(",")
        for group in groups:
            groupEvents = "search-" + " search-".join(str(events['event']) for events in Element.objects.filter(skill_grp = group['skill_grp'],disc=request.session.get('disc',1)).order_by('event').values('event').distinct())
            groupDict[group['skill_grp']] = groupEvents
        for value in vals:
            valueEvents = "search-" + " search-".join(str(events['event']) for events in Element.objects.filter(value = value['value'],disc=request.session.get('disc',1)).order_by('event').values('event').distinct())
            valueDict[value['value']] = valueEvents
        context = {
            'vals':vals,
            'groups': groups,
            'groupsEvents': groupDict,
            'valueEvents': valueDict,
            'events': events,
            'ranges': ranges,
            'search_type':'element',
            'vault_low':Disc.objects.filter(id=request.session.get('disc',1)).first().vault_range_low,
            'vault_high':Disc.objects.filter(id=request.session.get('disc',1)).first().vault_range_high,
            'vault_slider':VersionSettings.objects.first().use_level_slider
            }
        return render(request, 'app/element_search_aer.html',context=context)

    else:
        vals = Element.objects.filter(disc=request.session.get('disc',1)).exclude(event="V").order_by('letter_value').values('letter_value').distinct()
        groups = Element.objects.filter(disc=request.session.get('disc',1)).order_by('str_grp').values('str_grp').distinct()
        ranges = Element.objects.filter(disc=request.session.get('disc',1)).order_by('range').values('range').exclude(range='').annotate(int_order=Cast('range',IntegerField())).order_by('int_order').distinct()
        groupDict = {}
        valueDict = {}
        #Video.objects.filter(id__in=TCExample.objects.all().values_list('video__id')).update(approved_liason=True,approved_final=True,approved_sts=True)

        events=request.session.get('disc_events','V,UB,BB,FX').split(",")
        for group in groups:
            groupEvents = "search-" + " search-".join(str(events['event']) for events in Element.objects.filter(str_grp = group['str_grp'],disc=request.session.get('disc',1)).order_by('event').values('event').distinct())
            groupDict[group['str_grp']] = groupEvents
        for value in vals:
            valueEvents = "search-" + " search-".join(str(events['event']) for events in Element.objects.filter(letter_value = value['letter_value'],disc=request.session.get('disc',1)).order_by('event').values('event').distinct())
            valueDict[value['letter_value']] = valueEvents
        context = {
            'vals':vals,
            'groups': groups,
            'groupsEvents': groupDict,
            'valueEvents': valueDict,
            'events': events,
            'ranges': ranges,
            'search_type':'element',
            'vault_low':Disc.objects.filter(id=request.session.get('disc',1)).first().vault_range_low,
            'vault_high':Disc.objects.filter(id=request.session.get('disc',1)).first().vault_range_high,
            'vault_slider':VersionSettings.objects.first().use_level_slider
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
    value_display = dget['value_display'][0]
    del dget['value_display']
    event = dget['element__event']
    query = Q(language="EN")
    for k,v in dget.items():
        innerQuery = Q()
        for i in v:
            for ks in k.split(','):#allow multi things
                kwargs = {'{0}'.format(ks): i}
                innerQuery.add(Q(**kwargs), Q.OR)
        query.add(innerQuery,Q.AND)
    elements = ElementText.objects.filter(query).order_by('element__str_grp','element__code_order')
    if search != "":
        elements = elements.filter(element__usernote__note__icontains=search).distinct() | elements.filter(text__icontains=search).distinct() | elements.filter(short_text__icontains=search).distinct() | elements.filter(named__icontains=search).distinct() | elements.filter(additional_info__icontains=search).distinct()
    elements = elements.filter(element__disc=request.session.get('disc',1))
    groups = StructureGroup.objects.filter(disc_id=request.session.get('disc',1),event=event[0]).order_by('group')
    if request.session.get('disc_path') == 'aer':
        image_sex = 'M'
    else:
        image_sex = ''
    context = {
        'lang_elements': elements,
        'num_elements': str(len(elements)) + " Elements",
        'display': display,
        'val_display': value_display,
        'groups':groups,
        'image_sex':image_sex
        }

    #activity log
    log_activity(request,'Elements','List',request.GET.get('element__event'))
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
    #not used
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
    sections = Rule.objects.filter(disc=request.session.get('disc',1)).order_by('display_order','search_display','section').values('section','display_order','search_display').distinct()
    sectionDict = {}
    #for section in sections:
    #    sectionDict[section['section']] = section['search_];
    context = {
        'sections':sections,
        'sectionsDict': sectionDict,
        'search_type': 'rule',
        }
    return render(request, 'app/element_search.html',context=context)

def rule_list(request):
    dget = dict(request.GET)
    search = dget['search'][0]
    search = search.replace("1/2","½")
    search = search.replace("1/4","¼")
    collapsed = False
    del dget['search']
    value_display = dget['value_display'][0]
    del dget['value_display']
    query = Q()
    for k,v in dget.items():
        innerQuery = Q()
        for i in v:
            kwargs = {'{0}'.format(k): i}
            innerQuery.add(Q(**kwargs), Q.OR)
        query.add(innerQuery,Q.AND)
    rules = RuleText.objects.filter(query).order_by('rule__display_order','rule_id')
    if search != "":
        rules = rules.filter(cue__icontains=search) | rules.filter(response__icontains=search) | rules.filter(rule_description__icontains=search) | rules.filter(specific_deduction__icontains=search) | rules.filter(additional_info__icontains=search)
    rules = rules.filter(rule__disc=request.session.get('disc',1))
    vidcounts = []
    if len(dget.items()) == 0  and search == "":
        collapsed = True
    for r in rules:
        totalvids=0
        lastcat=-1
        if r.rule.rulelink_set.count() > 0:
            for rl in r.rule.rulelink_set.all().order_by('category_order'):
                if lastcat != rl.category_order:
                    vids = rl.videonote_set.all().filter(video__tcexample=None).values('id').distinct().count()
                    if vids > 4:
                        vids = 4
                    totalvids += vids
                    lastcat = rl.category_order
        vidcounts.append(totalvids)
    #r.rule.rulelink_set.annotate(rls = Count('rule__rulelink__videonote__video__id',distinct=True))
    #rules = rules.annotate(rls = Count('rule__rulelink__videonote'))
    context = {
        'rules': zip(rules,vidcounts),
        'num_rules': str(len(rules)) + " Rules",
        'section_header' : VersionSettings.objects.first().rule_sub_header,
        'collapsed':collapsed
        }
    #activity log
    log_activity(request,'Rules','View','')
    return render(request, 'app/rule_list.html',context=context)

def rule_vid_ref(request):
    idIn = request.GET.get('id')
    rule = RuleText.objects.get(rule__id=idIn)

    totalvids=0
    lastcat=-1
    if rule.rule.rulelink_set.count() > 0:
        for rl in rule.rule.rulelink_set.all().order_by('category_order'):
            if lastcat != rl.category_order:
                vids = rl.videonote_set.all().filter(video__tcexample=None).values('id').distinct().count()
                if vids > 4:
                    vids = 4
                totalvids += vids
                lastcat = rl.category_order
    #r.rule.rulelink_set.annotate(rls = Count('rule__rulelink__videonote__video__id',distinct=True))
    #rules = rules.annotate(rls = Count('rule__rulelink__videonote'))
    context = {
        'rule': rule,
        'vidcount':totalvids
        }
    #activity log
    log_activity(request,'Rules','View Reference','')
    return render(request, 'app/rule_vid_ref.html',context=context)

#shorthand
@login_required(login_url='/login/')
@user_passes_test(subscription_check,login_url='/subscriptions/')
def shorthand_training(request):
    #DrawnImage.objects.filter(label__contains='bb').update(event='bb')
    #dupes = SymbolDuplicate.objects.all()
    #for dupe in dupes:
        #DrawnImage.objects.filter(label=dupe.symbol).update(label=dupe.replace_with)
    #Element.objects.filter(event="V").filter(value__gte=7.0).filter(value__lt=8.0).update(range=7)
    context = {
        'type':'shorthand_trainer',
        'search_type':'element',
        'list_type':'element',
        }
     #activity log
    log_activity(request,'Shorthand Training','List','')
    return render(request, 'app/elements_fixed.html',context=context)

def shorthand_trainer(request):
    idIn = request.GET.get('id')
    value_display = request.GET.get('value_display')
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
        'symbol_duplicates' : symbol_duplicates,
        'val_display':value_display,
        'drawing_prefix':VersionSettings.objects.first().drawing_prefix
        }
    #activity log
    log_activity(request,'Shorthand Training','View',str(element[0].element))
    return render(request, 'app/shorthand_trainer.html',context=context)

def save_record_image(request):
    datauri = request.POST.get('data','')
    imgstr = re.search(r'base64,(.*)', datauri).group(1)
    binary_data = a2b_base64(imgstr)
    label_save = request.POST.get('label','')
    #remove the first '/' below to test local saving
    output = open('/' + settings.MEDIA_ROOT + '/drawnimages/' + request.session.get('disc_full_name','womens').lower() + '/' + request.POST.get('event','') + '/' + request.POST.get('name','') + '.png', 'wb')
    output.write(binary_data)
    output.close()
    replace_with = SymbolDuplicate.objects.filter(event=request.POST.get('event',''),symbol=request.POST.get('label',''),disc=request.session.get('disc',1))
    if (len(replace_with) != 0):
        label_save = replace_with[0].replace_with
    d = DrawnImage(name=request.POST.get('name','') + '.png', label=label_save,event=request.POST.get('event',''),disc_id=request.session.get('disc',1))
    d.save()

    count = DrawnImage.objects.filter(disc=request.session.get('disc',1),label=request.POST.get('label','')).count()

     #activity log
    log_activity(request,'Shorthand Training','Draw','')

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
        'drawing_prefix':VersionSettings.objects.first().drawing_prefix
        }
    #activity log
    log_activity(request,'Shorthand Lookup','View','')
    return render(request, 'app/shorthand_lookup.html',context=context)

def element_for_shorthand(request):
    idIn = request.GET.get('id')
    eventIn = request.GET.get('event')
    element = ElementText.objects.filter(element__id_number=idIn).filter(element__event=eventIn).filter(element__disc=request.session.get('disc',1))
    userNote = UserNote.objects.filter(user=request.user.id,element=element[0].element.id)
    if (len(userNote) > 0):
        userNote = userNote[0].note;
    else:
        userNote = '';
    context = {
        'lang_elements': element[0],
        'user_note': userNote,
        'val_display': 'value',
        }
    #activity log
    log_activity(request,'Shorthand Lookup','Draw',str(element[0].element))
    return render(request, 'app/element.html',context=context)

   

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
    events=request.session.get('disc_events','V,UB,BB,FX').split(",")
    context = {
        'vals':vals,
        'groups': groups,
        'groupsEvents': groupDict,
        'valueEvents': valueDict,
        'events': events,
        'ranges': ranges,
        'search_type':'shorthand',
        }
    return render(request, 'app/element_search.html',context=context)

def element_lookup(request):
    eventIn = request.GET.get('event').upper()
    if (eventIn == "V"):
        vals = Element.objects.filter(disc=request.session.get('disc',1)).order_by('range').values('range').exclude(range='').annotate(int_order=Cast('range',IntegerField())).order_by('int_order').distinct()
    else:
        vals = Element.objects.filter(disc=request.session.get('disc',1)).filter(event=eventIn).order_by('letter_value').values('letter_value').distinct()   
    groups = Element.objects.filter(disc=request.session.get('disc',1)).filter(event=eventIn).order_by('str_grp').values('str_grp').distinct()
    #groups = StructureGroup.objects.filter(disc_id=request.session.get('disc',1),event=eventIn).order_by('group')
    elements = ElementText.objects.filter(element__disc=request.session.get('disc',1)).filter(element__event=eventIn,language="EN").order_by('element__str_grp','element__letter_value','element__code_order')
    context = {
        'vals':vals,
        'groups': groups,
        'elements': elements,
        'event':eventIn,
        }
    #activity log
    log_activity(request,'Shorthand Lookup','Element Lookup','')
    return render(request, 'app/element_lookup.html',context=context)

#Quiz
@login_required(login_url='/login/')
@user_passes_test(subscription_check,login_url='/subscriptions/')
def quiz_shorthand(request):
    context = {
        'type':'Shorthand',
        }
    #activity log
    log_activity(request,'Shorthand Quiz','View','')
    return render(request, 'app/quiz_base.html',context=context)

@login_required(login_url='/login/')
@user_passes_test(subscription_check,login_url='/subscriptions/')
def quiz_element(request):
    context = {
        'type':'Element',
        }
    #activity log
    log_activity(request,'Element Quiz','View','')
    return render(request, 'app/quiz_base.html',context=context)

def quiz_setup(request):
    if request.session.get('disc_path') == 'tra':
        #trampoline so get different stuff
        twists = Element.objects.filter(disc=request.session.get('disc',1)).order_by('tramp_twists').values_list('tramp_twists',flat=True).distinct()
        flips = Element.objects.filter(disc=request.session.get('disc',1))#.order_by('tramp_flips').values_list('tramp_flips',flat=True).distinct()
        flips = flips.filter(event="TU") | flips.filter(event="DM")
        flips = flips.order_by('tramp_flips').values_list('tramp_flips',flat=True).distinct()
        events=request.session.get('disc_events','V,UB,BB,FX').split(",")
        positions = 'feet,front,back'.split(",")
        twistsDict = {}
        for twist in twists:
            if twist == 0:
                t = "0"
            elif twist % 2 != 0:
                t = str(int(twist)) + "/2"
            else:
                t = str(int(twist/2)) + "/1"
            twistsDict[twist] = t
        context = {
            'twists':twists,
            'flips': flips,
            'events': events,
            'search_type':'element',
            'value_low':0,
            'value_high':6,
            'positions':positions,
            'twistsDict': twistsDict,
            'type': request.GET.get('type'),
            'tramp': True
            }
        return render(request, 'app/quiz_setup.html',context=context)
    else:
        events=request.session.get('disc_events','V,UB,BB,FX').split(",")
        vals = Element.objects.filter(disc=request.session.get('disc',1)).exclude(event="V").order_by('letter_value').values('letter_value').distinct()
        groups = Element.objects.filter(disc=request.session.get('disc',1)).order_by('str_grp').values('str_grp').distinct()
        groupDict = {}
        valueDict = {}
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
            'events':events,
            'type': request.GET.get('type'),
            'tramp': False
            }
        return render(request, 'app/quiz_setup.html',context=context)

def quiz(request):
    missed = request.GET.get('missed',-1)
    
    #search = dget['search'][0]
    #search = search.replace("1/2","½")
    #search = search.replace("1/4","¼")
    #del dget['search']
    if missed == -1:
        dget = dict(request.GET)
        del dget['undefined']
        del dget['prompt']
        del dget['type']
        del dget['event']
        query = Q(language="EN")
        for k,v in dget.items():
            innerQuery = Q()
            for i in v:
                kwargs = {'{0}'.format(k): i}
                innerQuery.add(Q(**kwargs), Q.OR)
            query.add(innerQuery,Q.AND)
        quiz = ElementText.objects.filter(query).order_by('?')
        #if search != "":
            #elements = elements.filter(element__usernote__note__icontains=search).distinct() | elements.filter(text__icontains=search).distinct() | elements.filter(short_text__icontains=search).distinct() | elements.filter(named__icontains=search).distinct() | elements.filter(additional_info__icontains=search).distinct()
        quiz = quiz.filter(element__disc=request.session.get('disc',1))
        #quiz = ElementText.objects.filter(element__event=request.GET.get('event'),element__disc=request.session.get('disc',1)).order_by('?')
        elements = quiz
    else:
        quiz = ElementText.objects.filter(element__in=QuizResult.objects.filter(id=missed)[0].missed.all().values_list('id'))
        elements = ElementText.objects.filter(element__event=request.GET.get('event'),element__disc=request.session.get('disc',1))
    #elements = ElementText.objects.filter(element__event=request.GET.get('event'))
    if request.session.get('disc_path') == 'tra':
        vals = Element.objects.filter(event=request.GET.get('event')).filter(disc=request.session.get('disc',1)).order_by('value').values('value').distinct()
        context = {
            'event': request.GET.get('event'),
            'lang_elements': elements,
            'quiz': quiz,
            'prompt_type': request.GET.get('prompt'),
            'vals':vals,
            'direct_val':True
            }
    else:
        vals = Element.objects.filter(event=request.GET.get('event')).filter(disc=request.session.get('disc',1)).order_by('letter_value').values('letter_value').distinct()
        groups = Element.objects.filter(event=request.GET.get('event')).filter(disc=request.session.get('disc',1)).order_by('str_grp').values('str_grp').distinct()
    
        context = {
            'event': request.GET.get('event'),
            'lang_elements': elements,
            'quiz': quiz,
            'prompt_type': request.GET.get('prompt'),
            'vals':vals,
            'groups': groups,
            'direct_val':False
            }
    #activity log
    log_activity(request,request.GET.get('type','Shorthand') + ' Quiz','Start','')
    return render(request, 'app/quiz_main_' + request.GET.get('type','shorthand').lower() + '.html',context=context)

def quiz_save(request):
    QR = QuizResult(event=request.GET.get('event'),correct=request.GET.get('correct'),wrong=request.GET.get('wrong'),type=request.GET.get('type'),user=request.user,date_completed=datetime.today(),disc_id=request.session.get('disc',1))
    QR.save()
    for miss in request.GET.getlist('missed[]'):
        QR.missed.add(miss)
    QR.save()
     #activity log
    log_activity(request,'Shorthand Quiz','Finish','')
    return HttpResponse(status=200)

def quiz_delete(request):
    QuizResult.objects.filter(id=request.GET.get('id')).delete()
     #activity log
    log_activity(request,'Shorthand Quiz','Delete','')
    return HttpResponse(status=200)

def quiz_results(request):
    results = QuizResult.objects.filter(user=request.user,event=request.GET.get('event'),type__iexact=request.GET.get('type'),disc=request.session.get('disc',1)).order_by('-date_completed','-id')
    context = {
        'results': results
        }
    return render(request, 'app/quiz_results.html',context=context)

#Tour
def check_tour(request):
    page = request.GET.get('page')
    force = request.GET.get('force')
    tour = PageTour.objects.filter(url=page)
    resp = {'file':'none'}
   
    if len(tour) > 0:
        complete = UserToursComplete.objects.filter(page = tour[0],user=request.user)
        if len(complete) <= 0 or force == "True":
            context = {
                'tour': tour[0]
            }
            if force != "True":
                tour_comp = UserToursComplete(page = tour[0],user=request.user)
                tour_comp.save()
            resp = {'file':tour[0].file}
    return JsonResponse(resp)

#Videos
def video_player(request):
    elementid = request.GET.get('element',-1)
    coachelementid = request.GET.get('coachelement',-1)
    if elementid != -1: #element
        element = ElementText.objects.get(pk=elementid)
        potential_videos = Video.objects.filter(id__in=VideoNote.objects.filter(element_link=element.element).values_list('video').distinct())
        potential_videos = potential_videos.exclude(id__in=element.element.videolink_set.all().values_list('video'))
        context = {
            'element': element,
            'mode': 'element',
            'editable': request.user.is_staff,
            'editmode': request.GET.get('editmode'),
            'potential': potential_videos
        }
        return render(request, 'app/video_player.html',context=context)
    elif coachelementid != -1: #coach
        element = CoachInstruction.objects.get(pk=coachelementid)
        #potential_videos = Video.objects.filter(id__in=VideoNote.objects.filter(element_link=element.element).values_list('video').distinct())
        #potential_videos = potential_videos.exclude(id__in=element.element.videolink_set.all().values_list('video'))
        context = {
            'element': element,
            'mode': 'coach',
            'editable': request.user.is_staff,
            'editmode': request.GET.get('editmode'),
        }
        return render(request, 'app/video_player.html',context=context)
    else: #rule
        ruleid = request.GET.get('rule',-1)
        rule = RuleText.objects.get(pk=ruleid)
        rulelinks = rule.rule.rulelink_set.all().order_by('category_order')
        cat = []
        vids = []
        for c in rule.rule.rulelink_set.all().values('category_order').order_by('category_order').distinct():
            thiscat = RuleLink.objects.filter(rule = rule.rule,category_order=c['category_order']).first()
            cat.append(thiscat)
            vids.append(Video.objects.filter(tcexample=None,videonote__rule_link=thiscat))
        #cat0 = rulelinks.filter('category')
        context = {
            'rule': rule,
            'rulelinks': rulelinks,
            'cats':zip(cat,vids),
            'mode': 'rule',
            'editable': request.user.is_staff
        }
        return render(request, 'app/video_player.html',context=context)
   

@user_passes_test(lambda u: u.is_staff)
def video_notes_builder(request):
    event = request.GET.get('event','fx')
    tc = request.GET.get('tc','false')
    #Video.objects.update(approved_sts=True)
    if tc=="false":
        #videos = Video.objects.filter(event__iexact=event,disc=request.session.get('disc',1)).exclude(id__in=TCExample.objects.filter(video__event__iexact=event, video__disc=request.session.get('disc',1)).values_list('video__id'))
        videos = Video.objects.filter(event__iexact=event,disc=request.session.get('disc',1)).exclude(id__in=TCExample.objects.filter(video__event__iexact=event, video__disc=request.session.get('disc',1)).values_list('video__id')).exclude(id__in=CompetitionVideo.objects.filter(video__event__iexact=event, video__disc=request.session.get('disc',1)).values_list('video__id'))
    else:
        videos = Video.objects.filter(id__in=TCExample.objects.filter(video__event__iexact=event, video__disc=request.session.get('disc',1)).values_list('video__id'))
        #videos = Video.objects.filter(event__iexact=event,disc=request.session.get('disc',1))
    unrated = UnratedElement.objects.filter(event__iexact=event,disc=request.session.get('disc',1)).order_by('id')
    elements = ElementText.objects.filter(element__event__iexact=event,element__disc=request.session.get('disc',1)).order_by('element__str_grp','element__code_order')
    rules = RuleLink.objects.filter(event='',disc=request.session.get('disc',1)) | RuleLink.objects.filter(event__iexact=event,disc=request.session.get('disc',1))
    events=request.session.get('disc_events','V,UB,BB,FX').split(",")
    context = {
        'elements': elements,
        'rules': rules,
        'videos': videos,
        'event': event,
        'events': events,
        'unrateds': unrated,
        'drawing_prefix':VersionSettings.objects.first().drawing_prefix,
        'TC':tc,
        }
    return render(request, 'app/video_notes_builder.html',context=context)

def get_video_notes(request):
    video = request.GET.get('video')
    notes = VideoNote.objects.filter(video=video).order_by('frame').values()
    vid = Video.objects.get(pk=video)
    return JsonResponse({'notes': list(notes),
                         'extra': vid.extra_notes,
                         'approved_l': vid.approved_liason,
                         'approved_f': vid.approved_final,
                         'approved_s': vid.approved_sts})

def save_video_notes(request):
    data = json.loads(request.body)

    if data["video"] == 'temp':
        VideoNoteTemp.objects.all().delete()
        for note in data["notes"]:
            vn = VideoNoteTemp(**note)
            vn.save()
    else:
        VideoNote.objects.filter(video=data["video"]).delete()
        for note in data["notes"]:
            vn = VideoNote(**note)
            vn.save()
        vid =  Video.objects.get(pk=data["video"])
        vid.extra_notes = data["extra"]
        vid.save()
        send_mail(request.session.get('version_name','websts') + ' video note updated',request.session.get('version_name','websts') + ' ' + Disc.objects.get(id=request.session.get('disc',1)).folder_name.upper() + ' ' + Video.objects.get(id=data["video"]).event +' video ' + str(data["video"]) + ' updated by ' + request.user.username,'stsmailrecover@gmail.com',['gymjudgehills@gmail.com'],fail_silently=True)

    resp = {'updated':True}
    #activity log

    return JsonResponse(resp)

def update_video_approved(request):
    data = json.loads(request.body)

    vid =  Video.objects.get(pk=data["video"])
    vid.approved_liason = data["approved_l"]
    vid.approved_final = data["approved_f"]
    vid.approved_sts = data["approved_s"]
    vid.save()
    #send_mail(request.session.get('version_name','websts') + ' video note updated',request.session.get('version_name','websts') + ' ' + Disc.objects.get(id=request.session.get('disc',1)).folder_name.upper() + ' ' + Video.objects.get(id=data["video"]).event +' video ' + str(data["video"]) + ' updated by ' + request.user.username,'stsmailrecover@gmail.com',['gymjudgehills@gmail.com'],fail_silently=True)

    resp = {'updated':True}
    #activity log

    return JsonResponse(resp)

def video_notes(request):
    video = request.GET.get('video','')
    type = request.GET.get('type','rule')
    if type == "coach":
        video = request.GET.get('video','')
        coach_element = request.GET.get('element',-1)
        notes = CoachVideoLine.objects.filter(instruction=coach_element)
        frames = CoachVideoLink.objects.filter(coach_element=coach_element,video__id=video)[0]
        key_points = CoachVideoLine.objects.filter(instruction=coach_element,type='key')
        description = CoachVideoLine.objects.filter(instruction=coach_element,type='description')
        mechanics = CoachVideoLine.objects.filter(instruction=coach_element,type='mechanics')
        frame_jump = frames.frame_jump
        #if element != -1:
            #if type == 'element':
                #jnote = notes.filter(element_link__id = element)
            #else:
                #jnote = notes.filter(rule_link__rule__id = element)
            #if len(jnote) >= 1:
                #frame_jump = jnote[0].frame

        context = {
            'elementjump':frame_jump,
            'notes':notes,
            'keys':key_points,
            'descs':description,
            'mechs':mechanics,
            'frames':frames.frame_list.split(",")
            }

        return render(request, 'app/coach_video_notes.html',context=context)
    else:
        if video == 'temp':
            notes = VideoNoteTemp.objects.all().order_by('frame')
        else:
            notes = VideoNote.objects.filter(video=video).order_by('frame')
        element = request.GET.get('element',-1)
        frame_jump = -1
        if element != -1:
            if type == 'element':
                jnote = notes.filter(element_link__id = element)
            else:
                jnote = notes.filter(rule_link__rule__id = element)
            if len(jnote) >= 1:
                frame_jump = jnote[0].frame

        tc_type = ""
        extra_note = ""
        #remove 0 deductions if not rules
        if type == 'element':
            notes = notes.exclude(Q(rule_link__deduction_amount=0) & ~Q(rule_link__text='--- no E-jury deductions ---'))
        elif type == "example":
            tc = TCExample.objects.filter(video=video)
            tc_type = tc[0].type
            extra_note = tc[0].special_notes
        context = {
            'elementjump':frame_jump,
            'notes':notes,
            'type':tc_type.upper(),
            'extranote':extra_note,
            }

        return render(request, 'app/video_notes.html',context=context)


def update_video_links(request):
    data = json.loads(request.body)
    counter = 1;
    VideoLink.objects.filter(element=data["element"]).delete()
    for vid in data["videos"].split(','):
        vl = VideoLink(element_id=data["element"],video_id=vid,order=counter)
        vl.save()
        counter += 1

    resp = {'updated':True}
    #activity log

    return JsonResponse(resp)

@user_passes_test(lambda u: u.is_staff)
def import_from_fig(request):
    response = "";
    type = request.GET.get('type','')
    disc = request.GET.get('disc','')
    db = request.GET.get('db','')
    un = request.GET.get('user','')
    pw = request.GET.get('pw','')
    try:
        cnx = mysql.connector.connect(user=un, password=pw, host='212.147.112.242',database=db,port='8083')
    except mysql.connector.Error as err:
         return JsonResponse({'result':err})

    cursor = cnx.cursor()
    discipline = Disc.objects.filter(folder_name=disc)
    if discipline.exists():
        #delete for that disc
        discid = discipline[0].id
        if 'incrementvalue' in type:
            elements = Element.objects.filter(disc_id=discid)
            for e in elements:
                if e.letter_value != "":
                    e.up_value_letter = chr(ord(e.letter_value)+1)
                    if e.letter_value != "A":
                        e.down_value_letter = chr(ord(e.letter_value)-1)
                    else:
                        e.down_value_letter = "A"
                    e.save()
        if 'element' in type or type=='all':
            ElementText.objects.filter(element__disc_id=discid).delete()
            Element.objects.filter(disc_id=discid).delete()
            
            #elements
            query="Select DISTINCT main.event,main.strgrp,main.codeorder,main.`id number`, main.value, main.range, `id text`,shorttext,text,named,hold,`author's comments`,1dvlower,1dvhigher,internalid FROM Main INNER JOIN EnglishSkills ON Main.Event = EnglishSkills.Event AND Main.StrGrp = EnglishSkills.StrGrp AND Main.CodeOrder = EnglishSkills.CodeOrder"
            cursor.execute(query)

            for (event,strgrp,codeorder,idnum,value,rng,idtext,shorttext,text,named,hold,additional,downvalue,upvalue,oldid) in cursor:
                if downvalue == None:
                    downvalue = ''
                if upvalue == None:
                    upvalue = ''
                if rng == None:
                    rng = ''
                value = value.replace("points","")
                el = Element(disc_id=discid,event=event,str_grp=strgrp,code_order=codeorder,id_number=idnum,letter_value=value[:1],value=value[-3:],up_value_letter=upvalue,down_value_letter=downvalue,range=rng,old_id=oldid)
                el.save()
                if hold == None:
                    hold = ''
                if additional == None:
                    additional=''
                if shorttext == None:
                    shorttext = ''
                if named == None:
                    named = ''
                if shorttext == '':
                    shorttext = text
                et = ElementText(element=el, text=text,short_text=shorttext,named=named,additional_info=additional,hold_text=hold,id_number_text=idtext)
                et.save()

            response +=  " | elements created: " + str(Element.objects.filter(disc_id=discid).count())
        
        if 'unrated' in type or type=='all':
            UnratedElement.objects.filter(disc_id=discid).delete()

            query="Select id,event,name From extraskillsenglish order by event"
            cursor.execute(query)
            for (id,event,name) in cursor:
                ue = UnratedElement(disc_id=discid,old_id=id,event=event,name=name)
                ue.save()

            response +=  " | unrated created: " + str(UnratedElement.objects.filter(disc_id=discid).count())

        if 'video' in type or type=='all':
            Video.objects.filter(disc_id=discid).delete()

            query="Select VideoID,Event,File,FPS,Approved,JohannaApproved From VideosEnglish order by event"
            cursor.execute(query)
            for (id,event,file,fps,approved,approvedJ) in cursor:
                file = file.replace(".mov",".mp4")
                vid = Video(disc_id=discid,old_id=id,event=event,file=file,fps=fps,approved_final=approved,approved_liason=approvedJ)
                vid.save()

            response +=  " | videos created: " + str(Video.objects.filter(disc_id=discid).count())

        if 'vidlinks' in type or type=='all':
            #video links elements
            VideoLink.objects.filter(video__disc_id=discid).delete()
            query="Select file,videojump,internalid FROM Main where file is not null and file <> ''"
            cursor.execute(query)

            for (file,videojump,id) in cursor:
                element_ref = Element.objects.filter(old_id=id,disc_id=discid).first()
                order=0
                for link,jump in zip(file.split(','),videojump.split(',')):
                    try:
                        vl = VideoLink(video=Video.objects.filter(old_id=link,disc_id=discid).first(),element=element_ref,frame_jump=jump,order=order)
                        vl.save()
                    except:
                        errored = "video link missed"
                    order = order + 1

            response +=  " | videos linked: " + str(VideoLink.objects.filter(video__disc_id=discid).count())

        if 'rules' in type or type=='all':
            #rules
            RuleText.objects.filter(rule__disc_id=discid).delete()
            Rule.objects.filter(disc_id=discid).delete()
            query="Select DISTINCT qresp.question,RuleID,ArtEvt,RuleNo, SubRule, cue, response,ruledescription,`author's comments`,specificdeduction,cat0,cat1,cat2,cat3,cat4 FROM `qresp` INNER JOIN `qrespenglish` on `qresp`.question = `qrespenglish`.question ORDER BY `qresp`.`Question`"
            cursor.execute(query)
            order = 0
            last_rule = ""
            rule_no_order = 0
            last_art = ""

            for (oldid,ruleid,artevt,ruleno,subrule,cue,answer,ruledesc,additionalinfo,specificdeduction,cat0,cat1,cat2,cat3,cat4) in cursor:
                if ruleno == None:
                    ruleno = ''
                if subrule == None:
                    subrule = ''
                if cat0 == None:
                    cat0 = ''
                if cat1 == None:
                    cat1 = ''
                if cat2 == None:
                    cat2 = ''
                if cat3 == None:
                    cat3 = ''
                if cat4 == None:
                    cat4 = ''
                if additionalinfo == None:
                    additionalinfo=''
                if last_rule != ruleid:
                    order = order + 1
                    rule_no_order = 0
                if artevt != last_art:
                    rule_no_order = rule_no_order + 1
                last_art = artevt
                last_rule = ruleid
                answer = answer.replace("777","")

                cue = cue[4:]

                rl = Rule(disc_id=discid,event=ruleid,rule_id=ruleid,section=ruleid,rule_no=artevt,search_display=ruleid[:2].replace('A','S'),display_order=(order*10),old_id=oldid,sub_rule=(ruleid + "." + ruleno + "." + subrule))
                rl.save()
                rt = RuleText(rule=rl,cue=cue,response=answer,additional_info=additionalinfo,rule_description=ruledesc,specific_deduction=specificdeduction,cat0=cat0,cat1=cat1,cat2=cat2,cat3=cat3,cat4=cat4,section_text=artevt,chapter_text=ruleid)
                rt.save()

            response +=  " | rules added: " + str(Rule.objects.filter(disc_id=discid).count())

        if 'rulelinks' in type or type=='all':
            #rule links
            RuleLink.objects.filter(disc_id=discid).delete()
            RuleLink.objects.filter(disc=None).delete()
            query="Select text,rulelink,categoryname,categoryorder,deductionamount,connectedelements,type,event,id FROM rulelinksenglishconversion where rulelink is not null and categoryname is not null and categoryorder is not null"
            cursor.execute(query)

            for (text,rulelink,categoryname,categoryorder,deductionamount,connectedelements,type,event,id) in cursor:
                if event == None:
                    event = ''
                if deductionamount == '' or deductionamount == ' ' or deductionamount == None:
                    deductionamount = 0
                elif '.' in deductionamount:
                    deductionamount = deductionamount.replace('.','')
                rl = RuleLink(disc_id=discid,text=text,category_name=categoryname,category_order=categoryorder,deduction_amount=deductionamount,connected_elements=connectedelements,type=type[:1].upper(),event=event,old_id=id)
                rl.save();
                for link in rulelink.split(','):
                    rule = Rule.objects.filter(old_id=link,disc_id=discid).first()
                    if rule:
                        rl.rule.add(Rule.objects.filter(old_id=link,disc_id=discid).first())

                rl.save();

            response +=  " | rules linked: " + str(RuleLink.objects.filter(disc_id=discid).count())

        if 'vidnotes' in type or type=='all':
            #rule links
            VideoNote.objects.filter(video__disc_id=discid).delete()
            query="Select videoid,type,color,linkid,frame,Event,type,event,cr,overridetext,novaluetype,skipframe FROM videonotes order by videoid"
            cursor.execute(query)
            lastvid = ""

            for (videoid,type,color,linkid,frame,Event,type,event,cr,overridetext,novaluetype,skipframe) in cursor:
                if cr == None:
                    cr = ''
                if overridetext == None:
                    overridetext = ''
                if novaluetype == None:
                    novaluetype = ''
                if color == None:
                    color = ''
                if skipframe == None or skipframe == '' or skipframe == '0' or skipframe == 0:
                    skipframe = False
                else:
                    skipframe = True
                if color == '9':
                    color = ''
                elif color == 'b':
                    color = 'Blue'
                elif color == 'r':
                    color = 'Red'

                event = event.upper()
                
                if lastvid != videoid:
                    lastvid = videoid
                    video_ref = Video.objects.filter(old_id=videoid,disc_id=discid).first()
                if videoid == 584:
                    lastvid = videoid
                vn = VideoNote(video=video_ref,frame=frame,skip_frame=skipframe,color=color,event=event,cr=cr,override_text=overridetext,no_value_type=novaluetype)
                if type.lower() == "element" and novaluetype.lower() == "unrated":
                    ul = UnratedElement.objects.filter(old_id=linkid,disc_id=discid).first()
                    vn.unrated_link = ul
                elif type == 'E' or type == 'D':
                    rl = RuleLink.objects.filter(old_id=linkid,disc_id=discid).first()
                    vn.rule_link = rl
                else:
                    el = Element.objects.filter(old_id=linkid,disc_id=discid).first()
                    vn.element_link = el
                vn.save();

            response +=  " | video notes created: " + str(VideoNote.objects.filter(video__disc_id=discid).count())

        if 'tcexamples' in type or type=='all':
            #Video.objects.filter(disc_id=discid).delete()
            Video.objects.filter(disc_id=discid).exclude(tcexample=None).delete()
            query="Select ID,Event,Year,NoteType,File,FPS,SpecialNotes,name From tcexamples order by Year,NoteType,Event"
            cursor.execute(query)
            for (id,event,year,type,file,fps,special,name) in cursor:
                file = file.replace(".mov",".mp4")
                vid = Video(disc_id=discid,old_id=id+100000,event=event,file=file,fps=fps)
                vid.save()
                tcvid = TCExample(video=vid,name=name,type=type,year=year,short_name=year[2:],special_notes=special)
                tcvid.save()

            response +=  " | tc videos created: " + str(TCExample.objects.filter(video__disc_id=discid).count())

        if 'tcnotes' in type or type=='all':
            #VideoNote.objects.filter(video__disc_id=discid).delete()
            query="Select videoid,type,color,linkid,frame,Event,type,event,cr,overridetext,novaluetype,skipframe FROM tcexamplesnotes order by videoid"
            cursor.execute(query)
            lastvid = ""

            for (videoid,type,color,linkid,frame,Event,type,event,cr,overridetext,novaluetype,skipframe) in cursor:
                if cr == None:
                    cr = ''
                if overridetext == None:
                    overridetext = ''
                if novaluetype == None:
                    novaluetype = ''
                if color == None:
                    color = ''
                if skipframe == None or skipframe == '' or skipframe == '0' or skipframe == 0:
                    skipframe = False
                else:
                    skipframe = True
                if color == '9':
                    color = ''
                elif color == 'b':
                    color = 'Blue'
                elif color == 'r':
                    color = 'Red'

                event = event.upper()
                
                if lastvid != videoid:
                    lastvid = videoid
                    video_ref = Video.objects.filter(old_id=videoid+100000,disc_id=discid).first()
                vn = VideoNote(video=video_ref,frame=frame,skip_frame=skipframe,color=color,event=event,cr=cr,override_text=overridetext,no_value_type=novaluetype)
                if type.lower() == "element" and novaluetype.lower() == "unrated":
                    ul = UnratedElement.objects.filter(old_id=linkid,disc_id=discid).first()
                    vn.unrated_link = ul
                elif type == 'E' or type == 'D':
                    rl = RuleLink.objects.filter(old_id=linkid,disc_id=discid).first()
                    vn.rule_link = rl
                else:
                    el = Element.objects.filter(old_id=linkid,disc_id=discid).first()
                    vn.element_link = el
                vn.save();

            response +=  " | tc notes created: " + str(VideoNote.objects.filter(video__disc_id=discid).exclude(video__tcexample=None).count())

        if 'acrobalancepairs' in type or type=='acroall':
            AcroBalance.objects.filter(event='B').delete()
            
            #balance pairs
            query="Select Catagory,`Skill Number`,Value,Bonus,`Transition Bonus`,`Skill Name`,`Skill Description`,TransitionGroup,`Top/Bottom`,`Top Interface Point`,`Bottom Interface Point`,BaseNumber,PageNumber,ThumbnailDirection FROM main"
            cursor.execute(query)

            for (cat,skillnum,value,bonus,transbonus,name,description,transgroup,topbottom,topinterface,bottominterface,basenumber,pagenumber,thumbnaildirection) in cursor:
                if transbonus == None:
                    transbonus = ''
                if transgroup == None:
                    transgroup = ''
                if topinterface == None:
                    topinterface = ''
                if bottominterface == None:
                    bottominterface = ''
                if basenumber == None:
                    basenumber = ''
                if value == None:
                    value = -1
                if bonus == None:
                    bonus = -1
                ab = AcroBalance(event='B',category=cat,skill_number=skillnum,value=value,bonus=bonus,transition_bonus=transbonus,skill_name=name,skill_description=description,transition_group=transgroup,top_bottom=topbottom,top_interface_point=topinterface,bottom_interface_point=bottominterface, \
                    base_number=basenumber,page_number=pagenumber,thumbnail_direction=thumbnaildirection)
                ab.save()

            response +=  " | acro balance pairs created: " + str(AcroBalance.objects.all().count())

        if 'acrobalancetrio' in type or type=='acroall':
            AcroBalance.objects.filter(event='BT').delete()

             #balance trios
            query="Select Event,Category,`Skill Number`,Value,Value2,Value3,Value4,Bonus,`Transition Bonus`,`Skill Name`,`Skill Description`,Orientation,Layer,BaseBoxNumber,TransitionGroup,`Top/Bottom`,`Top Interface Point`,`Bottom Interface Point`,`Bottom Interface Point 2`,SpecialBaseNumber,BaseNumber,PageNumber,ThumbnailDirection,StartNumber FROM maintrio"
            cursor.execute(query)

            for (event,cat,skillnum,value,value2,value3,value4,bonus,transbonus,name,description,orientation,layer,baseboxnumber,transgroup,topbottom,topinterface,bottominterface,bottominterface2,specialbasenumber,basenumber,pagenumber,thumbnaildirection,startnumber) in cursor:
                if transbonus == None:
                    transbonus = ''
                if transgroup == None:
                    transgroup = ''
                if topinterface == None:
                    topinterface = ''
                if description == None:
                    description = ''
                if bottominterface == None:
                    bottominterface = ''
                if basenumber == None:
                    basenumber = ''
                if startnumber == None:
                    startnumber = ''
                if orientation == None:
                    orientation = ''
                if cat == None:
                    cat = ''
                if layer == None:
                    layer = ''
                if specialbasenumber == None:
                    specialbasenumber = ''
                if bottominterface2 == None:
                    bottominterface2 = ''
                if value == None:
                    value = -1
                if value2 == None:
                    value2 = -1
                if value3 == None:
                    value3 = -1
                if value4 == None:
                    value4 = -1
                if bonus == None:
                    bonus = -1
                ab = AcroBalance(event='BT',category=cat,skill_number=skillnum,value=value,value2=value2,value3=value3,value4=value4,bonus=bonus,transition_bonus=transbonus,skill_name=name,skill_description=description,transition_group=transgroup,top_bottom=topbottom,top_interface_point=topinterface,bottom_interface_point=bottominterface,bottom_interface_point2=bottominterface2, \
                    base_number=basenumber,page_number=pagenumber,thumbnail_direction=thumbnaildirection,orientation=orientation,layer=layer,special_base_number=specialbasenumber,start_number=startnumber,base_box_number=baseboxnumber)
                ab.save()

            response +=  " | acro balance trios created: " + str(AcroBalance.objects.all().count())

        if 'acrobalancegroup' in type or type=='acroall':
            AcroBalance.objects.filter(event='BG').delete()

             #balance trios
            query="Select Event,Category,`Skill Number`,Value,Value2,Value3,Value4,Bonus,`Transition Bonus`,`Skill Name`,`Skill Description`,Orientation,Layer,BaseBoxNumber,TransitionGroup,`Top/Bottom`,`Top Interface Point`,`Bottom Interface Point`,`Bottom Interface Point 2`,SpecialBaseNumber,BaseNumber,PageNumber,ThumbnailDirection,StartNumber FROM maingroup"
            cursor.execute(query)

            for (event,cat,skillnum,value,value2,value3,value4,bonus,transbonus,name,description,orientation,layer,baseboxnumber,transgroup,topbottom,topinterface,bottominterface,bottominterface2,specialbasenumber,basenumber,pagenumber,thumbnaildirection,startnumber) in cursor:
                if transbonus == None:
                    transbonus = ''
                if transgroup == None:
                    transgroup = ''
                if topinterface == None:
                    topinterface = ''
                if description == None:
                    description = ''
                if bottominterface == None:
                    bottominterface = ''
                if basenumber == None:
                    basenumber = ''
                if startnumber == None:
                    startnumber = ''
                if orientation == None:
                    orientation = ''
                if cat == None:
                    cat = ''
                if layer == None:
                    layer = ''
                if specialbasenumber == None:
                    specialbasenumber = ''
                if bottominterface2 == None:
                    bottominterface2 = ''
                if value == None or value == '':
                    value = -1
                if value2 == None or value2 == '':
                    value2 = -1
                if value3 == None or value3 == '':
                    value3 = -1
                if value4 == None or value4 == '':
                    value4 = -1
                if bonus == None or bonus == '':
                    bonus = -1
                ab = AcroBalance(event='BG',category=cat,skill_number=skillnum,value=value,value2=value2,value3=value3,value4=value4,bonus=bonus,transition_bonus=transbonus,skill_name=name,skill_description=description,transition_group=transgroup,top_bottom=topbottom,top_interface_point=topinterface,bottom_interface_point=bottominterface,bottom_interface_point2=bottominterface2, \
                    base_number=basenumber,page_number=pagenumber,thumbnail_direction=thumbnaildirection,orientation=orientation,layer=layer,special_base_number=specialbasenumber,start_number=startnumber,base_box_number=baseboxnumber)
                ab.save()

            response +=  " | acro balance groups created: " + str(AcroBalance.objects.all().count())

    return JsonResponse({'result':response})


#Competition Videos
@login_required(login_url='/login/')
@user_passes_test(subscription_check,login_url='/subscriptions/')
def comp_videos(request):
    context = {
        'type':'comp',
         'search_type':'comp',
        'list_type':'comp',
        }
    return render(request, 'app/elements_fixed.html',context=context)

def comp_search(request):
    types = CompetitionType.objects.filter(disc=request.session.get('disc',1)).order_by('display_order').distinct()
    comps = Competition.objects.filter(type__disc=request.session.get('disc',1)).order_by('short_name').values('short_name').distinct()
    groups = CompetitionGroup.objects.filter(competition__type__disc=request.session.get('disc',1)).order_by('short_name').values('short_name').distinct()
    compsDict = {}
    groupsDict = {}

    events=request.session.get('disc_events','V,UB,BB,FX').split(",")
    for comp in comps:
        compTypes = "search-" + " search-".join(str(types['type__short_name']) for types in Competition.objects.filter(short_name = comp['short_name']).values('type__short_name').distinct())
        compsDict[comp['short_name']] = compTypes
    for group in groups:
        groupTypes = "search-" + " search-".join(str(types['competition__type__short_name']) for types in CompetitionGroup.objects.filter(short_name = group['short_name']).values('competition__type__short_name').distinct())
        groupsDict[group['short_name']] = groupTypes
    context = {
        'types':types,
        'comps': comps,
        'groups': groups,
        'compsByType': compsDict,
        'groupsByType': groupsDict,
        'events': events,
        'search_type':'comp',
        }
    return render(request, 'app/video_search.html',context=context)


def comp_list(request):
    dget = dict(request.GET)
    search = dget['search'][0]
    search = search.replace("1/2","½")
    search = search.replace("1/4","¼")
    del dget['search']
    value_display = dget['value_display'][0]
    del dget['value_display']
    query = Q()
    for k,v in dget.items():
        innerQuery = Q()
        for i in v:
            kwargs = {'{0}'.format(k): i}
            innerQuery.add(Q(**kwargs), Q.OR)
        query.add(innerQuery,Q.AND)
    videos = CompetitionVideo.objects.filter(query).order_by('competition_group__competition__year','competition_group__competition__name','competition_group__short_name','name')
    if search != "":
        videos = videos.filter(name__icontains=search)
    videos = videos.filter(competition_group__competition__type__disc_id=request.session.get('disc',1))
    context = {
        'videos': videos,
        'num_videos': str(len(videos)) + " Videos",
        }
    #activity log
    log_activity(request,'Competition Videos','List','')
    return render(request, 'app/video_list.html',context=context)

def comp_video(request):
    vid = CompetitionVideo.objects.get(pk=request.GET.get('compvid'))
    context = {
        'video': vid,
        'type':'comp',
        }
    log_activity(request,'Competition Videos','View',str(vid))
    return render(request, 'app/video_single.html',context=context)

#TCExamples videos
@login_required(login_url='/login/')
@user_passes_test(subscription_check,login_url='/subscriptions/')
def tc_examples(request):
    context = {
        'type':'tc',
        'search_type':'tc',
        'list_type':'tc',
        }
    return render(request, 'app/elements_fixed.html',context=context)

def tc_search(request):
    years = TCExample.objects.filter(video__disc=request.session.get('disc',1)).order_by('short_name').values('short_name').distinct()
    events=request.session.get('disc_events','V,UB,BB,FX').split(",")
    context = {
        'years':years,
        'events': events,
        'search_type':'tc',
        }
    return render(request, 'app/video_search.html',context=context)


def tc_list(request):
    dget = dict(request.GET)
    search = dget['search'][0]
    search = search.replace("1/2","½")
    search = search.replace("1/4","¼")
    del dget['search']
    value_display = dget['value_display'][0]
    del dget['value_display']
    query = Q()
    for k,v in dget.items():
        innerQuery = Q()
        for i in v:
            kwargs = {'{0}'.format(k): i}
            innerQuery.add(Q(**kwargs), Q.OR)
        query.add(innerQuery,Q.AND)
    videos = TCExample.objects.filter(query).order_by('-year','type','name')
    if search != "":
        videos = videos.filter(name__icontains=search)
    videos = videos.filter(video__disc_id=request.session.get('disc',1))
    context = {
        'videos': videos,
        'num_videos': str(len(videos)) + " Videos",
        }
    #activity log
    log_activity(request,'TC Examples','List','')
    return render(request, 'app/tc_list.html',context=context)

def tc_video(request):
    vid = TCExample.objects.get(pk=request.GET.get('tcid'))
    context = {
        'video': vid,
        'type':'tc',
        }
    log_activity(request,'TC Examples','View',str(vid))
    return render(request, 'app/video_tc.html',context=context)

#Judge Instructions
@login_required(login_url='/login/')
@user_passes_test(subscription_check,login_url='/subscriptions/')
def judge_instructions(request):
    context = {
        'type':'ji',
        'search_type':'ji',
        'list_type':'ji',
        }
    return render(request, 'app/elements_fixed.html',context=context)

def ji_search(request):
    years = JudgeInstruction.objects.filter(disc=request.session.get('disc',1)).order_by('year').values('year').distinct()
    types = JudgeInstruction.objects.filter(disc=request.session.get('disc',1)).order_by('type').values('type').distinct()
    events=request.session.get('disc_events','V,UB,BB,FX').split(",")
    context = {
        'years':years,
        'events': events,
        'types': types,
        'search_type':'ji',
        }
    return render(request, 'app/ji_search.html',context=context)

def ji_list(request):
    dget = dict(request.GET)
    discipline = Disc.objects.get(id=request.session.get('disc',1)).full_name
    event = dget['event__iexact'][0];
    type = dget['type'][0];
    year = dget['year'][0];
    path = "https://web-sts.com/" + discipline + "/JudgeInstructions/20" + year + "/" + event + "/" + type + "/index.html"
    context = {
        'path': path,
        }
    log_activity(request,'Judge Instructions','View',str(event + " " + type + " " + year))
    return render(request, 'app/ji_display.html',context=context)

def change_disc(request):
    disc = Disc.objects.get(folder_name=request.GET.get('disc'))
    request.session['disc'] = disc.id
    request.session['disc_path'] = disc.folder_name
    request.session['disc_full_name'] = disc.full_name
    request.session['disc_events'] = disc.event_list
    request.session['disc'] = disc.id;
    request.session['version_name'] = VersionSettings.objects.first().name
    request.session['exclude_screens'] = disc.exclude_screens
    
    return redirect(request.GET.get('next'))  

def contact(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, 'email from: ' + from_email + '\r\n' + message, 'stsmailrecover@gmail.com', ['gymjudgehills@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return render(request, "app/contact.html", context={'form': form,'success':'success'})
    return render(request, "app/contact.html", {'form': form})

def coach_elements(request):
    context = {
        'type':'coach_element',
        'search_type':'coach_element',
        'list_type':'coach_element',
        }
    return render(request, 'app/elements_fixed.html',context=context)

def coach_element_search(request):   
    levels = CoachInstruction.objects.filter(disc=request.session.get('disc',1)).order_by('level').values_list('level',flat=True).distinct()
    events=request.session.get('disc_events','V,UB,BB,FX').split(",")
    context = {
        'levels':levels,
        'events': events,
        'search_type':'element',
        }
    return render(request, 'app/coach_element_search.html',context=context)

def coach_element(request):
    idIn = request.GET.get('id')
    element = CoachInstruction.objects.filter(id=idIn)
    key_points = CoachVideoLine.objects.filter(instruction=idIn,type='key')
    description = CoachVideoLine.objects.filter(instruction=idIn,type='description')
    mechanics = CoachVideoLine.objects.filter(instruction=idIn,type='mechanics')
    #userNote = UserNote.objects.filter(user=request.user.id,element=idIn)
    #if (len(userNote) > 0):
        #userNote = userNote[0].note;
    #else:
        #userNote = '';
    context = {
        'coach_element': element[0],
        'key_points' : key_points,
        'descriptions' : description,
        'mechanics' : mechanics
        }
    #activity log
    log_activity(request,'Coach_Elements','View',str(element[0]))
    return render(request, 'app/coach_element.html',context=context)

def coach_element_list(request):
    dget = dict(request.GET)
    search = dget['search'][0]
    search = search.replace("1/2","½")
    search = search.replace("1/4","¼")
    del dget['search']
    event = dget['event']
    query = Q()
    for k,v in dget.items():
        innerQuery = Q()
        for i in v:
            for ks in k.split(','):#allow multi things
                kwargs = {'{0}'.format(ks): i}
                innerQuery.add(Q(**kwargs), Q.OR)
        query.add(innerQuery,Q.AND)
    elements = CoachInstruction.objects.filter(query).order_by('display_order')
    if search != "":
        #element__usernote__note__icontains=search
        elements = elements.filter(text__icontains=search).distinct() | elements.filter(short_text__icontains=search).distinct() | elements.filter(notes1__icontains=search).distinct() | elements.filter(notes2__icontains=search).distinct() | elements.filter(notes3__icontains=search).distinct()
    elements = elements.filter(disc=request.session.get('disc',1))
    context = {
        'coach_elements': elements,
        'num_elements': str(len(elements)) + " Elements",
        }

    #activity log
    log_activity(request,'Coach Elements','List',request.GET.get('event'))
    return render(request, 'app/coach_element_list.html',context=context)

def coach_update_user_note(request):
    elementIn = request.GET.get('element')
    noteIn = request.GET.get('note')
    elementInstance = Element.objects.get(pk=elementIn)
    note, created = UserNote.objects.update_or_create(
        user=request.user.id,element=elementIn,
        defaults={'user': request.user,'element':elementInstance,'note':noteIn},
    )
    resp = {'updated':True}
    #activity log
    log_activity(request,'Elements','Update User Note',str(elementInstance))
    return JsonResponse(resp)

@login_required(login_url='/login/')
@user_passes_test(subscription_check,login_url='/subscriptions/')
def coach_fundamentals(request):
    context = {
        'type':'Element',
        }
    #activity log
    log_activity(request,'Coach Fundamental','View','')
    return render(request, 'app/coach_base.html',context=context)

def coach_fundamentals_setup(request):
    sects = CoachFundamentalSection.objects.filter(category__disc=request.session.get('disc',1)).order_by('category__display_order','display_order')
    progress = CoachFundamentalUserProgress.objects.filter(user=request.user.id)
    sectDict = {}
    prev_cat = ""
    lock_next = False
    for sect in sects:
        if prev_cat != sect.category:
            lock_next=False
            prev_cat = sect.category
        sectDict[sect.id] = lock_next
        this_sect = progress.filter(section=sect)
        if len(this_sect) > 0:
            if this_sect[0].finished:
                lock_next=False
            else:
                lock_next=True
        else:
            lock_next=True
    context = {
        'sects':sects,
        'locked':sectDict
        }
    return render(request, 'app/coach_fundamentals_setup.html',context=context)

def coach_fundamentals_slides(request):
    sectionIn = request.GET.get('section')
    restart = request.GET.get('restart')
    section = CoachFundamentalSection.objects.get(pk=sectionIn)
    category_on = section.category.id
    categories = CoachFundamentalCategory.objects.filter(disc=request.session.get('disc',1))
    notes = CoachUserNote.objects.filter(user_id=request.user.id,category__disc=request.session.get('disc',1))
    isexam = False
    isquiz = False
    if section.is_graded:
        isexam = True
    if section.is_quiz:
        isquiz = True
    #check for quiz and quiz structure
    if section.is_quiz:
        #check to see if quiz is made
        quiz = CoachFundamentalUserQuiz.objects.filter(slide__section=section).order_by('display_order')
        if len(quiz) <= 0:
            #make quiz
            slides = CoachFundamentalSlide.objects.filter(section=sectionIn).order_by('?')
            for x in range(section.number_of_questions):
                uq = CoachFundamentalUserQuiz(slide=slides[x],user_id=request.user.id,display_order=x)
                uq.save()
            quiz = CoachFundamentalUserQuiz.objects.filter(slide__section=section).order_by('display_order')
        elif restart=="true":
            #this is a restart, go through their answers and use the ones they got wrong to start it
            CoachFundamentalUserQuiz.objects.filter(slide__section=section).delete()
            prev_answers =  CoachFundamentalUserAnswer.objects.filter(answer__slide__section=section,user_id=request.user.id,answer__correct=False)
            already_used = list()
            for x in range(len(prev_answers)):
                uq = CoachFundamentalUserQuiz(slide=prev_answers[x].answer.slide,user_id=request.user.id,display_order=x)
                uq.save()
                already_used.append(prev_answers[x].answer.slide.id)
            slides = CoachFundamentalSlide.objects.filter(section=sectionIn).exclude(id__in=already_used).order_by('?')
            for x in range(len(prev_answers),section.number_of_questions):
                uq = CoachFundamentalUserQuiz(slide=slides[x],user_id=request.user.id,display_order=x)
                uq.save()
            quiz = CoachFundamentalUserQuiz.objects.filter(slide__section=section).order_by('display_order')
            CoachFundamentalUserAnswer.objects.filter(answer__slide__section=section,user_id=request.user.id).delete()
            CoachFundamentalUserProgress.objects.filter(section=sectionIn,user=request.user.id).delete()
        #order slides
        slide_list = list()
        for q in quiz:
            slide_list.append(q.slide.id)
        clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(slide_list)])
        ordering = 'CASE %s END' % clauses
        slides = CoachFundamentalSlide.objects.filter(id__in=slide_list).extra(select={'ordering': ordering}, order_by=('ordering',))
    else:
        if restart=="true":
            CoachFundamentalUserAnswer.objects.filter(answer__slide__section=section,user_id=request.user.id).delete()
            CoachFundamentalUserProgress.objects.filter(section=sectionIn,user=request.user.id).delete()
        slides = CoachFundamentalSlide.objects.filter(section=sectionIn).order_by('display_order')
    highest = CoachFundamentalUserProgress.objects.filter(section=sectionIn,user=request.user.id).values("highest_slide")
    if len(highest) <= 0:
        highest=0
    else:
        highest=highest[0]["highest_slide"]
    context = {
        'slides':slides,
        'section':sectionIn,
        'highest':highest,
        'isexam':isexam,
        'isquiz':isquiz,
        'categories':categories,
        'category_on':category_on,
        'notes':notes
        }
    return render(request, 'app/coach_fundamentals_slides.html',context=context)

def coach_fundamentals_slide(request):
    slideIn = request.GET.get('slide')
    slide = CoachFundamentalSlide.objects.get(pk=slideIn)
    if slide.interaction_random_order:
        answers = CoachFundamentalAnswer.objects.filter(slide=slideIn).order_by('?')
    else:
        answers = CoachFundamentalAnswer.objects.filter(slide=slideIn).order_by('id')
    user_answers = CoachFundamentalUserAnswer.objects.filter(answer__slide=slide,user_id=request.user.id)
    context = {
        'slide':slide,
        'answers':answers,
        'user_answers':user_answers
        }
    return render(request, 'app/coach_fundamentals_individual_slide.html',context=context)

def coach_check_answer(request):
    data = json.loads(request.body)
    slide = CoachFundamentalSlide.objects.get(pk=data["slide"])
    answers = CoachFundamentalAnswer.objects.filter(slide=slide)
    correct = True
    answers_dict = {}
    count = 0
    correct_id = -1
    for answer in answers:
        if str(answer.id) in data["answers"]:
            answers_dict[count] = {}
            answers_dict[count]['id'] = answer.id
            answers_dict[count]['response'] = answer.response_text
            answers_dict[count]['correct'] = answer.correct
            count += 1
        if answer.correct == False and str(answer.id) in data["answers"]:
            correct = False
        if answer.correct:
            correct_id = answer.id
    resp = {'Correct':correct,
            'Answers':answers_dict,
            'Correct_ID':correct_id}
    #activity log

    return JsonResponse(resp)

def coach_update_progress(request):
    section = request.GET.get('section')
    highest = request.GET.get('highest')
    finished = request.GET.get('finished',False)
    if finished == "false":
        finished = False
    else:
        finished = True
    sectionInstance = CoachFundamentalSection.objects.get(pk=section)
    progress, created = CoachFundamentalUserProgress.objects.update_or_create(
        user=request.user.id,section=sectionInstance,
        defaults={'user': request.user,'section':sectionInstance,'highest_slide':highest,'finished':finished},
    )
    unlock = -1
    if finished:
        ids = list(CoachFundamentalSection.objects.filter(category__disc=request.session.get('disc',1)).order_by('category__display_order','display_order').values_list('id',flat=True))
        index = ids.index(int(section))
        if index < len(ids)-1 and finished:
            this_sect = CoachFundamentalSlide.objects.filter(section__id=ids[index+1])
            if len(this_sect) > 0:
                unlock=ids[index+1]

    resp = {'updated':True,
            'unlock':unlock}
    return JsonResponse(resp)

def coach_set_answer(request):
    answers = request.GET.get('answers').split(",")
    for answer in answers:
        ua = CoachFundamentalUserAnswer(user_id=request.user.id,answer_id=answer)
        ua.save()
    resp = {'updated':True}
    return JsonResponse(resp)

def coach_save_note(request):
    categoryIn = request.GET.get('category')
    noteIn = request.GET.get('note')
    categoryInstance = CoachFundamentalCategory.objects.get(pk=categoryIn)
    note, created = CoachUserNote.objects.update_or_create(
        user=request.user.id,category=categoryInstance,
        defaults={'user': request.user,'category':categoryInstance,'note':noteIn},
    )
    resp = {'updated':True}
    #activity log
    #log_activity(request,'Elements','Update User Note',str(elementInstance))
    return JsonResponse(resp)