from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from messaging_app.permissions import IsSenderOrReceiver
from .models import Message
from .serializers import MessageSerializer, UserRegistrationSerializer
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.core.exceptions import ValidationError

class CustomAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]  
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(user=request.user)
        return Response({'token': token.key})

class MessageList(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        is_read_param = self.request.query_params.get('is_read', None)

        # Get the user from the request
        user = self.request.user

        user_condition = Q(sender=user) | Q(receiver=user)

        if is_read_param is not None:
            try:
                queryset = Message.objects.filter(user_condition & Q(is_read=is_read_param)).order_by("id")
            except ValidationError as ex:
                raise serializers.ValidationError(ex)
        else:
            queryset = Message.objects.filter(user_condition).order_by("id")

        return queryset

    def perform_create(self, serializer):
        # Get the sender and receiver usernames from the request data
        sender_username = self.request.user
        receiver_username = self.request.data.get('receiver')

        # Retrieve the user objects based on the usernames
        sender = User.objects.get(username=sender_username)
        try:
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Receiver does not exist.")

        # Set the sender and receiver as user objects in the serializer
        serializer.save(sender=sender, receiver=receiver)


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsSenderOrReceiver]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if the is_read field is False before updating
        if not instance.is_read:
            instance.is_read = True
            instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
