from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserSettingsForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    plate_number = forms.CharField(max_length=15, required=True)
    password = forms.CharField(max_length=100, required=False, widget=forms.PasswordInput, help_text='Leave blank if no change.')

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'plate_number', 'selected_slot', 'selected_area', 'arrival_time', 'exit_time']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['plate_number'].initial = user.profile.plate_number

        # disabled field
        self.fields['selected_slot'].disabled = True
        self.fields['selected_area'].disabled = True
        self.fields['arrival_time'].disabled = True
        self.fields['exit_time'].disabled = True

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = self.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        profile = self.instance
        profile.plate_number = self.cleaned_data['plate_number']
        profile.selected_slot = self.cleaned_data['selected_slot']
        profile.selected_area = self.cleaned_data['selected_area']
        profile.arrival_time = self.cleaned_data['arrival_time']
        profile.exit_time = self.cleaned_data['exit_time']
        profile.save()
        return profile
