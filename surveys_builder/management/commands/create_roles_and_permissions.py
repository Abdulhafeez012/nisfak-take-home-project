from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from surveys_builder.models import *
from rest_framework.permissions import IsAuthenticated


class Command(BaseCommand):
    help = 'Create groups and assign permissions for the application'

    def handle(self, *args, **kwargs):
        all_permissions = Permission.objects.all()
        view_permissions = Permission.objects.filter(
            codename__contains = 'view'
        )

        change_permissions = Permission.objects.filter(
            codename__contains = 'change'
        )

        admin_group, _ = Group.objects.get_or_create(name = 'Admin')
        analyst_group, _ = Group.objects.get_or_create(name = 'Analyst')
        data_viewer_group, _ = Group.objects.get_or_create(name = 'Data Viewer')

        admin_group.permissions.set(all_permissions)
        analyst_group.permissions.set(list(change_permissions) + list(view_permissions))
        data_viewer_group.permissions.set(view_permissions)

        self.stdout.write(self.style.SUCCESS('Groups and permissions created successfully'))