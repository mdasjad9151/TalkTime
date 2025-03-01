import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import PrivateMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.friend_username = self.scope['url_route']['kwargs']['username']
        self.user = self.scope.get("user")

        if self.user.is_authenticated:
            self.room_name = f"chat_{min(self.user.username, self.friend_username)}_{max(self.user.username, self.friend_username)}"
            self.room_group_name = f"chat_{self.room_name.replace('@', '_')}"

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            # Send undelivered messages
            await self.send_undelivered_messages()

        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        #  Save message in database asynchronously
        await self.save_message(self.user.username, self.friend_username, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username
            }
        )

    async def chat_message(self, event):
        # Don't send the message back to the sender
        if event['sender'] != self.user.username:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'sender': event['sender']
            }))

    @database_sync_to_async
    def save_message(self, sender_username, receiver_username, message):
        sender = User.objects.get(username=sender_username)
        receiver = User.objects.get(username=receiver_username)
        PrivateMessage.objects.create(sender=sender, receiver=receiver, message=message)

    @database_sync_to_async
    def get_undelivered_messages(self):
        """ Get undelivered messages as a list of dictionaries (not model objects) """
        messages = PrivateMessage.objects.filter(receiver__username=self.user.username, is_delivered=False)
        return [
            {"message": msg.message, "sender": msg.sender.username}
            for msg in messages
        ]

    async def send_undelivered_messages(self):
        undelivered_messages = await self.get_undelivered_messages()
        for msg in undelivered_messages:
            await self.send(text_data=json.dumps(msg))

        #  Mark them as delivered
        await self.mark_messages_as_delivered()

    @database_sync_to_async
    def mark_messages_as_delivered(self):
        PrivateMessage.objects.filter(receiver__username=self.user.username, is_delivered=False).update(is_delivered=True)
