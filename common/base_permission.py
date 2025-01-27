from rest_framework.permissions import BasePermission

from core_apps.user.models import User


class IsGigWorker(BasePermission):
    """
    Allows access only to users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.is_verified and not request.user.is_locked and (
            request.user.has_role(User.GIG_WORKER_ROLE))


class IsCustomer(BasePermission):
    """
    Allows access only to users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.is_verified and not request.user.is_locked and (
            request.user.has_role(User.CUSTOMER_ROLE))


class IsConsultant(BasePermission):
    """
    Allows access only to users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.is_verified and not request.user.is_locked and (
            request.user.has_any_role([User.CONSULTANT_ROLE, User.CONSULTANT_MANAGER_ROLE, User.ADMIN_ROLE]))


class IsTaskManager(BasePermission):
    """
    Allows access only to users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.is_verified and not request.user.is_locked and (
            request.user.has_any_role([User.TASK_MANAGER_ROLE, User.ADMIN_ROLE]))




class IsOverEmployee(BasePermission):
    """
    Allows access only to users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.is_verified and not request.user.is_locked and (
            request.user.has_role(User.OVER_EMPLOYEE_ROLE))


class IsConsultantManager(BasePermission):
    """
    Allows access only to users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.is_verified and not request.user.is_locked and (
            request.user.has_any_role([User.CONSULTANT_MANAGER_ROLE, User.ADMIN_ROLE]))


class IsBilling(BasePermission):
    """
    Allows access only to users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.is_verified and not request.user.is_locked and (
            request.user.has_any_role([User.BILLING_ROLE, User.ADMIN_ROLE]))


class IsSales(BasePermission):
    """
    Allows access only to users.
    """

    def has_permission(self, request, view):
        return (
                request.user and request.user.is_active and request.user.is_verified and not request.user.is_locked and (
            request.user.has_any_role([User.SALES_ROLE, User.ADMIN_ROLE])))


class IsAdmin(BasePermission):
    """
    Allows access only to "admin" users.
    """
    message = 'Only admin have permission to perform this action.'

    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.is_verified and not request.user.is_locked and request.user.has_role(
            User.ADMIN_ROLE)


class IsSuperAdmin(BasePermission):
    """
    Allows access only to "super admin" users.
    """
    message = 'Only super admin have permission to perform this action.'

    def has_permission(self, request, view):
        return request.user and request.user.is_super_admin and request.user.is_active and request.user.is_verified and not request.user.is_locked


class CustomMethodNotAllowed(BasePermission):
    def has_permission(self, request, view):
        return False
