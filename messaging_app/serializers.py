from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Message

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class MessageSerializer(serializers.ModelSerializer):
    receiver = serializers.CharField(source='receiver.username')
    sender = serializers.CharField(source='sender.username')
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender','receiver', 'subject', 'content', 'is_read', 'created_at']

    def create(self, validated_data):
        # Get the receiver username from the validated data
        receiver_username = validated_data['receiver']

        # Retrieve the sender user object from the request user (token-based)
        sender = self.context['request'].user

        try:
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Receiver does not exist.")
        

        # Set the sender and receiver as user objects in the serializer
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            subject=validated_data['subject'],
            content=validated_data['content']
        )
        return message

