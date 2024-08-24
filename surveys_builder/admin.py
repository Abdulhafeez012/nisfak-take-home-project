from django.contrib import admin
from surveys_builder.models import (
    FieldType,
    Survey,
    Section,
    Option,
    Field,
    SurveyResponse,
    AuditLog,
    Condition,
    ConditionDependency,
    Dependency
)


class SectionAdmin(admin.ModelAdmin):
    list_display = ('survey', 'title', 'order')

    def save_model(self, request, obj, form, change):
        obj.save(request = request)


class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        obj.save(request = request)


class FieldAdmin(admin.ModelAdmin):
    list_display = ('section', 'label', 'field_type', 'order')

    def save_model(self, request, obj, form, change):
        obj.save(request = request)


class FieldTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'widget')

    def save_model(self, request, obj, form, change):
        obj.save(request = request)


class OptionAdmin(admin.ModelAdmin):
    list_display = ('field', 'value', 'order')

    def save_model(self, request, obj, form, change):
        obj.save(request = request)


class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        obj.save(request = request)


class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'survey', 'section', 'field')



class ConditionAdmin(admin.ModelAdmin):
    list_display = ('source_field', 'operator', 'value')

    def save_model(self, request, obj, form, change):
        obj.save(request = request)


class ConditionDependencyAdmin(admin.ModelAdmin):
    list_display = ('condition', 'affected_field', 'affected_section')

    def save_model(self, request, obj, form, change):
        obj.save(request = request)


class DependencyAdmin(admin.ModelAdmin):
    list_display = ('source_field', 'target_field', 'dependency_type')

    def save_model(self, request, obj, form, change):
        obj.save(request = request)


admin.site.register(Survey, SurveyAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(FieldType, FieldTypeAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(SurveyResponse, SurveyResponseAdmin)
admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(Condition, ConditionAdmin)
admin.site.register(ConditionDependency, ConditionDependencyAdmin)
admin.site.register(Dependency, DependencyAdmin)
