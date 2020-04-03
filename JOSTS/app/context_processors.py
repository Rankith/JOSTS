from django.conf import settings # import the settings file

def video_settings(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'SHOW_COMPETITION_VIDEOS': settings.SHOW_COMPETITION_VIDEOS,
            'SHOW_JUDGE_INSTRUCTIONS': settings.SHOW_JUDGE_INSTRUCTIONS,
            'SHOW_TC_EXAMPLES': settings.SHOW_TC_EXAMPLES,
            'SHOW_DISC_SWITCH': settings.SHOW_DISC_SWITCH,
            'SHOW_VIDEOS': settings.SHOW_VIDEOS}