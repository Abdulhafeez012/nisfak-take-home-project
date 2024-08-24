from django.test import TestCase
from surveys_builder.serializers import SurveySerializer, SectionSerializer, FieldSerializer
from surveys_builder.models import Survey, Section, Field, FieldType, Option
from django.contrib.auth.models import User, Group


class SurveySerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'testuser')
        admin_group, created = Group.objects.get_or_create(name = 'Admin')
        self.user.groups.add(admin_group)
        self.survey_data = {
            'title': 'New Survey',
            'description': 'A new survey'
        }

    def test_survey_serializer_valid(self):
        serializer = SurveySerializer(data = self.survey_data)
        self.assertTrue(serializer.is_valid())
        survey = serializer.save(created_by = self.user)
        self.assertEqual(survey.title, self.survey_data['title'])
        self.assertEqual(survey.description, self.survey_data['description'])


class SectionSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'testuser')
        admin_group, created = Group.objects.get_or_create(name = 'Admin')
        self.user.groups.add(admin_group)
        self.survey = Survey.objects.create(title = 'Survey', created_by = self.user)
        self.section_data = {
            'survey': self.survey.id,
            'title': 'Section 1'
        }

    def test_section_serializer_valid(self):
        serializer = SectionSerializer(data = self.section_data)
        self.assertTrue(serializer.is_valid())
        section = serializer.save(created_by = self.user)
        self.assertEqual(section.title, self.section_data['title'])


class FieldSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        admin_group, created = Group.objects.get_or_create(name='Admin')
        self.user.groups.add(admin_group)
        self.survey = Survey.objects.create(title='Survey', created_by=self.user)
        self.section = Section.objects.create(survey=self.survey, title='Section 1', created_by=self.user, order=1)
        self.field_type_data = {'name': 'Text', 'widget': 'text_input'}
        self.field_data = {
            'label': 'Field 1',
            'required': True,
            'field_type': self.field_type_data,
            'section': self.section.id,
            'options': [],
            'conditional_logic': [],
            'dependencies': []
        }

    def test_field_serializer_valid(self):
        serializer = FieldSerializer(data=self.field_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)