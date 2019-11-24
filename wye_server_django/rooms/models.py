from django.db import models

# Create your models here.
class EscapeRoomSession(models.Model):
    name = models.CharField(max_length=255)
    played_datetime = models.DateTimeField()
    duration_time = models.DurationField()
    number_of_hints = models.IntegerField()
    user = models.ForeignKey("account.WYEUser", on_delete=models.CASCADE)
