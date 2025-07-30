from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, F, FloatField, ExpressionWrapper, Q
from datetime import timedelta, date
from dateutil.parser import parse as parse_date
from api.models import OrderItem, CatalogItem, Contract, Case, Supplier
from django.db.models.functions import TruncMonth, TruncQuarter, TruncYear
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# --- Shared utility functions ---
def get_contract_product_codes():
    return set(CatalogItem.objects.exclude(contract_id=None).values_list('product_code', flat=True))

def get_items(start, end):
    return OrderItem.objects.filter(order__order_date__range=(start, end))

def get_date_range(request):
    start_date_str = request.query_params.get("start_date", "2023-10-01")
    end_date_str = request.query_params.get("end_date", "2027-01-31")
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)
    previous_start = start_date - timedelta(days=(end_date - start_date).days)
    previous_end = start_date
    return start_date, end_date, previous_start, previous_end, start_date_str, end_date_str

# --- Swagger query parameters ---
contract_usage_query_params = [
    openapi.Parameter(
        'start_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING
    ),
    openapi.Parameter(
        'end_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING
    ),
]

# --- KPI Section ---
class ContractUsageKPI(APIView):
    """
    GET /contract-usage/kpi/
    Returns contract usage KPIs for the given date range.
    Query Parameters:
        - start_date (YYYY-MM-DD): Start date for filtering order items (default: 2023-10-01)
        - end_date (YYYY-MM-DD): End date for filtering order items (default: 2025-01-31)
    Response:
        {
            "kpi_section": {
                "orders": {"current": int, "previous": int},
                "order_items": {"current": int, "previous": int},
                "order_item_value": {"current": int, "previous": int},
                "contract_usage_count": {"current": int, "previous": int},
                "contract_usage_eur": {"current": int, "previous": int},
                "contract_usage_rate": {"current": float, "previous": float},
                "contract_available_but_not_used_count": {"current": int, "previous": int},
                "contract_available_but_not_used_eur": {"current": int, "previous": int}
            }
        }
    """
    @swagger_auto_schema(manual_parameters=contract_usage_query_params)
    def get(self, request, format=None):
        """
        Retrieve contract usage KPIs for the current and previous period.
        """
        start_date, end_date, previous_start, previous_end, *_ = get_date_range(request)
        contract_product_codes = get_contract_product_codes()

        def get_kpi_metrics(start, end):
            items = get_items(start, end)
            total_items = items.count()
            total_orders = items.values('order_id').distinct().count()
            total_value = items.aggregate(
                value=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
            )["value"] or 0
            contract_items_used = items.filter(material_code__in=contract_product_codes, contract_used=True)
            contract_items_not_used = items.filter(material_code__in=contract_product_codes, contract_used=False)
            contract_count = contract_items_used.count()
            contract_value = contract_items_used.aggregate(
                value=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
            )["value"] or 0
            contract_not_used_count = contract_items_not_used.count()
            contract_not_used_value = contract_items_not_used.aggregate(
                value=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
            )["value"] or 0
            contract_rate = (contract_count / total_items * 100) if total_items else 0
            return {
                "orders": total_orders,
                "order_items": total_items,
                "order_item_value": round(total_value),
                "contract_usage_count": contract_count,
                "contract_usage_eur": round(contract_value),
                "contract_usage_rate": round(contract_rate, 1),
                "contract_available_but_not_used_count": contract_not_used_count,
                "contract_available_but_not_used_eur": round(contract_not_used_value)
            }

        current_metrics = get_kpi_metrics(start_date, end_date)
        previous_metrics = get_kpi_metrics(previous_start, previous_end)
        return Response({
            "kpi_section": {
                "orders": {"current": current_metrics["orders"], "previous": previous_metrics["orders"]},
                "order_items": {"current": current_metrics["order_items"], "previous": previous_metrics["order_items"]},
                "order_item_value": {"current": current_metrics["order_item_value"], "previous": previous_metrics["order_item_value"]},
                "contract_usage_count": {"current": current_metrics["contract_usage_count"], "previous": previous_metrics["contract_usage_count"]},
                "contract_usage_eur": {"current": current_metrics["contract_usage_eur"], "previous": previous_metrics["contract_usage_eur"]},
                "contract_usage_rate": {"current": current_metrics["contract_usage_rate"], "previous": previous_metrics["contract_usage_rate"]},
                "contract_available_but_not_used_count": {"current": current_metrics["contract_available_but_not_used_count"], "previous": previous_metrics["contract_available_but_not_used_count"]},
                "contract_available_but_not_used_eur": {"current": current_metrics["contract_available_but_not_used_eur"], "previous": previous_metrics["contract_available_but_not_used_eur"]}
            }
        })

