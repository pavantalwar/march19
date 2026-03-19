from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "id",
            "patient_id",
            "full_name",
            "mobile",
            "address",
            "relation",
            "status",
            "user_id",
            "user_name",
            "user_email",
            "created_at"
        ]

    # ================= EXTRA FIELDS =================
    def get_user_id(self, obj):
        if obj.user:
            return obj.user.id
        return None

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.full_name
        return None

    def get_user_email(self, obj):
        if obj.user:
            return obj.user.email
        return None