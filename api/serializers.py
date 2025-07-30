from rest_framework import serializers
from .models import  Activity, Variant




class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for the Activity model.

    This serializer converts Activity instances to native Python datatypes
    that can be easily rendered into JSON, XML or other content types.

    Meta:
        model (Activity): The model to be serialized.
        fields (list): The fields of the model to be serialized.
    """

    class Meta:
        model = Activity
        fields = '__all__'

class VariantSerializer(serializers.ModelSerializer):
    """
    Serializer for the Variant model.
    This serializer converts Variant model instances into JSON format and vice versa.
    It includes the following fields:
    - id: The unique identifier for the variant.
    - activities: The activities associated with the variant.
    - cases: The cases related to the variant.
    - number_cases: The number of cases for the variant.
    - percentage: The percentage representation of the variant.
    - avg_time: The average time associated with the variant.
    """

    class Meta:
        model = Variant
        fields = '__all__'
