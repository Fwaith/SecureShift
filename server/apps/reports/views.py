import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Report, Votes, Comments
from habitability.models import Neighborhood, OutcodeCountyMapping
from accounts.models import User

def _get_session_user(request):
    return User.objects.get(pk=request.session["user_id"])

def _extract_outcode(postcode):
    if not postcode:
        return None
    
    # Remove spaces and convert to uppercase
    clean_postcode = postcode.upper().replace(" ", "")
    
    # If longer than 4, drop last 3 and trim
    if len(clean_postcode) > 4:
        return clean_postcode[:-3].strip()
    
    return clean_postcode.strip()

def _lookup_coordinates_from_outcode(outcode):
    """Look up coordinates (lat, lon) for an outcode from OutcodeCountyMapping.
    
    Returns tuple (lat, lon) on success, or (None, None) if not found.
    """
    if not outcode:
        return None, None
    
    try:
        mapping = OutcodeCountyMapping.objects.get(outcode=outcode)
        return mapping.lat, mapping.lon
    except OutcodeCountyMapping.DoesNotExist:
        return None, None

def _format_report_status(status):
    normalized = (status or "").strip().lower().replace("_", " ")
    if normalized == "in progress":
        return "In Progress"
    if normalized == "resolved":
        return "Resolved"
    return "Pending"

def serialize_report_overview(report):
    return {
        "id": report.report_id,
        "lat": report.lat,
        "lng": report.lon,
        "type": report.type,
        "area": report.postcode,
        "severity": report.severity,
        "status": _format_report_status(report.status),
        "votes": report.vote_count,
        "timestamp": int(report.date_submitted.strftime("%s")) if report.date_submitted else None,
        "title": report.title,
    }

def serialize_comment(comment):
    return {
        "commentId": comment.comment_id,
        "reportId": comment.report_id,
        "username": comment.user.username,
        "description": comment.description,
        "createdAt": int(comment.created_at.timestamp()),
        "replyToCommentId": comment.reply_to_id,
        "comments": [serialize_comment(r) for r in comment.replies.all()],
    }


def serialize_report(report, include_comments=False):
    data = {
        "reportId": report.report_id,
        "postcode": report.postcode,
        "lat": report.lat,
        "lon": report.lon,
        "username": report.user.username,
        "title": report.title,
        "description": report.description,
        "severity": report.severity,
        "type": report.type,
        "status": report.status,
        "voteCount": report.vote_count,
        "createdAt": int(report.date_submitted.strftime("%s")) if report.date_submitted else None,
    }
    if include_comments:
        top_level = report.comments.filter(reply_to=None).prefetch_related("replies")
        data["comments"] = [serialize_comment(c) for c in top_level]
    return data


# GET /api/v1/reports?neighbourhoodId=1
# Depreciated
@csrf_exempt
@require_http_methods(["GET"])
def get_reports(request):
    raise NotImplementedError("This endpoint is deprecated and should not be used")
    neighbourhood_id = request.GET.get("neighbourhoodId")
    if not neighbourhood_id:
        return JsonResponse({"error": "MISSING_PARAM", "message": "neighbourhoodId is required"}, status=400)

    reports = Report.objects.filter(neighbourhood_id=neighbourhood_id).order_by("-vote_count")
    return JsonResponse([serialize_report(r) for r in reports], safe=False)


# GET /api/v1/reports/overview
@csrf_exempt
@require_http_methods(["GET"])
def get_reports_overview(request):
    reports = Report.objects.order_by("-date_submitted", "-vote_count")
    return JsonResponse([serialize_report_overview(r) for r in reports], safe=False)


# GET /api/v1/reports/<reportId>
@csrf_exempt
@require_http_methods(["GET"])
def get_report(request, report_id):
    try:
        report = Report.objects.get(pk=report_id)
    except Report.DoesNotExist:
        return JsonResponse({"error": "NOT_FOUND", "message": "Report not found"}, status=404)
    return JsonResponse(serialize_report(report, include_comments=True))


