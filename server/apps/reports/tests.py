import json
from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import JsonResponse
from django.test import TestCase

from habitability.models import OutcodeCountyMapping, Region
from reports.models import Comments, Report, Votes


class ReportsModelTests(TestCase):
	"""Model tests for Report, Votes, and Comments database constraints/relationships."""

	def setUp(self):
		self.warwickshire, _ = Region.objects.get_or_create(
			region_name="Warwickshire",
			defaults={'region_name': "Warwickshire"}
		)

		self.mapping, _ = OutcodeCountyMapping.objects.get_or_create(
			outcode="B76",
			defaults={"county": "Warwickshire", "lat": 52.55, "lon": -1.75}
		)

		self.user = self._create_user("model-owner")
		self.other_user = self._create_user("model-peer")

	def _create_user(self, username):
		return get_user_model().objects.create_user(
			username=username,
			password="StrongPass123!",
			email=f"{username}@example.com",
			postcode="B761AA",
		)

	def _create_report(self, user=None, **overrides):
		data = {
			"user": user or self.user,
			"postcode": "B761AA",
			"lat": 52.5,
			"lon": -1.9,
			"title": "Pothole on Main Street",
			"description": "Large pothole creating safety risk.",
			"severity": "high",
			"type": "road",
			"status": "pending",
			"date_submitted": date(2026, 3, 24),
			"vote_count": 0,
		}
		data.update(overrides)
		return Report.objects.create(**data)

	def test_report_string_representation_returns_title(self):
		"""Report.__str__ should return title for readable admin/debug output."""
		report = self._create_report(title="Streetlight outage")
		self.assertEqual(str(report), "Streetlight outage", msg="Expected __str__ to match report title exactly.")

	def test_votes_unique_constraint_allows_only_one_vote_per_user_per_report(self):
		"""Votes model should enforce one_vote_per_user unique constraint."""
		report = self._create_report(user=self.other_user)
		Votes.objects.create(user=self.user, report=report, date_voted=date(2026, 3, 24))

		with self.assertRaisesMessage(
			IntegrityError,
			"UNIQUE constraint failed",
			msg="Creating a second vote for same user/report should violate one_vote_per_user.",
		):
			Votes.objects.create(user=self.user, report=report, date_voted=date(2026, 3, 24))

	def test_votes_unique_constraint_still_allows_different_users(self):
		"""Different users should be able to vote on the same report."""
		report = self._create_report(user=self.user)
		first_vote = Votes.objects.create(user=self.user, report=report, date_voted=date(2026, 3, 24))
		second_vote = Votes.objects.create(user=self.other_user, report=report, date_voted=date(2026, 3, 24))

		self.assertNotEqual(
			first_vote.vote_id,
			second_vote.vote_id,
			msg="Votes by different users should create distinct rows for same report.",
		)

	def test_comments_reply_relationship_supports_nested_threads(self):
		"""Comments should support parent/child reply threading via reply_to relation."""
		report = self._create_report()
		parent = Comments.objects.create(report=report, user=self.user, description="Top-level issue")
		child = Comments.objects.create(
			report=report,
			user=self.other_user,
			description="I can confirm this.",
			reply_to=parent,
		)

		self.assertEqual(parent.replies.count(), 1, msg="Parent comment should have exactly one reply.")
		self.assertEqual(parent.replies.first(), child, msg="Reply should be accessible through parent.replies relation.")


