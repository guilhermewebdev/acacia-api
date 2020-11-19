from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Chat(models.Model):
    participants = models.ManyToManyField(
        User,
        related_name='chats',
    )

    class Meta:
        ordering = ['-messages__registration_date']
        
class Message(models.Model):
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages_sent',
    )
    registration_date = models.DateTimeField(
        auto_now=True,
    )
    content = models.TextField()

    class Meta:
        ordering = ['-registration_date']