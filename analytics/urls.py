from django.urls import path

from .views import FeeView, DataView, DataDetailView, ZipAll


urlpatterns = [
    path("fee/", FeeView.as_view()),
    path("data/", DataView.as_view()),
    path("data/<str:file>/", DataDetailView.as_view()),
    path("zip/", ZipAll.as_view()),
    # path("zip/<str:file>/", ZipDetailView.as_view()),
]
