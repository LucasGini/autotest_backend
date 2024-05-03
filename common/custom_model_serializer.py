from rest_framework import serializers
from common.utils.default_write import default_write


class CustomModelSerializer(serializers.ModelSerializer):
    """
    重写ModelSerializer
    """

    # updated_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    # created_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    def __init__(self, *args, **kwargs):
        super(CustomModelSerializer, self).__init__(*args, **kwargs)
        if self.instance:
            if isinstance(self.instance, list):
                print(self.instance)
                self.instance = self.instance[0]

            if hasattr(self.instance, 'created_date'):
                print("Has created_date:", self.instance.created_date)  # 检查是否存在
                if self.instance.created_date:
                    self.fields['created_date'] = serializers.DateTimeField(
                        format='%Y-%m-%d %H:%M:%S',
                    )
                if hasattr(self.instance, 'updated_date') and self.instance.updated_date:
                    self.fields['updated_date'] = serializers.DateTimeField(
                        format='%Y-%m-%d %H:%M:%S',
                    )

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
