from rest_framework import serializers

from .models import Category, Services, Parameters


class CategoryGET(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    items_count = serializers.IntegerField()


class CategoryPOST(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['name', 'description', 'items_count']

    extra_kwargs = {
        "items_count": {
            "read_only": True
        }
    }


class ParameterSerializerGet(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    norm = serializers.CharField()


class ParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parameters
        fields = ['name', 'norm']


class ServiceGet(serializers.Serializer):
    id = serializers.IntegerField()
    category_id = CategoryGET(read_only=True)
    name = serializers.CharField()
    price = serializers.IntegerField()
    fee = serializers.IntegerField()
    parameters = ParameterSerializerGet(read_only=True, many=True)


class ServicePost(serializers.ModelSerializer):

    class Meta:
        model = Services
        fields = '__all__'


# This serializers to serialize Category and Service together

class ServiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.IntegerField()
    fee = serializers.IntegerField()


class CategoryAndServiceGet(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField
    items_count = serializers.IntegerField()
    service = ServiceSerializer(many=True, read_only=True)


