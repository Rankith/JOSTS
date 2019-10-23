"""
Definition of urls for JOSTS.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views


urlpatterns = [
    path('', views.elements, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('elements/', views.elements, name='elements'),
    path('element/', views.element, name='element'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    path('ajax/update_user_note', views.update_user_note, name='update_user_note'),
    path('element_search/', views.element_search, name='element_search'),
    path('element_list/', views.element_list, name='element_list'),
    path('rules/', views.rules, name='rules'),
    path('rule/', views.rule, name='rule'),
    path('rule_search/', views.rule_search, name='rule_search'),
    path('rule_list/', views.rule_list, name='rule_list'),
]
