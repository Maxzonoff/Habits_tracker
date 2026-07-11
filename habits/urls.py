from django.urls import path

from .views import HabitDetailView, HabitListCreateView, PublicHabitListView

urlpatterns = [
    path("", HabitListCreateView.as_view(), name="habit-list-create"),
    path("public/", PublicHabitListView.as_view(), name="public-habits"),
    path("<int:pk>/", HabitDetailView.as_view(), name="habit-detail"),
]
