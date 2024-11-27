from django.contrib.auth.models import User
from .models import ChatRoom, Message
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from datetime import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    
    @database_sync_to_async
    def get_or_create_room(self, room_name):
        # রুমটি নিশ্চিত করা বা তৈরি করা
        room, created = ChatRoom.objects.get_or_create(name=room_name)
        return room, created
    @database_sync_to_async
    def save_message(self, user, room, message):
        if not user or not user.is_authenticated:
            print("Invalid user. Cannot save message.")
            return
        if not room:
            print("Invalid room. Cannot save message.")
            return
        Message.objects.create(user=user, room=room, content=message)
        print("Message saved successfully.")
    @database_sync_to_async
    def get_room_users(self):
        # রুমে থাকা ব্যবহারকারীর তালিকা ফিরিয়ে দেয়
        return [user.username for user in self.room.users.all()]
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # ব্যবহারকারী তথ্য প্রিন্ট করা
        user = self.scope.get('user')
        print(f"Scope: {self.scope}") 
        print(f"Connected user: {user} (Authenticated: {user.is_authenticated})")


        # রুম তৈরি বা খুঁজে পাওয়া
        self.room, created = await self.get_or_create_room(self.room_name)
  

        if user and user.is_authenticated :        
            # রুমে ব্যবহারকারীদের তালিকা অ্যাসিঙ্ক্রোনাসলি প্রিন্ট করা
            room_users = await self.get_room_users()
            print(f"Room Users: {room_users}")

            if user.username in room_users:
                print(f"User {user.username} is already in the room.")
            else:
                print(f"User {user.username} is not in the room.")
                await self.close()

        else:
            # রুমে ব্যবহারকারী থাকে না, সংযোগ চালু রাখা হবে
            print(f"User is not authenticated. Connection will stay open.")        

        # চ্যানেল গ্রুপে যোগ করা
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"User {user.username} connected to room {self.room_name}")


    async def disconnect(self, close_code):
        # গ্রুপ থেকে চ্যানেল বাদ দেওয়া
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"User disconnected from room {self.room_name}")

    async def receive(self, text_data):
        # মেসেজ গ্রহন করা
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # যদি ব্যবহারকারী লগইন থাকে
        user = self.scope.get('user') if self.scope.get('user') and self.scope.get('user').is_authenticated else None
        if user:
            username = user.username  # লগইন করা ব্যবহারকারীর নাম
        else:
            username = text_data_json.get('username', 'Anonymous')  # ব্যবহারকারী নাম পাঠানো না হলে 'Anonymous' হবে

        # Debugging log
        print(f"Received message: {message} from {username}")

        # ডেটাবেসে মেসেজ সেভ করা
        await self.save_message(user, self.room, message)

        # গ্রুপে মেসেজ পাঠানো
        print(f"Sending message: {message} to group {self.room_group_name}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )


    async def chat_message(self, event):
        # মেসেজ এবং ইউজারনেম গ্রহন করা
        message = event['message']
        username = event['username']  # Retrieve username from the event
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

        # মেসেজ ক্লায়েন্টে পাঠানো
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'time': current_time  

        }))
