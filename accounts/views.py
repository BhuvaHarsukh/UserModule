from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, AccessToken
from .serializers import UserSerializer, UserCreateSerializer
from .permissions import IsAdminUserOnly, IsSelfOrAdmin
import bcrypt
import secrets
from django.utils import timezone
from rest_framework.views import APIView

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUserOnly]
        elif self.action == 'retrieve':
            permission_classes = [IsSelfOrAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        raw_password = data.get('password')

        if not raw_password:
            return Response({"detail": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Encrypt password
        hashed = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()
        data['password'] = hashed

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "User Deleted"}, status=status.HTTP_200_OK)


class UserLoginView(APIView):
    permission_classes = []  # Allow any to login

    def post(self, request):
        cell_number = request.data.get('cell_number')
        password = request.data.get('password')

        if not cell_number or not password:
            return Response({"detail": "Cell number and password required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(cell_number=cell_number)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if not bcrypt.checkpw(password.encode(), user.password.encode()):
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate token
        token = secrets.token_urlsafe(64)
        ttl = 30000000000000  # example ttl in ms

        AccessToken.objects.create(
            token=token,
            ttl=ttl,
            user=user,
            created_at=timezone.now()
        )

        return Response({
            "token": token,
            "ttl": ttl,
            "user_id": user.id
        })
    
