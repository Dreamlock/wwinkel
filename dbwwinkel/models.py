from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
import datetime
from django.utils.translation import ugettext_lazy as _
# Create your models here.


class State(models.Model):

  state = models.CharField(max_length = 10)

class Question(models.Model):

    # Visible and editable: mandatory
    question_text = models.TextField()
    reason = models.TextField()
    purpose = models.TextField()
    own_contribution = models.TextField()

    # Visible and editable: optional
    remarks = models.TextField(blank = True)
    internal_remarks = models.TextField(blank = True)
    how_know_WW = models.TextField(blank = True)
    deadline = models.DateField(blank = True, null = True)

    public = models.BooleanField()

    # metadata: invisible
    creation_date = models.DateTimeField(default = timezone.now)
    active = models.BooleanField(default=True)
    status = models.ForeignKey(State)

    organisation = models.ForeignKey(settings.AUTH_USER_MODEL)

    def clean(self):
        if self.deadline is not None and self.deadline < datetime.date.today():
            raise ValidationError({'deadline': _('Deadlines kunnen niet in het verleden zijn')})