# --- Branch Table (Plant) ---
class ContractUsageBranchTable(APIView):
    """
    GET /contract-usage/branch-table/
    Returns contract usage metrics by plant (branch) for the given date range.
    Query Parameters:
        - start_date (YYYY-MM-DD)
        - end_date (YYYY-MM-DD)
    Response:
        {"branch_table": [{"plant": str, "usageRate": float, "usageEUR": int, "orderItems": int, "netOrderValue": int}, ...]}
    """
    @swagger_auto_schema(manual_parameters=contract_usage_query_params)
    def get(self, request, format=None):
        """
        Retrieve contract usage metrics by plant (branch).
        """
        start_date, end_date, *_ = get_date_range(request)
        contract_product_codes = get_contract_product_codes()
        items = get_items(start_date, end_date)
        plant_metrics = items.values('order__branch').annotate(
            usageRate=ExpressionWrapper(
                Count('id', filter=Q(material_code__in=contract_product_codes)) * 100.0 / Count('id'),
                output_field=FloatField()
            ),
            usageEUR=Sum(
                F('quantity') * F('unit_price'),
                filter=Q(material_code__in=contract_product_codes),
                output_field=FloatField()
            ),
            orderItems=Count('id'),
            netOrderValue=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
        ).order_by('-orderItems')
        return Response({
            "branch_table": [
                {
                    "plant": p['order__branch'],
                    "usageRate": round(p['usageRate'], 1),
                    "usageEUR": round(p['usageEUR'] or 0),
                    "orderItems": p['orderItems'],
                    "netOrderValue": round(p['netOrderValue'] or 0)
                } for p in plant_metrics
            ]
        })

# --- Value Opportunities ---
class ContractUsageValueOpportunities(APIView):
    """
    GET /contract-usage/value-opportunities/
    Returns value opportunities for contracts (missing, not used, used, expired) for the given date range.
    Query Parameters:
        - start_date (YYYY-MM-DD)
        - end_date (YYYY-MM-DD)
    Response:
        {"value_opportunities": [
            {"type": str, "orders": int, "orderItems": int, "netOrderValue": int}, ...
        ]}
    """
    @swagger_auto_schema(manual_parameters=contract_usage_query_params)
    def get(self, request, format=None):
        """
        Retrieve value opportunities for contracts.
        """
        start_date, end_date, *_ = get_date_range(request)
        contract_product_codes = get_contract_product_codes()
        items = get_items(start_date, end_date)
        missing_contract = items.exclude(material_code__in=CatalogItem.objects.values_list('product_code', flat=True))
        contract_not_used = items.filter(
            material_code__in=contract_product_codes,
            contract_used=False
        )
        contract_used = items.filter(
            material_code__in=contract_product_codes,
            contract_used=True
        )
        today = date.today()
        expired_contract_ids = Contract.objects.filter(end_date__lt=today).values_list('id', flat=True)
        expired_product_codes = CatalogItem.objects.filter(contract_id__in=expired_contract_ids).values_list('product_code', flat=True)
        contract_expired = items.filter(
            material_code__in=expired_product_codes,
            contract_used=False
        )
        def agg(qs):
            return {
                "orders": qs.values('order_id').distinct().count(),
                "orderItems": qs.count(),
                "netOrderValue": round(qs.aggregate(
                    value=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
                )["value"] or 0)
            }
        return Response({
            "value_opportunities": [
                {"type": "Missing Contract", **agg(missing_contract)},
                {"type": "Contract Available but not used", **agg(contract_not_used)},
                {"type": "Contract Available and used", **agg(contract_used)},
                {"type": "Contract Available but expired", **agg(contract_expired)},
            ]
        })

