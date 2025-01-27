import uuid

from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.base_mongo import MongoDBClient
from common.base_view import BaseView, custom_exception_handler
from core_apps.user.models import Chatroom, User
from core_apps.user.serializers.chatroom_serializer import ChatRoomSerializer


# Create your views here.
class ChatroomView(BaseView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer
    model = Chatroom

    @transaction.atomic
    @custom_exception_handler
    def post(self, request):
        with transaction.atomic():
            serializer = self.serializer_class(data=request.data, context={'request': request})

            if serializer.is_valid():
                instance = serializer.save()
                consumer = User.objects.get(id=request.data.get("consumer_id"))

                if not consumer.chat_id:
                    consumer.chat_id = uuid.uuid4()
                    consumer.save()

                data = {
                    "sender_id": request.user.chat_id,
                    "receiver_id": consumer.chat_id,
                    "chat_room_id": instance.chat_room_id
                }
                return Response({"message": "Successfully created", "data": data}, status=status.HTTP_201_CREATED)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @custom_exception_handler
    def get(self, request, object_id=None):
        if object_id:
            m_class = MongoDBClient()
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            data = m_class.get_chat_history(object_id, page, limit)
            return Response({"message": "Successfully retrieved", "data": data}, status=status.HTTP_200_OK)
        else:
            chat_rooms = Chatroom.objects.filter(Q(init_user=request.user) | Q(consumer=request.user))
            page = self.paginate_queryset(chat_rooms, request)
            serializer = self.serializer_class(page, many=True, context={'request': request})
            count = chat_rooms.count()
            return Response({"data": serializer.data, "count": count})
