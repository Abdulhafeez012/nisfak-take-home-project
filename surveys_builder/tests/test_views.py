from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User, Group
from surveys_builder.models import Survey, Section, Field, FieldType

class SurveyViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        admin_group, created = Group.objects.get_or_create(name='Admin')
        self.user.groups.add(admin_group)
        self.client.force_authenticate(user=self.user)
        self.survey = Survey.objects.create(title="Survey 1", created_by=self.user)
        self.list_url = reverse('surveys-list')
        self.detail_url = reverse('surveys-detail', kwargs={'pk': self.survey.id})

    def test_survey_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_survey_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.survey.title)


class SectionViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        admin_group, created = Group.objects.get_or_create(name='Admin')
        self.user.groups.add(admin_group)
        self.client.force_authenticate(user=self.user)
        self.survey = Survey.objects.create(title="Survey 1", created_by=self.user)
        self.section = Section.objects.create(survey=self.survey, title="Section 1", created_by=self.user)
        self.list_url = reverse('sections-list')
        self.detail_url = reverse('sections-detail', kwargs={'pk': self.section.id})

    def test_section_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_section_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.section.title)


class FieldViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        admin_group, created = Group.objects.get_or_create(name='Admin')
        self.user.groups.add(admin_group)
        self.client.force_authenticate(user=self.user)
        self.survey = Survey.objects.create(title="Survey 1", created_by=self.user)
        self.section = Section.objects.create(survey=self.survey, title="Section 1", created_by=self.user)
        self.field_type = FieldType.objects.create(name="Text", widget="text_input", created_by=self.user)
        self.field = Field.objects.create(section=self.section, field_type=self.field_type, label="Field 1", created_by=self.user)
        self.list_url = reverse('fields-list')
        self.detail_url = reverse('fields-detail', kwargs={'pk': self.field.id})

    def test_field_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_field_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['label'], self.field.label)
