from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from users.models import Emails


class ActiveEmailOnly(BasePermission):
    """Permission class to check if the email is active or not

    Args:
        BasePermission (class): DRF base permission class
    """

    def has_object_permission(self, request, view, obj: Emails) -> bool:
        """This is object based permission that will be used by calling
        `self.check_object_permissions(request, email_obj)` inside the view

        Args:
            request (django.request): django request object
            view ([type]): django view object
            obj (Emails): Email object `users.models.Emails`

        Raises:
            PermissionDenied: raise error to client with custom message(403 code)

        Returns:
            bool: permission granted or not
        """
        if not obj.is_active:
            raise PermissionDenied(detail="email not activated")

        return True
