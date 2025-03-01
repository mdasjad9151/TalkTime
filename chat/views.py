from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .models import FriendRequest,PrivateMessage

@login_required
def home(request):
    """Load the landing page with dynamic friends"""
    friend_requests = FriendRequest.objects.filter(
        Q(receiver=request.user) | Q(sender=request.user), 
        status="accepted"
    )

    # Extract actual user objects
    friends = set()
    for fr in friend_requests:
        if fr.sender == request.user:
            friends.add(fr.receiver)  # Friend is the receiver
        else:
            friends.add(fr.sender)  # Friend is the sender

    return render(request, "chat/index.html", {
        "friends": friends
    })


@login_required
def chat_view(request, username):
    """Render chat page (for API calls, WebSocket handles messages)"""
    return render(request, "chat/index.html", {"selected_friend": username})

@login_required
def add_friends(request):
    """Show all non-friends except the logged-in user and superusers"""
    
    # Get all friends of the logged-in user
    friends = User.objects.filter(
        Q(sent_requests__receiver=request.user, sent_requests__status="accepted") |  
        Q(received_requests__sender=request.user, received_requests__status="accepted")
    )

    # Exclude the logged-in user, superusers, and existing friends
    users = User.objects.exclude(
        Q(id=request.user.id) |  
        Q(is_superuser=True) |  
        Q(id__in=friends.values_list("id", flat=True))
    )

    return render(request, "chat/add_friends.html", {"users": users})

@csrf_exempt
@login_required
def send_friend_request(request, user_id):
    """Send a friend request"""
    if request.method == "POST":
        receiver = User.objects.get(id=user_id)
        if not FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
            FriendRequest.objects.create(sender=request.user, receiver=receiver)
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Request already sent."})

@login_required
def show_requests(request):
    """Show all pending friend requests received by the user"""
    friend_requests = FriendRequest.objects.filter(receiver=request.user, status="pending")
    # print(friend_requests)
    return render(request, "chat/friend_requests.html", {
        "friend_requests": friend_requests
    })


@login_required
def accept_friend_request(request, request_id):
    """Accept a friend request (change status to 'accepted')"""
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    
    if request.method == "POST":
        friend_request.status = "accepted"
        friend_request.save()
        return JsonResponse({"success": True, "message": "Friend request accepted!"})

    return JsonResponse({"success": False, "error": "Invalid request."})

@login_required
def reject_friend_request(request, request_id):
    """Reject a friend request (delete the row)"""
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)

    if request.method == "POST":
        friend_request.delete()
        return JsonResponse({"success": True, "message": "Friend request rejected!"})

    return JsonResponse({"success": False, "error": "Invalid request."})


@login_required
def fetch_messages(request, username):
    """ Fetch previous messages between logged-in user and selected user. """
    selected_user = get_object_or_404(User, username=username)
    logged_user = request.user

    # Get messages where sender or receiver is either of the users
    messages = PrivateMessage.objects.filter(
        sender__in=[logged_user, selected_user],
        receiver__in=[logged_user, selected_user]
    ).order_by('timestamp')

    # Serialize messages
    message_list = [
        {
            'message': msg.message,
            'sender': msg.sender.username,
            'receiver': msg.receiver.username,
            'timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M"),
        } for msg in messages
    ]

    return JsonResponse({'messages': message_list})