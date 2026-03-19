from rest_framework.views import APIView
from core.utils import error_response, success_response, Response
from . import validators, models
from core import general
from rest_framework import status
from django.contrib.auth import authenticate
from core.exception import SerializerError


# ================= REGISTER =================
class UserRegistrationView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            validator = validators.UserRegisterValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)

            data = validator.validated_data

            email = data.get("email")
            mobile = data.get("mobile")

            # ================= DUPLICATE CHECK =================
            if models.CustomUser.objects.filter(email=email).exists():
                return Response(
                    error_response(
                        message="Email already exists",
                        errors="Duplicate email"
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )

            if models.CustomUser.objects.filter(mobile=mobile).exists():
                return Response(
                    error_response(
                        message="Mobile already exists",
                        errors="Duplicate mobile"
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )

            password = data.pop("password")

            # ================= CREATE USER =================
            user = models.CustomUser.objects.create_user(
                email=email,
                password=password,
                full_name=data.get("full_name"),
                mobile=mobile,
                gender=data.get("gender"),
                role=data.get("role"),
                age=data.get("age")
            )

            if data.get("image"):
                user.image = data.get("image")
                user.save()

            return Response(
                success_response(
                    message="User registered successfully",
                    data={
                        "id": str(user.id),
                        "full_name": user.full_name,
                        "email": user.email,
                        "mobile": user.mobile,
                        "role": user.role
                    }
                ),
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                error_response(
                    message="Something went wrong",
                    errors=str(e)
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ================= LOGIN =================
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            validator = validators.LoginValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)

            data = validator.validated_data

            email = data['email']
            password = data['password']
            role = data['role']

            # ================= USER CHECK =================
            try:
                user = models.CustomUser.objects.get(email=email, is_active=True)
            except models.CustomUser.DoesNotExist:
                return Response(
                    error_response(
                        message="User not found",
                        errors="Invalid email"
                    ),
                    status=status.HTTP_404_NOT_FOUND
                )

            # ================= ROLE CHECK =================
            if user.role != role:
                return Response(
                    error_response(
                        message="Role mismatch",
                        errors=f"User is not {role}"
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )

            # ================= AUTHENTICATION =================
            user = authenticate(request, username=email, password=password)

            if not user:
                return Response(
                    error_response(
                        message="Invalid credentials",
                        errors="Wrong password"
                    ),
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # ================= TOKENS =================
            tokens = general.get_tokens_for_user(user)

            return Response(
                success_response(
                    message="Login successful",
                    data=tokens
                ),
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                error_response(
                    message="Something went wrong",
                    errors=str(e)
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
