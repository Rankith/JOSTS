"""
Definition of urls for JOSTS.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from django.conf import settings
from django.conf.urls.static import static


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
    path('shorthand_training/', views.shorthand_training, name='shorthand_training'),
    path('shorthand_trainer/', views.shorthand_trainer, name='shorthand_trainer'),
    path('save_record_image/', views.save_record_image, name='save_record_image'),
    path('shorthand_lookup/', views.shorthand_lookup, name='shorthand_lookup'),
    path('shorthand_search/', views.shorthand_search, name='shorthand_search'),
    path('element_for_shorthand/', views.element_for_shorthand, name='element_for_shorthand'),
    path('element_lookup/', views.element_lookup, name='element_lookup'),
    path('quiz_shorthand/', views.quiz_shorthand, name='quiz_shorthand'),
    path('quiz_setup/', views.quiz_setup, name='quiz_setup'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
