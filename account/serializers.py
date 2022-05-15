import os

from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Photo


class ImageSerializer(serializers.Serializer):
    photo = serializers.FileField()


class UserSerializer(serializers.ModelSerializer):
    photo = ImageSerializer()
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'password', 'photo', "new_password"]

        extra_kwargs = {
            'password': {
                'write_only': True
             },
            'email': {
                'required': True
            },
            'photo': {
                'required': False
            }
        }

    def update(self, instance, validated_data):
        if self.context.get('photo') is not None:
            temp, created = Photo.objects.get_or_create(pk=instance.id)
            if not created:
                file_path = os.path.join(settings.BASE_DIR, f"mediafiles/{str(temp.photo).replace('media', '')}")
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            temp.photo = self.context['photo']
            temp.save()
        if self.context.get("new_password") is not None:
            instance.set_password(self.context.get("new_password"))
            # instance.save()
        firstname = validated_data.get('first_name', "")
        last_name = validated_data.get('last_name', "")

        instance.first_name = instance.first_name if firstname == "" else firstname
        instance.last_name = instance.last_name if last_name == "" else last_name
        instance.save()
        return instance

    # def validate_new_password(self, value: str):
    #     length_error = len(value) < 8
    #     digit_error = re.search(r"\d", value) is None
    #     uppercase_error = re.search(r"[A-Z]", value) is None
    #     lowercase_error = re.search(r"[a-z]", value) is None
    #     symbol_error = re.search(r"[!@#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', value) is None
    #
    #     if length_error:
    #         raise serializers.ValidationError('password must contain 8 symbols')
    #     elif digit_error:
    #         raise serializers.ValidationError('password must contain digits')
    #     elif lowercase_error:
    #         raise serializers.ValidationError('password must contain at least one lowercase latter')
    #     elif uppercase_error:
    #         raise serializers.ValidationError('password must contain at least one uppercase latter')
    #     elif symbol_error:
    #         raise serializers.ValidationError('password must contain at least one punctuation latter')
    #
    #     return value

#
# class ChangePasswordSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True, required=True)
#     # old_password = serializers.CharField(write_only=True, required=True)
#
#     class Meta:
#         model = User
#         fields = ('password', 'password2')
#
#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})
#         return attrs
#
#     # def validate_old_password(self, value):
#     #     user = self.context['request'].user
#     #     if not user.check_password(value):
#     #         raise serializers.ValidationError({"old_password": "Old password is not correct"})
#     #     return value
#
#     def update(self, instance, validated_data):
#         instance.set_password(validated_data['password'])
#         instance.save()
#         return instance

