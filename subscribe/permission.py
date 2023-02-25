from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404

from subscribe.models import Subscribe


class WriterPermissionRequiredMixin(PermissionRequiredMixin):
    check_permission_path_variable = None

    def has_permission(self) -> bool:
        if not self.request.user.is_authenticated:
            return False

        if self.check_permission_path_variable and not self.request.user.is_superuser:
            subscribe_id = self.kwargs[self.check_permission_path_variable]
            subscribe = get_object_or_404(Subscribe, pk=subscribe_id)

            return subscribe.user_id == self.request.user.id

        return self.request.user.is_superuser