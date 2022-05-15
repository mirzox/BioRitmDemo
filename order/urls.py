from django.urls import path

from .views import OrderView, ResultView, ResultsDetailView, OrderFilesView

urlpatterns = [
    path('order/', OrderView.as_view()),
    path('result/', ResultView.as_view()),
    path('result/<int:pk>/', ResultsDetailView.as_view()),
    path('files/', OrderFilesView.as_view())
]
