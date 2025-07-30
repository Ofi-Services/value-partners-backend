from rest_framework.views import APIView
from rest_framework.response import Response
import random
from django.db import models
from api.models import Case, OrderItem, Supplier, Inventory, Activity, Variant, Invoice, GoodRecevied

class Alerts(APIView):
  """
  API view to return alerts about three-way match issues.
  Alerts are generated if the rate of mismatches exceeds a threshold.
  """
  def get(self, request, format=None):
    # Calculate total GoodRecevied and mismatches
    total_items = GoodRecevied.objects.count()
    quantity_mismatches = GoodRecevied.objects.exclude(quantity=models.F('invoice__quantity')).count()
    value_mismatches = GoodRecevied.objects.exclude(unit_price=models.F('invoice__unit_price')).count()
    both_mismatches = GoodRecevied.objects.exclude(
      quantity=models.F('invoice__quantity')
    ).exclude(
      unit_price=models.F('invoice__unit_price')
    ).count()

    # Calculate rates
    quantity_mismatch_rate = quantity_mismatches / total_items if total_items else 0
    value_mismatch_rate = value_mismatches / total_items if total_items else 0
    both_mismatch_rate = both_mismatches / total_items if total_items else 0

    # Thresholds for alerts
    threshold = 0.1  # 10%

    alerts = []

    if quantity_mismatch_rate > threshold:
      alerts.append({
        "type": "quantity-mismatch",
        "message": f"High rate of quantity mismatches detected: {quantity_mismatches} out of {total_items} items ({quantity_mismatch_rate:.1%}).",
        "rate": round(quantity_mismatch_rate, 3),
        "UUID": "quantity-mismatch-" + str(random.randint(1000, 9999)),
      })

    if value_mismatch_rate > threshold:
      alerts.append({
        "type": "value-mismatch",
        "message": f"High rate of value mismatches detected: {value_mismatches} out of {total_items} items ({value_mismatch_rate:.1%}).",
        "rate": round(value_mismatch_rate, 3),
        "UUID": "value-mismatch-" + str(random.randint(1000, 9999)),
      })

    if both_mismatch_rate > threshold:
      alerts.append({
        "type": "quantity-and-value-mismatch",
        "message": f"High rate of items with both quantity and value mismatches: {both_mismatches} out of {total_items} items ({both_mismatch_rate:.1%}).",
        "rate": round(both_mismatch_rate, 3),
        "UUID": "both-mismatch-" + str(random.randint(1000, 9999)),
      })

    if not alerts:
      alerts.append({
        "type": "threeway-match-ok",
        "message": "Three-way match rates are within acceptable limits.",
        "UUID": "threeway-match-ok-" + str(random.randint(1000, 9999)),
      })

    return Response({"alerts": alerts})
class KPIDataView(APIView):
    """
    API view to return KPI data with real data from the database.
    """
    def get(self, request, format=None):
        total_orders = Case.objects.count()
        total_order_items = OrderItem.objects.count()
        total_order_value = Case.objects.aggregate(total=models.Sum('total_price'))['total'] or 0


        quantity_mismatch_count = GoodRecevied.objects.exclude(quantity=models.F('invoice__quantity')).count()
        quantity_mismatch_rate = quantity_mismatch_count / total_order_items if total_order_items else 0


        value_mismatch_count = GoodRecevied.objects.exclude(unit_price=models.F('invoice__unit_price')).count()
        value_mismatch_rate = value_mismatch_count / total_order_items if total_order_items else 0


        three_way_match_value = GoodRecevied.objects.filter(
            unit_price=models.F('invoice__unit_price'),
            quantity=models.F('invoice__quantity')
        ).aggregate(total=models.Sum(models.F('quantity') * models.F('unit_price')))['total'] or 0
        
        three_way_match_rate = Case.objects.filter(on_time=True, in_full=True).count() / total_orders if total_orders else 0

        kpi_data = {
            "totalOrders": total_orders,
            "totalOrderItems": total_order_items,
            "totalOrderValue": total_order_value,
            "quantityMismatchRate": round(quantity_mismatch_rate, 3),
            "valueMismatchRate": round(value_mismatch_rate, 3),
            "threeWayMatchValue": three_way_match_value,
            "threeWayMatchRate": round(three_way_match_rate, 3)
        }
        return Response(kpi_data)


class ValueOpportunitiesView(APIView):
    """
    API view to return value opportunities data.
    Returns a summary for each mismatch type in the specified template format.
    """
    def get(self, request, format=None):
        # Value mismatches: unit_price does not match invoice.unit_price
        value_mismatches = GoodRecevied.objects.exclude(unit_price=models.F('invoice__unit_price'))
        value_orders = value_mismatches.values('invoice_id').distinct().count()
        value_order_items = value_mismatches.count()
        value_net_order_value = value_mismatches.aggregate(
            total=models.Sum(models.F('quantity') * models.F('unit_price'))
        )['total'] or 0

        # Quantity mismatches: quantity does not match invoice.quantity
        quantity_mismatches = GoodRecevied.objects.exclude(quantity=models.F('invoice__quantity'))
        quantity_orders = quantity_mismatches.values('invoice_id').distinct().count()
        quantity_order_items = quantity_mismatches.count()
        quantity_net_order_value = quantity_mismatches.aggregate(
            total=models.Sum(models.F('quantity') * models.F('unit_price'))
        )['total'] or 0

        value_opportunities = [
            {
                "type": "Value mismatch",
                "orders": value_orders,
                "orderItems": value_order_items,
                "netOrderValue": value_net_order_value
            },
            {
                "type": "Quantity mismatch",
                "orders": quantity_orders,
                "orderItems": quantity_order_items,
                "netOrderValue": quantity_net_order_value
            }
        ]
        return Response(value_opportunities)


