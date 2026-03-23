from django.db import models
from django.db.models import F     # refers to model field value directly in database


def _extract_outcode(postcode):
    if not postcode:
        return None

    normalized = postcode.strip().upper()
    if not normalized:
        return None

    parts = normalized.split()
    if len(parts) > 1:
        return parts[0]

    compact = "".join(parts)
    if len(compact) > 3:
        return compact[:-3]

    return compact

def _lookup_coordinates_from_postcode(postcode):
    outcode = _extract_outcode(postcode)
    if not outcode:
        return None, None

    try:
        mapping = OutcodeCountyMapping.objects.get(outcode=outcode)
        return mapping.lat, mapping.lon
    except OutcodeCountyMapping.DoesNotExist:
        return None, None

def _lookup_county_from_postcode(postcode):
    """Look up county from UK postcode outcode mapping table."""
    outcode = _extract_outcode(postcode)
    if not outcode:
        return None

    try:
        mapping = OutcodeCountyMapping.objects.get(outcode=outcode)
        return mapping.county
    except OutcodeCountyMapping.DoesNotExist:
        return None

    return None

class Region(models.Model):
    region_id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=20)

    # For our use/ testing
        # shows the value rather than just the object
    def __str__(self):
        return self.region_name


class OutcodeCountyMapping(models.Model):
    """Maps UK postcode outcodes to their corresponding counties."""
    outcode = models.CharField(max_length=4, unique=True, primary_key=True)
    county = models.CharField(max_length=50)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Outcode County Mappings"

    def __str__(self):
        return f"{self.outcode} -> {self.county}"


class Neighborhood(models.Model):
    neighborhood_id = models.AutoField(primary_key=True)
    region = models.ForeignKey("Region", on_delete=models.CASCADE, related_name="neighborhoods", null=True, blank=True)
    neighborhood_name = models.CharField(max_length=100, unique=True)
    postcode = models.CharField(max_length=7, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.postcode:
            self.postcode = "".join(self.postcode.upper().split())
            
            # Auto-assign region based on postcode if not already set
            if not self.region_id:
                county = _lookup_county_from_postcode(self.postcode)
                if county:
                    try:
                        self.region = Region.objects.get(region_name=county)
                        print(f"DEBUG: Assigned region '{county}' to postcode {self.postcode}")
                    except Region.DoesNotExist:
                        print(f"ERR: Region '{county}' not found in database for postcode {self.postcode}")
                else:
                    print(f"ERR: Could not determine county for postcode {self.postcode}")

        if self.postcode and (self.lat is None or self.lon is None):
            latitude, longitude = _lookup_coordinates_from_postcode(self.postcode)
            if self.lat is None:
                self.lat = latitude
            if self.lon is None:
                self.lon = longitude

        super().save(*args, **kwargs)

    # For our use/ testing
    def __str__(self):
        return self.neighborhood_name
class HabitabilityScores(models.Model):

    score_id = models.AutoField(primary_key=True)

    neighborhood = models.OneToOneField("Neighborhood", on_delete=models.CASCADE, related_name="habitability_score", null=True, blank=True) #1-1 relationship with HabitabilityScores
    
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
    overall_score = models.GeneratedField(
        expression = (F('economy_score')*0.30) + (F('environment_score')*0.20) + (F('infrastructure_score')*0.30) + (F('security_score')*0.20),
        output_field= models.FloatField(),
        db_persist=True     # saves values into a new column
    )
 
    # For our use/ testing
    def __str__(self):
        return self.neighborhood.neighborhood_name if self.neighborhood else f"Score {self.score_id}"
    

