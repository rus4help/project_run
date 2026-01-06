from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Run


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField() # Тут мы задаем новое поле, которого нет в модели БД

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'first_name', 'last_name', 'type'] # Здесь добавили данное поле type

    # Определяем метод, который вычисляет значение поля
    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserSerializer(source="athlete", read_only=True)

    class Meta:
        model = Run
        fields = '__all__'