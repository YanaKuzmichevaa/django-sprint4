from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

from django.views.generic import CreateView


class RegistrCreateView(CreateView):
    template_name = 'registration/registration_form.html',
    form_class = UserCreationForm,
    success_url = reverse_lazy('blog:index')
