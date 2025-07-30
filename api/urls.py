from django.urls import path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views.free_text_views import Alerts as FreeTextAlerts
from .views.duplicate_views import Alerts as DuplicateAlerts
from .views.rework_views import Alerts as ReworkAlerts
from .views.automation_views import Alerts as AutomationAlerts
from .views.otif_views import Alerts as OtifAlerts
from .views.process_mining_views import Alerts as ProcessMiningAlerts
from .views import three_match_views
from .views.contract_usage_views import (
    ContractUsageKPI,
    ContractUsageBranchTable,
    ContractUsageValueOpportunities,
    ContractUsageDevelopmentOverTime,
    ContractUsageClassification,
    ContractUsageKeyMetrics,
    ContractUsagePurchaseOrderItems,
    ContractUsageMetadata,
)
from .views.ocr_invoice_item_views import (
    OCRInvoiceItemList,
    OCRInvoiceItemDetail,
    OCRInvoiceItemMetadata,
    OCRInvoiceItemKPI,
    OCRInvoiceItemAlerts,
    OCRInvoiceItemAlertsGauge,
    OCRInvoiceItemTimeseriesPayments,
    OCRInvoiceItemTimeseriesMaterialPrices,
    OCRInvoiceItemTimeseriesMaterialAlerts,
    OCRInvoiceItemMaterialPriceMismatch,
    OCRInvoiceItemMaterialAlerts,
    OCRInvoiceItemMismatch,
    OCRInvoiceItemDetails,
)

from .views.views import (
   CaseList,
   ActivityList,
   VariantList,
   KPIList,
   InvoiceList,
   GroupList,
   InventoryList,
   OrderItemList,
   Alerts,
   SupplierStats,
   ActivityStats,
   DistinctActivityData,
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
   # Free Text Endpoints
   path('free-text/alerts/', FreeTextAlerts.as_view(), name='free-text-alerts'),


   # Duplicate Endpoints
   path('duplicate/alerts/', DuplicateAlerts.as_view(), name='duplicate-alerts'),


   # Process Mining Endpoints
   path('process-mining/alerts/', ProcessMiningAlerts.as_view(), name='process-mining-alerts'),

   # Rework Endpoints
   path('rework/alerts/', ReworkAlerts.as_view(), name='rework-alerts'),

   # Automation Endpoints
   path('automation/alerts/', AutomationAlerts.as_view(), name='automation-alerts'),

   # Otif Endpoints
   path('otif/alerts/', OtifAlerts.as_view(), name='otif-alerts'),

   #Three way match endpoints
   path('three-way-match/alerts/', three_match_views.Alerts.as_view(), name='three-way-match-alerts'),
   path('three-way-match/kpi/', three_match_views.KPIDataView.as_view(), name='three-way-match-kpi-data'),
   path('three-way-match/value-opportunities/', three_match_views.ValueOpportunitiesView.as_view(), name='three-way-match-value-opportunities'),
   path('three-way-match/development-over-time/', three_match_views.DevelopmentOverTimeView.as_view(), name='three-way-match-development-over-time'),
   path('three-way-match/key-metrics/', three_match_views.KeyMetricsByDimensionView.as_view(), name='three-way-match-key-metrics-by-dimension'),
   path('three-way-match/classification/', three_match_views.ClassificationByOrderItemsView.as_view(), name='three-way-match-classification-by-order-items'),
   path('three-way-match/orders/', three_match_views.PurchaseOrdersView.as_view(), name='three-way-match-purchase-orders'),

   # API Endpoints
   path("activity/", ActivityList.as_view(), name="activity-list"),
   path("activity/stats/", ActivityStats.as_view(), name="activity-list"),
   path('metadata/', DistinctActivityData.as_view(), name='distinct-activity-data'),
   path('variant/', VariantList.as_view(), name='variant-list'),
   path('kpi/', KPIList.as_view(), name='KPI-list'),
   path('kpi/<str:subpath>/', KPIList.as_view(), name='kpi-subpath-list'),
   path('invoice/', InvoiceList.as_view(), name='invoice-list'),
   path('group/', GroupList.as_view(), name='group-list'),
   path('case/', CaseList.as_view(), name='case-list'),
   path('inventory/', InventoryList.as_view(), name='inventory'),
   path('material/', OrderItemList.as_view(), name='materials'),
   path("alerts/", Alerts.as_view(), name="alerts"),
   path('supplier/stats/', SupplierStats.as_view(), name='supplier-summary'),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   
   # OCR Invoice Item Endpoints
   path('ocr-invoice-items/', OCRInvoiceItemList.as_view(), name='ocr-invoice-items-list'),
   path('ocr-invoice-items/<int:id>/', OCRInvoiceItemDetail.as_view(), name='ocr-invoice-items-detail'),
   path('ocr-invoice-items/metadata/', OCRInvoiceItemMetadata.as_view(), name='ocr-invoice-items-metadata'),
   path('ocr-invoice-items/kpi/', OCRInvoiceItemKPI.as_view(), name='ocr-invoice-items-kpi'),
   path('ocr-invoice-items/alerts/', OCRInvoiceItemAlerts.as_view(), name='ocr-invoice-items-alerts'),
   path('ocr-invoice-items/alerts-gauge/', OCRInvoiceItemAlertsGauge.as_view(), name='ocr-invoice-items-alerts-gauge'),
   path('ocr-invoice-items/timeseries/payments/', OCRInvoiceItemTimeseriesPayments.as_view(), name='ocr-invoice-items-timeseries-payments'),
   path('ocr-invoice-items/timeseries/material-prices/', OCRInvoiceItemTimeseriesMaterialPrices.as_view(), name='ocr-invoice-items-timeseries-material-prices'),
   path('ocr-invoice-items/timeseries/material-alerts/', OCRInvoiceItemTimeseriesMaterialAlerts.as_view(), name='ocr-invoice-items-timeseries-material-alerts'),
   path('ocr-invoice-items/material-price-mismatch/', OCRInvoiceItemMaterialPriceMismatch.as_view(), name='ocr-invoice-items-material-price-mismatch'),
   path('ocr-invoice-items/material-alerts/', OCRInvoiceItemMaterialAlerts.as_view(), name='ocr-invoice-items-material-alerts'),
   path('ocr-invoice-items/mismatch/', OCRInvoiceItemMismatch.as_view(), name='ocr-invoice-items-mismatch'),
   path('ocr-invoice-items/details/', OCRInvoiceItemDetails.as_view(), name='ocr-invoice-items-details'),
]

# Contract Usage Endpoints
urlpatterns += [
    path('contract-usage/kpi/', ContractUsageKPI.as_view(), name='contract-usage-kpi'),
    path('contract-usage/branch-table/', ContractUsageBranchTable.as_view(), name='contract-usage-branch-table'),
    path('contract-usage/value-opportunities/', ContractUsageValueOpportunities.as_view(), name='contract-usage-value-opportunities'),
    path('contract-usage/development-over-time/', ContractUsageDevelopmentOverTime.as_view(), name='contract-usage-development-over-time'),
    path('contract-usage/classification/', ContractUsageClassification.as_view(), name='contract-usage-classification'),
    path('contract-usage/key-metrics/', ContractUsageKeyMetrics.as_view(), name='contract-usage-key-metrics'),
    path('contract-usage/purchase-order-items/', ContractUsagePurchaseOrderItems.as_view(), name='contract-usage-purchase-order-items'),
    path('contract-usage/metadata/', ContractUsageMetadata.as_view(), name='contract-usage-metadata'),

]