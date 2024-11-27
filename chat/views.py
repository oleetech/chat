from django.shortcuts import render, get_object_or_404
from .models import ChatRoom

def index(request):
    rooms = ChatRoom.objects.all()  # ডাটাবেস থেকে সব রুম নিয়ে আসুন
    return render(request, "index.html", {"rooms": rooms})

def room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)  # রুমটি ডাটাবেস থেকে আনা
    return render(request, "room.html", {"room_name": room.name})

