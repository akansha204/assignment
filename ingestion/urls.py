from django.urls import path

from .views import (
    ActivityApproveView,
    ActivityEditView,
    ActivityListView,
    ActivityRejectView,
    SAPUploadView,
    TravelUploadView,
    UtilityUploadView,
)


urlpatterns = [
    path("upload/sap", SAPUploadView.as_view(), name="upload-sap"),
    path("upload/utility", UtilityUploadView.as_view(), name="upload-utility"),
    path("upload/travel", TravelUploadView.as_view(), name="upload-travel"),
    path("activities", ActivityListView.as_view(), name="activity-list"),
    path("activities/<int:pk>/approve", ActivityApproveView.as_view(), name="activity-approve"),
    path("activities/<int:pk>/reject", ActivityRejectView.as_view(), name="activity-reject"),
    path("activities/<int:pk>/edit", ActivityEditView.as_view(), name="activity-edit"),
]
