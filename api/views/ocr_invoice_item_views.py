from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from api.models import OCRInvoiceItem
from api.serializers import OCRInvoiceItemSerializer
from rest_framework.generics import RetrieveAPIView
from django.db.models import Count, Q, Sum
from datetime import datetime, timedelta
from collections import defaultdict
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

PAGINATION_SIZE = PageNumberPagination.page_size

class OCRInvoiceItemList(APIView):
    """
    API view to retrieve a list of OCR invoice items with optional filtering and pagination.
    Query Parameters:
        - invoice_no (str): Filter by invoice number.
        - supplier_id (str): Filter by supplier ID.
        - qty_match (bool): Filter by quantity match.
        - unit_price_match (bool): Filter by unit price match.
        - payment_terms_match (bool): Filter by payment terms match.
        - page_size (int): Number of items per page (default: 100000).
    """
    def get(self, request, format=None):
        queryset = OCRInvoiceItem.objects.all()

        # Optional filters
        invoice_no = request.query_params.get("invoice_no")
        supplier_id = request.query_params.get("supplier_id")
        qty_match = request.query_params.get("qty_match")
        unit_price_match = request.query_params.get("unit_price_match")
        payment_terms_match = request.query_params.get("payment_terms_match")

        if invoice_no:
            queryset = queryset.filter(invoice_no=invoice_no)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        if qty_match is not None:
            queryset = queryset.filter(qty_match=qty_match.lower() == "true")
        if unit_price_match is not None:
            queryset = queryset.filter(unit_price_match=unit_price_match.lower() == "true")
        if payment_terms_match is not None:
            queryset = queryset.filter(payment_terms_match=payment_terms_match.lower() == "true")

        paginator = PageNumberPagination()
        page_size = request.query_params.get("page_size", PAGINATION_SIZE)
        if not page_size:
            page_size = PAGINATION_SIZE
        paginator.page_size = page_size
        paginated_items = paginator.paginate_queryset(queryset, request)
        serializer = OCRInvoiceItemSerializer(paginated_items, many=True)
        return paginator.get_paginated_response(serializer.data)

class OCRInvoiceItemDetail(RetrieveAPIView):
    queryset = OCRInvoiceItem.objects.all()
    serializer_class = OCRInvoiceItemSerializer
    lookup_field = 'id'

class OCRInvoiceItemMetadata(APIView):
    """
    Returns distinct values for dropdowns/filters for OCRInvoiceItem fields.
    """
    def get(self, request, format=None):
        data = {
            'invoice_no': list(OCRInvoiceItem.objects.values_list('invoice_no', flat=True).distinct()),
            'supplier_id': list(OCRInvoiceItem.objects.values_list('supplier_id', flat=True).distinct()),
            'po_number': list(OCRInvoiceItem.objects.values_list('po_number', flat=True).distinct()),
        }
        return Response(data)

