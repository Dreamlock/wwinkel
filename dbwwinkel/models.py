from django.db import models
import datetime
# Create your models here.


class Question(models.Model):

    QUESTION_STATUS = (
        ('new', 'nieuw'),
        ('active', 'actief')
    )

    # Visible and editable: mandatory
    question_text = models.TextField()
    reason = models.TextField()
    purpose = models.TextField()
    own_contribution = models.TextField()

    # Visible and editable: optional
    remarks = models.TextField(blank = True)
    internal_remarks = models.TextField(blank = True)
    how_know_WW = models.TextField(blank = True)
    deadline = models.DateField(blank = True)

    public = models.BooleanField()

    # metadata: invisible
    # organisation = models.ForeignKey('Organisation')
    creation_date = models.DateTimeField(default = datetime.datetime.now())
    active = models.BooleanField(default=True)
    status = models.CharField(max_length = 10, choices= QUESTION_STATUS)
    log = models.ForeignKey('Log')
    intake = models.ForeignKey('Intake')


class Log(models.Model):
    pass

class Intake(models.Model):
    date = models.DateTimeField(default = datetime.datetime.now())
    remarks = models.TextField(blank = True)