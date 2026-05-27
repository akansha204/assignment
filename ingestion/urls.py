from django.urls import path

from .views import SAPUploadView, TravelUploadView, UtilityUploadView


urlpatterns = [
    path("upload/sap", SAPUploadView.as_view(), name="upload-sap"),
    path("upload/utility", UtilityUploadView.as_view(), name="upload-utility"),
    path("upload/travel", TravelUploadView.as_view(), name="upload-travel"),
]
