from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Run, AthleteInfo


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField() # Тут мы задаем новое поле, которого нет в модели БД
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'first_name', 'last_name', 'type', 'runs_finished'] # Здесь добавили данное поле type и runs_finished

    # Определяем метод, который вычисляет значение поля
    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    def get_runs_finished(self, obj):
        return obj.run_set.filter(status="finished").count()


# Сериализатор только для данных атлета (минималистичный)
class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteSerializer(source="athlete", read_only=True)

    class Meta:
        model = Run
        fields = '__all__'


class AthleteInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField()

    class Meta:
        model = AthleteInfo
        fields = ['user_id', 'weight', 'goals']

    def validate_weight(self, value):
        if value is not None:
            if value > 0 and value < 900:
                return value
            else:
                raise serializers.ValidationError("Weight must be between 0 and 900.")
        return value