class OCRInvoiceItemKPI(APIView):
    """
    Returns summary KPIs for OCRInvoiceItem (e.g., match rates, totals, etc).
    """
    @swagger_auto_schema(
        operation_description="Get summary KPIs for OCR invoice items.",
        responses={200: openapi.Response(
            description="KPI summary",
            examples={
                "application/json": {
                    "kpiSection": {
                        "totalInvoices": 1200,
                        "totalInvoicesWithAlerts": 315,
                        "totalMaterialsWithQuantityMismatches": 128,
                        "totalMaterialsWithPriceMismatches": 204,
                        "totalInvoicesWithQuantityMismatches": 95,
                        "totalInvoicesWithAlertTerms": 180,
                        "totalInvoicesWithContractExceeded": 47,
                        "totalInvoicesWithEarlyPayments": 60,
                        "totalDifferenceInPrices": 15432.75,
                        "invoiceExceptionRate": 26.25
                    }
                }
            }
        )}
    )
    def get(self, request, format=None):
        # Get total invoices (distinct invoice numbers)
        total = OCRInvoiceItem.objects.values('invoice_no').distinct().count()
        
        # Get invoices with any type of alert
        invoices_with_alerts = OCRInvoiceItem.objects.filter(
            Q(qty_match=False) | Q(unit_price_match=False) | Q(payment_terms_match=False)
        ).values('invoice_no').distinct().count()
        
        # Get materials with quantity mismatches
        materials_qty_mismatch = OCRInvoiceItem.objects.filter(
            qty_match=False,
            condition_qty_match__in=['higher', 'lower']
        ).count()
        
        # Get materials with price mismatches
        materials_price_mismatch = OCRInvoiceItem.objects.filter(
            unit_price_match=False,
            condition_price_match__in=['higher', 'lower']
        ).count()
        
        # Get invoices with quantity mismatches
        invoices_qty_mismatch = OCRInvoiceItem.objects.filter(
            qty_match=False,
            condition_qty_match__in=['higher', 'lower']
        ).values('invoice_no').distinct().count()
        
        # Get invoices with payment terms alerts
        invoices_terms_alert = OCRInvoiceItem.objects.filter(
            payment_terms_match=False,
            condition_payment_terms__in=['higher', 'lower']
        ).values('invoice_no').distinct().count()
        
        # Get invoices with contract exceeded (payment terms higher than database)
        invoices_contract_exceeded = OCRInvoiceItem.objects.filter(
            payment_terms_match=False,
            condition_payment_terms='higher'
        ).values('invoice_no').distinct().count()
        
        # Get invoices with early payments (payment terms lower than database)
        invoices_early_payments = OCRInvoiceItem.objects.filter(
            payment_terms_match=False,
            condition_payment_terms='lower'
        ).values('invoice_no').distinct().count()
        
        # Calculate total price difference
        total_price_difference = OCRInvoiceItem.objects.filter(
            unit_price_match=False
        ).aggregate(
            total_diff=Sum('diff_unit_price')
        )['total_diff'] or 0
        
        # Calculate exception rate
        exception_rate = round((invoices_with_alerts / total * 100), 2) if total else 0

        return Response({
            "kpiSection": {
                "totalInvoices": total,
                "totalInvoicesWithAlerts": invoices_with_alerts,
                "totalMaterialsWithQuantityMismatches": materials_qty_mismatch,
                "totalMaterialsWithPriceMismatches": materials_price_mismatch,
                "totalInvoicesWithQuantityMismatches": invoices_qty_mismatch,
                "totalInvoicesWithAlertTerms": invoices_terms_alert,
                "totalInvoicesWithContractExceeded": invoices_contract_exceeded,
                "totalInvoicesWithEarlyPayments": invoices_early_payments,
                "totalDifferenceInPrices": float(total_price_difference),
                "invoiceExceptionRate": exception_rate
            }
        })

class OCRInvoiceItemAlerts(APIView):
    """
    Returns a summary table of detected alerts (incident, flag, count, percent).
    """
    @swagger_auto_schema(
        operation_description="Get detected alerts summary for OCR invoice items.",
        responses={200: openapi.Response(
            description="Alerts summary",
            examples={
                "application/json": {
                    "alertsDetected": [
                        {
                            "incident": "Low confidence in vendor name extraction",
                            "flag": "Lower",
                            "invoiceCount": 12,
                            "percentTotal": 15
                        }
                    ]
                }
            }
        )}
    )
    def get(self, request, format=None):
        total_invoices = OCRInvoiceItem.objects.values('invoice_no').distinct().count()
        
        # Get alerts data
        alerts_data = []
        
        # Quantity mismatch alerts
        qty_mismatch_count = OCRInvoiceItem.objects.filter(
            qty_match=False,
            condition_qty_match__in=['higher', 'lower']
        ).values('invoice_no').distinct().count()
        
        if qty_mismatch_count > 0:
            alerts_data.append({
                "incident": "Quantity mismatch between Invoice and PO",
                "flag": "Higher",
                "invoiceCount": qty_mismatch_count,
                "percentTotal": round((qty_mismatch_count / total_invoices * 100), 2) if total_invoices else 0
            })
            
        # Price mismatch alerts
        price_mismatch_count = OCRInvoiceItem.objects.filter(
            unit_price_match=False,
            condition_price_match__in=['higher', 'lower']
        ).values('invoice_no').distinct().count()
        
        if price_mismatch_count > 0:
            alerts_data.append({
                "incident": "Unit price mismatch between Invoice and PO",
                "flag": "Higher",
                "invoiceCount": price_mismatch_count,
                "percentTotal": round((price_mismatch_count / total_invoices * 100), 2) if total_invoices else 0
            })
            
        # Payment terms alerts
        terms_mismatch_count = OCRInvoiceItem.objects.filter(
            payment_terms_match=False,
            condition_payment_terms__in=['higher', 'lower']
        ).values('invoice_no').distinct().count()
        
        if terms_mismatch_count > 0:
            alerts_data.append({
                "incident": "Payment terms mismatch",
                "flag": "Higher",
                "invoiceCount": terms_mismatch_count,
                "percentTotal": round((terms_mismatch_count / total_invoices * 100), 2) if total_invoices else 0
            })
            
        return Response({
            "alertsDetected": alerts_data
        })

