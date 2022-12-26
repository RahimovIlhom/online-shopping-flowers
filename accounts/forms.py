from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreateForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'age']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'age']