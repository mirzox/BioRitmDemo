from django.urls import path


from .views import LoginView, Logout,  AccountView, AccountDetailView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('logout/', Logout.as_view()),
    # path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('detail/', AccountView.as_view()),
    path('detail/<int:pk>/', AccountDetailView.as_view()),

]
