from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserMeSerializer, UserRegisterSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserMeView(generics.RetrieveAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny] 
    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        # Nếu không phải admin → ép role là 'staff'
        user = self.request.user
        if not user.is_authenticated or user.role != 'admin':
            serializer.validated_data['role'] = 'staff'
        serializer.save()