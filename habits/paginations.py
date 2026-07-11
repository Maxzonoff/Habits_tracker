from rest_framework.pagination import PageNumberPagination


class HabitPagination(PageNumberPagination):
    """
    Кастомная пагинация для привычек.
    limit/offset/count/results — стандарт DRF.
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100
