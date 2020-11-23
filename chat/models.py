from django.core.exceptions import ValidationError
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
    job = models.ForeignKey(
        'services.Job',
        on_delete=models.CASCADE,
        related_name='chat',
    )

    def validate_user(self, user):
        participants = (self.job.professional.user, self.job.user)
        if user not in participants:
            raise ValidationError(
                'You are not participating in the chat'
            )

    def validate_receiver(self):
        self.validate_user(self.receiver)
    
    def validate_sender(self):
        self.validate_user(self.sender)

    def validate_payment(self):
        if not self.job.payment.is_valid():
            raise ValidationError(
                'Payment is required to send the message'
            )
    
    def full_clean(self, *args, **kwargs):
        self.validate_payment()
        self.validate_sender()
        self.validate_receiver()
        return super(Message, self).full_clean(*args, **kwargs)

    def __str__(self):
        return f'{self.sender} to {self.receiver}: {self.content[0:15]}'
    class Meta:
        ordering = ['-registration_date']