from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.account.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = (
            'id',
            'username',
            'email',
            'phone',
            'role',
            'email_verified_at',
            'phone_verified_at',
            'last_activity_at',
            'first_name',
            'last_name',
        )

        read_only_fields = (
            'email_verified_at',
            'phone_verified_at',
            'last_activity_at',
            'role',
        )


class UserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=6
    )

    password_confirm = serializers.CharField(
        write_only=True,
        min_length=6
    )

    class Meta:
        model = User

        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'phone',
            'role',
            'password',
            'password_confirm',
        ]

    def validate_role(self, value):

        if value not in [
            User.RoleType.CLIENT,
            User.RoleType.DRIVER
        ]:
            raise serializers.ValidationError(
                "The role must be CLIENT or DRIVER."
            )

        return value

    def validate(self, attrs):

        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'The passwords do not match.'
            })

        password = attrs.get('password')

        user = User(
            email=attrs.get('email'),
            username=attrs.get('username'),
            first_name=attrs.get('first_name', ''),
            last_name=attrs.get('last_name', ''),
            phone=attrs.get('phone', ''),
            role=attrs.get('role', User.RoleType.CLIENT),
        )

        try:
            validate_password(
                password=password,
                user=user
            )

        except DjangoValidationError as error:
            raise serializers.ValidationError({
                'password': error.messages
            })

        return attrs

    def create(self, validated_data):

        password = validated_data.pop('password')
        validated_data.pop('password_confirm')

        user = User(**validated_data)

        user.set_password(password)
        user.save()

        return user