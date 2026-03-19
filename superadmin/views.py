from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from django.db.models import Q

from core.utils import error_response, success_response, Response,CustomPageNumberPagination
from core.exception import SerializerError

from . import models, validators, serializers
from authentication.models import CustomUser


def create_patient_id():
    last_patient = models.Patient.objects.all().order_by('-created_at').first()

    if not last_patient or not last_patient.patient_id:
        return "P-00001"

    last_number = int(last_patient.patient_id.split('-')[1])
    new_number = last_number + 1

    return f"P-{new_number:05d}"

class PatientView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    # ================= CREATE PATIENT =================
    def post(self, request):
        try:
            # ✅ ROLE CHECK (updated)
            if request.user.role not in ["superadmin", "owner"]:
                return Response(
                    error_response(
                        message="Permission denied",
                        errors="Only superadmin and owner can create patients."
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
            logined_user = request.user
            validator = validators.PatientCreateValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)

            data = validator.validated_data
            patient_id = create_patient_id()

            with transaction.atomic():

                # ✅ DUPLICATE CHECK
                if models.CustomUser.objects.filter(email=data.get("email")).exists():
                    return Response(
                        error_response(
                            message="Email already exists",
                            errors="Duplicate email"
                        ),
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if models.CustomUser.objects.filter(mobile=data.get("mobile")).exists():
                    return Response(
                        error_response(
                            message="Mobile already exists",
                            errors="Duplicate mobile"
                        ),
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # ✅ CREATE USER (customer role)
                user = CustomUser.objects.create_user(
                    email=data.get("email"),
                    password=data.get("password"),
                    full_name=data.get("full_name"),
                    mobile=data.get("mobile"),
                    gender=data.get("gender"),
                    role="customer",
                    age=data.get("age")
                )

                if data.get("image"):
                    user.image = data.get("image")
                    user.save()

                # ✅ CREATE PATIENT
                patient = models.Patient.objects.create(
                    patient_id=patient_id,
                    user=user,
                    full_name=data.get("full_name"),
                    mobile=data.get("mobile"),
                    address=data.get("address"),
                    relation=data.get("relation"),
                    created_by=logined_user
                )

            return Response(
                success_response(
                    message="Patient created successfully",
                    data={}
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

    # ================= LIST PATIENT =================
    def get(self, request):
        try:
            if request.user.role not in ["superadmin", "owner"]:
                return Response(
                    error_response(
                        message="Permission denied",
                        errors="Only authorized users can view patients."
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )

            queryset = models.Patient.objects.filter(is_active=True).order_by("-created_at")

            # ✅ SEARCH FILTER
            search = request.query_params.get("search")
            if search:
                queryset = queryset.filter(
                    Q(full_name__icontains=search) |
                    Q(patient_id__icontains=search) |
                    Q(mobile__icontains=search) |
                    Q(user__email__icontains=search)
                )

            # ✅ STATUS FILTER
            status_filter = request.query_params.get("status")
            if status_filter:
                queryset = queryset.filter(status=status_filter)

            if not queryset.exists():
                return Response(
                    error_response(
                        message="No records found",
                        errors="No matching patients found"
                    ),
                    status=status.HTTP_404_NOT_FOUND
                )

            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializer = serializers.PatientSerializer(
                paginated_queryset,
                many=True,
                context={'request': request}
            )

            paginated_data = paginator.get_paginated_response(serializer.data)

            return Response(
                success_response(
                    message="Patients fetched successfully",
                    data=paginated_data.data
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









