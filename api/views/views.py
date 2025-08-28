from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from ..models import Activity, Variant
from ..serializers import (
    ActivitySerializer,
    VariantSerializer,
)
from rest_framework.pagination import PageNumberPagination
from datetime import datetime





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
                activities = activities.filter(case__in=case_ids)
            if names:
                activities = activities.filter(name__in=names)
            # Note: The following filters are commented out because 'case' is a CharField, not a foreign key
            # If you need these filters, you'll need to add these fields to the Activity model
            # if type:
            #     activities = activities.filter(case__type=type)
            # if branch:
            #     activities = activities.filter(case__branch=branch)
            # if ramo:
            #     activities = activities.filter(case__ramo=ramo)
            # if brocker:
            #     activities = activities.filter(case__brocker=brocker)
            # if state:
            #     activities = activities.filter(case__state=state)
            # if client:
            #     activities = activities.filter(case__client=client)
            # if creator:
            #     activities = activities.filter(case__creator=creator)
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

                    activities = activities.filter(case__in=case_ids)
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
            

            attributes = [
                {"name": "case", "type": "number", "distincts": distinct_cases},
                {"name": "timestamp", "type": "date", "distincts": []},
                {"name": "name", "type": "str", "distincts": distinct_names},
               
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


# APIView to execute ORM queries via POST request
class ORMQueryExecutor(APIView):
    """
    Receives a Django ORM query as a string via POST and executes it.
    Request body: { "query": "Activity.objects.filter(name='Test')" }
    Returns: Queryset results or error message.
    """
    def post(self, request):
        script = request.data.get("script")
        if not script:
            return Response({"error": "Missing 'script' in request body."}, status=400)
        # Replace '\n' with actual line breaks
        script = script.replace("\\n", "\n")
        from django.db.models import Count, Sum, Avg, Min, Max, F, Q
        context = {
            "Activity": Activity,
            "Variant": Variant,
            "Count": Count,
            "Sum": Sum,
            "Avg": Avg,
            "Min": Min,
            "Max": Max,
            "F": F,
            "Q": Q,
        }
        # Remove import statements for objects already in context
        import re
        context_keys = set(context.keys())
        filtered_lines = []
        for line in script.splitlines():
            match = re.match(r"from\s+([\w\.]+)\s+import\s+([\w, ]+)", line.strip())
            if match:
                imported = [x.strip() for x in match.group(2).split(",")]
                # Skip import if all imported objects are already in context
                if all(obj in context_keys for obj in imported):
                    continue
            filtered_lines.append(line)
        script = "\n".join(filtered_lines)
        # End Remove import statements for objects already in context


        script = script.replace(".models", "")
        local_vars = {}
        try:
            exec(script, context, local_vars)
            result = local_vars.get("result")
            return Response({"result": result})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
