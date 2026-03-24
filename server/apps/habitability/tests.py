from datetime import date

from django.http import JsonResponse
from django.test import RequestFactory, TestCase

from .models import (
	HabitabilityScores,
	Neighborhood,
	OutcodeCountyMapping,
	Region,
	_extract_outcode,
)
from .views import get_habitability_by_postcode


class HabitabilityModelTests(TestCase):
	"""Model-level tests for postcode parsing, save behavior, and generated scores."""

	def test_extract_outcode_supports_common_postcode_shapes(self):
		"""Outcode extraction should handle spaced, compact, and empty values consistently."""
		cases = [
			(None, None),
			("", None),
			("   ", None),
			("sw1a 1aa", "SW1A"),
			("SW1A1AA", "SW1A"),
			("AB", "AB"),
		]

		for raw_postcode, expected_outcode in cases:
			with self.subTest(raw_postcode=raw_postcode, expected_outcode=expected_outcode):
				self.assertEqual(
					_extract_outcode(raw_postcode),
					expected_outcode,
					msg=f"Expected outcode '{expected_outcode}' for input '{raw_postcode}', but got a different value.",
				)

	def test_neighborhood_save_normalizes_and_autofills_region_and_coordinates(self):
		"""Saving a neighborhood should normalize postcode and infer region/coordinates from outcode mapping."""
		region = Region.objects.create(region_name="Greater London")
		OutcodeCountyMapping.objects.create(
			outcode="SW1A",
			county="Greater London",
			lat=51.501,
			lon=-0.141,
		)

		neighborhood = Neighborhood.objects.create(
			neighborhood_name="Westminster",
			postcode="sw1a 1aa",
		)

		neighborhood.refresh_from_db()
		self.assertEqual(
			neighborhood.postcode,
			"SW1A1AA",
			msg="Neighborhood.save should store normalized compact uppercase postcode.",
		)
		self.assertEqual(
			neighborhood.region_id,
			region.region_id,
			msg="Neighborhood.save should auto-assign region using outcode-to-county mapping.",
		)
		self.assertAlmostEqual(
			neighborhood.lat,
			51.501,
			places=3,
			msg="Neighborhood.save should fill latitude from outcode mapping when missing.",
		)
		self.assertAlmostEqual(
			neighborhood.lon,
			-0.141,
			places=3,
			msg="Neighborhood.save should fill longitude from outcode mapping when missing.",
		)

	def test_habitability_generated_scores_follow_weighted_formulas(self):
		"""Generated fields should match the weighted formulas defined in the model."""
		region = Region.objects.create(region_name="Surrey")
		neighborhood = Neighborhood.objects.create(
			neighborhood_name="Guildford",
			postcode="GU11AA",
			region=region,
		)

		score = HabitabilityScores.objects.create(
			neighborhood=neighborhood,
			employment_rate=0.8,
			income=0.6,
			inflation=0.5,
			air_quality=0.7,
			water_quality=0.6,
			land_fertility=0.8,
			waste_management=0.9,
			education=0.85,
			healthcare=0.75,
			transportation=0.65,
			crime=0.7,
			politics=0.8,
			disaster_risks=0.6,
			civic_engagement=0.9,
			date_scored=date(2026, 3, 24),
		)
		score.refresh_from_db()

		expected_economy = (0.8 * 0.25) + (0.6 * 0.35) + (0.5 * 0.40)
		expected_environment = (0.7 * 0.20) + (0.6 * 0.15) + (0.8 * 0.25) + (0.9 * 0.40)
		expected_infrastructure = (0.85 * 0.30) + (0.75 * 0.30) + (0.65 * 0.40)
		expected_security = (0.7 * 0.30) + (0.8 * 0.25) + (0.6 * 0.30) + (0.9 * 0.15)
		expected_overall = (
			(expected_economy * 0.30)
			+ (expected_environment * 0.20)
			+ (expected_infrastructure * 0.30)
			+ (expected_security * 0.20)
		)

		self.assertAlmostEqual(
			score.economy_score,
			expected_economy,
			places=6,
			msg="economy_score should match weighted formula for employment, income, and inflation.",
		)
		self.assertAlmostEqual(
			score.environment_score,
			expected_environment,
			places=6,
			msg="environment_score should match weighted formula for environmental indicators.",
		)
		self.assertAlmostEqual(
			score.infrastructure_score,
			expected_infrastructure,
			places=6,
			msg="infrastructure_score should match weighted formula for education/healthcare/transportation.",
		)
		self.assertAlmostEqual(
			score.security_score,
			expected_security,
			places=6,
			msg="security_score should match weighted formula for crime/politics/disaster/civic metrics.",
		)
		self.assertAlmostEqual(
			score.overall_score,
			expected_overall,
			places=6,
			msg="overall_score should match weighted blend of the four category scores.",
		)


