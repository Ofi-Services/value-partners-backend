from django.db import models
from .constants import ACTIVITY_CHOICES, PATTERN_CHOICES

class Activity(models.Model):
    """
    A model representing an activity related to a case.

    Attributes:
        id (int): The primary key for the activity.
        case (Case): The related case of the activity
        timestamp (datetime): The timestamp of the activity.
        name (str): The name of the activity, chosen from ACTIVITY_CHOICES.
        case_index (int): The index of the case, with a default value of 0.
        tpt (float): The time per task of the activity, with a default value of 0.
    """
    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(Case, related_name='activities', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    name = models.CharField(max_length=60)
    tpt = models.FloatField(default=0)
    user = models.CharField(max_length=50, default='None')
    user_type = models.CharField(max_length=50, default='None')
    automatic = models.BooleanField(default=False)
    rework = models.BooleanField(default=False)
    case_index = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.case.id} - {self.name} at {self.timestamp}"
    
class Variant(models.Model):
    """
    A model representing a variant.

    Attributes:
        id (int): The primary key for the variant.
        activities (str): The activities of the variant.
        cases (str): The cases of the variant.
        number_cases (int): The amount of cases of the variant.
        percentage (float): The percentage of cases the variant includes.
        avg_time (float): The average time per case of the variant.
    """
    id = models.AutoField(primary_key=True)
    activities = models.TextField()
    cases = models.TextField()
    number_cases = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    avg_time = models.FloatField(default=0)

    def __str__(self):
        return self.name
    
