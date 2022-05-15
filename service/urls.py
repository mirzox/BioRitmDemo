from django.urls import path

from .views import CategoryView, CategoryDetailView, ServiceView, ServiceDetailView, ParameterView, ParameterDetailView

urlpatterns = [
    path('category/', CategoryView.as_view()),
    path('category/<int:pk>/', CategoryDetailView.as_view()),
    path('service/', ServiceView.as_view()),
    path('service/<int:pk>/', ServiceDetailView.as_view()),
    path('parameters/', ParameterView.as_view()),
    path('parameters/<int:pk>/', ParameterDetailView.as_view())
]
