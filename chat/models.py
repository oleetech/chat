from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)  # রুমের নাম
    created_at = models.DateTimeField(auto_now_add=True)  # রুম তৈরির তারিখ ও সময়
    users = models.ManyToManyField(User, related_name='chat_rooms',blank=True)  # অনেক ব্যবহারকারীকে সংযুক্ত করার জন্য ManyToManyField

    def __str__(self):
        return self.name
    
# চ্যাট মেসেজ মডেল
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # মেসেজ পাঠানো ব্যবহারকারী
    username = models.CharField(max_length=255, null=True, blank=True)  # ইউজারনেম যদি প্রয়োজন হয়
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)  # রুম যেটিতে মেসেজ পাঠানো
    content = models.TextField()  # মেসেজের কন্টেন্ট
    timestamp = models.DateTimeField(auto_now_add=True)  # মেসেজের সময়

