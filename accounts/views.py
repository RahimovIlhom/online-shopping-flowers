from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreateForm

class SignUpView(CreateView):
    form_class = CustomUserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'