from rest_framework import serializers

from .models import Doctor, Patient


class DoctorGetSerializer(serializers.Serializer):
    id = serializers.CharField()
    firstname = serializers.CharField()
    secondname = serializers.CharField()
    location = serializers.CharField()
    phone = serializers.CharField()


class DoctorPostSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Doctor
        fields = ["id", "firstname", "secondname", "location", "phone"]

    extra_kwargs = {
        "id": {
            "required": True,
        }
    }

    def validate_id(self, value):
        if len(value) != 6:
            raise serializers.ValidationError('ID must contain 6 digits')
        if Doctor.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Doctor with this id is already exists.')
        return value

    # def validate_phone(self, value: str):
    #     if not value.startswith('998'):
    #         raise serializers.ValidationError('phone number must start with 998')
    #     elif len(value) != 12:
    #         raise serializers.ValidationError('phone must contains 12 digits')
    #     return value


class PatientGetSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    p_id = serializers.IntegerField(required=False)
    doctor_id = serializers.CharField(source='doctor_id_id')
    firstname = serializers.CharField()
    secondname = serializers.CharField()
    lastname = serializers.CharField()
    gender = serializers.CharField()
    birth = serializers.IntegerField()
    phone = serializers.CharField()
    order_status = serializers.CharField()


class PatientPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = "__all__"

    def validate_birth(self, value):
        if len(str(value)) != 4:
            raise serializers.ValidationError('Birth year must contain 4 digits')
        return value

    def validate_phone(self, value: str):
        if not value.startswith('998'):
            raise serializers.ValidationError('phone number must start with 998')
        elif len(value) != 12:
            raise serializers.ValidationError('phone must contains 12 digits')
        return value

    def validate_doctor_id_id(self, value):
        if len(value) != 6:
            raise serializers.ValidationError('ID must contain 6 digits')
        return value


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate_phone(self, value: str):
        if not value.startswith('998'):
            raise serializers.ValidationError('phone number must start with 998')
        elif len(value) != 12:
            raise serializers.ValidationError('phone must contains 12 digits')
        elif Patient.objects.filter(phone=value).exists():
            raise serializers.ValidationError(f'{value} is taken')
        return value
