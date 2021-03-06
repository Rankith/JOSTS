"""
Definition of urls for JOSTS.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from app import forms, views
from django.conf import settings
from django.conf.urls.static import static
from app.models import Disc


urlpatterns = [
    path('', views.elements, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('elements/', views.elements, name='elements'),
    path('element/', views.element, name='element'),
    path('login/', views.loginview, name='loginview'),
   # path('login/',
    #     LoginView.as_view
    #     (
    #         template_name='app/login.html',
    #         authentication_form=forms.BootstrapAuthenticationForm,
    #         extra_context=
    #         {
    #             'discs': Disc.objects.all(),
    #             'title': 'Log in',
    #             'year' : datetime.now().year,
    #         }
    #     ),
    #     name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    path('ajax/update_user_note', views.update_user_note, name='update_user_note'),
    path('element_search/', views.element_search, name='element_search'),
    path('element_list/', views.element_list, name='element_list'),
    path('rules/', views.rules, name='rules'),
    path('rule/', views.rule, name='rule'),
    path('rule_search/', views.rule_search, name='rule_search'),
    path('rule_list/', views.rule_list, name='rule_list'),
    path('rule_vid_ref/', views.rule_vid_ref, name='rule_vid_ref'),
    path('shorthand_training/', views.shorthand_training, name='shorthand_training'),
    path('shorthand_trainer/', views.shorthand_trainer, name='shorthand_trainer'),
    path('save_record_image/', views.save_record_image, name='save_record_image'),
    path('shorthand_lookup/', views.shorthand_lookup, name='shorthand_lookup'),
    path('shorthand_search/', views.shorthand_search, name='shorthand_search'),
    path('element_for_shorthand/', views.element_for_shorthand, name='element_for_shorthand'),
    path('element_lookup/', views.element_lookup, name='element_lookup'),
    path('quiz_shorthand/', views.quiz_shorthand, name='quiz_shorthand'),
    path('quiz_element/', views.quiz_element, name='quiz_element'),
    path('quiz_setup/', views.quiz_setup, name='quiz_setup'),
    path('quiz/', views.quiz, name='quiz'),
    path('quiz_save/', views.quiz_save, name='quiz_save'),
    path('quiz_results/', views.quiz_results, name='quiz_results'),
    path('quiz_delete/', views.quiz_delete, name='quiz_delete'),
    path('signup/', views.signup, name='signup'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('unsubscribe_feedback/', views.unsubscribe_feedback, name='unsubscribe_feedback'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('cancel/', views.subscription_cancel, name='cancel'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('user_settings/', views.user_settings, name='user_settings'),
    path('video_player/', views.video_player, name='video_player'),
    path('video_notes_builder/', views.video_notes_builder, name='video_notes_builder'),
    path('get_video_notes/', views.get_video_notes, name='get_video_notes'),
    path('video_notes/', views.video_notes, name='video_notes'),
    path('ajax/update_video_links/', views.update_video_links, name='update_video_links'),
    path('ajax/save_video_notes/', views.save_video_notes, name='save_video_notes'),
    path('ajax/update_video_approved/', views.update_video_approved, name='update_video_approved'),
    path('check_tour/', views.check_tour, name='check_tour'),
    path('fig_import/', views.import_from_fig, name='fig_import'),
    path('competition_videos/', views.comp_videos, name='competition_videos'),
    path('comp_search/', views.comp_search, name='comp_search'),
    path('comp_list/', views.comp_list, name='comp_list'),
    path('comp_video/', views.comp_video, name='comp_video'),
    path('tc_examples/', views.tc_examples, name='tc_examples'),
    path('tc_search/', views.tc_search, name='tc_search'),
    path('tc_list/', views.tc_list, name='tc_list'),
    path('tc_video/', views.tc_video, name='tc_video'),
    path('judge_instructions/', views.judge_instructions, name='judge_instructions'),
    path('ji_search/', views.ji_search, name='ji_search'),
    path('ji_list/', views.ji_list, name='ji_list'),
    path('change_disc/', views.change_disc, name='change_disc'),
    path('contact/', views.contact, name='contact'),
    path('coach_elements/', views.coach_elements, name='coach_elements'),
    path('coach_element_search/', views.coach_element_search, name='coach_element_search'),
    path('coach_element_list/', views.coach_element_list, name='coach_element_list'),
    path('coach_element/', views.coach_element, name='coach_element'),
    path('coach_update_user_note/', views.coach_update_user_note, name='coach_update_user_note'),
    path('coach_fundamentals/', views.coach_fundamentals, name='coach_fundamentals'),
    path('coach_fundamentals_setup/', views.coach_fundamentals_setup, name='coach_fundamentals_setup'),
    path('coach_fundamentals_slides/', views.coach_fundamentals_slides, name='coach_fundamentals_slides'),
    path('coach_fundamentals_slide/', views.coach_fundamentals_slide, name='coach_fundamentals_slide'),
    path('ajax/coach_check_answer/', views.coach_check_answer, name='coach_check_answer'),
    path('ajax/coach_update_progress', views.coach_update_progress, name='coach_update_progress'),
    path('ajax/coach_set_answer', views.coach_set_answer, name='coach_set_answer'),
    path('ajax/coach_save_note', views.coach_save_note, name='coach_save_note'),
    path('element_builder_acro/', views.element_builder_acro, name='element_builder_acro'),
    path('ajax/acro_get_score/', views.acro_get_score, name='acro_get_score'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
