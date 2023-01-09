from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=20,
                                        required=True, write_only=True)
    password2 = serializers.CharField(min_length=8, max_length=20,
                                        required=True, write_only=True)

    class Meta:
        model = User
        fields = (
                'email',
                'password',
                'password2',
                'number',
                )

    def validate(self, attrs):
        password2 = attrs.pop('password2')
        if attrs['password'] != password2:
            raise serializers.ValidationError('Passworddid not match!!!')
        elif not attrs['password'].isalnum():
            raise serializers.ValidationError('password field must contain'
                                            'alpha sympols and numbers')

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    default_error_messages = {'bad_token': _('Token is invalid or expired')}

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')

    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100,
                                        required=True)


class RestorePasswordSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    password2 = serializers.CharField(min_length=8, required=True, write_only=True)

    def validate(self, attrs):
        password2 = attrs.pop('password2')
        if attrs['password'] != password2:
            raise serializers.ValidationError('Passwords did not match!')
        # if not attrs['password'].isalnum():
        #     raise serializers.ValidationError('Password field must contain'
        #                                       'alpha symbols and numbers!')
        try:
            user = User.objects.get(
                activation_code=attrs['code']
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Invalid code'
            )
        attrs['user'] = user
        return attrs
    
    def save(self, **kwargs):
        data = self.validated_data
        user = data['user']
        user.set_password(data['password'])
        user.activate_code = ''
        user.save()
        return user

