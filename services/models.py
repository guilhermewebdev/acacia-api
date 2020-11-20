from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from core.models import OCCUPATIONS, Professional, STATES, SERVICES, ValidateChoices
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def future_validator(date_time):
    if timezone.now() > date_time:
        raise ValidationError(
            'This date has passed'
        )

class Job(models.Model):
    proposal = models.OneToOneField(
        'Proposal',
        on_delete=models.DO_NOTHING,
        related_name='job',
    )
    professional = models.ForeignKey(
        'core.Professional',
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hires',
    )
    value = models.FloatField(
        validators=[MinValueValidator(65)],
    )
    registration_date = models.DateTimeField(
        auto_now=True,
        editable=False,
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(
        null=True,
        blank=True,
    )

    def validate_client(self):
        if self.client != self.proposal.client:
            raise ValidationError(
                'The client needs to be the same as the proposal'
            )
    
    def validate_professional(self):
        if self.professional !=self.proposal.professional:
            raise ValidationError(
                'The professional needs to be the same as the proposal'
            )

    def full_clean(self, *args, **kwargs):
        self.validate_client()
        self.validate_professional()
        return super(Job, self).full_clean(*args, **kwargs)

    def __set_stats(self, attr):
        if getattr(self, attr) != None:
            stats = 'started' if attr == 'start_datetime' else 'finished'
            raise ValidationError(f'This job has already been {stats}')
        setattr(self, attr, timezone.now())
        self.full_clean()
        self.save(update_fields=[attr])
        return self

    def finish(self):
        return self.__set_stats('end_datetime')

    def start(self):
        return self.__set_stats('start_datetime')

class AcceptMixin(models.Model):
    _accepted = models.BooleanField(
        null=True,
        blank=True,
        editable=False,
    )

    @property
    def accepted(self):
        return self._accepted

    def __accept_or_reject(self, status):
        if not self.id: raise ValidationError(f'This {self.__class__.__name__} cannot be approved or rejected as it has not been saved')
        if self.accepted != None:
            current_status = 'approved' if self.accepted else 'rejected'
            raise ValidationError(
                f'This {self.__class__.__name__} has already been {current_status}.',
            )
        self._accepted = status
        self.save(update_fields=['_accepted'])
        return self


    def accept(self):
        self.__accept_or_reject(True)
        self._create_job()
        return self

    def reject(self):
        return self.__accept_or_reject(False)

    class Meta:
        abstract = True

class Proposal(AcceptMixin):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='proposals',
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='proposals',
    )
    city = models.CharField(
        max_length=100,
    )
    state = models.CharField(
        max_length=2,
        choices=STATES,
        validators=[ValidateChoices(STATES)],
    )
    professional_type = models.CharField(
        max_length=2,
        choices=OCCUPATIONS,
        validators=[ValidateChoices(OCCUPATIONS)],
    )
    service_type = models.CharField(
        max_length=2,
        choices=SERVICES,
        validators=[ValidateChoices(SERVICES)],
    )
    start_datetime = models.DateTimeField(
        validators=[future_validator],
    )
    end_datetime = models.DateTimeField(
        validators=[future_validator]
    )
    value = models.FloatField(
        validators=[MinValueValidator(65)],
    )
    description = models.TextField()
    registration_date = models.DateTimeField(
        auto_now=True,
        editable=False,
    )

    def _create_job(self):
        job = Job(
            proposal=self,
            value=self.value,
            start_datetime=self.start_datetime,
            professional=self.professional,
            client=self.client,
        )
        job.full_clean()
        job.save()
        return job

    def validate_end_start(self):
        if self.start_datetime > self.end_datetime:
            raise ValidationError(
                'The start must be before the end'
            )

    def validate_self_proposal(self):
        if self.client == self.professional.user:
            raise ValidationError(
                "You cannot make a proposal for yourself"
            )

    def full_clean(self, *args, **kwargs):
        self.validate_end_start()
        self.validate_self_proposal()
        return super(Proposal, self).full_clean(*args, **kwargs)

class CounterProposal(AcceptMixin):
    proposal = models.OneToOneField(
        Proposal,
        related_name='counter_proposal',
        on_delete=models.CASCADE,
    )
    value = models.FloatField(
        validators=[MinValueValidator(65)],
        default=models.F('proposal__value'),
    )
    description = models.TextField()
    registration_date = models.DateTimeField(
        auto_now=True,
        editable=False,
    )

    def _create_job(self):
        job = Job(
            proposal=self.proposal,
            value=self.value,
            start_datetime=self.proposal.start_datetime,
            professional=self.proposal.professional,
            client=self.proposal.client,
        )
        job.full_clean()
        job.save()
        return job
    
    def __accept_or_reject(self, status):
        self.proposal.__accept_or_reject(status)
        if self.proposal.is_valid():
            self.proposal.save(update_fields=['_accepted'])
        super(CounterProposal, self).__accept_or_reject(status)

    def validate_value(self):
        if (self.value > (1.2 * self.proposal.value)):
            raise ValidationError('The counter offer must be a maximum of 20% more than the offer')
        if (self.value < (0.8 * self.proposal.value)):
            raise ValidationError('The counter offer must be at least 20% more than the offer')
    
    def full_clean(self, *args, **kwargs):
        self.validate_value()
        return super(CounterProposal, self).full_clean(*args, **kwargs)



class Rating(models.Model):
    client = models.ForeignKey(
        User,
        on_delete = models.DO_NOTHING,
        related_name='rates',
    )
    job = models.ForeignKey(
        Job,
        on_delete = models.CASCADE,
        related_name='rates',
    )
    grade = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )

    def validate_user(self):
        if self.client != self.job.client:
            raise ValidationError(
                'It is not possible to evaluate the hiring of another user'
            )
        if self.client == self.job.professional.user:
                raise ValidationError(
                    'It is not possible to rate yourself'
                )

    def full_clean(self, *args, **kwargs) -> None:
        self.validate_user()
        return super(Rating, self).full_clean(*args, **kwargs)
    class Meta:
        unique_together = ('client', 'job')