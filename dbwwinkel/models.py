from django.db import models

# Create your models here.


class Question(models.Model):
    question_text = models.TextField()
    reason = models.TextField()
    #creation_date = models.DateTimeField()
    purpose = models.TextField()
    deadline = models.DateField()
    own_contribution = models.TextField()
    remarks = models.TextField()
    internal_remarks = models.TextField()
    how_know_WW = models.TextField()
    puplical = models.BooleanField()
    #active = models.BooleanField(default=True)
    #status = models.ForeignKey(QuestionStatus)
    #log = models.ForeignKey(Log)
    #intake = models.ForeignKey(Intake)