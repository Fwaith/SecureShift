from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_reports),                        # GET  /api/v1/reports
    path('create', views.create_report),                # POST /api/v1/reports/create
    path('<int:report_id>', views.get_report),          # GET  /api/v1/reports/<id>
    path('upvote', views.upvote_report),                # POST /api/v1/reports/upvote
    path('upvote/remove', views.remove_upvote),         # POST /api/v1/reports/upvote/remove
]