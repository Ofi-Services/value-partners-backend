from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from ..models import Case, Activity, Variant, Inventory, OrderItem, Invoice
from ..serializers import (
    CaseSerializer,
    ActivitySerializer,
    VariantSerializer,
    InvoiceSerializer,
    InventorySerializer,
    OrderItemSerializer,
)
from rest_framework.pagination import PageNumberPagination
from datetime import datetime
from django.db.models import Sum, Count, Q, F, FloatField
import random




PAGINATION_SIZE = PageNumberPagination.page_size

# Custom view for listing Activity objects with optional filtering and pagination
class ActivityList(APIView):
    """
    ActivityList APIView
    This API view is designed to retrieve a list of activities with optional filtering
    based on various query parameters. It supports pagination and allows filtering
    by case IDs, names, and other attributes.
    Methods:
        get(request):
            Handles GET requests to retrieve a filtered and paginated list of activities.
            Query Parameters:
                - case (list[str]): List of case IDs to filter activities.
                - name (list[str]): List of names to filter activities.
                - case_index (str): Case index to filter activities.
                - page_size (int): Number of activities per page (default: 100000).
                - type (str): Case type to filter activities.
                - branch (str): Case branch to filter activities.
                - ramo (str): Case ramo to filter activities.
                - brocker (str): Case brocker to filter activities.
                - state (str): Case state to filter activities.
                - client (str): Case client to filter activities.
                - creator (str): Case creator to filter activities.
                - var (list[str]): List of variant IDs to filter activities.
                - start_date (str): Start date (YYYY-MM-DD) to filter activities.
                - end_date (str): End date (YYYY-MM-DD) to filter activities.
                Response: A paginated response containing the filtered list of activities
                or an error message in case of failure.
            Raises:
                - 400 Bad Request: If the date format is invalid.
                - 500 Internal Server Error: If an unexpected error occurs.

    API view to retrieve list of activities with optional filtering by case IDs and names.
    Supports pagination.
    """

    def get(self, request):
        """
        Handle GET request to list activities with optional filtering and pagination.

        Args:
            request: The HTTP request object.

        Returns:
            Response: The paginated list of activities.
        """
        try:
            case_ids = request.query_params.getlist("case")
            names = request.query_params.getlist("name")
            case_index = request.query_params.get("case_index")
            page_size = request.query_params.get("page_size", PAGINATION_SIZE)
            type = request.query_params.get("type")
            branch = request.query_params.get("branch")
            ramo = request.query_params.get("ramo")
            brocker = request.query_params.get("brocker")
            state = request.query_params.get("state")
            client = request.query_params.get("client")
            creator = request.query_params.get("creator")
            variant_ids = request.query_params.getlist("var")
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")

            # Validate date format
            try:
                if start_date:
                    start_date = datetime.strptime(start_date, "%Y-%m-%d")
                if end_date:
                    end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."}, status=400
                )

            activities = Activity.objects.all()
            if case_index:
                activities = activities.filter(case_index=case_index)
            if case_ids:
                activities = activities.filter(case__id__in=case_ids)
            if names:
                activities = activities.filter(name__in=names)
            if type:
                activities = activities.filter(case__type=type)
            if branch:
                activities = activities.filter(case__branch=branch)
            if ramo:
                activities = activities.filter(case__ramo=ramo)
            if brocker:
                activities = activities.filter(case__brocker=brocker)
            if state:
                activities = activities.filter(case__state=state)
            if client:
                activities = activities.filter(case__client=client)
            if creator:
                activities = activities.filter(case__creator=creator)
            if variant_ids:
                variants = Variant.objects.filter(id__in=variant_ids)

                if variants:
                    case_ids = set()
                    for variant in variants:
                        case_ids.update(
                            {
                                case_id.strip().replace("'", "")
                                for case_id in variant.cases[1:-1].split(",")
                            }
                        )

                    activities = activities.filter(case__id__in=case_ids)
            if start_date:
                activities = activities.filter(timestamp__gte=start_date)
            if end_date:
                activities = activities.filter(timestamp__lte=end_date)

            activities = activities.order_by("timestamp")

            paginator = PageNumberPagination()
            paginator.page_size = page_size
            paginated_activities = paginator.paginate_queryset(activities, request)
            serializer = ActivitySerializer(paginated_activities, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# View for listing all distinct activity names and case IDs
class DistinctActivityData(APIView):
    """
    API view to retrieve a list of all distinct activity names and case IDs.
    """

    def get(self, request, format=None):
        """
        Handle GET request to list all distinct activity names and case IDs.

        Args:
            request: The HTTP request object.
            format: The format of the response.

        Returns:
            Response: The list of distinct activity names and case IDs.
        """
        try:
            distinct_names = list(
                Activity.objects.values_list("name", flat=True).distinct()
            )
            distinct_cases = list(
                Activity.objects.values_list("case", flat=True).distinct()
            )
            distinct_branches = list(
                Case.objects.values_list("branch", flat=True).distinct()
            )
            distinct_suppliers = list(
                Case.objects.values_list("supplier", flat=True).distinct()
            )
            distict_users = list(
                Activity.objects.values_list("user", flat=True).distinct()
            )
            distinct_user_types = list(
                Activity.objects.values_list("user_type", flat=True).distinct()
            )
            distinct_patterns = list(
                Invoice.objects.values_list("pattern", flat=True).distinct()
            )
            distinct_groups = list(
                Invoice.objects.values_list("group_id", flat=True).distinct()
            )
            distinct_payment = list(
                Invoice.objects.values_list("payment_method", flat=True).distinct()
            )

            attributes = [
                {"name": "case", "type": "number", "distincts": distinct_cases},
                {"name": "timestamp", "type": "date", "distincts": []},
                {"name": "name", "type": "str", "distincts": distinct_names},
                {"name": "branch", "type": "str", "distincts": distinct_branches},
                {"name": "supplier", "type": "str", "distincts": distinct_suppliers},
                {"name": "user", "type": "str", "distincts": distict_users},
                {"name": "user_type", "type": "str", "distincts": distinct_user_types},
                {"name": "pattern", "type": "str", "distincts": distinct_patterns},
                {"name": "group_id", "type": "number", "distincts": distinct_groups},
                {
                    "name": "payment_method",
                    "type": "str",
                    "distincts": distinct_payment,
                },
            ]

            return Response({"attributes": attributes})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class VariantList(APIView):
    """
    VariantList API View
    This API view is designed to retrieve a list of all distinct activity names and case IDs.
    It supports filtering by activity names and provides paginated results.
    Methods:
        get(request, format=None):
            Handles GET requests to retrieve and paginate the list of variants.
    Attributes:
        - activities_param: A list of activity names to filter the variants.
        - page_size: The number of items per page for pagination (default is 100,000).
        - variants: A queryset of Variant objects, optionally filtered by activities.
        - paginator: An instance of PageNumberPagination for handling pagination.
        - serializer: A serializer to convert the paginated queryset into JSON format.
    Query Parameters:
        - activities: A list of activity names to filter the variants (optional).
        - page_size: The number of items per page for pagination (optional, default is 100,000).
        - A paginated response containing the serialized list of variants, ordered by percentage in descending order.

    API view to retrieve a list of all distinct activity names and case IDs.
    """

    def get(self, request, format=None):
        """
        Handle GET request to list all distinct activity names and case IDs.

        Args:
            request: The HTTP request object.
            format: The format of the response.

        Returns:
            Response: The paginated list of variants.
        """
        activities_param = request.query_params.getlist("activities")
        page_size = request.query_params.get(
            "page_size", PAGINATION_SIZE
        )  # Default page size is 10 if not provided
        variants = Variant.objects.all()
        if activities_param:
            for param in activities_param:
                variants = variants.filter(activities__icontains=param)

        variants = variants.order_by("-percentage")

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_variants = paginator.paginate_queryset(variants, request)
        serializer = VariantSerializer(paginated_variants, many=True)
        return paginator.get_paginated_response(serializer.data)


class KPIList(APIView):
    """
    API view to retrieve various Key Performance Indicators (KPIs) based on the provided date range.
    Methods:
        get(request, format=None):
            Handles GET requests to calculate and return KPIs.
    KPIs:
        - case_quantity: Total number of distinct cases.
        - variant_quantity: Total number of variants.
        - bill_quantity: Total number of bills.
        - rework_quantity: Total number of reworks.
        - approved_cases: Total number of approved cases.
        - cancelled_by_company: Total number of cases cancelled by the company.
        - cancelled_by_broker: Total number of cases cancelled by the broker.
    Query Parameters:
        - start_date (str, optional): Start date for filtering data in the format 'YYYY-MM-DD'.
        - end_date (str, optional): End date for filtering data in the format 'YYYY-MM-DD'.
    Responses:
        - 200 OK: Returns a dictionary containing the calculated KPIs.
        - 400 Bad Request: Returned if the date format is invalid.
        - 500 Internal Server Error: Returned if an unexpected error occurs.
    Example Response:
            "case_quantity": 100,
            "variant_quantity": 50,
            "bill_quantity": 200,
            "rework_quantity": 10,
            "approved_cases": 80,
            "cancelled_by_company": 10,
            "cancelled_by_broker": 10
    """

    def get(self, request, subpath = None, format=None):
        
        try:
            startdate = request.query_params.get("start_date")
            enddate = request.query_params.get("end_date")

            # Validate date format
            try:
                if startdate:
                    startdate = datetime.strptime(startdate, "%Y-%m-%d")
                if enddate:
                    enddate = datetime.strptime(enddate, "%Y-%m-%d")
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."}, status=400
                )
            if subpath == "free-text":
                data = self.get_free_text_kpis()
                return Response(data)
            
            variants = Variant.objects.all()

            activities = Activity.objects.all()

            if startdate:
                activities = activities.filter(timestamp__gte=startdate)
            if enddate:
                activities = activities.filter(timestamp__lte=enddate)

            total_invoices = Invoice.objects.count()
            total_groups = Invoice.objects.values("group_id").distinct().count()
            total_open_invoices = Invoice.objects.filter(open=True).count()
            total_open_groups = (
                Invoice.objects.filter(open=True).values("group_id").distinct().count()
            )
            total_value = Invoice.objects.aggregate(Sum("value"))["value__sum"]
            total_open_value = Invoice.objects.filter(open=True).aggregate(
                Sum("value")
            )["value__sum"]
            case_quantity = activities.values("case").distinct().count()
            variant_quantity = variants.count()
            return Response(
                {
                    "case_quantity": case_quantity,
                    "variant_quantity": variant_quantity,
                    'total_potential_double_payment': total_invoices - total_groups,
                    'total_open_potential_double_payment': total_open_invoices - total_open_groups,
                    'total_value_of_potential_double_payment': total_value,
                    'total_value_of_open_potential_double_payment': total_open_value
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def get_free_text_kpis(self):
        total_cases = Case.objects.all().count()
        total_cases_amount = Case.objects.all().aggregate(total=Sum('total_price'))['total']
        total_items = OrderItem.objects.all().count()
        total_items_ft = OrderItem.objects.filter(is_free_text=True).count()

        total_items_ft_amount = OrderItem.objects.filter(is_free_text=True).aggregate(total=Sum(F('unit_price') * F('quantity')))['total']
        ft_percentage = (total_items_ft / total_items) * 100
        ft_amount_percentage = (total_items_ft_amount / total_cases_amount) * 100
        return {
            'total_cases': total_cases,
            'total_cases_amount': total_cases_amount,
            'total_items': total_items,
            'total_items_ft': total_items_ft,
            'total_items_ft_amount': total_items_ft_amount,
            'ft_percentage': ft_percentage,
            'ft_amount_percentage': ft_amount_percentage
           
        }

class InvoiceList(APIView):
    """
    API view to retrieve a list of invoices with optional filters.

    Filters:
        - reference: Filter by invoice references (multiple values allowed)
        - vendor: Filter by vendor names (multiple values allowed)
        - pattern: Filter by pattern types (multiple values allowed)
        - open: Filter by open status (true/false)
        - group: Filter by group ID
        - start_date: Filter by start date (inclusive)
        - end_date: Filter by end date (inclusive)
        - random: Randomize the order of the results (true/false)
    """

    def get(self, request, format=None):
        try:
            references = request.query_params.getlist("reference")
            vendors = request.query_params.getlist("vendor")
            patterns = request.query_params.getlist("pattern")
            open = request.query_params.get("open")
            group = request.query_params.get("group_id")
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            random = request.query_params.get("random")

            print(
                f"Received request with filters: references={references}, vendors={vendors}, patterns={patterns}, open={open}, group={group}, start_date={start_date}, end_date={end_date}, random={random}"
            )

            invoices = Invoice.objects.all()
            print(f"Found {invoices.count()} invoices")
            if references:
                invoices = invoices.filter(reference__in=references)
            if vendors:
                invoices = invoices.filter(vendor__in=vendors)
            if patterns:
                invoices = invoices.filter(pattern__in=patterns)
            if open:
                invoices = invoices.filter(open=open.lower() == "true")
            if group:
                invoices = invoices.filter(group_id=group)
            if start_date:
                invoices = invoices.filter(date__gte=start_date)
            if end_date:
                invoices = invoices.filter(date__lte=end_date)
            if random and random.lower() == "true":
                invoices = invoices.order_by("?")

            paginator = PageNumberPagination()
            page_size = request.query_params.get("page_size", PAGINATION_SIZE)
            if not page_size:
                page_size = PAGINATION_SIZE
            paginator.page_size = page_size
            paginated_invoices = paginator.paginate_queryset(invoices, request)
            serializer = InvoiceSerializer(paginated_invoices, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            print(f"Error processing request: {e}")
            return Response({"error": str(e)}, status=500)


class GroupList(APIView):
    """
    API view to retrieve a paginated list of invoice groups with aggregated data.
    Methods:
        get(request, format=None):
            Handles GET requests to retrieve a list of invoice groups with their
            aggregated data, including overpaid amount, item count, date, region,
            pattern, open status, confidence, and serialized invoice items.
    Attributes:
        None
    GET Parameters:
        - page_size (int, optional): The number of groups to display per page. Defaults to 20.
    Aggregated Data for Each Group:
        - group_id (int): The unique identifier of the group.
        - amount_overpaid (float): The total overpaid amount for the group, calculated
          as the sum of invoice values minus the value of the first invoice in the group.
        - itemCount (int): The total number of invoices in the group.
        - date (datetime): The date of the earliest invoice in the group.
        - region (str): The region of the first invoice in the group.
        - pattern (str): The pattern associated with the first invoice in the group.
        - open (bool): The open status of the first invoice in the group.
        - confidence (float): The confidence level of the first invoice in the group.
        - items (list): A serialized list of all invoices in the group.
    Returns:
        Response: A paginated response containing the aggregated group data or an error message
        with a 500 status code in case of an exception.
    Exceptions:
        - Handles any exceptions during processing and returns a 500 status code with an error message.
    """

    def get(self, request, format=None):
        try:
            group_list = Invoice.objects.values_list("group_id", flat=True).distinct()
            group_data = []

            for group_id in group_list:
                group_invoices = Invoice.objects.filter(group_id=group_id)
                group_value = group_invoices.aggregate(Sum("value"))["value__sum"]
                first_invoice_value = (
                    group_invoices.first().value if group_invoices.exists() else 0
                )
                group_value -= first_invoice_value
                group_invoices_count = group_invoices.count()
                serialized_invoices = InvoiceSerializer(group_invoices, many=True).data

                group_data.append(
                    {
                        "group_id": group_id,
                        "amount_overpaid": group_value,
                        "itemCount": group_invoices_count,
                        "date": (
                            group_invoices.order_by("date").first().date
                            if group_invoices.exists()
                            else None
                        ),
                        "pattern": (
                            group_invoices.first().pattern
                            if group_invoices.exists()
                            else None
                        ),
                        "open": (
                            group_invoices.first().open
                            if group_invoices.exists()
                            else None
                        ),
                        "confidence": (
                            group_invoices.first().confidence
                            if group_invoices.exists()
                            else None
                        ),
                        "items": serialized_invoices,
                    }
                )

            paginator = PageNumberPagination()
            page_size = request.query_params.get("page_size", PAGINATION_SIZE)
            if not page_size:
                page_size = PAGINATION_SIZE
            paginator.page_size = page_size
            paginated_group_data = paginator.paginate_queryset(group_data, request)
            return paginator.get_paginated_response(paginated_group_data)

        except Exception as e:
            print(f"Error processing request: {e}")
            return Response({"error": str(e)}, status=500)


class InventoryList(APIView):
    """
    API view to retrieve a list of inventory items with optional filtering and pagination.
    Methods:
        get(request, format=None):
            Handles GET requests to retrieve and paginate the list of inventory items.
    Query Parameters:
        - page_size (int): Number of inventory items per page (default: 100000).
        - A paginated response containing the serialized list of inventory items.
    """

    def get(self, request, format=None):
        """
        Handle GET request to list inventory items with optional filtering and pagination.

        Args:
            request: The HTTP request object.
            format: The format of the response.

        Returns:
            Response: The paginated list of inventory items.
        """
        page_size = request.query_params.get(
            "page_size", PAGINATION_SIZE
        )  # Default page size is 10 if not provided
        inventories = Inventory.objects.all()

        paginator = PageNumberPagination()
        page_size = request.query_params.get("page_size", PAGINATION_SIZE)
        if not page_size:
            page_size = PAGINATION_SIZE
        paginator.page_size = page_size
        paginated_inventories = paginator.paginate_queryset(inventories, request)
        serializer = InventorySerializer(paginated_inventories, many=True)
        return paginator.get_paginated_response(serializer.data)


class CaseList(APIView):
    """
    API view to retrieve a list of cases with optional filtering and pagination.
    Includes aggregated activity data: total activities, rework activities, automatic activities,
    free text percentage, and free text price.
    """

    def get(self, request, format=None):
        """
        Handle GET request to list cases with optional filtering and pagination.

        Args:
            request: The HTTP request object.
            format: The format of the response.

        Returns:
            Response: The paginated list of cases with aggregated activity data.
        """
        # Annotate cases with activity counts
        cases = Case.objects.annotate(
            total_activities=Count("activities"),
            rework_activities=Count("activities", filter=Q(activities__rework=True)),
            automatic_activities=Count("activities", filter=Q(activities__automatic=True)),
            total_items=Count("orderitem"),  # Total items for the case
            free_text_items=Count("orderitem", filter=Q(orderitem__is_free_text=True)),  # Free text items
            free_text_price=Sum(
                F("orderitem__unit_price") * F("orderitem__quantity"),
                filter=Q(orderitem__is_free_text=True),
                output_field=FloatField()
            ),  # Total price of free text items
        ).annotate(
            free_text_percentage=F("free_text_items") * 100.0 / F("total_items")  # Calculate percentage
        )

        paginator = PageNumberPagination()
        page_size = request.query_params.get("page_size", PAGINATION_SIZE)
        if not page_size:
            page_size = PAGINATION_SIZE
        paginator.page_size = page_size
        paginated_cases = paginator.paginate_queryset(cases, request)
        serializer = CaseSerializer(paginated_cases, many=True)

        # Add aggregated data to the serialized response
        serialized_data = serializer.data
        for case, data in zip(cases, serialized_data):
            data["total_activities"] = case.total_activities
            data["rework_activities"] = case.rework_activities
            data["automatic_activities"] = case.automatic_activities
            data["free_text_percentage"] = round(case.free_text_percentage, 2) if case.total_items > 0 else 0.0
            data["free_text_price"] = round(case.free_text_price, 2)/10 if case.free_text_price else 0.0
            data["free_text_price_percentage"] = (
                round((case.free_text_price / case.total_price )*10, 2) 
                if case.free_text_price and case.total_price else 0.0
            )
        return paginator.get_paginated_response(serialized_data)
    
class OrderItemList(APIView):
    """
    API view to list the order items with optional filtering and pagination.
    This view handles GET requests to retrieve a list of order items.
    Methods:
        get(request, format=None):
    GET Method:
    """

    def get(self, request, format=None):
        """
        Handles GET requests to retrieve a list of order items.

        Query Parameters:
            material_code (list of str): List of material codes to filter order items.

        Returns:
            Response: Paginated response with serialized order item data.
        """
        # Get query parameters
        free_text_param = request.query_params.get('free_text')
        material_codes = request.query_params.getlist('material_code')

        if free_text_param is not None:
            free_text_param = free_text_param.lower()
            if free_text_param not in {"true", "false"}:
                return Response(
                    {"detail": "The 'free_text' param only allow 'true' or 'false'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            is_free_text = free_text_param == "true"
        else:
            is_free_text = None
            
        
        order_items = OrderItem.objects.all()
        # Filter order items by free text
        if is_free_text is not None:
            order_items = order_items.filter(is_free_text=is_free_text)
        # Filter order items by material code
        if material_codes:
            order_items = order_items.filter(material_code__in=material_codes)
            
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get(
            "page_size", PAGINATION_SIZE
        )  
        paginated_order_items = paginator.paginate_queryset(order_items, request)
        serializer = OrderItemSerializer(paginated_order_items, many=True)
        return paginator.get_paginated_response(serializer.data)


class Alerts(APIView):

    def get(self, request, format=None):
        return Response(
            {
                "Alert": {
                    "content": {
                        "new_invoices": 54,
                        "new_duplicate_invoices": 12,
                    },
                    "type": "duplicated",
                    "message": "The Canada Customs & Revenue Agency has 9 new invoices with a high confidence level of being duplicated. I recommend reviewing these invoices.",
                    "UUID": "173cc4a2d7b9fc54dc35b9951cc28a7308b9b394bc09fc7544134a0f015d19e6",
                },
            }
        )


class ActivityStats(APIView):
    """
    API view to retrieve a summary of all activities, including:
    - Total occurrences
    - Number of automatic activities
    - Number of rework activities
    """

    def get(self, request, format=None):
        try:
            # Aggregate data for activities
            activity_summary = (
                Activity.objects.values("name")
                .annotate(
                    total_occurrences=Count("id"),
                    automatic_count=Count("id", filter=Q(automatic=True)),
                    rework_count=Count("id", filter=Q(rework=True)),
                )
                .order_by("-total_occurrences")
            )

            return Response(activity_summary)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class SupplierStats(APIView):
    """
    API view to retrieve a summary of suppliers with:
    - Total number of cases
    - Number of cases on time
    - Number of cases in full
    - Number of OTIF (on time and in full) cases
    """

    def get(self, request, format=None):
        try:
            # Aggregate data for suppliers
            supplier_summary = (
                Case.objects.values("supplier")
                .annotate(
                    total_cases=Count("id"),
                    on_time_cases=Count("id", filter=Q(on_time=True)),
                    in_full_cases=Count("id", filter=Q(in_full=True)),
                    otif_cases=Count("id", filter=Q(on_time=True, in_full=True)),
                )
                .order_by("-total_cases")
            )

            return Response(supplier_summary)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
