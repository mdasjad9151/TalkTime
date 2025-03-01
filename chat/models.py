from django.db import models
from django.contrib.auth.models import User

class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.message[:30]}"



class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name="sent_requests", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_requests", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("accepted", "Accepted")], default="pending")
    timestamp = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"