# --- Development Over Time ---
class ContractUsageDevelopmentOverTime(APIView):
    """
    GET /contract-usage/development-over-time/
    Returns contract usage development over time (monthly, quarterly, yearly).
    Query Parameters:
        - start_date (YYYY-MM-DD)
        - end_date (YYYY-MM-DD)
    Response:
        {"development_over_time": {
            "data": [{"name": str, "value": int, "rate": float}, ...],
            "timeframes": {
                "Month": {"data": [...]},
                "Quarter": {"data": [...]},
                "Year": {"data": [...]}
            }
        }}
    """
    @swagger_auto_schema(manual_parameters=contract_usage_query_params)
    def get(self, request, format=None):
        """
        Retrieve contract usage development over time (monthly, quarterly, yearly).
        """
        start_date, end_date, *_ = get_date_range(request)
        contract_product_codes = get_contract_product_codes()
        items = get_items(start_date, end_date)
        # Monthly
        monthly = items.annotate(month=TruncMonth('order__order_date')).values('month').annotate(
            value=Count('id'),
            rate=ExpressionWrapper(
                Count('id', filter=Q(material_code__in=contract_product_codes)) * 100.0 / Count('id'),
                output_field=FloatField()
            )
        ).order_by('month')
        # Quarterly
        quarterly = items.annotate(quarter=TruncQuarter('order__order_date')).values('quarter').annotate(
            value=Count('id'),
            rate=ExpressionWrapper(
                Count('id', filter=Q(material_code__in=contract_product_codes)) * 100.0 / Count('id'),
                output_field=FloatField()
            )
        ).order_by('quarter')
        # Yearly
        yearly = items.annotate(year=TruncYear('order__order_date')).values('year').annotate(
            value=Count('id'),
            rate=ExpressionWrapper(
                Count('id', filter=Q(material_code__in=contract_product_codes)) * 100.0 / Count('id'),
                output_field=FloatField()
            )
        ).order_by('year')
        return Response({
            "development_over_time": {
                "data": [
                    {"name": d['month'].strftime("%b-%Y"), "value": d['value'], "rate": round(d['rate'], 1)} for d in monthly
                ],
                "timeframes": {
                    "Month": {"data": [
                        {"name": d['month'].strftime("%b-%Y"), "value": d['value'], "rate": round(d['rate'], 1)} for d in monthly
                    ]},
                    "Quarter": {"data": [
                        {"name": f"Q{((d['quarter'].month-1)//3 + 1)}-{d['quarter'].year}", "value": d['value'], "rate": round(d['rate'], 1)} for d in quarterly
                    ]},
                    "Year": {"data": [
                        {"name": str(d['year'].year), "value": d['value'], "rate": round(d['rate'], 1)} for d in yearly
                    ]}
                }
            }
        })

