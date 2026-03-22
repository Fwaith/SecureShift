from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests

from .models import HabitabilityScores, Neighborhood, Region

@csrf_exempt
@require_http_methods(["GET"])
def get_neighbourhoods(request):
	neighbourhoods = Neighborhood.objects.all().order_by("neighborhood_id")
	payload = [
		{
			"neighbourhoodId": neighbourhood.neighborhood_id,
			"postcode": neighbourhood.postcode or "",
		}
		for neighbourhood in neighbourhoods
	]
	return JsonResponse(payload, safe=False)

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

def _lookup_county_from_postcode(postcode):
    """Look up county from UK postcode using postcodes.io API"""
    outcode = _extract_outcode(postcode)
    if not outcode:
        return None
    
    try:
        response = requests.get(f"https://api.postcodes.io/outcodes/{outcode}")
        print(f"URL: https://api.postcodes.io/outcodes/{outcode} - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('result'):
                # postcodes.io returns 'county' or 'admin_county'
                county = data['result'].get('county') or data['result'].get('admin_county')
                print(f"DEBUG: Postcode {outcode} maps to county: {county}")
                return county[0] if county else None
        else:
            print(f"ERR: postcodes.io returned status {response.status_code} for {outcode}")
    except Exception as e:
        print(f"ERR: postcodes.io lookup failed for {outcode}: {str(e)}")
    
    return None

def _serialize_habitability_score(score, postcode, region):
	return {
		"scoreId": score.score_id,
		"postcode": postcode,
		"regionId": region.region_id,
		"regionName": region.region_name,
		"employmentRate": score.employment_rate,
		"income": score.income,
		"inflation": score.inflation,
		"airQuality": score.air_quality,
		"waterQuality": score.water_quality,
		"landFertility": score.land_fertility,
		"wasteManagement": score.waste_management,
		"education": score.education,
		"healthcare": score.healthcare,
		"transportation": score.transportation,
		"crime": score.crime,
		"politics": score.politics,
		"disasterRisks": score.disaster_risks,
		"civicEngagement": score.civic_engagement,
		"economyScore": score.economy_score,
		"environmentScore": score.environment_score,
		"infrastructureScore": score.infrastructure_score,
		"securityScore": score.security_score,
		"overallScore": score.overall_score,
		"dateScored": score.date_scored.isoformat() if score.date_scored else None,
	}

def _random_habitability_score_for_fallback(requested_postcode):
	random_score = (
		HabitabilityScores.objects.select_related("neighborhood__region")
		.filter(neighborhood__region__isnull=False)
		.order_by("?")
		.first()
	)

	region = random_score.neighborhood.region
	postcode = random_score.neighborhood.postcode or requested_postcode
	return _serialize_habitability_score(random_score, postcode, region)

@csrf_exempt
@require_http_methods(["GET"])
def get_habitability_by_postcode(request, postcode):
	mPc = (postcode or "").strip().upper()
	if not mPc:
		return JsonResponse(
			{"error": "MISSING_POSTCODE", "message": "Postcode is required"},
			status=400,
		)

	county = _lookup_county_from_postcode(mPc)
	if not county:
		fallback_payload = _random_habitability_score_for_fallback(mPc)
		return JsonResponse(fallback_payload)

	region = Region.objects.filter(region_name__iexact=county).first()
	if not region:
		return JsonResponse(
			{"error": "NOT_FOUND", "message": f"Region '{county}' not found"},
			status=404,
		)

	# Prefer the requested mapping: score id matches region id.
	score = HabitabilityScores.objects.filter(score_id=region.region_id).first()
	if not score:
		# Fallback to relational lookup when IDs do not align.
		score = HabitabilityScores.objects.filter(neighborhood__region=region).order_by("score_id").first()

	if not score:
		return JsonResponse(
			{"error": "NOT_FOUND", "message": "Habitability scores not found for this region"},
			status=404,
		)

	return JsonResponse(_serialize_habitability_score(score, mPc, region))
