from django.contrib import admin
from django.urls import path, include
from app_run.views import company_details, StartRunView, StopRunView, AthleteInfoView, ChallengeListView
from rest_framework.routers import DefaultRouter
from app_run.views import RunViewSet, UserViewSet

from debug_toolbar.toolbar import debug_toolbar_urls

router = DefaultRouter()
router.register('api/runs', RunViewSet)
router.register('api/users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details),
    path('api/runs/<int:run_id>/start/', StartRunView.as_view()),
    path('api/runs/<int:run_id>/stop/', StopRunView.as_view()),
    path('api/athlete_info/<int:user_id>/', AthleteInfoView.as_view()),
    path('api/challenges/', ChallengeListView.as_view()),
    path('', include(router.urls))
]

urlpatterns.extend(debug_toolbar_urls())