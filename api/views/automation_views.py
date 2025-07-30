from rest_framework.views import APIView
from rest_framework.response import Response
import random

class Alerts(APIView):
    """
    API view to return a mock alert about activities that are automatic or manual.
    """
    def get(self, request, format=None):
        # Mock data for activities
        total_activities = random.randint(50, 100)  # Random total activities
        automatic_activities = random.randint(20, total_activities)  # Random automatic activities
        manual_activities = total_activities - automatic_activities  # Calculate manual activities

        # Generate the alert message
        if automatic_activities > manual_activities:
            message = f"There are {automatic_activities} automatic activities, which is higher than the {manual_activities} manual activities."
            alert_type = "automatic-dominant"
        else:
            message = f"There are {manual_activities} manual activities, which is higher than the {automatic_activities} automatic activities."
            alert_type = "manual-dominant"

        # Mock UUID for the alert
        alert_uuid = "mock-uuid-" + str(random.randint(1000, 9999))

        # Return the mock alert
        return Response(
            {
                "Alert": {
                    "content": {
                        "total_activities": total_activities,
                        "automatic_activities": automatic_activities,
                        "manual_activities": manual_activities,
                    },
                    "type": alert_type,
                    "message": message,
                    "UUID": alert_uuid,
                },
            }
        )