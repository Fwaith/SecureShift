from django.db import models
from django.db.models import F     # refers to model field value directly in database

class Region(models.Model):
    region_id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=20)
    # Calculate habitability score from values when needed 

    # For our use/ testing
        # shows the value rather than just the object
    def __str__(self):
        return self.region_name


class Neighbourhood(models.Model):
    neighbourhood_id = models.AutoField(primary_key=True)
    region = models.ForeignKey("Region", on_delete=models.CASCADE, related_name="neighbourhoods")
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

    # Individual equations (excluding overall habitability score)
    #Economy = (Employment Rate * 0.25) + (Income * 0.35) + (Inflation * 0.40)
    economy_score = models.GeneratedField(
        expression = (F('employment_rate')*0.25) + (F('income')*0.35) + (F('inflation')*0.40),
        output_field= models.FloatField(),
        db_persist=True     # saves values into a new column
    )

    #Environment = (Air Quality * 0.20) + (Water Quality * 0.15) + (Land fertility * 0.25) + (Waste management * 0.40)
    environment_score = models.GeneratedField(
        expression = (F('air_quality')*0.20) + (F('water_quality')*0.15) + (F('land_fertility')*0.25) + (F('waste_management')*0.40),
        output_field= models.FloatField(),
        db_persist=True     # saves values into a new column
    )

    #Infrastructure = (Education * 0.30) + (Healthcare * 0.30) + (Transportation * 0.40)
    infrastructure_score = models.GeneratedField(
        expression = (F('education')*0.30) + (F('healthcare')*0.30) + (F('transportation')*0.4),
        output_field= models.FloatField(),
        db_persist=True     # saves values into a new column
    )

    #Security = (Crime * 0.30) + (Political Stability * 0.25) + (Disaster Risk * 0.30) + (Civic Engagement * 0.15)
    security_score = models.GeneratedField(
        expression = (F('crime')*0.30) + (F('politics')*0.25) + (F('disaster_risks')*0.30) + (F('civic_engagement')*0.15),
        output_field= models.FloatField(),
        db_persist=True     # saves values into a new column
    )


 
    # For our use/ testing
    def __str__(self):
        return self.county
    

