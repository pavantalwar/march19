#restframework import
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination

#Django imports
from datetime import datetime
from django.conf import settings

#local imports
from authentication.models import CustomUser

#black blaze sdk imports
# from b2sdk.v2 import InMemoryAccountInfo, B2Api

import requests

def get_tokens_for_user(CustomUser: CustomUser):
    """
    Generate JWT refresh and access tokens for a given user.

    Adds custom claims (full_name, email, mobile) into the token.

    Args:
        user (User): The user instance for whom to generate tokens.

    Returns:
        dict: A dictionary containing:
            - refresh (str): Refresh token as a string.
            - access (str): Access token as a string.
            - expiry_time (int): Token expiry timestamp in milliseconds.
    """
    token = RefreshToken.for_user(CustomUser)
    token["full_name"] = CustomUser.full_name
    token["email"] = CustomUser.email
    token["mobile"] = CustomUser.mobile
    token["role"] = CustomUser.role
    return {
    'refresh': str(token),
    'access': str(token.access_token),
    'expiry_time': (token.access_token['exp'] * 1000),
    'full_name': CustomUser.full_name,
    'email': CustomUser.email,
    'mobile': CustomUser.mobile,
    'role': CustomUser.role
}



def datetime_fmt(datetime_obj=None) -> str:
    return datetime.strftime(datetime_obj, "%d %b %y %I:%M %p")
    
def handle_exception(exception: Exception):
    message = "Some Exception was thrown."
    if len(exception.args):
        message = exception.args[0]
    return message

def handle_pagination(paginator: PageNumberPagination):
    return_dict = {
        "page": 1,
        "next_page": 0,
        "prev_page": 0,
    }
    return_dict['page'] = paginator.page.number
    return_dict['next_page'] = True if paginator.get_next_link() else False
    return_dict['prev_page'] = True if paginator.get_previous_link() else False
    return return_dict

def copy_with_specific_properties(source_dict, properties):
    return {key: source_dict[key] for key in properties if key in source_dict}

