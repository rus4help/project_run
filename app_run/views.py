from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from rest_framework.pagination import PageNumberPagination

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.filters import SearchFilter
from .models import Run, AthleteInfo, Challenge
from django.contrib.auth.models import User
from .serializers import RunSerializer, UserSerializer, AthleteInfoSerializer


@api_view(['GET'])
def company_details(request):
    details = {'company_name': settings.COMPANY_NAME,
               'slogan': settings.SLOGAN,
               'contacts': settings.CONTACTS}
    return Response(details)

class RunAndUserPagination(PageNumberPagination):
    page_size_query_param = 'size'  # Разрешаем изменять количество объектов через query параметр size в url


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]  # Указываем какой класс будет использоваться для фильтра
    filterset_fields = ['status', 'athlete']  # Поля, по которым будет происходить фильтрация
    ordering_fields = ['created_at']  # Поля по которым будет возможна сортировка
    ordering = ['created_at'] # Сортировка по умолчанию, если на будущее в ordering_fields будет добавлено больше полей
    pagination_class = RunAndUserPagination

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.none()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # Подключаем SearchFilter здесь
    search_fields = ['first_name', 'last_name']  # Указываем поля по которым будет вестись поиск
    ordering_fields = ['date_joined']
    ordering = ['date_joined']
    pagination_class = RunAndUserPagination

    def get_queryset(self):
        # Исключаем суперпользователей
        queryset = User.objects.filter(is_superuser=False)

        user_type = self.request.query_params.get('type', None)

        if user_type == 'coach':
            queryset = queryset.filter(is_staff=True)
        elif user_type == 'athlete':
            queryset = queryset.filter(is_staff=False)
        # Иначе — все (is_superuser исключены)

        return queryset


class StartRunView(APIView):
    def post(self, request, run_id):
        # 1. Получаем объект или 404
        run = get_object_or_404(Run, id=run_id)

        # 2. Проверяем, можно ли стартовать
        if run.status != 'init':
            return Response(
                {'error': 'Невозможно запустить забег: он уже запущен или уже завершён.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Меняем статус и сохраняем
        run.status = 'in_progress'
        run.save()

        # 4. Возвращаем JSON-ответ
        return Response({'status': run.status}, status=status.HTTP_200_OK)


class StopRunView(APIView):
    def post(self, request, run_id):
        # 1. Получаем объект или 404
        run = get_object_or_404(Run, id=run_id)

        # 2. Проверяем, можно ли стартовать
        if run.status != 'in_progress':
            return Response(
                {'error': 'Невозможно закончить забег: он ещё не начат или уже завершён.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Меняем статус и сохраняем
        run.status = 'finished'
        run.save()

        athlete = run.athlete
        finished_runs_count = Run.objects.filter(athlete=athlete, status='finished').count()

        if finished_runs_count == 10:
            Challenge.objects.get_or_create(athlete=athlete)

        # 4. Возвращаем JSON-ответ
        return Response({'status': run.status}, status=status.HTTP_200_OK)

class AthleteInfoView(APIView):
    def get(self, request, user_id):
        # 1. Проверяем, существует ли пользователь
        user = get_object_or_404(User, id=user_id)

        # 2. Получаем или создаём AthleteInfo для этого пользователя
        athlete_info, created = AthleteInfo.objects.get_or_create(user=user)

        # 3. Сериализуем данные
        serializer = AthleteInfoSerializer(athlete_info)

        # 4. Возвращаем с 200 OK (даже если создали запись)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        athlete_info, created = AthleteInfo.objects.get_or_create(user=user)

        # Передаём И входящие данные, И существующий объект
        serializer = AthleteInfoSerializer(athlete_info, data=request.data)

        if serializer.is_valid():
            serializer.save()  # ← это обновит запись в БД
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)