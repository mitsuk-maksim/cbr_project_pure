from allauth.account.utils import setup_user_email
from django.contrib.auth.models import User
from graphene import Context
from allauth.account.adapter import get_adapter


class AuthControllerService:

    def sign_up(self, request: Context):
        # Get AccountAdapter `user.functions.CustomtAccountAdapter`
        adapter = get_adapter()
        self.request = request
        # Creates new empty user and saves it, triggers post_save signal for User
        # Why user gets saved when new_user is called?
        # new_user -> from DefaultAccountAdapter.new_user
        user: User = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])

        return user

    def get_cleaned_data(self):
        data = self.request.input
        return {
            'username': data.get('username', 'test'),
            'email': data.get('email', '')
        }

    def validate_new_password(self, password):
        return get_adapter().clean_password(password)
