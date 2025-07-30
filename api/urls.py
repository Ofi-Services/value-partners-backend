from django.urls import path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


from .views.views import (
   ActivityList,
   VariantList,
)

"""
URL configuration for the API.
This module defines the URL patterns for the API endpoints and maps them to the corresponding views.
Endpoints:
- cases/ : List and create cases.
- activities/ : List and create activities.
- activities/<int:id>/ : Retrieve, update, and destroy a specific activity by ID.
- activity-list/ : List all activities.
- meta-data/ : Retrieve distinct activity data.
- variants/ : List all variants.
- KPI/ : List all KPIs.
- bills/ : List all bills.
- reworks/ : List all reworks.
"""
from . import views

schema_view = get_schema_view(
   openapi.Info(
      title="SOFIA API",
      default_version='v1',
      description="API documentation",
      terms_of_service="",
      contact=openapi.Contact(email="contact@ofiservices.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
 
   # API Endpoints
   path("activity/", ActivityList.as_view(), name="activity-list"),
 
   path('variant/', VariantList.as_view(), name='variant-list'),
  
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
  
]