class HabitabilityApiTests(TestCase):
	"""Endpoint tests for neighborhood listing and postcode-based habitability retrieval."""

	def setUp(self):
		self.factory = RequestFactory()

	def _create_region_with_mapping(self, region_name, outcode, lat=51.0, lon=-0.1):
		region = Region.objects.create(region_name=region_name)
		OutcodeCountyMapping.objects.create(outcode=outcode, county=region_name, lat=lat, lon=lon)
		return region

	def _create_score_for_region(self, region, neighborhood_name, postcode, score_id=None):
		neighborhood = Neighborhood.objects.create(
			neighborhood_name=neighborhood_name,
			postcode=postcode,
			region=region,
		)
		return HabitabilityScores.objects.create(
			score_id=score_id,
			neighborhood=neighborhood,
			employment_rate=0.7,
			income=0.7,
			inflation=0.7,
			air_quality=0.7,
			water_quality=0.7,
			land_fertility=0.7,
			waste_management=0.7,
			education=0.7,
			healthcare=0.7,
			transportation=0.7,
			crime=0.7,
			politics=0.7,
			disaster_risks=0.7,
			civic_engagement=0.7,
			date_scored=date(2026, 3, 24),
		)

	def test_get_neighbourhoods_returns_ordered_payload(self):
		"""Neighbourhood endpoint should return ordered list with expected keys as JSON."""
		region = Region.objects.create(region_name="Kent")
		Neighborhood.objects.create(neighborhood_name="Second", postcode="ME11AA", region=region)
		Neighborhood.objects.create(neighborhood_name="Third", postcode="ME21AA", region=region)

		response = self.client.get("/api/v1/neighbourhoods")

		self.assertEqual(response.status_code, 200, msg="Expected 200 from neighbourhoods endpoint.")
		self.assertIsInstance(response, JsonResponse, msg="Expected Django JsonResponse object for API endpoint.")
		self.assertTrue(
			response["Content-Type"].startswith("application/json"),
			msg="Django JsonResponse must advertise JSON content type.",
		)

		payload = response.json()
		self.assertEqual(len(payload), 2, msg="Expected two neighborhoods in neighbourhoods payload.")
		self.assertListEqual(
			[item["postcode"] for item in payload],
			["ME11AA", "ME21AA"],
			msg="Neighbourhoods should be ordered by neighborhood_id and return compact postcodes.",
		)

	def test_get_habitability_by_postcode_returns_400_for_blank_postcode(self):
		"""Direct view call with blank postcode should return MISSING_POSTCODE response."""
		request = self.factory.get("/api/v1/habitability/")

		response = get_habitability_by_postcode(request, "   ")
		payload = response.json()

		self.assertEqual(response.status_code, 400, msg="Blank postcode should be rejected with HTTP 400.")
		self.assertEqual(payload["error"], "MISSING_POSTCODE", msg="Expected MISSING_POSTCODE error code.")

	def test_get_habitability_by_postcode_returns_score_when_score_id_matches_region_id(self):
		"""Endpoint should prioritize score lookup where score_id equals region_id."""
		region = self._create_region_with_mapping("Surrey", "RH1")
		score = self._create_score_for_region(
			region=region,
			neighborhood_name="Redhill",
			postcode="RH11AA",
			score_id=region.region_id,
		)

		response = self.client.get("/api/v1/habitability/RH1%201AA")
		payload = response.json()

		self.assertEqual(response.status_code, 200, msg="Expected 200 when habitability score is available.")
		self.assertEqual(payload["scoreId"], score.score_id, msg="Expected score_id lookup path to return exact score.")
		self.assertEqual(payload["regionName"], "Surrey", msg="Region name should match mapping-derived county.")
		self.assertEqual(payload["postcode"], "RH1 1AA", msg="Payload postcode should preserve normalized request form.")
		self.assertIn("overallScore", payload, msg="Serialized habitability payload should contain overallScore key.")

	def test_get_habitability_by_postcode_uses_relational_fallback_when_ids_do_not_align(self):
		"""If score_id != region_id, endpoint should fallback to neighborhood__region lookup."""
		region = self._create_region_with_mapping("Essex", "CM1")
		score = self._create_score_for_region(
			region=region,
			neighborhood_name="Chelmsford",
			postcode="CM11AA",
		)

		response = self.client.get("/api/v1/habitability/CM1%201AA")
		payload = response.json()

		self.assertEqual(response.status_code, 200, msg="Expected relational fallback to find score for region.")
		self.assertEqual(payload["scoreId"], score.score_id, msg="Fallback lookup should return region-linked score.")

	def test_get_habitability_by_postcode_returns_fallback_payload_when_county_mapping_missing(self):
		"""If outcode mapping is missing, endpoint should return a random existing score payload."""
		fallback_region = Region.objects.create(region_name="Fallbackshire")
		self._create_score_for_region(
			region=fallback_region,
			neighborhood_name="FallbackTown",
			postcode="FB11AA",
		)

		response = self.client.get("/api/v1/habitability/ZZ1%201AA")
		payload = response.json()

		self.assertEqual(response.status_code, 200, msg="Missing mapping should return fallback payload with HTTP 200.")
		self.assertIn("regionName", payload, msg="Fallback payload should still include serialized region data.")
		self.assertIn("overallScore", payload, msg="Fallback payload should include computed score fields.")

	def test_get_habitability_by_postcode_returns_404_when_region_not_found(self):
		"""Mapped county without a matching Region row should produce NOT_FOUND 404."""
		OutcodeCountyMapping.objects.create(outcode="AB1", county="NoSuchRegion", lat=10.0, lon=20.0)

		response = self.client.get("/api/v1/habitability/AB1%201AA")
		payload = response.json()

		self.assertEqual(response.status_code, 404, msg="Missing Region should return HTTP 404.")
		self.assertEqual(payload["error"], "NOT_FOUND", msg="Missing Region should map to NOT_FOUND error code.")

	def test_get_habitability_by_postcode_returns_404_when_region_exists_without_scores(self):
		"""Resolved region without any HabitabilityScores should produce NOT_FOUND 404."""
		self._create_region_with_mapping("Dorset", "DT1")

		response = self.client.get("/api/v1/habitability/DT1%201AA")
		payload = response.json()

		self.assertEqual(response.status_code, 404, msg="Missing scores for region should return HTTP 404.")
		self.assertEqual(
			payload["error"],
			"NOT_FOUND",
			msg="Expected NOT_FOUND code when no score is present for the resolved region.",
		)
