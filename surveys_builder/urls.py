from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from surveys_builder.views import (
    SurveyViewSet,
    FieldViewSet,
    SectionViewSet,
    SurveyResponseViewSet,
    AuditLogViewSet,
    GenerateReportView,
    ExportSurveyResponsesView,
    SendSurveyInvitationsView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

schema_view = get_schema_view(
    openapi.Info(
        title = "Survey API",
        default_version = 'v1',
        description = "A simple survey API"
    ),
    public = True,
    permission_classes = [permissions.AllowAny, ],
    authentication_classes = ([]),
)

router = DefaultRouter()
router.register(r'surveys', SurveyViewSet, basename = 'surveys')
router.register(r'survey-responses', SurveyResponseViewSet, basename = 'survey_responses')
router.register(r'sections', SectionViewSet, basename = 'sections')
router.register(r'fields', FieldViewSet, basename = 'fields')
urlpatterns = [
    # API Resources
    path('', include(router.urls)),

    # AUTHENTICATION
    path('token/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),

    # SWAGGER
    path('swagger<format>/', schema_view.without_ui(cache_timeout = 0), name = 'schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout = 0), name = 'schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout = 0), name = 'schema-redoc'),

    # Celery Task API Resources
    path('surveys/responses/export/', ExportSurveyResponsesView.as_view(), name = 'export_survey_responses'),
    path('surveys/invitations/send/', SendSurveyInvitationsView.as_view(), name = 'send_survey_invitations'),
    path('audit-logs/reports/generate/', GenerateReportView.as_view(), name = 'generate_report'),
]
