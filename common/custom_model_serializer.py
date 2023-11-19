from rest_framework import serializers
from common.utils.default_write import default_write


class CustomModelSerializer(serializers.ModelSerializer):
    """
    重写ModelSerializer
    """

    def create(self, validated_data):
        instance = super().create(validated_data)
        request = self.context.get('request')
        default_write(instance, request)
        return instance

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        request = self.context.get('request')
        default_write(instance, request)
        return instance
