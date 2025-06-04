from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'deleted_at') 

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'profile_pic', 'name', 'cell_number', 'password', 'email', 'role_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('request') and self.context['request'].method in ['PATCH', 'PUT']:
            for field in self.fields.values():
                field.required = False

    def create(self, validated_data):
        import bcrypt
        password = validated_data.pop('password')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        validated_data['password'] = hashed.decode('utf-8')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        import bcrypt
        if 'password' in validated_data:
            password = validated_data.pop('password')
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            instance.password = hashed.decode('utf-8')
        return super().update(instance, validated_data)
