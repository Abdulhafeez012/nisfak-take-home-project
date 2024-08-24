from rest_framework import viewsets
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    permission_classes,
    action
)
from surveys_builder.permissions import (
    IsAdmin,
    IsAnalyst,
    IsDataViewer
)
from surveys_builder.models import (
    Field,
    Survey,
    Section,
    SurveyResponse,
    AuditLog
)
from surveys_builder.serializers import (
    SurveySerializer,
    FieldSerializer,
    SectionSerializer,
    SurveyResponseSerializer,
    AuditLogSerializer
)
from surveys_builder.tasks import (
    generate_report,
    export_survey_responses,
    send_survey_invitations
)


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    class Meta:
        abstract = True

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsAdmin | IsAnalyst]
        elif self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated, IsAdmin | IsAnalyst | IsDataViewer]
        else:
            self.permission_classes = [IsAuthenticated, IsAdmin]
        return super().get_permissions()


class SurveyViewSet(BaseViewSet):
    """
    A viewset for viewing and editing survey instances.
    """
    queryset = Survey.objects.all().prefetch_related(
        'sections__fields__options',
        'sections__fields__field_type'
    )
    serializer_class = SurveySerializer

    def perform_create(self, serializer):
        serializer.save(created_by = self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by = self.request.user)

    @method_decorator(cache_page(300, key_prefix = 'surveys_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(300, key_prefix = 'surveys_detail'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class SectionViewSet(BaseViewSet):
    """
    A viewset for viewing and editing section instances.
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    def perform_create(self, serializer):
        serializer.save(created_by = self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by = self.request.user)

    @method_decorator(cache_page(300, key_prefix = 'sections_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(300, key_prefix = 'sections_detail'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class FieldViewSet(BaseViewSet):
    """
    A viewset for viewing and editing field instances.
    """
    queryset = Field.objects.all()
    serializer_class = FieldSerializer

    def perform_create(self, serializer):
        serializer.save(created_by = self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by = self.request.user)

    @method_decorator(cache_page(300, key_prefix = 'fields_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(300, key_prefix = 'fields_detail'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class SurveyResponseViewSet(BaseViewSet):
    """
    A viewset for viewing and editing survey response instances.
    """
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer

    def perform_create(self, serializer):
        serializer.save(created_by = self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by = self.request.user)

    @method_decorator(cache_page(300, key_prefix = 'surveys_response_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(300, key_prefix = 'surveys_response_detail'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing audit log instances.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsAnalyst]

    @method_decorator(cache_page(300, key_prefix = 'audit_logs_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(300, key_prefix = 'audit_logs_detail'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class GenerateReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsAnalyst]

    @action(detail = False, methods = ['post'])
    def post(self, request):
        emails = request.data.get('emails', [])
        generate_report.delay(emails)
        return Response(
            {'success': True},
            status = status.HTTP_202_ACCEPTED
        )



class ExportSurveyResponsesView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsAnalyst]

    @action(detail = False, methods = ['post'])
    def post(self, request):
        try:
            survey_id = request.POST.get('survey_id')
            user_id = request.user.id
            task = export_survey_responses.delay(survey_id, user_id)
            return Response(
                {'success': True},
                status = status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status = status.HTTP_400_BAD_REQUEST
            )


class SendSurveyInvitationsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsAnalyst]

    @action(detail = False, methods = ['post'])
    def post(self, request):
        try:
            survey_id = request.POST.get('survey_id')
            emails = request.data.get('emails', [])
            user_id = request.user.id
            send_survey_invitations.delay(survey_id, emails, user_id)
            return Response(
                {"success": True},
                status = status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status = status.HTTP_400_BAD_REQUEST
            )
