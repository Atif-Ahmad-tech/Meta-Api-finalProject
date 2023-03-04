from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group

class IsMemberOfManagerGroup(BasePermission):
    def has_permission(self, request, view):
        group_name = 'Manager'
        group = Group.objects.get(name=group_name)
        return request.user.groups.filter(name=group_name).exists()

    def has_object_permission(self, request, view, obj):
        group_name = 'Manager'
        return request.user.groups.filter(name=group_name).exists()