# POST /api/v1/reports
@csrf_exempt
@require_http_methods(["POST"])
def create_report(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "UNAUTHORIZED", "message": "Login required"}, status=401)
    user = _get_session_user(request)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "INVALID_JSON", "message": "Invalid JSON body"}, status=400)

    postcode = body.get("postcode")
    title = body.get("title")
    description = body.get("description")
    severity = body.get("severity")
    report_type = body.get("type")

    if not all([postcode, title, description, severity, report_type]):
        return JsonResponse(
            {
                "error": "MISSING_FIELDS",
                "message": "postcode, title, description, severity and type are required",
            },
            status=400,
        )

    # Extract outcode and look up coordinates
    outcode = _extract_outcode(postcode)
    if not outcode:
        return JsonResponse(
            {
                "error": "INVALID_POSTCODE",
                "message": "Could not extract outcode from postcode",
            },
            status=400,
        )

    lat, lon = _lookup_coordinates_from_outcode(outcode)
    if lat is None or lon is None:
        return JsonResponse(
            {
                "error": "OUTCODE_NOT_FOUND",
                "message": f"Outcode '{outcode}' not found in mapping database",
            },
            status=400,
        )

    Report.objects.create(
        user=user,
        postcode=postcode,
        lat=lat,
        lon=lon,
        title=title,
        description=description,
        severity=severity,
        type=report_type,
        status="pending",
        vote_count=0,
        date_submitted=timezone.now().date(),
    )
    return JsonResponse({"success": True, "message": "Report created"})


# POST /api/v1/reports/upvote
@csrf_exempt
@require_http_methods(["POST"])
def upvote_report(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "UNAUTHORIZED", "message": "Login required"}, status=401)
    user = _get_session_user(request)

    try:
        body = json.loads(request.body)
        report = Report.objects.get(pk=body.get("reportId"))
    except (json.JSONDecodeError, Report.DoesNotExist):
        return JsonResponse({"error": "NOT_FOUND", "message": "Report not found"}, status=404)

    _, created = Votes.objects.get_or_create(
        user=user, report=report,
        defaults={"date_voted": timezone.now().date()}
    )
    if not created:
        return JsonResponse({"error": "ALREADY_VOTED", "message": "You have already upvoted this report"}, status=400)

    report.vote_count += 1
    report.save()
    return JsonResponse({"success": True, "message": "Vote added"})


# POST /api/v1/reports/upvote/remove
@csrf_exempt
@require_http_methods(["POST"])
def remove_upvote(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "UNAUTHORIZED", "message": "Login required"}, status=401)
    user = _get_session_user(request)

    try:
        body = json.loads(request.body)
        report = Report.objects.get(pk=body.get("reportId"))
    except (json.JSONDecodeError, Report.DoesNotExist):
        return JsonResponse({"error": "NOT_FOUND", "message": "Report not found"}, status=404)

    deleted, _ = Votes.objects.filter(user=user, report=report).delete()
    if not deleted:
        return JsonResponse({"error": "NOT_VOTED", "message": "You have not upvoted this report"}, status=400)

    report.vote_count = max(0, report.vote_count - 1)
    report.save()
    return JsonResponse({"success": True, "message": "Vote removed"})


# POST /api/v1/comments
@csrf_exempt
@require_http_methods(["POST"])
def add_comment(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "UNAUTHORIZED", "message": "Login required"}, status=401)
    user = _get_session_user(request)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "INVALID_JSON", "message": "Invalid JSON body"}, status=400)

    report_id = body.get("reportId")
    description = body.get("description")
    reply_to_id = body.get("replyToCommentId")

    if not all([report_id, description]):
        return JsonResponse({"error": "MISSING_FIELDS", "message": "reportId and description are required"}, status=400)

    try:
        report = Report.objects.get(pk=report_id)
    except Report.DoesNotExist:
        return JsonResponse({"error": "NOT_FOUND", "message": "Report not found"}, status=404)

    reply_to = None
    if reply_to_id:
        try:
            reply_to = Comments.objects.get(pk=reply_to_id)
        except Comments.DoesNotExist:
            return JsonResponse({"error": "NOT_FOUND", "message": "Parent comment not found"}, status=404)

    Comments.objects.create(
        report=report,
        user=user,
        description=description,
        reply_to=reply_to,
    )
    return JsonResponse({"success": True, "message": "Comment added"})