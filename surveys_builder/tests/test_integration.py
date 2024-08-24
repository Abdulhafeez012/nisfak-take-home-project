from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User, Group
from surveys_builder.models import Survey, Section, Field, FieldType


class SurveyIntegrationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username = 'testuser', password = 'testpass')
        admin_group, created = Group.objects.get_or_create(name = 'Admin')
        self.user.groups.add(admin_group)
        self.client.force_authenticate(user = self.user)

    def test_create_survey_with_sections_and_fields(self):
        self.survey_data = {
            "sections": [
                {
                    "fields": [
                        {
                            "label": "Field 1",
                            "required": True,
                            "field_type": {
                                "name": "Text",
                                "widget": "text_input"
                            },
                            "options": [
                                {"value": "Option 1"},
                                {"value": "Option 2"}
                            ]
                        }
                    ],
                    "title": "Section 1",
                    "order": 1,
                },
            ],
            "title": "Integration Survey",
            "description": "Integration test description",
        }
        response = self.client.post(reverse('surveys-list'), self.survey_data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_survey_response(self):
        survey = Survey.objects.create(title = "Survey 1", created_by = self.user)
        section = Section.objects.create(survey = survey, title = "Section 1", created_by = self.user, order = 1)
        field_type = FieldType.objects.create(name = "Text", widget = "text_input", created_by = self.user)
        field = Field.objects.create(section = section, field_type = field_type, label = "Field 1",
                                     created_by = self.user)

        response_data = {
            "sections": [
                {
                    "fields": [
                        {"id": field.id, "value": "Sample Response"}
                    ]
                }
            ]
        }
        survey_response_data = {
            "survey": survey.id,
            "user": self.user.id,
            "response_data": response_data
        }
        response = self.client.post(reverse('survey_responses-list'), survey_response_data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
