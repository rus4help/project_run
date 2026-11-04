from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Run, AthleteInfo, Challenge, Position, CollectibleItem, Subscribe


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()  # Тут мы задаем новое поле, которого нет в модели БД
    runs_finished = serializers.IntegerField(source='finished_runs_count', read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'first_name', 'last_name', 'type',
                  'runs_finished', 'rating']

    # Определяем метод, который вычисляет значение поля
    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'


# Сериализатор только для данных атлета (минималистичный)
class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteSerializer(source='athlete', read_only=True)

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
                raise serializers.ValidationError('Weight must be between 0 and 900.')
        return value


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['full_name', 'athlete']


class PositionSerializer(serializers.ModelSerializer):
    # DRF сам проверит существование ID и превратит его в объект Run
    run = serializers.PrimaryKeyRelatedField(queryset=Run.objects.all())

    # Явно указываем формат ввода и вывода
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f', input_formats=['%Y-%m-%dT%H:%M:%S.%f'])

    class Meta:
        model = Position
        fields = '__all__'

    def validate_latitude(self, value):
        if value is not None:
            if value >= -90 and value <= 90:
                return value
            else:
                raise serializers.ValidationError('Latitude must be between -90 and 90.')
        return value

    def validate_longitude(self, value):
        if value is not None:
            if value >= -180 and value <= 180:
                return value
            else:
                raise serializers.ValidationError('Longitude must be between -180 and 180.')
        return value

    def validate_run(self, value):
        # value — это объект Run. Просто проверяем статус.
        if value.status != 'in_progress':
            raise serializers.ValidationError('Run must be in progress status')
        return value


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = ['name', 'uid', 'latitude', 'longitude', 'picture', 'value']

    def validate_latitude(self, value):
        if value is not None:
            if value >= -90 and value <= 90:
                return value
            else:
                raise serializers.ValidationError('Latitude must be between -90 and 90.')
        return value

    def validate_longitude(self, value):
        if value is not None:
            if value >= -180 and value <= 180:
                return value
            else:
                raise serializers.ValidationError('Longitude must be between -180 and 180.')
        return value


class AthleteDetailSerializer(UserSerializer):
    # Добавляем только то, чего нет в родительском классе
    items = CollectibleItemSerializer(many=True, read_only=True)
    coach = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        # Наследуем все поля от родителя и добавляем 'items'
        fields = UserSerializer.Meta.fields + ['items', 'coach']

    def get_coach(self, obj):
        # Получить ID тренера из подписки
        subscription = obj.subscribe_athlete.first()
        return subscription.coach.id if subscription else None


class CoachDetailSerializer(UserSerializer):
    athletes = serializers.SerializerMethodField()  # Новое поле!

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['athletes']

    def get_athletes(self, obj):
        # Получить список ID атлетов из подписок
        return list(obj.subscribe_coach.values_list('athlete_id', flat=True))


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ['athlete', 'coach']

    def validate(self, data):
        if not data['coach'].is_staff:
            raise serializers.ValidationError("Coach must be a coach")
        if data['athlete'].is_staff:
            raise serializers.ValidationError("Athlete must be an athlete")
        return data


class RateCoachSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Subscribe
        fields = ['athlete', 'rating']


class AnalyticsForCoachSerializer(serializers.Serializer):
    longest_run_user = serializers.IntegerField(allow_null=True)
    longest_run_value = serializers.FloatField(allow_null=True)

    total_run_user = serializers.IntegerField(allow_null=True)
    total_run_value = serializers.FloatField(allow_null=True)

    speed_avg_user = serializers.IntegerField(allow_null=True)
    speed_avg_value = serializers.FloatField(allow_null=True)
