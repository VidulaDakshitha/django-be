import uuid

from django.db.models import Q
from rest_framework import serializers

from common.base_serializer import CustomBaseSerializer
from core_apps.user.models import User, Chatroom


class ChatRoomSerializer(CustomBaseSerializer):
    consumer_id = serializers.IntegerField(required=False, write_only=True)
    consumer_data = serializers.SerializerMethodField()

    class Meta:
        model = Chatroom
        fields = ['id', 'init_user', 'consumer', 'chat_room_id', 'consumer_id', 'consumer_data']
        read_only_fields = ('is_delete',)

    def validate(self, data):
        if data.get('consumer_id') is not None:
            try:
                data['consumer'] = User.objects.get(id=data.get('consumer_id'))
                data.pop('consumer_id')
            except User.DoesNotExist:
                raise serializers.ValidationError('User not found')

        return data

    def get_consumer_data(self, obj):
        request_user = self.context['request'].user
        other_user = obj.consumer if obj.init_user == request_user else obj.init_user
        return {
            "id": other_user.id,
            "first_name": other_user.first_name,
            "last_name": other_user.last_name,
            "chat_id": other_user.chat_id
        }

    def create(self, validated_data):
        validated_data["init_user"] = self.context["request"].user
        validated_data["chat_room_id"] = uuid.uuid4()

        query = Chatroom.objects.filter(
            (Q(init_user=validated_data["init_user"]) & Q(consumer=validated_data["consumer"])) |
            (Q(consumer=validated_data["init_user"]) & Q(init_user=validated_data["consumer"]))
        )

        if query.exists():
            return query.first()
        else:
            chatroom = Chatroom.objects.create(**validated_data)

        return chatroom
