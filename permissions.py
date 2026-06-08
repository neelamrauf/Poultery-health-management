"""
Custom DRF permission classes for role-based access control.

Roles defined on the User model:
  - 'Farmer'
  - 'Admin'
"""

from rest_framework.permissions import BasePermission


class IsFarmer(BasePermission):
    """Allow access only to authenticated users with the Farmer role."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'Farmer'
        )


class IsAdmin(BasePermission):
    """Allow access only to authenticated users with the Admin role."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'Admin'
        )


class IsFarmerOrAdmin(BasePermission):
    """Allow access to authenticated users with either the Farmer or Admin role."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('Farmer', 'Admin')
        )