class OCRInvoiceItemAlertsGauge(APIView):
    """
    Returns the value for the alerts gauge (number of invoices with alerts days in advance/invoice tolerant limit).
    """
    @swagger_auto_schema(
        operation_description="Get gauge value for invoice alerts days in advance/tolerant limit.",
        responses={200: openapi.Response(
            description="Gauge value",
            examples={
                "application/json": {
                    "alertGauge": {
                        "invoiceAlertLeadAvg": 120.18,
                        "invoiceTolerantLimit": 200,
                        "threshold": 140
                    }
                }
            }
        )}
    )
    def get(self, request, format=None):
        # Calculate average days in advance for payment terms mismatches
        payment_terms_diff = OCRInvoiceItem.objects.filter(
            payment_terms_match=False,
            condition_payment_terms__in=['higher', 'lower']
        ).aggregate(
            avg_diff=Sum('diff_payment_terms')
        )['avg_diff'] or 0
        
        # Set tolerant limit and threshold
        invoice_tolerant_limit = 200  # Maximum allowed days
        threshold = 140  # Warning threshold
        
        return Response({
            "alertGauge": {
                "invoiceAlertLeadAvg": float(payment_terms_diff),
                "invoiceTolerantLimit": invoice_tolerant_limit,
                "threshold": threshold
            }
        })

class OCRInvoiceItemTimeseriesPayments(APIView):
    """
    Returns timeseries data for quantity invoices per day and quantity of invoices with mismatch payments per day.
    """
    @swagger_auto_schema(
        operation_description="Get timeseries data for invoices and payment mismatches per day.",
        responses={200: openapi.Response(
            description="Timeseries data",
            examples={
                "application/json": [
                    {"date": "2024-05-01", "total_qty": 10000, "alert_qty": 2000},
                    {"date": "2024-05-02", "total_qty": 9000, "alert_qty": 1800}
                ]
            }
        )}
    )
    def get(self, request, format=None):
        # Example/mock data
        today = datetime.today()
        data = []
        for i in range(10):
            day = today - timedelta(days=9-i)
            data.append({
                "date": day.strftime("%Y-%m-%d"),
                "total_qty": 10000 - i*500,
                "alert_qty": 2000 + i*100
            })
        return Response(data)

class OCRInvoiceItemTimeseriesMaterialPrices(APIView):
    """
    Returns timeseries data for qty invoices per day and qty of invoices with mismatch on material and prices.
    """
    @swagger_auto_schema(
        operation_description="Get timeseries data for qty invoices and material/price mismatches per day.",
        responses={200: openapi.Response(
            description="Timeseries data",
            examples={
                "application/json": [
                    {"date": "2024-05-01", "qty_invoices": 8000, "qty_with_alert": 1500},
                    {"date": "2024-05-02", "qty_invoices": 7600, "qty_with_alert": 1580}
                ]
            }
        )}
    )
    def get(self, request, format=None):
        # Example/mock data
        today = datetime.today()
        data = []
        for i in range(10):
            day = today - timedelta(days=9-i)
            data.append({
                "date": day.strftime("%Y-%m-%d"),
                "qty_invoices": 8000 - i*400,
                "qty_with_alert": 1500 + i*80
            })
        return Response(data)

