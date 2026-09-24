from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ListBackedViewSetMixin:
    """Look up a child record inside the parent-scoped Python list."""

    lookup_field = "pk"
    lookup_url_kwarg = None

    def get_list_response(self, request, object_list, serializer_class):
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(object_list, request, view=self)
        if page is not None:
            serializer = serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = serializer_class(object_list, many=True)
        return Response(serializer.data)

    def get_object(self):
        object_list = self.get_object_list()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]

        # The list already contains only records owned by the URL parent.
        for instance in object_list:
            if str(getattr(instance, self.lookup_field)) == str(lookup_value):
                self.check_object_permissions(self.request, instance)
                return instance

        raise NotFound("The requested resource does not exist under this parent.")
