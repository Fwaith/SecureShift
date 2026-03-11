from django.db import models

class Region(models.Model):
    region_id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=20)
    # Calculate habitability score from values when needed 

    # For our use/ testing
    def __str__(self):
        return self.region_name


class Neighbourhood(models.Model):
    neighbourhood_id = models.AutoField(primary_key=True)
    region = models.ForeignKey("Region", on_delete=models.CASCADE, related_name="Neighbourhoods")
    county = models.CharField(max_length=100)
    postcode = models.CharField(max_length=7)

    # For our use/ testing
    def __str__(self):
        return self.postcode
class HabitabilityScores(models.Model):

    score_id = models.AutoField(primary_key=True)

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

    date_scored = models.DateField()

    # For our use/ testing
    def __str__(self):
        return self.county
