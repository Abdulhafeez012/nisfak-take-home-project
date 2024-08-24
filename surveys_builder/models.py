from django.db import models
from cryptography.fernet import Fernet
from django.contrib.auth.models import User
from surveys_builder.utils.constants import (
    ACTIONS,
    OPERATORS,
    AUDIT_LOG_ACTIONS
)


class BaseModelWithoutOrder(models.Model):
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    updated_by = models.ForeignKey(
        User,
        related_name = 'updated_%(class)ss',
        on_delete = models.SET_NULL,
        null = True,
        blank = True
    )
    created_by = models.ForeignKey(
        User,
        related_name = 'created_%(class)ss',
        on_delete = models.SET_NULL,
        null = True,
        blank = True
    )

    class Meta:
        abstract = True


class BaseModelWithOrder(BaseModelWithoutOrder):
    order = models.PositiveIntegerField(default = 0)

    class Meta:
        abstract = True
        ordering = ['order']


class Survey(BaseModelWithoutOrder):
    title = models.CharField(max_length = 150, blank = True, null = True)
    description = models.TextField(blank = True, null = True)

    class Meta:
        verbose_name_plural = "Surveys"
        indexes = [
            models.Index(fields = ['title', 'id'])
        ]

    def __str__(self):
        return self.title or f"Survey {self.id}"

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request and not self.created_by:
            self.created_by = request.user
        if request:
            self.updated_by = request.user
        super().save(*args, **kwargs)


class Section(BaseModelWithOrder, BaseModelWithoutOrder):
    survey = models.ForeignKey(Survey, related_name = 'sections', on_delete = models.CASCADE)
    title = models.CharField(max_length = 50, blank = True, null = True)

    class Meta(BaseModelWithOrder.Meta):
        unique_together = ('survey', 'order')
        indexes = [
            models.Index(fields = ['survey', 'order'])
        ]

    def __str__(self):
        return f"{self.survey.title} / {self.title}" if self.title else f"Section {self.order} of {self.survey.title}"

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request and not self.created_by:
            self.created_by = request.user
        if request:
            self.updated_by = request.user
        super().save(*args, **kwargs)


