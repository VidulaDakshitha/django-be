from rest_framework import serializers

from .models import User


class UseSampleSerializer(CustomBaseSerializer):
    password = serializers.CharField(required=True)
    # def __init__(self, *args, **kwargs):
    #     super(UserSerializer, self).__init__(*args, **kwargs)
    #     # Dynamically remove fields that shouldn't be exposed
    #     exclude = ('is_delete', 'login_attempts', 'reset_otp', 'is_res_tok_valid',)  # Add any field names you want to exclude
    #     for field_name in exclude:
    #         self.fields.pop(field_name, None)

    class Meta:
        model = User
        # fields = ['__all__']
        fields = ['id', 'first_name', 'last_name', 'user_name', 'email', 'phone_no', 'description', 'is_active',
                  'is_locked', 'is_verified', 'is_admin', 'is_super_admin', 'is_client', 'is_freelancer']
        read_only_fields = ('is_delete',)

    def validate(self, data):
        """
        Add any additional validation for your data here.
        For example, you might want to ensure that the product name is not already in use
        if you're creating a new product or updating the name of an existing one.
        """
        if self.instance is None:
            if User.objects.filter(email=data['email'], is_delete=False).exists():
                raise serializers.ValidationError({'email': 'Email already exists.'})

            if User.objects.filter(phone_no=data['phone_no'], is_delete=False).exists():
                raise serializers.ValidationError({'phone no': 'Phone no already exists.'})

            if User.objects.filter(user_name=data['user_name'], is_delete=False).exists():
                raise serializers.ValidationError({'user name': 'Username already exists.'})

        # else:
        #     if 'name' in data and data['name'] != self.instance.name:
        #         if User.objects.filter(name=data['name'], is_delete=False).exists():
        #             raise serializers.ValidationError({'name': 'name already exists.'})

        return data

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `User` instance, given the validated data.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_no = validated_data.get('phone_no', instance.phone_no)
        instance.user_name = validated_data.get('user_name', instance.user_name)
        instance.save()

        return instance
