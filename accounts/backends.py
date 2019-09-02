from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)

        if user:
            return user

        # id 로그인 실패 상황
        # e-mail 로그인 시도
        UserModel = get_user_model()
        # 원래 id 로그인 처리를 할 때 username이 넘어왔을 경우
        email = username

        if username is None:
            email = kwargs.get(UserModel.EMAIL_FIELD, kwargs.get('email'))
        try:
            user = UserModel._default_manager.get(email=email)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
