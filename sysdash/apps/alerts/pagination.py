from rest_framework.pagination import PageNumberPagination


class AlertEventPagination(PageNumberPagination):
    page_size = 5
