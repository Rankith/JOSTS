from django.contrib import admin
from app.models import Element, ElementText, Video, UserNote, Rule, RuleText, DrawnImage, SymbolDuplicate, SubscriptionTest, Subscription, SubscriptionSetup, QuizResult, ActivityLog, UnsubscribeFeedback, Theme, UserSettings, RuleLink, VideoNote, PageTour, UserToursComplete, VideoLink, Disc, UnratedElement
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class ElementAdmin(ImportExportModelAdmin): 
#class ElementAdmin(admin.ModelAdmin): 
    list_display = ('id_number','str_grp','code_order','disc','event','letter_value','value','id')
    list_filter = ('disc','event','str_grp','letter_value','range')
    search_fields = ('id_number',)#comment if importing
    list_editable = ('str_grp','code_order','event','letter_value','value')#comment if importing
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ('user','element','note')
class ElementTextAdmin(ImportExportModelAdmin): 
#class ElementTextAdmin(admin.ModelAdmin):
    list_display = ('element','language','id_number_text','text','short_text','named','additional_info','hold_text')
    list_filter = ('element__disc','element__event','element__str_grp','element__letter_value','element__range')
    search_fields = ('text','short_text','named') #comment if importing
    list_editable = ('language','id_number_text','text','short_text','named','additional_info','hold_text') #comment if importing

class RuleAdmin(ImportExportModelAdmin): 
    list_display = ('id','rule_id','disc','event','section','rule_no','sub_rule')
    list_filter = ('disc','event',)
    list_editable = ('event','section','rule_no','sub_rule')

class RuleTextAdmin(ImportExportModelAdmin):
    list_display = ('rule','cue','response','additional_info','rule_description','specific_deduction','cat0','cat1','cat2','cat3','cat4')
    list_filter = ('rule__disc','rule__event','rule__section')
    list_editable = ('cue','response','additional_info','rule_description','specific_deduction','cat0','cat1','cat2','cat3','cat4')
    search_fields = ('cue','response','additional_info','rule_description')

class DrawnImageAdmin(admin.ModelAdmin):
    list_display = ('id','name','label','disc','event')
    list_editable = ('name','label','disc','event')
    search_fields = ('name','label','event')
    list_filter = ('disc','event')

class SymbolDuplicateAdmin(ImportExportModelAdmin):
    list_display = ('id','symbol','replace_with','event','disc')
    list_editable = ('symbol','replace_with','event','disc')
    search_fields = ('symbol','replace_with','event')
    list_filter = ('event','disc')

class SubscriptionTestAdmin(admin.ModelAdmin):
    list_display = ('id','type')
    list_filter = ('type',)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id','user','customer_id','subscription_id','expires','interval','type','cancelled','free')
    search_fields = ('user','customer_id','subscription_id','type')
    list_filter = ('type','interval','cancelled','free')

class SubscriptionSetupAdmin(admin.ModelAdmin):
    list_display = ('id','display_text','stripe_plan_id','type','interval')
    list_editable = ('display_text','stripe_plan_id','type','interval')
    list_filter = ('type','interval')

class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('id','user','event','disc','date_completed','correct','wrong','type')
    list_editable = ('event','date_completed','correct','wrong','type')
    search_fields = ('event','date_completed','type')
    list_filter = ('disc','event','type')

class NormalUserFilter(admin.SimpleListFilter):
    title = "Normal User"
    parameter_name = 'users'

    def lookups(self, request, model_admin):
        return [('Normal User','Normal User'),]

    def queryset(self, request, queryset):
        if self.value() == "Normal User":
            return queryset.filter(actor__is_staff=False).filter(actor__is_superuser=False)

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id','actor','action_type','action_detail','action_item','disc','timestamp')
    search_fields = ('actor__username','actor__email','action_type','action_detail','disc','action_item')
    list_filter = ('disc','action_type',NormalUserFilter)

class UnsubscribeFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id','expensive','dont_need','different_features','low_quality','hard_to_use','other','other_details')

class ThemeAdmin(admin.ModelAdmin):
    list_display=('name','file')

class UserSettingsAdmin(admin.ModelAdmin):
    list_display=('user','theme')

class RuleLinkAdmin(ImportExportModelAdmin):
    list_display = ('id','text','type','event','category_name','category_order','deduction_amount','connected_elements')
    list_editable = ('text','type','event','category_name','category_order','deduction_amount','connected_elements')
    search_fields = ('event','text','category_name','deduction_amount','type','rule')
    list_filter = ('event','type')

class VideoNoteAdmin(admin.ModelAdmin):
    list_display = ('id','video','rule_link','element_link','frame','skip_frame','color','event','cr','override_text','no_value_type','timestamp')
    list_editable = ('frame','skip_frame','color','event','cr','override_text','no_value_type')
    search_fields = ('event','color','video__id','rule_link__id','element_link__id','color','override_text')
    list_filter = ('video__disc','event','color','no_value_type')

class PageTourAdmin(admin.ModelAdmin):
    list_display=('id','url','file')
    list_editable=('url','file')

class UserToursCompleteAdmin(admin.ModelAdmin):
    list_display=('id','user','page')
    search_fields = ('user','page')

class VideoLinkAdmin(admin.ModelAdmin):
    list_display=('id','video','element','order','frame_jump')
    list_editable=('video','element','order','frame_jump')

class VideoAdmin(admin.ModelAdmin):
    list_display=('id','disc','event','file','fps','approved', 'approved_johanna')
    list_editable=('disc','event','file','fps','approved', 'approved_johanna')

admin.site.register(Element,ElementAdmin)
admin.site.register(ElementText,ElementTextAdmin)
admin.site.register(Rule,RuleAdmin)
admin.site.register(RuleText,RuleTextAdmin)
admin.site.register(Video,VideoAdmin)
admin.site.register(UserNote,UserNoteAdmin)
admin.site.register(DrawnImage,DrawnImageAdmin)
admin.site.register(SymbolDuplicate,SymbolDuplicateAdmin)
admin.site.register(Subscription,SubscriptionAdmin)
admin.site.register(SubscriptionSetup,SubscriptionSetupAdmin)
admin.site.register(QuizResult,QuizResultAdmin)
admin.site.register(ActivityLog,ActivityLogAdmin)
admin.site.register(UnsubscribeFeedback,UnsubscribeFeedbackAdmin)
admin.site.register(Theme,ThemeAdmin)
admin.site.register(UserSettings,UserSettingsAdmin)
admin.site.register(RuleLink,RuleLinkAdmin)
admin.site.register(VideoNote,VideoNoteAdmin)
admin.site.register(VideoLink,VideoLinkAdmin)
admin.site.register(PageTour,PageTourAdmin)
admin.site.register(UserToursComplete,UserToursCompleteAdmin)
admin.site.register(Disc)
admin.site.register(UnratedElement)