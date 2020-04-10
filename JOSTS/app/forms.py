"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from app.models import SubscriptionSetup,UnsubscribeFeedback,UserSettings,Theme,Disc

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=200)
    subs = SubscriptionSetup.objects.all()
    subscription = forms.ModelChoiceField(subs,empty_label = None)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

class SettingsForm(forms.ModelForm):
    th = Theme.objects.all()
    theme = forms.ModelChoiceField(th,empty_label = None)

    class Meta:
        model = UserSettings
        fields = ('theme',)

class SubscriptionForm(forms.Form):
    subs = SubscriptionSetup.objects.all()
    subscription = forms.ModelChoiceField(subs,empty_label = None)
    #subscription = forms.ChoiceField(choices=choices, widget=forms.Select)

class UnsubscribeFeedbackForm(forms.ModelForm):
    class Meta:
        model = UnsubscribeFeedback
        exclude=('user',)
        labels = {
            "expensive": "Too Expensive",
            "dont_need": "No Longer Needed",
            "different_features": "Does Not Have Features I Want",
            "low_quality": "Quality Was Low",
            "hard_to_use": "Hard To Use",
            "other": "Other",
            "other_details": "Other Notes",
            }

class LoginForm(AuthenticationForm):
    discs = Disc.objects.filter(show_login=True)
    disc = forms.ModelChoiceField(discs,widget=forms.RadioSelect(attrs={'class':'radio_login'}), empty_label = None)

    class Meta:
        model = User
        fields = ('username', 'password')

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)