class OCRInvoiceItemTimeseriesMaterialAlerts(APIView):
    """
    Returns total qty without alert and total qty with alerts per material.
    """
    @swagger_auto_schema(
        operation_description="Get total qty without alert and with alerts per material.",
        responses={200: openapi.Response(
            description="Material alert summary",
            examples={
                "application/json": [
                    {"material": "Leche", "qty_without_alert": 8000, "qty_with_alert": 2000},
                    {"material": "Queso", "qty_without_alert": 6000, "qty_with_alert": 1000}
                ]
            }
        )}
    )
    def get(self, request, format=None):
        # Example/mock data
        data = [
            {"material": "Leche", "qty_without_alert": 8000, "qty_with_alert": 2000},
            {"material": "Queso", "qty_without_alert": 6000, "qty_with_alert": 1000},
            {"material": "Parmesano", "qty_without_alert": 5000, "qty_with_alert": 500},
        ]
        return Response(data)

class OCRInvoiceItemMaterialPriceMismatch(APIView):
    """
    Returns daily material and price mismatches data.
    """
    @swagger_auto_schema(
        operation_description="Get daily material and price mismatches data.",
        responses={200: openapi.Response(
            description="Material and price mismatches data",
            examples={
                "application/json": {
                    "materialPriceMismatch": [
                        {
                            "date": "2025-05-01",
                            "totalInvoices": 320,
                            "materialMismatches": 50,
                            "priceMismatches": 30
                        }
                    ]
                }
            }
        )}
    )
    def get(self, request, format=None):
        # Get data for the last 31 days
        today = datetime.today()
        data = []
        
        for i in range(31):
            day = today - timedelta(days=30-i)
            date_str = day.strftime("%Y-%m-%d")
            
            # Get total invoices for the day
            total_invoices = OCRInvoiceItem.objects.filter(
                created_at__date=day.date()
            ).values('invoice_no').distinct().count()
            
            # Get material mismatches (qty_match=False)
            material_mismatches = OCRInvoiceItem.objects.filter(
                created_at__date=day.date(),
                qty_match=False,
                condition_qty_match__in=['higher', 'lower']
            ).values('invoice_no').distinct().count()
            
            # Get price mismatches (unit_price_match=False)
            price_mismatches = OCRInvoiceItem.objects.filter(
                created_at__date=day.date(),
                unit_price_match=False,
                condition_price_match__in=['higher', 'lower']
            ).values('invoice_no').distinct().count()
            
            data.append({
                "date": date_str,
                "totalInvoices": total_invoices,
                "materialMismatches": material_mismatches,
                "priceMismatches": price_mismatches
            })
            
        return Response({
            "materialPriceMismatch": data
        })

class OCRInvoiceItemMaterialAlerts(APIView):
    """
    Returns alerts per material type.
    """
    @swagger_auto_schema(
        operation_description="Get alerts per material type.",
        responses={200: openapi.Response(
            description="Material alerts data",
            examples={
                "application/json": {
                    "materialAlertPerMaterial": [
                        {
                            "material": "Material A",
                            "totalQty": 5000,
                            "alertedQty": 2000
                        }
                    ]
                }
            }
        )}
    )
    def get(self, request, format=None):
        # Get all materials with their total quantities and alerted quantities
        materials_data = OCRInvoiceItem.objects.values('material_description').annotate(
            totalQty=Count('id'),
            alertedQty=Count('id', filter=Q(
                qty_match=False,
                condition_qty_match__in=['higher', 'lower']
            ) | Q(
                unit_price_match=False,
                condition_price_match__in=['higher', 'lower']
            ))
        ).order_by('-totalQty')
        
        return Response({
            "materialAlertPerMaterial": [
                {
                    "material": item['material_description'],
                    "totalQty": item['totalQty'],
                    "alertedQty": item['alertedQty']
                }
                for item in materials_data
            ]
        })

