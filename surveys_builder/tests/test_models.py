from django.test import TestCase
from django.contrib.auth.models import User, Group
from surveys_builder.models import (
    Survey, Section, FieldType, Field, Option, Condition, ConditionDependency,
    Dependency, SurveyResponse, AuditLog
)


class SurveyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'testuser')
        admin_group, created = Group.objects.get_or_create(name = 'Admin')
        self.user.groups.add(admin_group)
        self.survey = Survey.objects.create(
            title = "Test Survey",
            description = "Test Description",
            created_by = self.user
        )

    def test_survey_str(self):
        self.assertEqual(str(self.survey), "Test Survey")

    def test_survey_save(self):
        self.survey.save()
        self.assertIsNotNone(self.survey.created_at)
        self.assertEqual(self.survey.created_by, self.user)


class SectionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'testuser')
        admin_group, created = Group.objects.get_or_create(name = 'Admin')
        self.user.groups.add(admin_group)
        self.survey = Survey.objects.create(title = "Test Survey", created_by = self.user)
        self.section = Section.objects.create(survey = self.survey, title = "Test Section", created_by = self.user)

    def test_section_str(self):
        self.assertEqual(str(self.section), "Test Survey / Test Section")

    def test_section_save(self):
        self.section.save()
        self.assertIsNotNone(self.section.created_at)
        self.assertEqual(self.section.created_by, self.user)


class FieldTypeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'testuser')
        admin_group, created = Group.objects.get_or_create(name = 'Admin')
        self.user.groups.add(admin_group)
        self.field_type = FieldType.objects.create(name = "Text", widget = "text_input", created_by = self.user)

    def test_field_type_str(self):
        self.assertEqual(str(self.field_type), "Text")

    def test_field_type_save(self):
        self.field_type.save()
        self.assertIsNotNone(self.field_type.created_at)
        self.assertEqual(self.field_type.created_by, self.user)


class FieldModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'testuser')
        admin_group, created = Group.objects.get_or_create(name = 'Admin')
        self.user.groups.add(admin_group)
        self.survey = Survey.objects.create(title = "Test Survey", created_by = self.user)
        self.section = Section.objects.create(survey = self.survey, title = "Test Section", created_by = self.user)
        self.field_type = FieldType.objects.create(name = "Text", widget = "text_input", created_by = self.user)
        self.field = Field.objects.create(section = self.section, field_type = self.field_type, label = "Test Field",
                                          created_by = self.user)

    def test_field_str(self):
        self.assertEqual(str(self.field), "Field Test Field in Section 0")

    def test_field_save(self):
        self.field.save()
        self.assertIsNotNone(self.field.created_at)
        self.assertEqual(self.field.created_by, self.user)


class OptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'testuser')
        admin_group, created = Group.objects.get_or_create(name = 'Admin')
        self.user.groups.add(admin_group)
        self.survey = Survey.objects.create(title = "Test Survey", created_by = self.user)
        self.section = Section.objects.create(survey = self.survey, title = "Test Section", created_by = self.user)
        self.field_type = FieldType.objects.create(name = "Text", widget = "text_input", created_by = self.user)
        self.field = Field.objects.create(section = self.section, field_type = self.field_type, label = "Test Field",
                                          created_by = self.user)
        self.option = Option.objects.create(field = self.field, value = "Option 1", created_by = self.user)

    def test_option_str(self):
        self.assertEqual(str(self.option), "Option Option 1 in Field Test Field")


class ConditionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'testuser')
        admin_group, created = Group.objects.get_or_create(name = 'Admin')
        self.user.groups.add(admin_group)
        self.survey = Survey.objects.create(title = "Test Survey", created_by = self.user)
        self.section = Section.objects.create(survey = self.survey, title = "Test Section", created_by = self.user)
        self.field_type = FieldType.objects.create(name = "Text", widget = "text_input", created_by = self.user)
        self.field = Field.objects.create(section = self.section, field_type = self.field_type, label = "Test Field",
                                          created_by = self.user)
        self.condition = Condition.objects.create(source_field = self.field, operator = "equals", value = "value",
                                                  created_by = self.user)

    def test_condition_str(self):
        self.assertEqual(str(self.condition), "Test Field equals value")


class SurveyResponseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'testuser')
        admin_group, created = Group.objects.get_or_create(name = 'Admin')
        self.user.groups.add(admin_group)
        self.survey = Survey.objects.create(title = "Test Survey", created_by = self.user)
        self.section = Section.objects.create(survey = self.survey, title = "Section 1", created_by = self.user,
                                              order = 1)
        self.field_type = FieldType.objects.create(name = "Text", widget = "text_input", created_by = self.user)
        self.field = Field.objects.create(section = self.section, field_type = self.field_type, label = "Test Field",
                                          created_by = self.user)

        self.response_data = {
            "sections": [
                {
                    "fields": [
                        {"id": self.field.id, "value": "response"}
                    ]
                }
            ]
        }

        self.survey_response = SurveyResponse.objects.create(
            survey = self.survey,
            user = self.user,
            response_data = self.response_data
        )

    def test_survey_response_str(self):
        self.assertEqual(str(self.survey_response), f"Response for {self.survey.title} by {self.user.username}")


class AuditLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'testuser')
        admin_group, created = Group.objects.get_or_create(name = 'Admin')
        self.user.groups.add(admin_group)
        self.survey = Survey.objects.create(title = "Test Survey", created_by = self.user)
        self.audit_log = AuditLog.objects.create(user = self.user, survey = self.survey, action = "created")

    def test_audit_log_str(self):
        self.assertEqual(str(self.audit_log), f"{self.user.username} created")
