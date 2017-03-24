from django.db import models

# Create your models here.


class Question(models.Model):

    QUESTION_STATUS = (
        ('new', 'nieuw'),
        ('active', 'actief')
    )

    question_text = models.TextField()
    reason = models.TextField()
    purpose = models.TextField()
    own_contribution = models.TextField()
    remarks = models.TextField(blank = True)
    internal_remarks = models.TextField(blank = True)
    how_know_WW = models.TextField(blank = True)
    public = models.BooleanField()
    deadline = models.DateField(blank = True)

    creation_date = models.DateTimeField()
    active = models.BooleanField(default=True)
    status = models.CharField(max_length = 10, choices= QUESTION_STATUS)
    log = models.ForeignKey('Log')
    intake = models.ForeignKey('Intake')


class Log(models.Model):
    pass

class Intake(models.Model):
    date = models.DateTimeField()
    remarks = models.TextField()