class OCRInvoiceItemMismatch(APIView):
    """
    Returns daily invoice payment mismatches.
    """
    @swagger_auto_schema(
        operation_description="Get daily invoice payment mismatches.",
        responses={200: openapi.Response(
            description="Invoice payment mismatches data",
            examples={
                "application/json": {
                    "invoiceMismatch": [
                        {
                            "date": "2025-05-01",
                            "totalInvoices": 320,
                            "mismatchPayments": 45
                        }
                    ]
                }
            }
        )}
    )
    def get(self, request, format=None):
        # Get data for the last 31 days
        today = datetime.today()
        data = []
        
        for i in range(31):
            day = today - timedelta(days=30-i)
            date_str = day.strftime("%Y-%m-%d")
            
            # Get total invoices for the day
            total_invoices = OCRInvoiceItem.objects.filter(
                created_at__date=day.date()
            ).values('invoice_no').distinct().count()
            
            # Get payment mismatches (payment_terms_match=False)
            mismatch_payments = OCRInvoiceItem.objects.filter(
                created_at__date=day.date(),
                payment_terms_match=False,
                condition_payment_terms__in=['higher', 'lower']
            ).values('invoice_no').distinct().count()
            
            data.append({
                "date": date_str,
                "totalInvoices": total_invoices,
                "mismatchPayments": mismatch_payments
            })
            
        return Response({
            "invoiceMismatch": data
        })

class OCRInvoiceItemDetails(APIView):
    """
    Returns detailed information about invoice items including invoice and PO details.
    """
    @swagger_auto_schema(
        operation_description="Get detailed information about invoice items.",
        responses={200: openapi.Response(
            description="Invoice details data",
            examples={
                "application/json": {
                    "invoiceDetails": [
                        {
                            "id": 1,
                            "invoice": "10001",
                            "invoiceItem": 1,
                            "material": "Milk",
                            "supplier": "DairyBest",
                            "supplierId": "60000001001",
                            "invQty": 34,
                            "invUnitPrice": 10.0,
                            "invTotalPrice": 340.0,
                            "invPaymentTerms": 30,
                            "poQty": 30,
                            "poUnitPrice": 5.0,
                            "poPaymentTerms": 20,
                            "sofiaFlag": "Payment Terms Mismatches"
                        }
                    ]
                }
            }
        )}
    )
    def get(self, request, format=None):
        # Get all invoice items with their details
        queryset = OCRInvoiceItem.objects.all()
        
        # Apply filters if provided
        invoice_no = request.query_params.get("invoice_no")
        supplier_id = request.query_params.get("supplier_id")
        material = request.query_params.get("material")
        
        if invoice_no:
            queryset = queryset.filter(invoice_no=invoice_no)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        if material:
            queryset = queryset.filter(material_description=material)
            
        # Get the data
        data = []
        for item in queryset:
            # Determine sofia flag based on mismatches
            sofia_flag = "No Issues"
            if not item.payment_terms_match and item.condition_payment_terms in ['higher', 'lower']:
                sofia_flag = "Payment Terms Mismatches"
            elif not item.unit_price_match and item.condition_price_match in ['higher', 'lower']:
                sofia_flag = "Prices Mismatch"
            elif not item.qty_match and item.condition_qty_match in ['higher', 'lower']:
                sofia_flag = "Qty Mismatch"
                
            data.append({
                "id": item.id,
                "invoice": item.invoice_no,
                "invoiceItem": item.invoice_item,
                "material": item.material_description,
                "supplier": item.supplier,
                "supplierId": item.supplier_id,
                "invQty": float(item.invoice_qty),
                "invUnitPrice": float(item.invoice_unit_price),
                "invTotalPrice": float(item.invoice_qty * item.invoice_unit_price),
                "invPaymentTerms": item.invoice_payment_terms,
                "poQty": float(item.database_qty),
                "poUnitPrice": float(item.database_unit_price),
                "poPaymentTerms": item.database_payment_terms,
                "sofiaFlag": sofia_flag
            })
            
        return Response({
            "invoiceDetails": data
        }) 