"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest
from app.models import Skill,EnglishSkill,Video

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


def skills(request):
    skills = EnglishSkill.objects.filter(language="EN")
    context = {
        'lang_skills': skills,
        }
    return render(request, 'app/skills.html',context=context)

def skill(request):
    idIn = request.GET.get('id')
    skill = EnglishSkill.objects.filter(id=idIn)
    context = {
        'lang_skills': skill[0],
        }
    return render(request, 'app/skill.html',context=context)