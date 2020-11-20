from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
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
    viewed = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f'{self.sender} to {self.receiver}: {self.content[0:15]}'
    class Meta:
        ordering = ['-registration_date']