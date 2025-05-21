from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

# Create your views here.

class LandingPageView(TemplateView):
    template_name = 'coreapp/landing.html'

@login_required
def dashboard(request):
    user = request.user
    if hasattr(user, 'is_staff') and user.is_staff:
        return redirect('/learnmore/instructors/dashboard/')
    # Otherwise, redirect to the student dashboard
    return redirect('/learnmore/students/dashboard/')
