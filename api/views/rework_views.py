from rest_framework.views import APIView
from rest_framework.response import Response
import random

class Alerts(APIView):
    """
    API view to return a mock alert about rework in processes.
    """
    def get(self, request, format=None):
        # Mock data for rework
        total_processes = random.randint(50, 100)  # Random total processes
        rework_processes = random.randint(10, total_processes)  # Random rework processes
        non_rework_processes = total_processes - rework_processes  # Calculate non-rework processes

        # Generate the alert message
        if rework_processes > non_rework_processes:
            message = f"There has been a significant increase in rework processes. Out of {total_processes} total processes, {rework_processes} involved rework."
            alert_type = "rework-dominant"
        else:
            message = f"Rework processes are under control. Out of {total_processes} total processes, only {rework_processes} involved rework."
            alert_type = "rework-under-control"

        # Mock UUID for the alert
        alert_uuid = "mock-uuid-" + str(random.randint(1000, 9999))

        # Return the mock alert
        return Response(
            {
                "Alert": {
                    "content": {
                        "total_processes": total_processes,
                        "rework_processes": rework_processes,
                        "non_rework_processes": non_rework_processes,
                    },
                    "type": alert_type,
                    "message": message,
                    "UUID": alert_uuid,
                },
            }
        )