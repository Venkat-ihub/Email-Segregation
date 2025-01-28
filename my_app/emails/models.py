
# Create your models here.
# models.py

from djongo import models  # Assuming djongo is being used for MongoDB integration

class Applicant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    job_role = models.CharField(max_length=100)
    resume = models.CharField(max_length=100, blank=True, null=True)
    date_received = models.DateTimeField()  # Store date and time in Django model

    class Meta:
        db_table = 'applicants'
