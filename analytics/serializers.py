from rest_framework import serializers


class ServiceSerializer(serializers.Serializer):
    category = serializers.CharField(source="category_id.name")
    price = serializers.IntegerField()
    fee = serializers.IntegerField()


class OrderSerializer(serializers.Serializer):
    secondname = serializers.CharField(source="patient_id.secondname")
    services = ServiceSerializer(many=True, read_only=True)
