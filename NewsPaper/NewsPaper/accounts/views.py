from django.shortcuts import render, group
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from .forms import SignUpForm
from new.models import Author

class SignUp(CreateView):
    model = User
    form_class = SignUpForm
    success_url = '/accounts/login'
    template_name = 'registration/signup.html'
# Create your views here.

@login_required
def upgrade_user(request):
    user = request.user
    group = Group.objects.get(name='authors')
    Author.objects.create(authorUser=get(pk=user.id))
    return redirect('/')