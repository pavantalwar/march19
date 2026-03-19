#django
from django.db.models import Max
from django.db import transaction
from django.conf import settings

#restframework
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

#local imports
# from authentication.models import FCMToken

#external imports
# from pyfcm import FCMNotification  
import requests


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'  
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'next_page': self.get_next_link(),
            'prev_page': self.get_previous_link(),
            'count': self.page.paginator.count,
            'rows_per_page':self.page_size,
            'results': data
        })

def success_response(data=None, message="Success"):
    """
    Returns standardized success response dict.
    """
    return {
        "success": True,
        "message": message,
        "data": data
    }

def error_response(errors=None, message="Error"):
    """
    Returns standardized error response dict.
    """
    return {
        "success": False,
        "message": message,
        "errors": errors
    }



# def send_filing_alert_notification(target_users, filing, document_obj, sender_user):
#     """
#     Sends FCM notifications to target users for a filing document alert.

#     Args:
#         target_users (QuerySet or list of User): Users to send notifications to.
#         filing (Filing): Filing object.
#         document_obj (Document): The related document object.
#         sender_user (User): The user triggering the notification (e.g., request.user).
#     """

#     if not target_users:
#         return

#     # Prepare notification content
#     notification_title = 'Filing Document Alert!'
#     notification_body = f'You have a new alert request from {sender_user.full_name}!'

#     # Initialize FCM
#     fcm = FCMNotification(
#         service_account_file=settings.NOTIFICATION_FILE_PATH,
#         project_id='ca-arushi'
#     )

#     # Collect device tokens
#     device_tokens = FCMToken.objects.filter(
#         user__in=target_users,
#         is_active=True
#     ).values_list('token', flat=True)

#     if not device_tokens:
#         return

#     # Build notification list
#     notifications = [
#         {
#             'fcm_token': token,
#             'notification_title': notification_title,
#             'notification_body': notification_body,
#             'data_payload': {
#                 'filing_id': str(filing.id),
#                 'document_id': str(document_obj.id)
#             }
#         }
#         for token in device_tokens
#     ]

#     # Send notification
#     fcm.async_notify_multiple_devices(notifications)

def send_otp_via_msg91(mobile, payload=None):
    """
    Sends an OTP to the given mobile number using MSG91.
    Args:
        mobile: Mobile number (10 digits, no +91)
        payload: Optional dictionary with additional data (e.g., custom OTP)
    Returns:
        dict: MSG91 API response
    Raises:
        Exception: If sending the OTP fails
    """
    url = "https://control.msg91.com/api/v5/otp"
    params = {
        "template_id": settings.OTP_TEMPLATE_ID,
        "otp_length": 6,
        "mobile": f"91{mobile}",
        "authkey": settings.OTP_AUTH_KEY,
        "realTimeResponse": 1
    }
    headers = {
        "Content-Type": "application/json"
    }
    if payload is None:
        payload = {}
    try:
        response = requests.post(url, params=params, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("type") != "success":
            raise Exception(data.get("message", "OTP send failed"))
        return data
    except Exception as e:
        raise Exception("Failed to send OTP: " + str(e))
    
def verify_otp_via_msg91(mobile, otp):
    """
    Verifies the OTP entered by the user using MSG91.
    Args:
        mobile: Mobile number (10 digits)
        otp: OTP string entered by the user
    Returns:
        dict: MSG91 response
    Raises:
        Exception: If OTP verification fails
    """
    url = "https://control.msg91.com/api/v5/otp/verify"
    params = {
        "otp": otp,
        "mobile": f"91{mobile}",
        "authkey": settings.OTP_AUTH_KEY
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("type") != "success":
            raise Exception(data.get("message", "OTP verification failed"))
        return data
    except Exception as e:
        raise Exception("OTP verification failed: " + str(e))
    

# def save_fcm_token(user, token_type, fcm_token):
#     if not user.fcm_token:
#         token_data = {
#             token_type: fcm_token
#         }
#         fcm_token_obj = FCMToken.objects.create(**token_data)
#         user.fcm_token = fcm_token_obj
#         user.save(update_fields=['fcm_token'])
#     else:
#         setattr(user.fcm_token, token_type, fcm_token)
#         user.fcm_token.save()    