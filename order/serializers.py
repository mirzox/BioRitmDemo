from rest_framework import serializers

from .models import ParamResult, Result, Order
from service.serializers import ServiceGet, ParameterSerializerGet, ServiceSerializer
from client.serializers import PatientGetSerializer
from service.models import Services, Category


class ParamResultGet(serializers.Serializer):
    id = serializers.IntegerField()
    param_id = ParameterSerializerGet()
    res = serializers.CharField()


class ParamResultPost(serializers.ModelSerializer):

    class Meta:
        model = ParamResult
        fields = ['id', 'res']


class ResultGet(serializers.Serializer):
    id = serializers.IntegerField()
    patient_id = PatientGetSerializer()
    service_id = ServiceSerializer()
    result = ParamResultGet(many=True)
    status = serializers.CharField()


class ResultPost(serializers.ModelSerializer):
    result = ParamResultPost(many=True, )

    class Meta:
        model = Result
        fields = ["result", ]

    def update(self, instance, validated_data):
        print(instance)
        for i in validated_data.pop("results"):
            for j in i:
                pass


class OrderGet(serializers.Serializer):
    status_choices = (
        ('pending', 'В ожидании'),
        ('progress', 'В процессе'),
        ('finished', 'Завершен')
    )

    id = serializers.IntegerField(allow_null=True, required=False)
    patient_id = PatientGetSerializer()
    doctor_id = serializers.CharField(source='doctor_id_id')
    status = serializers.ChoiceField(choices=status_choices)
    services = ServiceSerializer(many=True, )
    # results = ResultGet(many=True, )
    cost = serializers.FloatField()
    file = serializers.URLField()
    result_file = serializers.URLField()


class OrderPost(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = "__all__"


class Temp(serializers.Serializer):
    service_id = ServiceSerializer()
    result = ParamResultGet(many=True)


class Temp2(serializers.Serializer):
    patient_id = PatientGetSerializer()
    results = Temp(many=True)
    result_file = serializers.URLField()


################################################3


class ParamResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    res = serializers.CharField()


class PatientOrderSerializer(serializers.Serializer):
    firstname = serializers.CharField()
    secondname = serializers.CharField()
    gender = serializers.CharField()
    birth = serializers.IntegerField()
    timestamp = serializers.DateTimeField()


class ServiceOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    category_id = serializers.CharField(source="category_id.name")
    name = serializers.CharField()


class ResultOrderSerializer(serializers.Serializer):
    service_id = ServiceOrderSerializer()
    result = ParamResultGet(many=True)


class OrderSerializer(serializers.Serializer):
    patient_id = PatientOrderSerializer(read_only=True)
    results = ResultOrderSerializer(many=True, read_only=True)


def gen_order_file(pk: int):
    order = Order.objects.filter(pk=pk).select_related("patient_id")
    # services = Order.objects.filter(pk=pk).values_list("services", flat=True)
    services = order.values_list("services", flat=True)
    categories = list(set(Services.objects.filter(pk__in=services).
                          select_related("category_id").values_list("category_id__name", flat=True)))
    serializer = OrderSerializer(order, many=True).data
    if len(serializer) != 0 and len(categories) != 0:
        serializer = serializer[0]
        results = {}

        for category in categories:
            if Category.objects.get(name=category).is_continuous:
                #if category not in ["УЗИ", "Консультации Врачей", "Услуги Гинеколога"]:
                results[category] = []
        for i in serializer['results']:
            results[i["service_id"]["category_id"]].append(i['result'])
        serializer["results"] = results

    return serializer




