from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        user_model = get_user_model()
        try:
            email = kwargs.get("email", None)
            if email is None:
                email = kwargs.get("username", None)

            user = user_model.objects.get(email=email, is_active=True)

            if user.check_password(kwargs.get("password", None)):
                return user
        except user_model.DoesNotExist:
            return None
        return None
