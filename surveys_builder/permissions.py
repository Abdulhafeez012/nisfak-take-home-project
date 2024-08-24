from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS
)

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(
            name='Admin'
        ).exists()

class IsAnalyst(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS + ('PUT', 'PATCH', 'POST'):
            return request.user.groups.filter(
                name='Analyst'
            ).exists()
        return False

class IsDataViewer(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.groups.filter(
                name='Data Viewer'
            ).exists()
        return False
