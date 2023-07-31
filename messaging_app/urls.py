from django.urls import path

from .views import CustomAuthToken, MessageList, MessageDetail, UserRegistrationView

urlpatterns = [
    path('messages/', MessageList.as_view(), name='message-list'),
    path('messages/<int:pk>/', MessageDetail.as_view(), name='message-detail'),
    path('api/register/', UserRegistrationView.as_view(), name='user-registration'),
    path('api/api-token-auth/', CustomAuthToken.as_view(), name='api-token-auth'),
]
