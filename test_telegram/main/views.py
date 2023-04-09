import json
from django.contrib.auth.decorators import login_required
from .models import User
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from .forms import LoginForm
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('user_profile')
        else:
            return redirect('main_page')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('user_profile')
        else:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            user_nickname = data.get('user_nickname')
            image_url = data.get('image_url')
            user_phone = data.get('user_phone')
            user_ = User.objects.create_user(username, email, password, user_nickname, image_url, user_phone)
            user_.get_remote_image()
            return HttpResponseRedirect(reverse_lazy('main_page'))


class LoginView(View):
    form_class = LoginForm
    template_name = "index.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('user_profile')
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request=request, data=request.POST)
        if form.is_valid():
            form.clean()
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect('user_profile')
            else:
                form.add_error('username', 'wrong login/password')
        else:
            form.add_error('username', 'wrong login/password')
        return render(request, self.template_name, {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html')

def logout_view(request):
    logout(request)
    return redirect('main_page')
