from django.urls import path
from .views import CustomAuthToken, MessageList, MessageDetail

urlpatterns = [
    path('messages/', MessageList.as_view(), name='message-list'),
    path('messages/<int:pk>/', MessageDetail.as_view(), name='message-detail'),
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
]
