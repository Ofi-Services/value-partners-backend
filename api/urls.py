from django.urls import path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


from .views.views import (
   ActivityList,
   VariantList,
   DistinctActivityData,
   ORMQueryExecutor,
   CaseExplorer,
   CaseActivityTimeline,
   SystemOverviewKPIs,
   ActivitySystemDistribution,
   ActivityCountSystem,
   ActivityTrend,
   ActivitiesPerformedOverYear,
   ActivitiesPerYear,
   AvgAutomationRate,
   ActivityAutomationMetrics,
   UserTATMetrics,
   SystemTriggeredVsManual,
   SystemViewDistribution,
   AutomationRatePerYear,
   BottlenecksTAT,
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


   path('metadata/', DistinctActivityData.as_view(), name='metadata-list'),

   path('query/', ORMQueryExecutor.as_view(), name='query'),

   path('case-explorer/', CaseExplorer.as_view(), name='case-explorer'),

   path('case/', CaseActivityTimeline.as_view(), name='case-list'),

   # System Overview Endpoints
   path('system-overview/kpis', SystemOverviewKPIs.as_view(), name='system-overview-kpis'),

   path('system-overview/activity-system-distribution', ActivitySystemDistribution.as_view(), name='activity-system-distribution'),

   path('system-overview/activity-count-system', ActivityCountSystem.as_view(), name='activity-count-system'),

   path('system-overview/activity-trend', ActivityTrend.as_view(), name='activity-trend'),

   path('system-overview/activities-performed-over-year', ActivitiesPerformedOverYear.as_view(), name='activities-performed-over-year'),

   path('system-overview/activities-per-year', ActivitiesPerYear.as_view(), name='activities-per-year'),

   # Automation Endpoints
   path('system-overview/avg-automation-rate', AvgAutomationRate.as_view(), name='avg-automation-rate'),

   path('automation/activity-metrics', ActivityAutomationMetrics.as_view(), name='activity-automation-metrics'),

   path('automation/user-tat', UserTATMetrics.as_view(), name='user-tat-metrics'),

   # Workload and Bottleneck Endpoints
   path('workload/system-triggered-vs-manual', SystemTriggeredVsManual.as_view(), name='system-triggered-vs-manual'),

   path('workload/system-view-distribution', SystemViewDistribution.as_view(), name='system-view-distribution'),

   path('workload/rate-per-year', AutomationRatePerYear.as_view(), name='automation-rate-per-year'),

   path('workload/bottlenecks-tat', BottlenecksTAT.as_view(), name='bottlenecks-tat'),

]