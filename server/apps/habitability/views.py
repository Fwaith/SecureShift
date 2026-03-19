from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Neighborhood

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
