from rest_framework.exceptions import NotFound


class ListBackedViewSetMixin:
    """Look up a child record inside the parent-scoped Python list."""

    def get_object(self):
        object_list = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]

        # The list already contains only records owned by the URL parent.
        for instance in object_list:
            if str(getattr(instance, self.lookup_field)) == str(lookup_value):
                self.check_object_permissions(self.request, instance)
                return instance

        raise NotFound("The requested resource does not exist under this parent.")