# --- Contract Usage Classification ---
class ContractUsageClassification(APIView):
    """
    GET /contract-usage/classification/
    Returns contract usage classification percentages for the given date range.
    Query Parameters:
        - start_date (YYYY-MM-DD)
        - end_date (YYYY-MM-DD)
    Response:
        {"contract_usage_classification": [
            {"name": str, "value": float, "color": str}, ...
        ]}
    """
    @swagger_auto_schema(manual_parameters=contract_usage_query_params)
    def get(self, request, format=None):
        """
        Retrieve contract usage classification percentages.
        """
        start_date, end_date, *_ = get_date_range(request)
        contract_product_codes = get_contract_product_codes()
        items = get_items(start_date, end_date)
        total_items = items.count()
        if total_items == 0:
            return Response({"contract_usage_classification": []})
        contract_used = items.filter(material_code__in=contract_product_codes, contract_used=True).count()
        contract_available = items.filter(material_code__in=contract_product_codes, contract_used=False).count()
        no_contract = items.exclude(material_code__in=CatalogItem.objects.values_list('product_code', flat=True)).count()
        return Response({
            "contract_usage_classification": [
                {"name": "Contract available and used", "value": round((contract_used / total_items) * 100, 2), "color": "#4ade80"},
                {"name": "Contract available but not used", "value": round((contract_available / total_items) * 100, 2), "color": "#ef4444"},
                {"name": "No contract available", "value": round((no_contract / total_items) * 100, 2), "color": "#f97316"}
            ]
        })

# --- Key Metrics by Dimension (Plant, Supplier, Region, Country) ---
class ContractUsageKeyMetrics(APIView):
    """
    GET /contract-usage/key-metrics/
    Returns contract usage metrics by dimension (plant, supplier, region, country).
    Query Parameters:
        - start_date (YYYY-MM-DD)
        - end_date (YYYY-MM-DD)
    Response:
        {"key_metrics_by_dimension": { ... }}
    """
    @swagger_auto_schema(manual_parameters=contract_usage_query_params)
    def get(self, request, format=None):
        """
        Retrieve contract usage metrics by dimension.
        """
        start_date, end_date, *_ = get_date_range(request)
        contract_product_codes = get_contract_product_codes()
        items = get_items(start_date, end_date)
        # Plant
        plant_metrics = items.values('order__branch').annotate(
            usageRate=ExpressionWrapper(
                Count('id', filter=Q(material_code__in=contract_product_codes)) * 100.0 / Count('id'),
                output_field=FloatField()
            ),
            usageEUR=Sum(
                F('quantity') * F('unit_price'),
                filter=Q(material_code__in=contract_product_codes),
                output_field=FloatField()
            ),
            orderItems=Count('id'),
            netOrderValue=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
        ).order_by('-orderItems')
        # Supplier
        supplier_metrics = items.values('order__supplier_id').annotate(
            usageRate=ExpressionWrapper(
                Count('id', filter=Q(material_code__in=contract_product_codes)) * 100.0 / Count('id'),
                output_field=FloatField()
            ),
            usageEUR=Sum(
                F('quantity') * F('unit_price'),
                filter=Q(material_code__in=contract_product_codes),
                output_field=FloatField()
            ),
            orderItems=Count('id'),
            netOrderValue=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
        ).order_by('-orderItems')
        # Region (if available)
        region_metrics = items.values('order__region').annotate(
            usageRate=ExpressionWrapper(
                Count('id', filter=Q(material_code__in=contract_product_codes)) * 100.0 / Count('id'),
                output_field=FloatField()
            ),
            usageEUR=Sum(
                F('quantity') * F('unit_price'),
                filter=Q(material_code__in=contract_product_codes),
                output_field=FloatField()
            ),
            orderItems=Count('id'),
            netOrderValue=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
        ).order_by('-orderItems') if 'region' in [f.name for f in Case._meta.fields] else []
        # Country (if available)
        country_metrics = items.values('order__country').annotate(
            usageRate=ExpressionWrapper(
                Count('id', filter=Q(material_code__in=contract_product_codes)) * 100.0 / Count('id'),
                output_field=FloatField()
            ),
            usageEUR=Sum(
                F('quantity') * F('unit_price'),
                filter=Q(material_code__in=contract_product_codes),
                output_field=FloatField()
            )
        ).order_by('-usageEUR') if 'country' in [f.name for f in Case._meta.fields] else []
        return Response({
            "key_metrics_by_dimension": {
                "Plant": {
                    "data": [
                        {
                            "plant": p['order__branch'],
                            "usageRate": round(p['usageRate'], 1),
                            "usageEUR": round(p['usageEUR'] or 0),
                            "orderItems": p['orderItems'],
                            "netOrderValue": round(p['netOrderValue'] or 0)
                        } for p in plant_metrics
                    ]
                },
                "Supplier": {
                    "data": [
                        {
                            "supplier": Supplier.objects.get(id=s['order__supplier_id']).name if s['order__supplier_id'] else None,
                            "usageRate": round(s['usageRate'], 1),
                            "usageEUR": round(s['usageEUR'] or 0),
                            "orderItems": s['orderItems'],
                            "netOrderValue": round(s['netOrderValue'] or 0)
                        } for s in supplier_metrics
                    ]
                },
                **({"Region": {"data": [
                    {
                        "region": r['order__region'],
                        "usageRate": round(r['usageRate'], 1),
                        "usageEUR": round(r['usageEUR'] or 0),
                        "orderItems": r['orderItems'],
                        "netOrderValue": round(r['netOrderValue'] or 0)
                    } for r in region_metrics
                ]}} if region_metrics else {}),
                **({"Country": {"data": [
                    {
                        "country": c['order__country'],
                        "usageRate": round(c['usageRate'], 1),
                        "usageEUR": round(c['usageEUR'] or 0)
                    } for c in country_metrics
                ]}} if country_metrics else {})
            }
        })

