from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
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
        
        # Get the username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')
        user_condition = Q(username=username) & Q(password=password)

        # Check if a user exists
        try:
            user = User.objects.get(user_condition)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)



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
    
class UserRegistrationView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