class DevelopmentOverTimeView(APIView):
    """
    API view to return development over time data.
    Returns the number of items and three way match rate for each month.
    """
    def get(self, request, format=None):
        from django.db.models.functions import TruncMonth
        from django.db.models import Count, Q

        # Annotate each GoodRecevied with its month
        goods_by_month = (
            GoodRecevied.objects
            .annotate(month=TruncMonth('invoice__date'))
            .values('month')
            .annotate(
                orderItems=Count('id'),
                threeWayMatchCount=Count(
                    'id',
                    filter=Q(
                        quantity=models.F('invoice__quantity'),
                        unit_price=models.F('invoice__unit_price')
                    )
                )
            )
            .order_by('month')
        )

        development_over_time = []
        for entry in goods_by_month:
            order_items = entry['orderItems']
            three_way_match_count = entry['threeWayMatchCount']
            three_way_match_rate = (
                three_way_match_count / order_items if order_items else 0
            )
            development_over_time.append({
                "month": entry['month'].strftime("%Y-%m") if entry['month'] else None,
                "orderItems": order_items,
                "threeWayMatchRate": round(three_way_match_rate, 3)
            })

        return Response(development_over_time)
    

class KeyMetricsByDimensionView(APIView):
  """
  API view to return key metrics by dimension (supplier) with real data.
  For each supplier, returns:
    - threeWayMatchRate: share of GoodRecevied where quantity and unit_price match invoice
    - orderItems: number of GoodRecevied for that supplier
    - netOrderValue: sum of quantity * unit_price for that supplier
  """
  def get(self, request, format=None):
      from django.db.models import Count, Sum, Q, F

      # Get all suppliers
      suppliers = Supplier.objects.all()
      data = []

      for supplier in suppliers:
          # All goods received for this supplier 
          goods = GoodRecevied.objects.filter(invoice__case__supplier=supplier)

          order_items = goods.count()
          net_order_value = goods.aggregate(
              total=Sum(F('quantity') * F('unit_price'))
          )['total'] or 0

          # Three way match: quantity and unit_price match invoice
          three_way_match_count = goods.filter(
              quantity=F('invoice__quantity'),
              unit_price=F('invoice__unit_price')
          ).count()
          three_way_match_rate = three_way_match_count / order_items if order_items else 0

          data.append({
              "supplier": supplier.name,
              "threeWayMatchRate": round(three_way_match_rate, 3),
              "orderItems": order_items,
              "netOrderValue": float(net_order_value),
          })

      return Response({
          "dimension": "supplier",
          "data": data
      })
  

class ClassificationByOrderItemsView(APIView):
    """
    API view to return classification by order items.
    """
    def get(self, request, format=None):
        classification_by_order_items = [
            {"reason": "Three Way Match", "orderItems": 150000},
            {"reason": "GR missing", "orderItems": 85000},
            {"reason": "Quantity match | IR mismatch", "orderItems": 60000},
            {"reason": "Order w/o quantity", "orderItems": 30000},
            {"reason": "Price mismatch", "orderItems": 45000},
            {"reason": "Invoice w/o PO", "orderItems": 25000},
            {"reason": "Duplicate invoice", "orderItems": 12000},
            {"reason": "Order closed before GR", "orderItems": 18000},
            {"reason": "Missing invoice", "orderItems": 22000},
            {"reason": "Manual intervention required", "orderItems": 17000},
            {"reason": "Supplier error", "orderItems": 28000},
            {"reason": "Currency mismatch", "orderItems": 14000},
            {"reason": "Partial delivery", "orderItems": 33000},
            {"reason": "No GR/IR link", "orderItems": 9000},
            {"reason": "Early invoice", "orderItems": 8000},
            {"reason": "Late invoice", "orderItems": 10000},
            {"reason": "Incorrect tax code", "orderItems": 6000},
            {"reason": "Blocked for payment", "orderItems": 16000},
            {"reason": "Vendor master issue", "orderItems": 11000},
            {"reason": "Order mismatch (unit)", "orderItems": 7000}
        ]
        return Response(classification_by_order_items)

class PurchaseOrdersView(APIView):
    """
    API view to return purchase orders data from the database.
    Each record follows the specified structure.
    """
    def get(self, request, format=None):
        purchase_orders = []
        goods = GoodRecevied.objects.select_related('invoice__case__supplier')

        for gr in goods:
            invoice = gr.invoice
            case = invoice.case
            supplier = case.supplier.name if case.supplier else None

            # Determine mismatches
            quantity_mismatch = gr.quantity != invoice.quantity
            value_mismatch = float(gr.unit_price) != float(invoice.unit_price)

            # Classification logic
            if not quantity_mismatch and not value_mismatch:
                classification = "Three Way Match"
            elif quantity_mismatch and value_mismatch:
                classification = "Quantity and value mismatch"
            elif quantity_mismatch:
                classification = "Quantity mismatch"
            elif value_mismatch:
                classification = "Value mismatch"
            else:
                classification = "Other"

            purchase_orders.append({
                "orderItemNr": f"{gr.id}",
                "supplier": supplier,
                "goodsReceived": True,
                "invoiced": True,
                "orderedQty": invoice.quantity,
                "grQty": gr.quantity,
                "irQty": invoice.quantity,
                "netAmount": float(invoice.value),
                "grValue": float(gr.quantity) * float(gr.unit_price),
                "irValue": float(invoice.quantity) * float(invoice.unit_price),
                "quantityMismatch": quantity_mismatch,
                "valueMismatch": value_mismatch,
                "classification": classification
            })

        return Response(purchase_orders)