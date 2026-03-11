from django.db import models



class HabitabilityScores(models.Model):

    #score_id = models.AutoField(primary_key=True)

    #neighbourhood = models.ForeignKey("Neighbourhood", on_delete=models.CASCADE)

    county = models.CharField(max_length=100, unique=True)
    employment_rate = models.FloatField()
    income = models.FloatField()
    inflation = models.FloatField()
    air_quality = models.FloatField()
    water_quality = models.FloatField()
    land_fertility = models.FloatField()
    waste_management = models.FloatField()
    education = models.FloatField()
    healthcare = models.FloatField()
    transportation = models.FloatField()
    crime = models.FloatField()
    politics = models.FloatField()
    disaster_risks = models.FloatField()
    civic_engagement = models.FloatField()

    #date_scored = models.DateTimeField()

    # For our use/ testing
    def __str__(self):
        return self.county
