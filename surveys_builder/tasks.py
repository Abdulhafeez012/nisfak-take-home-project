from celery.utils.log import get_task_logger
from celery import shared_task
from django.core.mail import send_mail
from surveys_builder.models import (
    Survey,
    AuditLog
)

logger = get_task_logger(__name__)


@shared_task
def generate_report(emails=None) -> list:
    if emails is None:
        emails = []
    logger.info(f'Generating report for Audit Log')
    audit_logs = AuditLog.objects.all()
    report = []
    for log in audit_logs:
        log_data = {
            'user': log.user.username,
            'action': log.action,
            'survey': log.survey.title,
            'section': log.section,
            'field': log.field,
        }
        report.append(log_data)
    send_mail(
        'Audit Log Report',
        'Please find the attached report for the Audit Log',
        'info@info.com',
        [emails],
    )
    logger.info(f'Report generated for Audit Log')
    return report


@shared_task
def export_survey_responses(survey_id: int, user_id: int = None) -> list:
    logger.info(f'Exporting survey responses for survey {survey_id}')
    survey = Survey.objects.get(pk = survey_id)
    responses = survey.responses.all()
    export_data = []
    for response in responses:
        response_data = response.decrypt_response(response.response_data)
        export_data.append(response_data)
    logger.info(f'Survey responses exported for survey {survey_id}')

    user = None
    if user_id:
        user = User.objects.get(pk = user_id)
    AuditLog.objects.create(
        user = user,
        survey = survey,
        action = 'export_response'
    )
    return export_data


@shared_task
def send_survey_invitations(survey_id: int, emails: list = [], user_id: int = None) -> None:
    logger.info(f'Sending survey invitations for survey {survey_id}')
    survey = Survey.objects.get(pk = survey_id)
    send_mail(
        'Survey Invitation',
        f'You have been invited to take the survey {survey.title}. Please click on the link to take the survey.',
        f'info@surveys-builder.com',
        emails,
        fail_silently = False
    )
    logger.info(f'Survey invitations sent for survey {survey_id}')

    user = None
    if user_id:
        user = User.objects.get(pk = user_id)
    AuditLog.objects.create(
        user = user,
        survey = survey,
        action = 'export_response'
    )
