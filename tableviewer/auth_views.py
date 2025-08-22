from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.conf import settings

from tableviewer.forms import UserLoginForm


class UserLogin(LoginView):
    template_name = "auth/login.html"
    authentication_form = UserLoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('index')
    redirect_field_name = 'next'

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(UserLogin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserLogin, self).get_context_data(**kwargs)
        context['title'] = "Login"
        # context['support_form'] = SupportForm(initial={'url': self.request.build_absolute_uri()})
        return context

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, 'Email or password is incorrect.')

        return super(UserLogin, self).form_invalid(form)


class UserLogout(View):
    @staticmethod
    def get(request, *args, **kwargs):
        logout(request)
        return redirect(settings.LOGIN_REDIRECT_URL)