# --- Purchase Order Items ---
class ContractUsagePurchaseOrderItems(APIView):
    """
    GET /contract-usage/purchase-order-items/
    Returns a sample of purchase order items for the given date range.
    Query Parameters:
        - start_date (YYYY-MM-DD)
        - end_date (YYYY-MM-DD)
    Response:
        {"purchase_order_items": [ ... ]}
    """
    @swagger_auto_schema(manual_parameters=contract_usage_query_params)
    def get(self, request, format=None):
        """
        Retrieve a sample of purchase order items.
        """
        start_date, end_date, *_ = get_date_range(request)
        contract_product_codes = get_contract_product_codes()
        items = OrderItem.objects.filter(order__order_date__range=(start_date, end_date))
        result = []
        for item in items:
            case = getattr(item, 'order', None)
            contract_ref = None
            classification = "No contract available"
            if item.material_code in contract_product_codes:
                contract_item = CatalogItem.objects.filter(product_code=item.material_code).first()
                if contract_item and contract_item.contract_id:
                    contract_ref = f"ContractItem_{contract_item.contract_id}"
                    classification = "Contract available and used" if item.contract_used else "Contract available but not used"
            result.append({
                "id": item.id,
                "plant": getattr(case, 'branch', None) if case else None,
                "contractRef": contract_ref,
                "classification": classification,
                "recommended": None,
                "quantity": item.quantity,
                "netUnitPrice": item.unit_price,
                "currency": "EUR",
                "value": round(item.quantity * item.unit_price, 2)
            })
        return Response({"purchase_order_items": result})

# --- Metadata Filters (for dropdowns etc.) ---
class ContractUsageMetadata(APIView):
    """
    GET /contract-usage/metadata/
    Returns metadata filters for contract usage dashboards (plants, regions, classifications).
    Response:
        {"filters": {"plants": [...], "regions": [...], "classifications": [...]}}
    """
    def get(self, request, format=None):
        """
        Retrieve metadata filters for contract usage dashboards.
        """
        plants = [
            {"id": branch, "name": branch}
            for branch in Case.objects.values_list("branch", flat=True).distinct() if branch
        ]
        regions = [
            {"id": region, "name": region}
            for region in Case.objects.values_list("region", flat=True).distinct() if region
        ] if 'region' in [f.name for f in Case._meta.fields] else []
        return Response({
            "filters": {
                "plants": plants,
                "regions": regions,
                "classifications": [
                    {"id": "CONTRACT_USED", "name": "Contract used"},
                    {"id": "NO_CONTRACT", "name": "No Contract used"},
                    {"id": "CONTRACT_AVAILABLE", "name": "Contract available"}
                ]
            }
        })
