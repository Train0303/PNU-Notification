from django.contrib.auth.mixins import PermissionRequiredMixin


class UserPermissionRequiredMixin(PermissionRequiredMixin):
    check_permission_path_variable = None

    def has_permission(self) -> bool:
        if not self.request.user.is_authenticated:
            return False

        if self.check_permission_path_variable and not self.request.user.is_superuser:
            user_id = self.kwargs[self.check_permission_path_variable]
            return user_id == self.request.user.id

        return self.request.user.is_superuser