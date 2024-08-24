from django.apps import AppConfig


class SurveyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'surveys_builder'

    def ready(self):
        import surveys_builder.signals