class ReportsApiTests(TestCase):
	"""Endpoint coverage for active reports APIs, including auth and error handling."""

	def setUp(self):
		self.warwickshire, _ = Region.objects.get_or_create(
			region_name="Warwickshire",
			defaults={'region_name': "Warwickshire"}
		)

		self.mapping, _ = OutcodeCountyMapping.objects.get_or_create(
			outcode="B76",
			defaults={"county": "Warwickshire", "lat": 52.55, "lon": -1.75}
		)
  
		self.user = self._create_user("api-owner")
		self.other_user = self._create_user("api-peer")
    
	def _create_user(self, username):
		return get_user_model().objects.create_user(
			username=username,
			password="StrongPass123!",
			email=f"{username}@example.com",
			postcode="B761AA",
		)

	def _authenticate(self):
		session = self.client.session
		session["user_id"] = self.user.id
		session.save()

	def _create_report(self, user=None, **overrides):
		data = {
			"user": user or self.user,
			"postcode": "B761AA",
			"lat": 52.5,
			"lon": -1.9,
			"title": "Road hazard",
			"description": "Debris on carriageway",
			"severity": "medium",
			"type": "road",
			"status": "pending",
			"date_submitted": date(2026, 3, 24),
			"vote_count": 0,
		}
		data.update(overrides)
		return Report.objects.create(**data)

	def test_get_reports_overview_orders_by_newest_then_votes(self):
		"""Overview endpoint should sort by -date_submitted then -vote_count."""
		self._create_report(
			title="Older popular",
			user=self.other_user,
			date_submitted=date(2026, 3, 1),
			vote_count=50,
		)
		newest = self._create_report(
			title="Newest low votes",
			user=self.user,
			date_submitted=date(2026, 3, 22),
			vote_count=1,
		)

		response = self.client.get("/api/v1/reports/overview")
		payload = response.json()

		self.assertEqual(response.status_code, 200, msg="Expected HTTP 200 for overview endpoint.")
		self.assertIsInstance(response, JsonResponse, msg="Expected Django JsonResponse object from overview endpoint.")
		self.assertEqual(payload[0]["id"], newest.report_id, msg="Newest report should appear first in overview payload.")
		self.assertIn("votes", payload[0], msg="Overview payload should include vote count field.")

	def test_get_report_returns_nested_comments(self):
		"""Report detail endpoint should include top-level comments with nested replies."""
		report = self._create_report()
		parent = Comments.objects.create(report=report, user=self.user, description="Please fix urgently")
		Comments.objects.create(
			report=report,
			user=self.other_user,
			description="Council notified.",
			reply_to=parent,
		)

		response = self.client.get(f"/api/v1/reports/{report.report_id}")
		payload = response.json()

		self.assertEqual(response.status_code, 200, msg="Existing report detail should return HTTP 200.")
		self.assertEqual(len(payload["comments"]), 1, msg="Expected one top-level comment in serialized report.")
		self.assertEqual(
			len(payload["comments"][0]["comments"]),
			1,
			msg="Expected one nested reply within top-level comment serialization.",
		)

	def test_get_report_returns_404_for_missing_report(self):
		"""Detail endpoint should return NOT_FOUND for unknown report id."""
		response = self.client.get("/api/v1/reports/999999")
		payload = response.json()

		self.assertEqual(response.status_code, 404, msg="Unknown report should return HTTP 404.")
		self.assertEqual(payload["error"], "NOT_FOUND", msg="Unknown report should return NOT_FOUND error code.")

	def test_create_report_requires_authenticated_session(self):
		"""Report creation should reject anonymous requests with UNAUTHORIZED."""
		response = self.client.post(
			"/api/v1/reports/create",
			data=json.dumps({"postcode": "B76 1AA"}),
			content_type="application/json",
		)
		payload = response.json()

		self.assertEqual(response.status_code, 401, msg="Anonymous report creation must return HTTP 401.")
		self.assertEqual(payload["error"], "UNAUTHORIZED", msg="Expected UNAUTHORIZED error for anonymous create.")

	def test_create_report_validates_json_fields_and_outcode_mapping(self):
		"""Create endpoint should report invalid JSON, missing fields, and unknown outcode paths."""
		self._authenticate()

		invalid_json_response = self.client.post(
			"/api/v1/reports/create",
			data="{bad-json",
			content_type="application/json",
		)
		self.assertEqual(
			invalid_json_response.status_code,
			400,
			msg="Malformed JSON body should return HTTP 400.",
		)
		self.assertEqual(
			invalid_json_response.json()["error"],
			"INVALID_JSON",
			msg="Malformed JSON should map to INVALID_JSON error.",
		)

		missing_fields_response = self.client.post(
			"/api/v1/reports/create",
			data=json.dumps({"postcode": "B76 1AA", "title": "Only title"}),
			content_type="application/json",
		)
		self.assertEqual(
			missing_fields_response.status_code,
			400,
			msg="Missing required report fields should return HTTP 400.",
		)
		self.assertEqual(
			missing_fields_response.json()["error"],
			"MISSING_FIELDS",
			msg="Missing fields should map to MISSING_FIELDS error.",
		)

		invalid_postcode_response = self.client.post(
			"/api/v1/reports/create",
			data=json.dumps(
				{
					"postcode": "   ",
					"title": "Issue",
					"description": "Description",
					"severity": "high",
					"type": "road",
				}
			),
			content_type="application/json",
		)
		self.assertEqual(
			invalid_postcode_response.status_code,
			400,
			msg="Whitespace-only postcode should fail outcode extraction.",
		)
		self.assertEqual(
			invalid_postcode_response.json()["error"],
			"INVALID_POSTCODE",
			msg="Invalid extracted outcode should map to INVALID_POSTCODE error.",
		)

		unknown_outcode_response = self.client.post(
			"/api/v1/reports/create",
			data=json.dumps(
				{
					"postcode": "ZZ9 1AA",
					"title": "Issue",
					"description": "Description",
					"severity": "high",
					"type": "road",
				}
			),
			content_type="application/json",
		)
		self.assertEqual(
			unknown_outcode_response.status_code,
			400,
			msg="Unknown outcode should return OUTCODE_NOT_FOUND.",
		)
		self.assertEqual(
			unknown_outcode_response.json()["error"],
			"OUTCODE_NOT_FOUND",
			msg="Outcode miss should map to OUTCODE_NOT_FOUND error.",
		)

	def test_create_report_successfully_persists_report_with_mapped_coordinates(self):
		"""Create endpoint should persist report using coordinates mapped from postcode outcode."""
		self._authenticate()
		# Removed because we now create the mapping in setUp()  

		response = self.client.post(
			"/api/v1/reports/create",
			data=json.dumps(
				{
					"postcode": "B76 1AA",
					"title": "Damaged traffic light",
					"description": "Signals are not working",
					"severity": "high",
					"type": "infrastructure",
				}
			),
			content_type="application/json",
		)
		payload = response.json()
		created = Report.objects.get(title="Damaged traffic light")

		self.assertEqual(response.status_code, 200, msg="Valid create request should return HTTP 200.")
		self.assertTrue(payload["success"], msg="Successful create response should include success=True.")
		self.assertAlmostEqual(created.lat, 52.55, places=2, msg="Created report latitude should match outcode mapping.")
		self.assertAlmostEqual(created.lon, -1.75, places=2, msg="Created report longitude should match outcode mapping.")
		self.assertEqual(created.vote_count, 0, msg="New reports should default vote_count to zero.")

	def test_upvote_endpoint_handles_auth_success_and_duplicate_vote(self):
		"""Upvote endpoint should require auth, allow first vote, and block duplicates."""
		report = self._create_report(user=self.other_user)

		unauthorized_response = self.client.post(
			"/api/v1/reports/upvote",
			data=json.dumps({"reportId": report.report_id}),
			content_type="application/json",
		)
		self.assertEqual(
			unauthorized_response.status_code,
			401,
			msg="Anonymous upvote should return HTTP 401.",
		)

		self._authenticate()
		first_vote_response = self.client.post(
			"/api/v1/reports/upvote",
			data=json.dumps({"reportId": report.report_id}),
			content_type="application/json",
		)
		self.assertEqual(first_vote_response.status_code, 200, msg="First upvote should succeed with HTTP 200.")

		duplicate_vote_response = self.client.post(
			"/api/v1/reports/upvote",
			data=json.dumps({"reportId": report.report_id}),
			content_type="application/json",
		)
		report.refresh_from_db()

		self.assertEqual(
			duplicate_vote_response.status_code,
			400,
			msg="Second upvote from same user should return HTTP 400.",
		)
		self.assertEqual(
			duplicate_vote_response.json()["error"],
			"ALREADY_VOTED",
			msg="Duplicate upvote should map to ALREADY_VOTED error.",
		)
		self.assertEqual(report.vote_count, 1, msg="Duplicate upvote attempt must not increment vote_count twice.")

	def test_remove_upvote_handles_not_voted_and_success_paths(self):
		"""Remove-upvote should fail for non-voters and succeed for existing votes."""
		report = self._create_report(user=self.other_user, vote_count=1)
		self._authenticate()

		not_voted_response = self.client.post(
			"/api/v1/reports/upvote/remove",
			data=json.dumps({"reportId": report.report_id}),
			content_type="application/json",
		)
		self.assertEqual(
			not_voted_response.status_code,
			400,
			msg="Removing upvote before voting should return HTTP 400.",
		)
		self.assertEqual(
			not_voted_response.json()["error"],
			"NOT_VOTED",
			msg="Expected NOT_VOTED error when user has no vote row.",
		)

		Votes.objects.create(user=self.user, report=report, date_voted=date(2026, 3, 24))
		remove_response = self.client.post(
			"/api/v1/reports/upvote/remove",
			data=json.dumps({"reportId": report.report_id}),
			content_type="application/json",
		)
		report.refresh_from_db()

		self.assertEqual(remove_response.status_code, 200, msg="Existing vote removal should return HTTP 200.")
		self.assertEqual(report.vote_count, 0, msg="Vote count should decrement and never go below zero.")

	def test_add_comment_validates_auth_and_supports_replies(self):
		"""Comments endpoint should enforce auth and allow top-level and reply comments."""
		report = self._create_report()

		unauthorized_response = self.client.post(
			"/api/v1/comments",
			data=json.dumps({"reportId": report.report_id, "description": "Anonymous"}),
			content_type="application/json",
		)
		self.assertEqual(
			unauthorized_response.status_code,
			401,
			msg="Anonymous comment creation should return HTTP 401.",
		)

		self._authenticate()

		invalid_json_response = self.client.post(
			"/api/v1/comments",
			data="{bad-json",
			content_type="application/json",
		)
		self.assertEqual(
			invalid_json_response.status_code,
			400,
			msg="Malformed comment JSON should return HTTP 400.",
		)
		self.assertEqual(
			invalid_json_response.json()["error"],
			"INVALID_JSON",
			msg="Malformed comment JSON should map to INVALID_JSON error.",
		)

		missing_fields_response = self.client.post(
			"/api/v1/comments",
			data=json.dumps({"reportId": report.report_id}),
			content_type="application/json",
		)
		self.assertEqual(
			missing_fields_response.status_code,
			400,
			msg="Missing description should return HTTP 400.",
		)
		self.assertEqual(
			missing_fields_response.json()["error"],
			"MISSING_FIELDS",
			msg="Missing required comment fields should map to MISSING_FIELDS error.",
		)

		parent_not_found_response = self.client.post(
			"/api/v1/comments",
			data=json.dumps(
				{
					"reportId": report.report_id,
					"description": "Replying",
					"replyToCommentId": 999999,
				}
			),
			content_type="application/json",
		)
		self.assertEqual(
			parent_not_found_response.status_code,
			404,
			msg="Unknown parent comment should return HTTP 404.",
		)
		self.assertEqual(
			parent_not_found_response.json()["error"],
			"NOT_FOUND",
			msg="Unknown parent comment should map to NOT_FOUND.",
		)

		top_level_response = self.client.post(
			"/api/v1/comments",
			data=json.dumps({"reportId": report.report_id, "description": "Top-level comment"}),
			content_type="application/json",
		)
		self.assertEqual(top_level_response.status_code, 200, msg="Top-level comment create should return HTTP 200.")

		parent = Comments.objects.get(description="Top-level comment")
		reply_response = self.client.post(
			"/api/v1/comments",
			data=json.dumps(
				{
					"reportId": report.report_id,
					"description": "Nested reply",
					"replyToCommentId": parent.comment_id,
				}
			),
			content_type="application/json",
		)

		self.assertEqual(reply_response.status_code, 200, msg="Reply comment create should return HTTP 200.")
		self.assertTrue(
			Comments.objects.filter(reply_to=parent, description="Nested reply").exists(),
			msg="Reply comment row should be linked to parent comment via reply_to.",
		)
