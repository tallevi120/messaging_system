from rest_framework.permissions import BasePermission

class IsSenderOrReceiver(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the request user is the sender or receiver of the message
        return obj.sender == request.user or obj.receiver == request.user
