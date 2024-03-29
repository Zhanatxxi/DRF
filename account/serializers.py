from django.contrib.auth import authenticate
from rest_framework import serializers


from account.models import MyUser
from account.utils import send_activation_code


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirm = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'password_confirm')

    def validate(self, validated_data):
        print(validated_data)
        password = validated_data.get('password')
        password_confirm = validated_data.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('passwords do not match!')
        return validated_data

    def create(self, validated_data):
        """ This function when self.save() method is called """
        email = validated_data.get('email')
        password = validated_data.get('password')
        user = MyUser.objects.create_user(email=email, password=password)
        send_activation_code(email=email, activation_code=user.activation_code)
        return user


#TODO: login serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(label='password', style={'input_type': 'password'},
                                     trim_whitespace=False)
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email,
                                password=password)
            if not user:
                message = 'unable to log in with provided credentials'
                raise serializers.ValidationError(message, code='authorization')
        else:
            message = 'must include "email" and "password"'
            raise serializers.ValidationError(message, code='authorization')

        attrs['user'] = user
        return attrs
