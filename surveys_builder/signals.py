import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from surveys_builder.models import (
    Survey,
    Section,
    Field,
    SurveyResponse,
    AuditLog
)


@receiver(post_save, sender = Survey)
def log_survey_save(instance, created, **kwargs) -> None:
    action = 'create' if created else 'update'
    AuditLog.objects.create(
        user = instance.created_by or instance.updated_by,
        survey = instance,
        action = action
    )


@receiver(post_delete, sender = Survey)
def log_survey_delete(instance, **kwargs) -> None:
    AuditLog.objects.create(
        user = instance.updated_by,
        survey = instance,
        action = 'delete'
    )


@receiver(post_save, sender = Section)
def log_section_save(instance, created, **kwargs) -> None:
    action = 'create' if created else 'update'
    AuditLog.objects.create(
        user = instance.created_by or instance.updated_by,
        section = instance,
        survey = instance.survey,
        action = action
    )


@receiver(post_delete, sender = Section)
def log_section_delete(instance, **kwargs) -> None:
    AuditLog.objects.create(
        user = instance.updated_by,
        section = instance,
        survey = instance.survey,
        action = 'delete'
    )


@receiver(post_save, sender = Field)
def log_field_save(instance, created, **kwargs) -> None:
    action = 'create' if created else 'update'
    AuditLog.objects.create(
        user = instance.created_by or instance.updated_by,
        field = instance,
        section = instance.section,
        survey = instance.section.survey,
        action = action
    )


@receiver(post_delete, sender = Field)
def log_field_delete(instance, **kwargs) -> None:
    AuditLog.objects.create(
        user = instance.updated_by,
        field = instance,
        section = instance.section,
        survey = instance.section.survey,
        action = 'delete'
    )


@receiver(post_save, sender = SurveyResponse)
def log_survey_response_save(instance, created, **kwargs) -> None:
    action = 'create' if created else 'update'
    AuditLog.objects.create(
        user = instance.created_by or instance.updated_by,
        survey_response = instance,
        survey = instance.survey,
        action = action
    )


@receiver(post_delete, sender = SurveyResponse)
def log_survey_response_delete(instance, **kwargs) -> None:
    AuditLog.objects.create(
        user = instance.updated_by,
        survey_response = instance,
        survey = instance.survey,
        action = 'delete'
    )
