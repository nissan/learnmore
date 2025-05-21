from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django import forms
from .models import UserProfile

# Create your views here.

class LandingPageView(TemplateView):
    template_name = 'coreapp/landing.html'

class UserLoginView(LoginView):
    template_name = 'coreapp/login.html'
    authentication_form = AuthenticationForm
    success_url = reverse_lazy('landing')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('landing')

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = UserProfile.ROLE_CHOICES
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label='Register as')

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('role',)

class UserRegisterView(FormView):
    template_name = 'coreapp/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('landing')

    def form_valid(self, form):
        user = form.save()
        role = form.cleaned_data['role']
        UserProfile.objects.create(user=user, role=role)
        login(self.request, user)
        return super().form_valid(form)
