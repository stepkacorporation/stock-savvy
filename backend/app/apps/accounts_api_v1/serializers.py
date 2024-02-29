from djoser.serializers import UserSerializer, UserCreateSerializer

from .models import User


class CustomUserSerializer(UserSerializer):
    """
    Responsible for viewing user data.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Responsible for creating the user.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id',)
