from rest_framework import serializers
from django.contrib.auth.models import User
from surveys_builder.utils.helpers import (
    evaluate_condition,
    get_section_field_map,
    check_dependency
)
from surveys_builder.models import (
    Field,
    FieldType,
    Option,
    Section,
    Survey,
    Condition,
    ConditionDependency,
    Dependency,
    SurveyResponse,
    AuditLog
)


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True
        exclude = ('created_at', 'updated_at', 'updated_by', 'created_by')


class OptionSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Option
        exclude = BaseModelSerializer.Meta.exclude + ('field',)


class FieldTypeSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = FieldType


class ConditionSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Condition
        exclude = BaseModelSerializer.Meta.exclude + ('source_field',)


class ConditionDependencySerializer(BaseModelSerializer):
    condition = ConditionSerializer()

    class Meta(BaseModelSerializer.Meta):
        model = ConditionDependency


class DependencySerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Dependency
        exclude = BaseModelSerializer.Meta.exclude + ('source_field',)


class FieldSerializer(BaseModelSerializer):
    field_type = FieldTypeSerializer()
    options = OptionSerializer(many = True)
    conditional_logic = ConditionDependencySerializer(many = True)
    dependencies = DependencySerializer(many = True)

    class Meta(BaseModelSerializer.Meta):
        model = Field

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        conditional_logic_data = validated_data.pop('conditional_logic', [])
        dependencies_data = validated_data.pop('dependencies', [])
        field_type_data = validated_data.pop('field_type')

        field_type, created = FieldType.objects.get_or_create(**field_type_data)
        validated_data['field_type'] = field_type

        field = Field.objects.create(**validated_data)

        if options_data:
            for option_data in options_data:
                Option.objects.create(field = field, **option_data)
        if conditional_logic_data:
            for condition_data in conditional_logic_data:
                condition = Condition.objects.create(**condition_data['condition'])
                ConditionDependency.objects.create(condition = condition, **condition_data)
        if dependencies_data:
            for dependency_data in dependencies_data:
                Dependency.objects.create(**dependency_data)
        return field


class SectionSerializer(BaseModelSerializer):
    fields = FieldSerializer(many = True, read_only = True)

    class Meta(BaseModelSerializer.Meta):
        model = Section

    def create(self, validated_data):
        fields_data = validated_data.pop('fields', [])
        section = Section.objects.create(**validated_data)
        for field_data in fields_data:
            Field.objects.create(section = section, **field_data)
        return section


class SurveySerializer(BaseModelSerializer):
    sections = SectionSerializer(many = True, read_only = True)

    class Meta(BaseModelSerializer.Meta):
        model = Survey

    def create(self, validated_data) -> Survey:
        sections_data = validated_data.pop('sections', [])
        survey = Survey.objects.create(**validated_data)
        if sections_data:
            for section_data in sections_data:
                fields_data = section_data.pop('fields', [])
                section = Section.objects.create(survey = survey, **section_data)
                for field_data in fields_data:
                    field_type_data = field_data.pop('field_type')
                    field_type, _ = FieldType.objects.get_or_create(**field_type_data)
                    Field.objects.create(section = section, field_type = field_type, **field_data)
        return survey


class SurveyResponseSerializer(BaseModelSerializer):
    response_data = serializers.JSONField(
        default = [
            {
                "sections": [
                    {
                        "id": 0,
                        "fields": [
                            {
                                "id": 0,
                                'value': 'string'
                            }
                        ],

                    }
                ],
            }
        ]
    )

    class Meta(BaseModelSerializer.Meta):
        model = SurveyResponse
        exclude = BaseModelSerializer.Meta.exclude + ('id',)

    def validate(self, data):
        section_field_map = get_section_field_map(data['response_data'])
        sections = data['response_data']['sections']
        for section in sections:
            for field in section['fields']:
                if 'conditional_logic' in field and field['conditional_logic']:
                    for condition_dependency in field['conditional_logic']:
                        condition = condition_dependency['condition']
                        if not evaluate_condition(condition, section_field_map):
                            raise serializers.ValidationError(
                                f"Condition {condition['id']} not met for field {field['id']}"
                            )
                if 'dependencies' in field and field['dependencies']:
                    for dependency in field['dependencies']:
                        dependent_field_value = section_field_map.get(dependency['target_field']['id'])
                        if not check_dependency(field, dependent_field_value):
                            raise serializers.ValidationError(
                                f"Dependency {dependency['id']} not met for field {field['id']}"
                            )
        return data

    def create(self, validated_data):
        survey_id = self.context.get('survey')
        user_id = self.context.get('user')

        if not survey_id or not user_id:
            raise serializers.ValidationError("Survey and user must be provided in the context.")

        response_data = validated_data.pop('response_data')
        survey_response = SurveyResponse.objects.create(
            survey_id = survey_id,
            user_id = user_id,
            response_data = {**response_data}
        )
        return survey_response


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