class FieldType(BaseModelWithoutOrder):
    name = models.CharField(max_length = 50)
    widget = models.CharField(max_length = 50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Field Type"
        verbose_name_plural = "Field Types"

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request and not self.created_by:
            self.created_by = request.user
        if request:
            self.updated_by = request.user
        super().save(*args, **kwargs)


class Field(BaseModelWithOrder, BaseModelWithoutOrder):
    section = models.ForeignKey(Section, related_name = 'fields', on_delete = models.CASCADE)
    field_type = models.ForeignKey(FieldType, related_name = 'fields', on_delete = models.CASCADE)
    label = models.CharField(max_length = 50, blank = True, null = True)
    required = models.BooleanField(default = False)
    is_sensitive = models.BooleanField(default = False)

    class Meta(BaseModelWithOrder.Meta):
        indexes = [
            models.Index(fields = ['section', 'order'])
        ]

    def __str__(self):
        return f"Field {self.label or self.id} in Section {self.section.order}"

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request and not self.created_by:
            self.created_by = request.user
        if request:
            self.updated_by = request.user
        super().save(*args, **kwargs)


class Option(BaseModelWithOrder, BaseModelWithoutOrder):
    field = models.ForeignKey(Field, related_name = 'options', on_delete = models.CASCADE)
    value = models.CharField(max_length = 255, blank = True, null = True)

    def __str__(self):
        return f"Option {self.value or self.id} in Field {self.field.label or self.field.id}"

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request and not self.created_by:
            self.created_by = request.user
        if request:
            self.updated_by = request.user
        super().save(*args, **kwargs)


class Condition(BaseModelWithoutOrder):
    source_field = models.ForeignKey(
        Field,
        related_name = 'conditions',
        on_delete = models.CASCADE,
    )
    operator = models.CharField(
        max_length = 50,
        choices = OPERATORS
    )
    value = models.CharField(
        max_length = 255
    )

    def __str__(self):
        return f"{self.source_field.label or self.source_field.id} {self.operator} {self.value}"

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request and not self.created_by:
            self.created_by = request.user
        if request:
            self.updated_by = request.user
        if not self.source_field:
            self.source_field = self
        super().save(*args, **kwargs)


class ConditionDependency(BaseModelWithoutOrder):
    condition = models.ForeignKey(
        Condition,
        related_name = 'dependencies',
        on_delete = models.CASCADE
    )
    affected_field = models.ForeignKey(
        Field,
        related_name = 'conditional_logic',
        on_delete = models.CASCADE,
        blank = True,
        null = True,
    )
    affected_section = models.ForeignKey(
        Section,
        related_name = 'conditional_logic',
        on_delete = models.CASCADE,
        blank = True,
        null = True,
    )

    def __str__(self):
        target = self.field if self.field else self.section
        return f"Conditional Logic for {target.label or target.id}"

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request and not self.created_by:
            self.created_by = request.user
        if request:
            self.updated_by = request.user
        super().save(*args, **kwargs)


class Dependency(BaseModelWithoutOrder):
    source_field = models.ForeignKey(
        Field,
        related_name = 'dependencies',
        on_delete = models.CASCADE,
    )
    target_field = models.ForeignKey(
        Field,
        related_name = 'dependents',
        on_delete = models.CASCADE,
    )
    dependency_type = models.CharField(
        max_length = 100,
        null = False,
        blank = False,
    )

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request and not self.created_by:
            self.created_by = request.user
        if request:
            self.updated_by = request.user
        if not self.source_field:
            self.source_field = self
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Field {self.field.label or self.field.id} depends on Field {self.dependents_on.label or self.dependents_on.id}"


class SurveyResponse(BaseModelWithoutOrder):
    survey = models.ForeignKey(Survey, related_name = 'responses', on_delete = models.CASCADE)
    user = models.ForeignKey(User, related_name = 'responses', on_delete = models.CASCADE)
    response_data = models.JSONField()

    class Meta:
        indexes = [
            models.Index(fields = ['survey', 'user'])
        ]
        unique_together = ('survey', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Response for {self.survey.title} by {self.user.username}"

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request and not self.created_by:
            self.created_by = request.user
        if request:
            self.updated_by = request.user
        self.response_data = self._encrypt_response(self.response_data)
        super().save(*args, **kwargs)

    @classmethod
    def _encrypt_response(cls, response_data: dict) -> dict:
        for section in response_data['sections']:
            for field in section['fields']:
                field_obj = Field.objects.get(id = field['id'])
                if field_obj.is_sensitive:
                    f = Fernet(Fernet.generate_key())
                    field['value'] = f.encrypt(field['value'].encode()).decode()
        return cls.response_data

    @staticmethod
    def decrypt_response(response_data: dict) -> dict:
        for section in survey['sections']:
            for field in section['fields']:
                field_obj = Field.objects.get(id = field['id'])
                if field_obj.is_sensitive:
                    f = Fernet(Fernet.generate_key())
                    field['value'] = f.decrypt(field['value'].encode()).decode()
        return response_data


class AuditLog(models.Model):
    user = models.ForeignKey(
        User,
        related_name = 'audit_logs',
        on_delete = models.CASCADE
    )
    survey = models.ForeignKey(
        Survey,
        related_name = 'audit_logs',
        on_delete = models.CASCADE,
        null = True,
        blank = True
    )
    section = models.ForeignKey(
        Section,
        related_name = 'audit_logs',
        on_delete = models.CASCADE,
        null = True,
        blank = True
    )
    field = models.ForeignKey(
        Field,
        related_name = 'audit_logs',
        on_delete = models.CASCADE,
        null = True,
        blank = True
    )
    survey_response = models.ForeignKey(
        SurveyResponse,
        related_name = 'audit_logs',
        on_delete = models.CASCADE,
        null = True,
        blank = True
    )
    action = models.CharField(
        max_length = 50,
        choices = AUDIT_LOG_ACTIONS
    )

    def __str__(self):
        return f"{self.user.username} {self.action}"
