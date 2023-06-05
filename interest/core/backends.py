from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Check if username is provided as an email
        if '@' in username:
            kwargs = {'email': username}
        # Check if username is provided as a phone number
        elif username.isdigit():
            kwargs = {'phone': username}
        else:
            kwargs = {'username': username}

        try:
            user = User.objects.get(**kwargs)
        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None