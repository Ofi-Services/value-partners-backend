
from ..models import Activity, Variant
from ..serializers import (
    ActivitySerializer,
    VariantSerializer,
)
from rest_framework.pagination import PageNumberPagination
from datetime import datetime

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView




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


class CaseExplorer(APIView):
    """
    Returns a JSON list for each case with:
    - case id
    - number of activities
    - throughput time (difference between first and last activity timestamps)
    - name and timestamp of first activity
    - name and timestamp of last activity
    """
    def get(self, request):
        try:
            cases = Activity.objects.values_list('case', flat=True).distinct()
            result = []
            for case_id in cases:
                activities = Activity.objects.filter(case=case_id).order_by('timestamp')
                if not activities.exists():
                    continue
                first = activities.first()
                last = activities.last()
                throughput = (last.timestamp - first.timestamp).total_seconds() if first and last else None
                result.append({
                    'case': case_id,
                    'activity_count': activities.count(),
                    'throughput_time_seconds': throughput,
                    'first_activity': {
                        'name': first.name,
                        'timestamp': first.timestamp,
                    },
                    'last_activity': {
                        'name': last.name,
                        'timestamp': last.timestamp,
                    }
                })
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class CaseActivityTimeline(APIView):
    """
    Returns a list of activities for a given case id, with timestamp and time since first activity.
    GET parameter: id
    """
    def get(self, request):
        case_id = request.query_params.get('id')
        if not case_id:
            return Response({'error': 'Missing id parameter.'}, status=400)
        activities = Activity.objects.filter(case=case_id).order_by('timestamp')
        if not activities.exists():
            return Response({'error': 'No activities found for this case.'}, status=404)
        first_time = activities.first().timestamp
        result = []
        for activity in activities:
            time_since_first = (activity.timestamp - first_time).total_seconds()
            result.append({
                'name': activity.name,
                'timestamp': activity.timestamp,
                'time_since_first_seconds': time_since_first
            })
        return Response(result)

# --- Automation Endpoints ---
class AvgAutomationRate(APIView):
    def get(self, request):
        return Response({"avg_automation_rate": 58})

class ActivityAutomationMetrics(APIView):
    def get(self, request):
        return Response({
            "activities": [
                {"activity": "01) Stampanti - Contratti", "automation_rate": 100, "avg_number_of_events": 21, "avg_tat": "0 days"},
                {"activity": "02) Stampanti - Cartellini", "automation_rate": 13, "avg_number_of_events": 1, "avg_tat": "1 day"},
                {"activity": "03) Stampanti - Dichiarazioni", "automation_rate": 11, "avg_number_of_events": 1, "avg_tat": "8 days"}
                # ... continue for all rows
            ]
        })

class UserTATMetrics(APIView):
    def get(self, request):
        return Response({
            "users": [
                {"activity": "01) Stampanti - Contratti", "user_id": "GBS01526", "avg_tat_seconds": 46311079},
                {"activity": "01) Stampanti - Contratti", "user_id": "-", "avg_tat_seconds": 94852386},
                {"activity": "02) Stampanti - Cartellini", "user_id": "GBS09123", "avg_tat_seconds": 0}
                # ... continue for all rows
            ]
        })

# --- Workload and Bottleneck Endpoints ---
class SystemTriggeredVsManual(APIView):
    def get(self, request):
        return Response({
            "automation_distribution": [
                {"type": "Manual", "percentage": 42.05},
                {"type": "System Triggered", "percentage": 57.95}
            ]
        })

class SystemViewDistribution(APIView):
    def get(self, request):
        return Response({
            "distribution": {
                "manual": {"mysella": 84019, "workday": 24857},
                "system_triggered": {"mysella": 73450, "workday": 73650}
            }
        })

class AutomationRatePerYear(APIView):
    def get(self, request):
        return Response({
            "years": [
                {"year": 2022, "automation_rate": 75},
                {"year": 2023, "automation_rate": 58},
                {"year": 2024, "automation_rate": 56},
                {"year": 2025, "automation_rate": 58}
            ]
        })

class BottlenecksTAT(APIView):
    def get(self, request):
        return Response({
            "activities": [
                {"activity": "Stampanti - Contratti", "tat_days": 501, "cases": 915},
                {"activity": "Stampanti - Cartellini", "tat_days": 901, "cases": 853},
                {"activity": " Stampanti - Dichiarazioni", "tat_days": 113, "cases": 762}
                # ...
            ]
        })

# --- System Overview Endpoints ---
class SystemOverviewKPIs(APIView):
    def get(self, request):
        return Response({
            "total_number_of_employees": 1091,
            "number_of_activities": 259007,
            "average_number_of_activities": 237,
            "tat_days": 1124
        })

class ActivitySystemDistribution(APIView):
    def get(self, request):
        return Response({
            "distribution": [
                {"system": "MySella", "percentage": 60.42},
                {"system": "Workday", "percentage": 39.58}
            ]
        })

class ActivityCountSystem(APIView):
    def get(self, request):
        return Response({
            "years": [
                {"year": 2022, "total_activities": 14870, "mysella_activities": 14870, "workday_activities": 0},
                {"year": 2023, "total_activities": 61313, "mysella_activities": 28519, "workday_activities": 32794},
                {"year": 2024, "total_activities": 106231, "mysella_activities": 72295, "workday_activities": 33936},
                {"year": 2025, "total_activities": 76503, "mysella_activities": 56695, "workday_activities": 19818}
            ]
        })

class ActivityTrend(APIView):
    def get(self, request):
        return Response({
            "years": [
                {"year": 2022, "number_of_activities": 14870, "avg_activities_per_case": 73},
                {"year": 2023, "number_of_activities": 61313, "avg_activities_per_case": 125},
                {"year": 2024, "number_of_activities": 106231, "avg_activities_per_case": 125},
                {"year": 2025, "number_of_activities": 76503, "avg_activities_per_case": 128}
            ]
        })

class ActivitiesPerformedOverYear(APIView):
    def get(self, request):
        return Response({
            "years": [
                {"year": 2022, "activity_count": 14870, "count": 73, "avg": 78},
                {"year": 2023, "activity_count": 61313, "count": 125, "avg": 90},
                {"year": 2024, "activity_count": 106313, "count": 125, "avg": 100},
                {"year": 2025, "activity_count": 76503, "count": 128, "avg": 71}
            ]
        })

class ActivitiesPerYear(APIView):
    def get(self, request):
        return Response({
            "activities": [
                {"name": "01) Stampanti - Contratti", "2022": 3438, "2023": 5868, "2024": 6012, "2025": 3132},
                {"name": "02) Stampanti - Cartellini", "2022": 136, "2023": 290, "2024": 201, "2025": 97},
                {"name": "03) Stampanti - Dichiarazioni", "2022": 135, "2023": 194, "2024": 191, "2025": 97},
                {"name": "05) Obblighi da CCNL", "2022": 137, "2023": 302, "2024": 302, "2025": 96},
                {"name": "06) Informativa sul Trattamento", "2022": 183, "2023": 1430, "2024": 1020, "2025": 0}
                # ... add more as needed
            ]
        })